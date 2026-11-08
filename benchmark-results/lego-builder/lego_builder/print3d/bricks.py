"""Mode 1 : individual printable bricks (own parametric geometry, rectangular plates/bricks/tiles only). Outputs one STL per brick type, per-colour build plates (3MF) and a metrics report."""
import json, math, sqlite3
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import manifold3d as M
from .common import PARAMS, classify, colour_rgb, read_ldr, write_3mf, write_stl, LDU
def _cyl(r, h, x, y, z=0.0, seg=32): return M.Manifold.cylinder(h, r, r, seg).translate([x, y, z])
def brick_mesh(kind, nx, ny, P=PARAMS):
    """kind plate|brick|tile ; nx x ny studs. Origin at the base corner, z up. Hollow underside, top skin, studs (not for tiles), tubes for 2x2 and larger."""
    h = P["brick_h"] if kind == "brick" else P["plate_h"]; L, W = nx * P["pitch"] - 2 * P["tol"], ny * P["pitch"] - 2 * P["tol"]; o = P["tol"]
    body = M.Manifold.cube([L, W, h]).translate([o, o, 0]); depth = h - P["top"]
    cav = M.Manifold.cube([L - 2 * P["wall"], W - 2 * P["wall"], depth]).translate([o + P["wall"], o + P["wall"], 0]); body = body - cav
    if nx >= 2 and ny >= 2:
        tubes = [(_cyl(P["tube_od"] / 2, depth, o + (i + 1) * P["pitch"] - o * 0 - 0.0, o + (j + 1) * P["pitch"] - 0.0) - _cyl(P["tube_id"] / 2, depth, o + (i + 1) * P["pitch"], o + (j + 1) * P["pitch"])) for i in range(nx - 1) for j in range(ny - 1)]
        body = M.Manifold.batch_boolean([body] + tubes, M.OpType.Add)
    if kind != "tile":
        studs = [_cyl(P["stud_d"] / 2, P["stud_h"], o + (i + 0.5) * P["pitch"] - o, o + (j + 0.5) * P["pitch"] - o, h) for i in range(nx) for j in range(ny)]
        body = M.Manifold.batch_boolean([body] + studs, M.OpType.Add)
    return body
def mesh_arrays(m):
    mm = m.to_mesh(); return np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts)
def export(ldr, catalog, rb_db, out, bed=(250.0, 250.0), gap=3.0, P=PARAMS):
    out = Path(out); (out / "stl").mkdir(parents=True, exist_ok=True); (out / "plates").mkdir(exist_ok=True); db = sqlite3.connect(rb_db)
    parts = read_ldr(ldr); ok = Counter(); bad = Counter(); inst = defaultdict(list); cache = {}; types = {}
    for p in parts:
        c = classify(p["part"], catalog)
        if c is None: bad[p["part"]] += 1; continue
        key = (c["kind"], min(c["nx"], c["nz"]), max(c["nx"], c["nz"])); types[key] = c; ok[(p["part"], p["colour"])] += 1; inst[p["colour"]].append((key, p["part"]))
    meta = {}
    for key in sorted(types):
        kind, a, b = key; m = brick_mesh(kind, a, b, P); v, f = mesh_arrays(m); write_stl(v, f, out / "stl" / ("%s_%dx%d.stl" % key)); cache[key] = (v, f, m.volume(), m.genus() if hasattr(m, "genus") else None)
        mm = m.to_mesh(); bb = np.asarray(v).max(0) - np.asarray(v).min(0)
        meta["%s_%dx%d" % key] = dict(volume_mm3=round(m.volume(), 1), bbox_mm=[round(float(x), 2) for x in bb], watertight_manifold=bool(m.status() == M.Error.NoError), triangles=int(len(f)))
    # shelf packing per colour on beds
    plates = []; names = {}
    for col, items in sorted(inst.items(), key=lambda kv: -len(kv[1])):
        names[col] = colour_rgb(col, db); items = sorted(items, key=lambda it: -(it[0][2] * 8)); x = y = 0.0; row_h = 0.0; cur = []; plate_no = 0
        for key, part in items:
            w, d = key[1] * 8 + gap, key[2] * 8 + gap
            if x + w > bed[0]: x = 0.0; y += row_h; row_h = 0.0
            if y + d > bed[1]: plates.append((col, cur)); cur = []; x = y = 0.0; row_h = 0.0
            cur.append((key, part, x + gap / 2, y + gap / 2)); x += w; row_h = max(row_h, d)
        if cur: plates.append((col, cur))
    tot_vol = 0.0; per_colour = defaultdict(float); written = 0
    for i, (col, cur) in enumerate(plates):
        vol = sum(cache[k][2] for k, _, _, _ in cur); tot_vol += vol; per_colour[col] += vol
        if i < int(P.get("write_plates", 6)):
            hexc = names[col][1]; objs = [dict(name="%s_%s" % (part, ("%dx%d" % (k[1], k[2]))), v=cache[k][0], f=cache[k][1], colour_hex=hexc.upper(), offset=(px, py, 0)) for k, part, px, py in cur]; write_3mf(objs, out / "plates" / ("plate_%03d_colour%d.3mf" % (i + 1, col))); written += 1
    mass = tot_vol / 1000 * P["density_g_cm3"] * P["effective_fill"]; hours = tot_vol / 8.0 / 3600 + 0.1 * len(plates)
    res = dict(mode="individual_bricks", model=str(ldr), parts_total=len(parts), parts_supported=sum(ok.values()), parts_unsupported=sum(bad.values()), supported_share=round(sum(ok.values()) / len(parts), 4),
               unsupported_types=dict(bad.most_common(20)), supported_types=len(types), colours=len(inst), colour_names={k: names[k][0] for k in inst}, plates=len(plates), plates_3mf_written=written, bed_mm=list(bed),
               material_volume_cm3=round(tot_vol / 1000, 1), mass_g_upper_bound=round(mass, 1), print_hours_estimate=round(hours, 1), filament_swaps_if_one_colour_per_plate=max(0, len(inst) - 1), mass_by_colour_g={names[c][0]: round(v / 1000 * P["density_g_cm3"], 1) for c, v in per_colour.items()},
               geometry=meta, assumptions=dict(P, volumetric_rate_mm3_s=8.0, plate_overhead_h=0.1, note="mass = mesh volume x density (100 % solid = upper bound) ; time = volume / 8 mm3/s + 0.1 h per plate : FORMULA ESTIMATES, no slicer was run"))
    json.dump(res, open(out / "report_bricks.json", "w"), indent=1); return res
