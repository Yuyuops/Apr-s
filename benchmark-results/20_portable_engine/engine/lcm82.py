"""LEGO V8.2 (derived from lcm.py V8.1, which stays unchanged) - generic module "lines and cavities" (LCM) for small facial features that the voxel volume cannot render:
mouth openings, tongue, lips, fine lines.

Input : details.json (detect.py: patches with colour, outward normal, axis, size), the V8 body grid (corps_V8.npz, after the
        ears and the V8 micro-details were carved), the GLB frame (axe_museau / plan sagittal).
Everything is derived from the GLB patches and from LDraw geometry measured on the parts; no Paco coordinate, no part number
chosen for Paco.

Treatments, chosen from the orientation of the patch normal (angle to the vertical):
  UP / inclined up (tongue, jaw edge, upper surfaces)   -> T1 "surface inclinee" : the tilt of the TOP FACE of every candidate
        part (tiles, cheese slopes, 45 degree slopes) is measured on its mesh; part, quarter turn and cell set are chosen by
        cost = tilt error + footprint overlap (IoU with the patch ellipse) + protrusion; the part sits on a real stud row
        (the mounting cells' tiles become plates, as for the V8 eyes); the colour is the patch colour (Rebrickable >= 20 sets).
  DOWN (palate, underside of the lip)                    -> T2 "plafond" : surface cells under the patch footprint AND the cell(s)
        behind them (LINING_LAYERS plates) take the patch colour. The down face of a plate is the visible face seen from below
        and its edge is the visible line seen from the side, so the lining is real geometry (plates), 2 plates thick (6.4 mm)
        so that its edge is visible from the side. A part hanging below a ceiling would need the same studs UP into the ceiling
        underside, i.e. the same plates: the lining is therefore built as body plates, and no part is glued under it.
  Cavity relief (variant B)                              -> T3 "ouverture" : the empty cells under a ceiling within CEIL_MAX
        layers, near a mouth patch, form the cavity; where its clear height is under MIN_OPEN layers the cells of the ceiling
        next to the open edge are removed (in the footprint of the patch only) so that the opening is at least MIN_OPEN
        layers high: the relief is created by geometry, not by colour. The compromise is reported (height added in mm).
V8.2 change (variant C), decided by the visibility diagnosis (proto/v82/visibility.py): the cavity colours are TRANSFERRED FROM THE GLB onto the cavity surface cells that are
exposed to the outside (colour of the nearest GLB surface point under 3x3 samples of each exposed cell face; dark / red cells are recoloured, skin cells are left natural).
The V8.1 steps "lip line / tongue / interior walls" (one colour for all edge cells) are removed: they added far more dark than the GLB shows (about 40 % of the visible cavity
against 4 %).
usage: lcm82.py <corps_V8.npz> <details.json> <out dir> <variant A|B|C>  (variant C needs the env variable GLB_REF = the GLB in the LEGO frame)
"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import json, os, pickle, sys
import numpy as np
sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, ENGINE_DIR)
sys.path.insert(0, ENGINE_DIR)
import conn, partlib as PL
import sqlite3

MIN_SETS = 20
LDC = {}          # class -> LDraw code, filled in run() from the colours observed on the GLB and the palette of the subject (palette_util.class_codes)
LINING_LAYERS = 2          # plates of lining behind a down-facing surface (6.4 mm: visible edge)
MARGIN_MM = 4.0            # footprint margin around a patch
CEIL_MAX = 5               # layers: an empty cell with a solid cell at most this far above belongs to a cavity
MIN_OPEN = 3               # variant B: minimal clear height of a cavity opening (layers)
TOP_FAMILY = ["3070b", "3069b", "63864", "2431", "24246", "54200", "85984", "3040b", "3039", "4286"]    # tiles, cheese slopes, slopes
RB = RB_DB
_db = None

def avail(num, colour):
    global _db
    if _db is None: _db = sqlite3.connect(RB)
    return int(_db.execute("select count(distinct inventory_id) from inventory_parts where part_num=? and color_id=?", (num, colour)).fetchone()[0] or 0)

def top_face(num):
    """measured on the LDraw mesh: tilt (degrees from vertical) and horizontal direction (LDraw x,z) of the top face normal,
    footprint in studs, height (LDU) of the part above its lowest plane"""
    T, _ = PL.lib().geom(num + ".dat"); T = np.asarray(T).reshape(-1, 3, 3).astype(float)
    nn = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); a = np.linalg.norm(nn, axis=1); nn = nn / np.maximum(a[:, None], 1e-9)
    P = conn.part(num); mid = (np.array(P["lo"]) + np.array(P["hi"])) / 2
    nn = nn * np.sign(((T.mean(1) - mid) * nn).sum(1))[:, None]
    up = (nn[:, 1] < -0.3) & (a > 1.0)
    v = (nn[up] * a[up, None]).sum(0); v /= np.linalg.norm(v)
    lo, hi = np.array(P["lo"]), np.array(P["hi"])
    return dict(tilt=float(np.degrees(np.arccos(np.clip(-v[1], -1, 1)))), h=np.array([v[0], v[2]]), w=int(round((hi[0] - lo[0]) / 20)), l=int(round((hi[2] - lo[2]) / 20)),
                height=float(hi[1] - lo[1]), lo=lo, hi=hi)

def rot_y(r): return PL.rot_y(r)

def box_corners(num):
    P = conn.part(num)
    return np.array([[x, y, z] for x in (P["lo"][0], P["hi"][0]) for y in (P["lo"][1], P["hi"][1]) for z in (P["lo"][2], P["hi"][2])])

def to_ldu(p): p = np.asarray(p, float); return np.array([p[0] / 0.4, -p[1] / 0.4, -p[2] / 0.4])

def run(npz, details, out, variant):
    d = np.load(npz); G = d["grid"].astype(int); F = d["fine"]; K = int(d["k"]); NX, NY, NZ = G.shape
    occ = (G >= 0) & (F.reshape(NX, K, NY, K, NZ, K).mean(axis=(1, 3, 5)) >= 0.5)
    import palette_util; LDC.update(palette_util.class_codes(details, npz)); LIGHT = LDC["blanc"]
    D = json.load(open(details)); patches = [p for p in D["details"] if p["classe"] == "bouche"]
    cell_mm = np.array([8.0, 3.2, 8.0])
    def cen_mm(c): return (np.array(c) + 0.5) * cell_mm * np.array([1, 1, -1])
    recolour, carve, parts, report = {}, set(), [], []
    for p in sorted(patches, key=lambda q: -q["aire_mm2"]):
        n = np.array(p["normale"]); c = np.array(p["centre_mm"]); t1 = np.array(p["axe_long"]); t2 = np.cross(n, t1)
        L, W = p["longueur_mm"], p["largeur_mm"]; colour = LDC[p["couleur"]]
        orient = "haut" if n[1] > 0.5 else "bas" if n[1] < -0.5 else "lateral"
        tilt = float(np.degrees(np.arccos(abs(n[1]))))
        e = dict(id=p["id"], couleur=p["couleur"], orientation=orient, inclinaison_deg=round(tilt, 1), longueur_mm=L, largeur_mm=W)
        # candidate cells: footprint of the patch in its own plane (+margin), within 1.5 cells of the plane
        idx = np.argwhere(occ); cm = np.array([cen_mm(i) for i in idx]); rel = cm - c
        a_, b_, h_ = rel @ t1, rel @ t2, rel @ n
        foot = ((a_ / (L / 2 + MARGIN_MM)) ** 2 + (b_ / (W / 2 + MARGIN_MM)) ** 2 <= 1) & (np.abs(h_) <= 7.0)
        cells = [tuple(i) for i in idx[foot]]
        if orient == "bas":
            exposed = [x for x in cells if not (x[1] > 0 and occ[x[0], x[1] - 1, x[2]])]
            for (x, y, z) in exposed:
                for k in range(LINING_LAYERS):
                    if y + k < NY and occ[x, y + k, z] and (x, y + k, z) not in carve: recolour[(x, y + k, z)] = colour
            e.update(traitement="T2 plafond : %d cellules de surface + %d plaque(s) derriere" % (len(exposed), LINING_LAYERS - 1), cellules_recolorees=len(exposed) * LINING_LAYERS, confiance="haute" if tilt < 20 else "moyenne")
        elif orient == "haut":
            exposed = [x for x in cells if not (x[1] + 1 < NY and occ[x[0], x[1] + 1, x[2]])]
            if not exposed: e.update(traitement="aucune surface superieure libre (capacite manquante)"); report.append(e); continue
            ytop = max(x[1] for x in exposed); top = [x for x in exposed if x[1] >= ytop - 1]
            ellipse = lambda X, Z: ((((np.array(cen_mm((X, ytop, Z))) - c) @ t1) / (L / 2 + MARGIN_MM)) ** 2 + (((np.array(cen_mm((X, ytop, Z))) - c) @ t2) / (W / 2 + MARGIN_MM)) ** 2) <= 1.0
            # desired horizontal direction of the surface normal in LDraw axes
            hd = np.array([n[0], -n[2]]); hd = hd / max(np.linalg.norm(hd), 1e-9)
            best = None
            cand_cells = {(x, z) for (x, y, z) in top}
            xs = [x for x, z in cand_cells]; zs = [z for x, z in cand_cells]
            for num in TOP_FAMILY:
                if avail(num, colour) < MIN_SETS: continue
                tf = top_face(num); P = conn.part(num)
                for r in range(4):
                    Rm = rot_y(r); w, l = (tf["w"], tf["l"]) if r % 2 == 0 else (tf["l"], tf["w"])
                    hdir = Rm[[0, 2]][:, [0, 2]] @ tf["h"]
                    err = 0.0
                    if tf["tilt"] > 1.0:
                        cosang = np.dot(hdir, hd) / max(np.linalg.norm(hdir), 1e-9); err = np.degrees(np.arccos(np.clip(cosang, -1, 1)))
                    elif r > 0: continue
                    for x0 in range(min(xs) - 1, max(xs) + 1):
                        for z0 in range(min(zs) - 1, max(zs) + 1):
                            fc = [(x0 + i, z0 + j) for i in range(w) for j in range(l)]
                            if not all(0 <= x < NX and 0 <= z < NZ and occ[x, ytop, z] and not occ[x, ytop + 1, z] if ytop + 1 < NY else False for x, z in fc): continue
                            if not all(occ[x, ytop - 1, z] for x, z in fc): continue
                            cover = sum(1 for x, z in fc if ellipse(x, z)) / len(fc)
                            ell_cells = sum(1 for x, z in cand_cells if ellipse(x, z))
                            iou = cover * len(fc) / max(len(fc) + ell_cells - cover * len(fc), 1)
                            prot = max(0.0, (tf["height"] - 8.0) / 8.0)            # plates above the replaced layer
                            cost = abs(tf["tilt"] - tilt) / 30.0 + err / 90.0 * (1.0 if tf["tilt"] > 1 else 0) + (1 - iou) + 0.2 * prot
                            if best is None or cost < best[0]: best = (cost, num, r, x0, z0, w, l, tf, iou, err, prot)
            if best is None: e.update(traitement="aucune piece de surface valide (capacite manquante)"); report.append(e); continue
            cost, num, r, x0, z0, w, l, tf, iou, err, prot = best
            Rm = rot_y(r); rc = box_corners(num) @ Rm.T
            o = np.array([20 * x0, -8 * ytop, 20 * z0]) - np.array([rc[:, 0].min(), rc[:, 1].max(), rc[:, 2].min()])     # footprint corner on the grid, BOTTOM of the part on the top of the mounting cell
            parts.append(dict(detail=p["id"], role="incrustation", colour=colour, num=num, R=Rm.tolist(), o=np.round(o, 4).tolist()))
            for i in range(w):
                for j in range(l): carve.add((x0 + i, ytop, z0 + j))
            e.update(traitement="T1 surface inclinee", piece=num, inclinaison_piece_deg=round(tf["tilt"], 1), erreur_direction_deg=round(float(err), 1), iou_empreinte=round(iou, 2),
                     saillie_plaques=round(prot, 1), cout=round(cost, 2), confiance="haute" if (tilt < 20 or abs(tf["tilt"] - tilt) < 10) else "moyenne")
        else:
            e.update(traitement="surface laterale : non traitee dans ce module (capacite manquante, aucune bouche concernee)")
        report.append(e)
    # T3 cavity relief and lining (variant B)
    if variant in ("B", "C") and patches:
        from scipy import ndimage
        FLOOR_MAX = 6
        down = [p for p in patches if p["normale"][1] < -0.5]; up = [p for p in patches if p["normale"][1] > 0.5]
        line_col = LDC[max(down, key=lambda q: q["aire_mm2"])["couleur"]] if down else LDC["noir"]                    # dominant colour of the ceiling patches
        # 1. pocket cells: empty, OPEN TO THE OUTSIDE (flood fill from the grid border; voids left by the ears are not cavities),
        #    with a ceiling within CEIL_MAX layers above and a floor within FLOOR_MAX below (nothing in between)
        lab_e, ne = ndimage.label(~occ)
        border = np.unique(np.concatenate([lab_e[0].ravel(), lab_e[-1].ravel(), lab_e[:, 0].ravel(), lab_e[:, -1].ravel(), lab_e[:, :, 0].ravel(), lab_e[:, :, -1].ravel()]))
        outside = np.isin(lab_e, border[border > 0])
        pocket = {}
        for x in range(NX):
            for z in range(NZ):
                for y in range(FLOOR_MAX, NY - CEIL_MAX - 1):
                    if occ[x, y, z] or not outside[x, y, z]: continue
                    up_k = next((k for k in range(1, CEIL_MAX + 1) if occ[x, y + k, z]), None); dn_k = next((k for k in range(1, FLOOR_MAX + 1) if occ[x, y - k, z]), None)
                    if up_k is None or dn_k is None: continue
                    pocket.setdefault((x, z), []).append(y)
        cavity_info = None
        if variant == "C":
            # V8.2 fix of the SELECTION (the V8.1 bug): the pocket was kept per (x, z) COLUMN with all its heights, so a column of the mouth zone also carried the pockets of the same
            # column lower in the body (between the legs, under the arms): 130 of the 223 cells recoloured by V8.1 are far from the mouth. Here the pocket is selected as a 3D component
            # (6-connected cells) that touches a mouth patch; only its cells are used afterwards.
            arr3 = np.zeros(occ.shape, bool)
            for (x_, z_), ys_ in pocket.items():
                for y_ in ys_: arr3[x_, y_, z_] = True
            lab3, n3 = ndimage.label(arr3); keep3 = set()
            for k_ in range(1, n3 + 1):
                idx3 = np.argwhere(lab3 == k_)
                for p in patches:
                    if min(np.linalg.norm(cen_mm(tuple(c_)) - np.array(p["centre_mm"])) for c_ in idx3) <= p["longueur_mm"] / 2 + 2 * MARGIN_MM: keep3.add(k_)
            pocket = {}
            for k_ in keep3:
                for (x_, y_, z_) in np.argwhere(lab3 == k_): pocket.setdefault((int(x_), int(z_)), []).append(int(y_))
            allc = np.array([(x_, y_, z_) for (x_, z_), ys_ in pocket.items() for y_ in ys_])
            cavity_info = dict(composantes_3D_gardees=len(keep3), cellules=int(len(allc)), ix=[int(allc[:, 0].min()), int(allc[:, 0].max())], iy=[int(allc[:, 1].min()), int(allc[:, 1].max())], iz=[int(allc[:, 2].min()), int(allc[:, 2].max())])
        # 2. components of pocket columns (4-connected) that touch a mouth patch (distance from its centre to the component <= L/2 + 2 margins)
        cols = sorted(pocket); colset = set(cols); comp = {}; cid = 0
        for c in cols:
            if c in comp: continue
            cid += 1; stack = [c]; comp[c] = cid
            while stack:
                x, z = stack.pop()
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (x + dx, z + dz)
                    if q in colset and q not in comp: comp[q] = cid; stack.append(q)
        keep = set()
        for k in range(1, cid + 1):
            members = [c for c in cols if comp[c] == k]
            for p in patches:
                dmin = min(np.linalg.norm(cen_mm((x, int(np.median(pocket[(x, z)])), z)) - np.array(p["centre_mm"])) for x, z in members)
                if dmin <= p["longueur_mm"] / 2 + 2 * MARGIN_MM: keep.add(k)
        pk = {c: pocket[c] for c in cols if comp[c] in keep}
        # 3. opening: clear height under MIN_OPEN -> remove ceiling cells (relief by geometry); protected (white) cells stay
        added = 0
        for (x, z), ys in pk.items():
            if len(ys) < MIN_OPEN:
                for k in range(MIN_OPEN - len(ys)):
                    c3 = (x, max(ys) + 1 + k, z)
                    if c3[1] < NY and occ[c3] and G[c3] != LIGHT: carve.add(c3); added += 1
        if variant == "B":
            # 4. lip line: ceiling cells (LINING_LAYERS plates) of the pocket columns that touch the open side (a neighbour column that is not a pocket column and is
            #    empty at the pocket mid-height: the opening seen from the side)
            line = 0; sides = {"x+": 0, "x-": 0, "z+": 0, "z-": 0}
            for (x, z), ys in pk.items():
                mid = int(np.median(ys)); cy = max(ys) + 1 + (MIN_OPEN - len(ys) if len(ys) < MIN_OPEN else 0)
                open_sides = [n for n, (dx, dz) in {"x+": (1, 0), "x-": (-1, 0), "z+": (0, 1), "z-": (0, -1)}.items()
                              if (x + dx, z + dz) not in pk and 0 <= x + dx < NX and 0 <= z + dz < NZ and not occ[x + dx, mid, z + dz]]
                if not open_sides: continue
                for n in open_sides: sides[n] += 1
                for k in range(LINING_LAYERS):
                    if cy + k < NY and occ[x, cy + k, z] and (x, cy + k, z) not in carve: recolour[(x, cy + k, z)] = line_col; line += 1
            # 5. tongue: the top plates of the floor under a pocket column near an up-facing patch take the patch colour (floor plates seen from the side)
            tongue = 0
            for (x, z), ys in pk.items():
                fy = min(ys) - 1
                while fy >= 0 and not occ[x, fy, z]: fy -= 1
                if fy < 1: continue
                for p in up:
                    if np.linalg.norm(cen_mm((x, fy, z)) - np.array(p["centre_mm"])) <= p["longueur_mm"] / 2 + 2 * MARGIN_MM:
                        for k in range(LINING_LAYERS):
                            if occ[x, fy - k, z] and (x, fy - k, z) not in carve: recolour[(x, fy - k, z)] = LDC[p["couleur"]]; tongue += 1
            # 6. depth of the cavity: the wall cells that bound the pocket horizontally (what one sees THROUGH the opening, on the far side) take the interior colour
            #    (dark; the plate below the floor top stays as is) over the pocket height
            walls = 0
            for (x, z), ys in pk.items():
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (x + dx, z + dz)
                    if q in pk: continue
                    for y in ys:
                        c = (q[0], y, q[1])
                        if 0 <= q[0] < NX and 0 <= q[1] < NZ and occ[c] and c not in carve and c not in recolour and G[c] != LIGHT: recolour[c] = line_col; walls += 1

        else:
            # 4. colour transfer from the GLB onto the exposed cavity surface cells
            import trimesh
            from scipy.spatial import cKDTree
            m = trimesh.load(os.environ["GLB_REF"], force="mesh", process=False); Vg = np.asarray(m.vertices); Fg = np.asarray(m.faces)
            Cg = np.asarray(m.visual.vertex_colors)[:, :3].astype(float)[Fg].mean(1); cg = Vg[Fg].mean(1)
            tree = cKDTree(cg)
            cavset = {(x, y, z) for (x, z), ys in pk.items() for y in ys} | set(carve)
            def klass(rgb):
                r_, g_, b_ = rgb
                if r_ > 140 and g_ < 120 and b_ < 120: return "rouge"
                if min(rgb) > 185: return "clair"
                if max(rgb) < 85: return "sombre"
                return "peau"
            faces = {}
            for (x, y, z) in cavset:
                for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                    sc = (x + dx, y + dy, z + dz)
                    if not (0 <= sc[0] < NX and 0 <= sc[1] < NY and 0 <= sc[2] < NZ) or not occ[sc] or sc in carve or G[sc] == LIGHT: continue
                    n = np.array([-dx, -dy, dz], float)                      # outward normal (cavity side) of the solid cell face, mm frame (z negated)
                    ctr = cen_mm(sc) + n * np.array([4, 1.6, 4]); t1 = np.cross(n, [0, 1, 0]) if abs(n[1]) < .5 else np.array([1.0, 0, 0]); t2 = np.cross(n, t1); ext = np.array([4, 1.6, 4])
                    P = np.array([ctr + a_ * t1 * ext + b_ * t2 * ext for a_ in (-.6, 0, .6) for b_ in (-.6, 0, .6)])
                    dd, ii = tree.query(P); ok = dd <= 6.0
                    faces.setdefault(sc, []).append((n, [klass(Cg[i]) for i, o in zip(ii, ok) if o]))
            transfer = {"sombre": 0, "rouge": 0, "peau": 0, "clair": 0}; recol = 0
            COL = {"sombre": LDC["noir"], "rouge": LDC["rouge"], "peau": LDC["jaune"]}
            for sc, lst in faces.items():
                cl = [k for n_, ks in lst for k in ks]
                if not cl: continue
                best = max(("sombre", "rouge", "peau", "clair"), key=lambda q: cl.count(q))      # majority class of the GLB colours seen by the exposed faces of the cell
                transfer[best] += 1
                if best == "clair": continue                                                      # white detail (eyes): left to the existing modules
                vertical = any(abs(n_[1]) > .5 for n_, ks in lst)
                layers = LINING_LAYERS if vertical else 1
                step = -1 if any(n_[1] > .5 for n_, ks in lst) else 1                             # floor: the plates under the face; ceiling: the plates above
                for k in range(layers):
                    c3 = (sc[0], sc[1] + (step * k if vertical else 0), sc[2])
                    if 0 <= c3[1] < NY and occ[c3] and c3 not in carve and G[c3] != LIGHT and G[c3] != COL[best]: recolour[c3] = COL[best]; recol += 1
            tongue = line = walls = 0; sides = {}
            report.append(dict(id="T3C", traitement="transfert des couleurs du GLB sur les cellules de cavite exposees", cellules_cavite_exposees=len(faces), cellules_sombres=transfer["sombre"], cellules_rouges=transfer["rouge"], cellules_peau=transfer["peau"], cellules_claires=transfer["clair"], cellules_recolorees=recol, cavite=cavity_info))
        report.append(dict(id="T3", traitement=("cavite ouverte : ouverture minimale %d plaques (%.1f mm), ligne de levre sur les bords ouverts, langue sur le plancher" if variant == "B" else "cavite ouverte : ouverture minimale %d plaques (%.1f mm) ; couleurs transferees du GLB (voir T3C)") % (MIN_OPEN, MIN_OPEN * 3.2),
                           colonnes_cavite=len(pk), composantes_gardees=len(keep), cellules_creusees_plafond=added, cellules_ligne_levre=line, cotes_ouverts=sides, cellules_langue=tongue, cellules_parois=walls))
    os.makedirs(out, exist_ok=True)
    pickle.dump(dict(recolour=recolour, carve=sorted(carve), parts=parts), open(os.path.join(out, "lcm_%s.pkl" % variant), "wb"))
    json.dump(dict(variante=variant, regles=dict(lining_layers=LINING_LAYERS, marge_mm=MARGIN_MM, ceil_max=CEIL_MAX, min_open=MIN_OPEN, min_sets=MIN_SETS, famille_haut=TOP_FAMILY), traitements=report,
                   cellules_recolorees=len(recolour), cellules_creusees=len(carve), pieces=len(parts)), open(os.path.join(out, "lcm_%s.json" % variant), "w"), indent=1, ensure_ascii=False,
              default=lambda x: x.tolist() if hasattr(x, "tolist") else str(x))
    for r in report: print(r)

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
