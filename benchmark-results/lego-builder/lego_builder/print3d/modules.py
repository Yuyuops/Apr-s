"""Mode 2 : printed MODULES. The LDraw model is voxelised on the stud grid (8 mm x 8 mm x 3.2 mm plate), cut into modules that fit the print bed, rebuilt as solid per-colour bodies with LEGO-like studs on exposed
upper faces (parts without studs : tiles : leave a smooth face), and joined by dowels (cylindrical sockets in both faces). EXPERIMENTAL : bounding-box voxels, so slopes and rounds become blocks ;
nothing is validated in Bambu Studio or on a printer."""
import json, math, sqlite3
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import manifold3d as M
from .common import PARAMS, classify, colour_rgb, read_ldr, write_3mf, write_stl
from . import shapes
def voxelise(parts, catalog, shape_aware=False):
    occ = {}; stud = {}; ghost = set(); hulls = []                                         # (ix, iy, iz) -> colour ; stud flag of the part owning the voxel
    for p in parts:
        c = catalog.get(p["part"])
        if not c and shape_aware:
            pts = shapes.part_points(p["part"])
            if len(pts) < 4: continue
            c = dict(lo=pts.min(0).tolist(), hi=pts.max(0).tolist(), title="hull-only", studs=False)
        if not c: continue
        lo, hi = np.array(c["lo"], float), np.array(c["hi"], float); corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]); w = p["pos"] + corners @ p["rot"].T
        mn, mx = w.min(0), w.max(0); ix0, ix1 = int(round(mn[0] / 20)), int(round(mx[0] / 20)); iz0, iz1 = int(round(mn[2] / 20)), int(round(mx[2] / 20)); iy0, iy1 = int(round(-mx[1] / 8)), int(round(-mn[1] / 8))
        has_stud = bool(c.get("studs")) and "tile" not in c["title"].lower()
        is_hull = shape_aware and (p["part"] not in catalog or classify(p["part"], catalog) is None)
        if is_hull: hulls.append(p)
        for ix in range(ix0, ix1):
            for iz in range(iz0, iz1):
                for iy in range(iy0, iy1):
                    occ[(ix, iy, iz)] = p["colour"]; stud[(ix, iy, iz)] = has_stud
                    if is_hull: ghost.add((ix, iy, iz))
                    else: ghost.discard((ix, iy, iz))
    return occ, stud, ghost, hulls
def _box(x0, y0, z0, x1, y1, z1, P): return M.Manifold.cube([(x1 - x0) * P["pitch"], (z1 - z0) * P["pitch"], (y1 - y0) * P["plate_h"]]).translate([x0 * P["pitch"], z0 * P["pitch"], y0 * P["plate_h"]])
def build(ldr, catalog, rb_db, out, max_studs=30, max_layers=70, P=PARAMS, write_files=True, shape_aware=False):
    out = Path(out); (out / "modules").mkdir(parents=True, exist_ok=True); db = sqlite3.connect(rb_db); parts = read_ldr(ldr); occ, stud, ghost, hulls = voxelise(parts, catalog, shape_aware); hull_cache = {}
    xs, ys, zs = zip(*occ); x0, x1, y0, y1, z0, z1 = min(xs), max(xs) + 1, min(ys), max(ys) + 1, min(zs), max(zs) + 1; sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    nxm, nym, nzm = math.ceil(sx / max_studs), math.ceil(sy / max_layers), math.ceil(sz / max_studs)
    ex = [x0 + round(i * sx / nxm) for i in range(nxm + 1)]; ey = [y0 + round(i * sy / nym) for i in range(nym + 1)]; ez = [z0 + round(i * sz / nzm) for i in range(nzm + 1)]
    mods = {}; res_mod = []; tot_vol = 0.0; bodies = 0; dowels = 0; per_colour = Counter(); t_swaps = 0; lay_changes = 0
    for a in range(nxm):
        for b in range(nym):
            for c in range(nzm):
                cells = {k: v for k, v in occ.items() if ex[a] <= k[0] < ex[a + 1] and ey[b] <= k[1] < ey[b + 1] and ez[c] <= k[2] < ez[c + 1]}
                if not cells: continue
                bycol = defaultdict(list)
                for (ix, iy, iz), col in cells.items():
                    if (ix, iy, iz) not in ghost: bycol[col].append((ix, iy, iz))
                hcol = defaultdict(list)
                if shape_aware:
                    cellbox = _box(ex[a], ey[b], ez[c], ex[a + 1], ey[b + 1], ez[c + 1], P)
                    for hp in hulls:
                        key = id(hp)
                        if key not in hull_cache: hull_cache[key] = shapes.hull_body(hp["part"], hp["pos"], hp["rot"], P)
                        h = hull_cache[key]
                        if h is None: continue
                        bb = h.bounding_box(); 
                        if bb[0] >= ex[a + 1] * P["pitch"] or bb[3] <= ex[a] * P["pitch"] or bb[1] >= ez[c + 1] * P["pitch"] or bb[4] <= ez[c] * P["pitch"] or bb[2] >= ey[b + 1] * P["plate_h"] or bb[5] <= ey[b] * P["plate_h"]: continue
                        piece = h ^ cellbox
                        if piece.volume() > 1.0: hcol[hp["colour"]].append(piece)
                    for col in hcol: bycol.setdefault(col, [])
                sockets = []                                    # dowel sockets on the faces shared with the next module (+x, +z, +y) : same positions are cut in the neighbour (see below)
                modmeshes = []
                for col, vox in bycol.items():
                    col_set = set(vox); runs = []; seen = set()
                    for (ix, iy, iz) in sorted(vox, key=lambda k: (k[0], k[2], k[1])):
                        if (ix, iy, iz) in seen: continue
                        h = iy
                        while (ix, h + 1, iz) in col_set: h += 1
                        for q in range(iy, h + 1): seen.add((ix, q, iz))
                        runs.append((ix, iy, iz, h + 1))
                    solids = [_box(ix, iy, iz, ix + 1, h1, iz + 1, P) for ix, iy, iz, h1 in runs]
                    studs = [M.Manifold.cylinder(P["stud_h"], P["stud_d"] / 2, P["stud_d"] / 2, 24).translate([(ix + 0.5) * P["pitch"], (iz + 0.5) * P["pitch"], h1 * P["plate_h"]]) for ix, iy, iz, h1 in runs if stud.get((ix, h1 - 1, iz)) and (ix, h1, iz) not in occ]
                    body = M.Manifold.batch_boolean(solids + studs + hcol.get(col, []), M.OpType.Add); modmeshes.append((col, body))
                # dowel sockets on internal cut faces : one socket pair per face every ~6 studs along the face, mid-height of the module
                cutters = []
                for axis, (lo_edge, hi_edge, nb) in enumerate(((ex[a], ex[a + 1], nxm - a - 1), (ez[c], ez[c + 1], nzm - c - 1))):
                    pass
                mid_h = (ey[b] + ey[b + 1]) / 2 * P["plate_h"]; r = P["peg_d"] / 2 + P["socket_clear"]
                def sock(px, py, pz, axis, sign):
                    cyl = M.Manifold.cylinder(P["peg_len"] + 0.5, r, r, 24)
                    if axis == "x": cyl = cyl.rotate([0, 90, 0]) if sign > 0 else cyl.rotate([0, -90, 0])
                    elif axis == "z": cyl = cyl.rotate([-90, 0, 0]) if sign > 0 else cyl.rotate([90, 0, 0])
                    return cyl.translate([px, py, pz])
                face_cuts = []
                for axis in ("x", "z"):
                    for sign in (+1, -1):
                        if axis == "x":
                            edge = ex[a + 1] if sign > 0 else ex[a]; has_nb = (a + 1 < nxm) if sign > 0 else (a > 0); span = (ez[c], ez[c + 1])
                        else:
                            edge = ez[c + 1] if sign > 0 else ez[c]; has_nb = (c + 1 < nzm) if sign > 0 else (c > 0); span = (ex[a], ex[a + 1])
                        if not has_nb: continue
                        n = max(2, int((span[1] - span[0]) // 6)); pos = [span[0] + (span[1] - span[0]) * (i + 0.5) / n for i in range(n)]
                        for q in pos:
                            if axis == "x": face_cuts.append(sock(edge * P["pitch"] + (-(P["peg_len"] + 0.5) / 2 * sign) + 0, (q) * P["pitch"], mid_h, "x", sign))
                            else: face_cuts.append(sock((q) * P["pitch"], edge * P["pitch"] + (-(P["peg_len"] + 0.5) / 2 * sign) + 0, mid_h, "z", sign))
                for col, body in modmeshes:
                    if face_cuts: body = body - M.Manifold.batch_boolean(face_cuts, M.OpType.Add)
                    vol = body.volume(); tot_vol += vol; per_colour[col] += vol; bodies += 1
                    if write_files:
                        v = np.asarray(body.to_mesh().vert_properties)[:, :3]; f = np.asarray(body.to_mesh().tri_verts); mods.setdefault((a, b, c), []).append(dict(name="module_%d_%d_%d_colour%d" % (a, b, c, col), v=v, f=f, colour_hex=colour_rgb(col, db)[1].upper(), vol=vol, col=col))
                    else: mods.setdefault((a, b, c), []).append(dict(vol=vol, col=col))
                ncol = len(bycol); t_swaps += ncol - 1
                res_mod.append(dict(index=[a, b, c], studs=[ex[a + 1] - ex[a], ez[c + 1] - ez[c]], layers=ey[b + 1] - ey[b], size_mm=[round((ex[a + 1] - ex[a]) * 8, 1), round((ez[c + 1] - ez[c]) * 8, 1), round((ey[b + 1] - ey[b]) * 3.2, 1)], colours=ncol, voxels=len(cells), faces_with_dowels=len(face_cuts)))
                dowels += len(face_cuts) // 2
    if write_files and dowels:                                  # B1 finding : the pegs themselves were never exported (only the sockets) -> one dowel STL, to print `dowel_pairs` times
        pg = M.Manifold.cylinder(2 * P["peg_len"], P["peg_d"] / 2, P["peg_d"] / 2, 32); pv = np.asarray(pg.to_mesh().vert_properties)[:, :3]; write_stl(pv, np.asarray(pg.to_mesh().tri_verts), out / "dowel_peg.stl")
    if write_files:
        for key, objs in mods.items():
            lo = np.min([o["v"].min(0) for o in objs], axis=0)                      # each module is moved to the bed origin, base face on z = 0
            write_3mf([dict(o, v=o["v"] - lo, offset=(1.0, 1.0, 0)) for o in objs], out / "modules" / ("module_%d_%d_%d.3mf" % key), title="module %s" % (key,))
    mass = tot_vol / 1000 * P["density_g_cm3"] * P["effective_fill"]; hours = tot_vol / 8.0 / 3600 + 0.1 * len(res_mod)
    res = dict(mode="printed_modules", model=str(ldr), voxel_grid_studs=[sx, sz], layers=sy, size_mm=[sx * 8, sz * 8, round(sy * 3.2, 1)], bed_limit=dict(max_studs=max_studs, max_layers=max_layers), modules=len(res_mod), colour_bodies=bodies, dowel_pairs=dowels, module_list=res_mod,
               material_volume_cm3=round(tot_vol / 1000, 1), mass_g_upper_bound=round(mass, 1), mass_g_estimate_30pct_effective_fill=round(tot_vol / 1000 * P["density_g_cm3"] * 0.30, 1), print_hours_upper_bound=round(hours, 1), print_hours_estimate_30pct_fill=round(tot_vol * 0.30 / 8.0 / 3600 + 0.1 * len(res_mod), 1), colours=len(per_colour), colour_names={c: colour_rgb(c, db)[0] for c in per_colour},
               min_colour_swaps_one_body_per_colour=t_swaps, approximations=(["non-rectangular parts are replaced by the CONVEX HULL of their real geometry (exact for slopes and rounds, fills arches and cavities ; their studs are omitted)"] if shape_aware else ["parts are replaced by their bounding boxes (slopes, round tiles and corners become blocks)"]) + ["studs only on exposed upper faces of stud-bearing parts", "dowels : one dowel_peg.stl (diameter %.1f x %.0f mm) is exported, to be printed once per dowel pair ; sockets are cut in both faces" % (P["peg_d"], 2 * P["peg_len"])],
               assumptions=dict(P, volumetric_rate_mm3_s=8.0, plate_overhead_h=0.1, note="FORMULA ESTIMATES, no slicer was run ; mass = mesh volume x density (100 % solid) = upper bound"))
    json.dump(res, open(out / "report_modules.json", "w"), indent=1); return res
