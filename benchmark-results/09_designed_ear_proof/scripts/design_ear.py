"""LEGO V5: ear designed by hand (direct design, no voxel placement).

Every piece below was chosen by hand from the measured outline of the reference ear (sil_mesh.npy,
module frame of V4.1). The script only converts this explicit layout into LDraw lines and draws checks.
Nothing is searched, sampled or optimised.

Panel frame (module frame of V4.1, R_mod / O from module_report.json):
  u = module x (along the 3832 plate, turntables at u = 0 and u = 100), v = -module y (up),
  module z: the ear plane normal; the outer face of the ear faces -z.
  Cells: column i = u 20i .. 20i+20, row k = v 56+20k .. 76+20k (bracket side studs at v 66 and 86).
Layers (module z):  A  -12 .. -4  plates, bottoms on the bracket studs (structure)
                    B  -20 .. -12 plates and shaped plates (outline)
                    C  -28 .. -20 tiles (outer face)
usage: design_ear.py <outdir>
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.expanduser("~/bench/tools")); sys.path.insert(0, os.path.expanduser("~/bench/proto"))
import conn, partlib as PL

BLACK, LBG = 0, 71
HERE = os.path.dirname(os.path.abspath(__file__))
REP = json.load(open(os.path.expanduser("~/bench/proto/ear08/run/module_report.json")))
R_MOD, O = np.array(REP["R_mod"]), np.array(REP["O"])
V0 = 56                                           # bottom of row k = 0
R_PM = np.c_[[1, 0, 0], [0, 0, 1], [0, -1, 0]]    # panel-local (x=u, y=module z, z=v) -> module
LAYER_TOP = {"A": -12, "B": -20, "C": -28}        # module z of the stud face of each layer

def place_line(colour, num, M, o):
    return f"1 {colour} {o[0]:.4f} {o[1]:.4f} {o[2]:.4f} " + " ".join(f"{v:.6f}" for v in np.asarray(M).ravel()) + f" {num}.dat"

def box_corners(num):
    P = conn.part(num)
    return np.array([[x, y, z] for x in (P["lo"][0], P["hi"][0]) for y in (P["lo"][1], P["hi"][1]) for z in (P["lo"][2], P["hi"][2])])

def axis_place(num, R, target_min):
    return np.array(target_min, float) - (box_corners(num) @ R.T).min(0)

# local quarter turns about the plate normal; flip=True turns the part over about the u axis (v -> -v) is NOT
# allowed (studs would face the head), so mirror images use the left/right versions of the parts.
def panel_piece(num, r, i0, k0, layer):
    """part rotated by r quarter turns about its stud axis, body box starting at cell (i0, k0)."""
    Rl = PL.rot_y(r)
    o_l = axis_place(num, Rl, (20 * i0, LAYER_TOP[layer], V0 + 20 * k0))
    M, o = R_PM @ Rl, R_PM @ o_l
    st = studs_uv(num, M, o)            # wings have bodies narrower than their stud grid: snap the studs on the grid
    if st:
        a, b = st[0]
        du = (a - 10) - 20 * round((a - 10) / 20); dv = (b - V0 - 10) - 20 * round((b - V0 - 10) / 20)
        o = o - np.array([du, -dv, 0.0])
    return M, o

# ---------------------------------------------------------------- explicit layout (designer choices)
# (part, quarter turns, i0, k0, role)
LAYER_B = [
    ("22888", 1, -9, 1, "S1 bout arrondi : demi-disque 4x8, rayon 4 tenons (u -180..-100, v 76..236)"),
    ("24307", 0, -5, 0, "S2 bord inferieur gauche : aile 2x2 (u -100..-60, v 56..96)"),
    ("41770", 3, -1, 7, "S3 bord superieur : aile 2x4 (u -20..60, v 196..236)"),
    ("24299", 3, 3, 6, "S4 bord superieur : aile 2x2 (u 60..100, v 176..216)"),
    ("24299", 3, 5, 5, "S5 bord superieur : aile 2x2 (u 100..140, v 156..196)"),
    ("24299", 3, 7, 4, "S6 bord superieur, cote crane : aile 2x2 (u 140..180, v 136..176)"),
    ("3020", 0, -5, 7, "B1 2x4"),
    ("3031", 0, -5, 3, "B2 4x4"),
    ("3023", 0, -5, 2, "B3 1x2"),
    ("3021", 1, -3, 0, "B4 2x3"),
    ("3031", 0, -1, 3, "B5 4x4"),
    ("3020", 0, -1, 1, "B6 2x4"),
    ("3710", 0, -1, 0, "B7 1x4"),
    ("3795", 1, 3, 0, "B8 2x6"),
    ("3020", 1, 5, 1, "B9 2x4"),
    ("3023", 0, 5, 0, "B10 1x2"),
    ("3023", 1, 7, 2, "B11 1x2"),
]
# layer A: one-row plates, joints offset from those of layer B (rows k = 8 .. 0)
ROWS_A = {8: [(-5, 4)], 7: [(-7, 8), (1, 2)], 6: [(-8, 6), (-2, 4), (2, 3)], 5: [(-8, 8), (0, 6), (6, 1)],
          4: [(-8, 6), (-2, 8), (6, 3)], 3: [(-8, 8), (0, 6), (6, 2)], 2: [(-7, 4), (-3, 4), (1, 6), (7, 1)],
          1: [(-4, 3), (-1, 8)], 0: [(-4, 2), (-2, 4), (2, 4), (6, 1)]}
PLATE_1xN = {1: "3024", 2: "3023", 3: "3623", 4: "3710", 6: "3666", 8: "3460"}
LAYER_A = [(PLATE_1xN[n], 0, i0, k, f"A rangee {k}") for k, segs in ROWS_A.items() for (i0, n) in segs]

# module (reused, already validated in 07/08): turntable bases in the skull pocket, turntable tops, plate 2x10;
# new: short stem (brick 2x4, plate 2x4, plate 1x4 + tile 1x4) and 2 brackets 1x2 - 2x2 Up (99207)
def module_parts():
    out = []
    for mx in (0.0, 100.0):
        out.append((BLACK, "3680", np.eye(3), np.array([mx, -8.0, 0.0]), "base", "base de plateau tournant"))
        out.append((LBG, "3679", np.eye(3), np.array([mx, -8.0, 0.0]), "module", "dessus de plateau tournant"))
    def along_x(num):
        P = conn.part(num); return np.eye(3) if (P["hi"][0] - P["lo"][0]) >= (P["hi"][2] - P["lo"][2]) else PL.rot_y(1)
    for num, lo, note in (("3034", (-20, -16, -20), "plaque 2x8 a 53,13 deg (2x10 en V4.1)"), ("3001", (40, -40, -20), "pied : brique 2x4"),
                          ("3020", (40, -48, -20), "pied : plaque 2x4"), ("3710", (40, -56, 0), "pied : plaque 1x4 (cote crane)"),
                          ("2431", (40, -56, -20), "pied : tuile 1x4 (cote exterieur, sous l'oreille)"),
                          ("3068b", (-20, -24, -20), "tuile 2x2 sur la plaque 2x8"), ("3069b", (20, -24, -20), "tuile 1x2 sur la plaque 2x8"),
                          ("3069b", (120, -24, -20), "tuile 1x2 sur la plaque 2x8 (bout cote crane)")):
        R = along_x(num) if num != "3069b" else along_x(num) @ PL.rot_y(1)   # the 1x2 tile runs across the plate
        out.append((BLACK, num, R, axis_place(num, R, lo), "module", note))
    for bx in (60.0, 100.0):
        out.append((BLACK, "99207", np.eye(3), np.array([bx, -64.0, 10.0]), "module", "equerre 1x2 - 2x2 (4 tenons lateraux)"))
    return out

def footprint(num, M, o, res=5.0):
    """(u, v) cells of the real solid of a placed panel piece (module frame)"""
    p = conn.solid_points(num) @ M.T + o
    return {(int(np.floor(q[0] / res)), int(np.floor(-q[1] / res))) for q in p}

def studs_uv(num, M, o):
    P = conn.part(num); s = []
    for (pos, ax) in P["studs"]:
        w = M @ np.array(pos) + o; a = M @ np.array(ax)
        if a[2] < -0.9: s.append((w[0], -w[1]))
    return s

def tiles_for(pieces):
    """layer C, chosen by hand per piece of layer B (same footprint where a tile of that shape exists)"""
    T = []
    for num, r, i0, k0, role in pieces:
        tag = role.split()[0]
        if num == "22888":   # half disc: rounded 1x1 tiles at the curve, straight tiles inside (studs of the 22888)
            T.append(("1126", 1, i0, k0 + 3, "C tuile 1x2 a bouts arrondis (pointe du bout arrondi)", None))
            T.append(("25269", 1, i0 + 1, k0 + 1, "C tuile 1x1 quart de rond (bas)", None))
            T.append(("2431", 1, i0 + 1, k0 + 2, "C tuile 1x4", None))
            T.append(("25269", 2, i0 + 1, k0 + 6, "C tuile 1x1 quart de rond (haut)", None))
            T.append(("69729", 1, i0 + 2, k0 + 1, "C tuile 2x6", None))
            T.append(("25269", 1, i0 + 3, k0, "C tuile 1x1 quart de rond (bas)", None))
            T.append(("25269", 2, i0 + 3, k0 + 7, "C tuile 1x1 quart de rond (haut)", None))
        elif num in ("3020",): T.append(("87079", r, i0, k0, f"C tuile 2x4 sur {tag}", None))
        elif num == "3031": T.append(("1751", r, i0, k0, f"C tuile 4x4 sur {tag}", None))
        elif num == "3023": T.append(("3069b", r, i0, k0, f"C tuile 1x2 sur {tag}", None))
        elif num == "3021": T.append(("26603", r, i0, k0, f"C tuile 2x3 sur {tag}", None))
        elif num == "3710": T.append(("2431", r, i0, k0, f"C tuile 1x4 sur {tag}", None))
        elif num == "3795": T.append(("69729", r, i0, k0, f"C tuile 2x6 sur {tag}", None))
    return T

def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    panel = []      # (colour, num, M_module, o_module, layer, role)
    for layer, plist in (("A", LAYER_A), ("B", LAYER_B)):
        for num, r, i0, k0, role in plist:
            M, o = panel_piece(num, r, i0, k0, layer); panel.append((BLACK, num, M, o, layer, role))
    # tiles on the wing studs: one tile per straight row of studs (placed after reading the stud positions)
    for col, num, M, o, layer, role in list(panel):
        if layer != "B" or num not in ("41770", "24299", "24307"): continue
        s = studs_uv(num, M, o)
        us = sorted({round(a) for a, b in s}); vs = sorted({round(b) for a, b in s})
        if len(us) == 1:    # a vertical row of studs
            n = len(vs); i0 = int((us[0] - 10) // 20); k0 = int((vs[0] - 10 - V0) // 20)
            tile = {1: "3070b", 2: "3069b", 4: "2431"}[n]; rr = 1 if n > 1 else 0
        else:
            n = len(us); i0 = int((us[0] - 10) // 20); k0 = int((vs[0] - 10 - V0) // 20)
            tile = {1: "3070b", 2: "3069b", 3: "63864", 4: "2431"}[n]; rr = 0
        M2, o2 = panel_piece(tile, rr, i0, k0, "C")
        panel.append((BLACK, tile, M2, o2, "C", f"C tuile sur {role.split()[0]} ({len(s)} tenons)"))
    for num, r, i0, k0, role, q in tiles_for(LAYER_B):
        if q is None:
            M, o = panel_piece(num, r, i0, k0, "C")
        else: raise SystemExit("unexpected tile " + num)
        panel.append((BLACK, num, M, o, "C", role))
    mod = module_parts()
    # ---- checks on the explicit layout: overlaps inside a layer, tiles outside layer B, stud cover
    rep = {"pieces": {}}
    fp = {}
    for idx, (c, num, M, o, layer, role) in enumerate(panel):
        fp[idx] = footprint(num, M, o)
    for layer in "ABC":
        ids = [i for i, p in enumerate(panel) if p[4] == layer]; over = 0
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                n_ = len(fp[ids[a]] & fp[ids[b]])
                if n_: over += n_; print("overlap", layer, panel[ids[a]][5], "/", panel[ids[b]][5], n_)
        rep["pieces"][layer] = len(ids); rep[f"overlap_cells_{layer}"] = over
    allB = set().union(*[fp[i] for i, p in enumerate(panel) if p[4] == "B"])
    allA = set().union(*[fp[i] for i, p in enumerate(panel) if p[4] == "A"])
    allC = set().union(*[fp[i] for i, p in enumerate(panel) if p[4] == "C"])
    rep["A_outside_B_cells"] = len(allA - allB); rep["C_outside_B_cells"] = len(allC - allB)
    # studs left visible: every stud of the panel and of the module must meet a receptor (anti-stud)
    allp = [(num, M, o) for c, num, M, o, l_, r_ in panel] + [(num, M, o) for c, num, M, o, g, n_ in mod]
    REC = np.array([M @ np.array(rc[0]) + o for num, M, o in allp for rc in conn.part(num)["receptors"]])
    vis = [num for num, M, o in allp for (pos, ax) in conn.part(num)["studs"] if np.linalg.norm(REC - (M @ np.array(pos) + o), axis=1).min() > 2]
    rep["visible_studs"] = len(vis); rep["visible_studs_parts"] = sorted(set(vis))
    # ascii views (5 LDU cells) against the reference outline
    S = np.load(os.path.join(HERE, "sil_mesh.npy")); sj = json.load(open(os.path.join(HERE, "sil_mesh.json")))
    def ref(u, v):
        a = int((u - sj["u0"]) / sj["res"]); b = int((v - sj["v0"]) / sj["res"])
        return 0 <= a < S.shape[0] and 0 <= b < S.shape[1] and S[a, b]
    lines = []
    for v in range(250, 40, -5):
        row = ""
        for u in range(-200, 220, 5):
            c = (u // 5, v // 5); inB = c in allB; r_ = ref(u + 2.5, v + 2.5)
            row += ("#" if r_ else "+") if inB else ("." if r_ else " ")
        lines.append(row)
    open(os.path.join(out, "plan_couche_B_vs_reference.txt"), "w").write(
        "# = piece et reference, + = piece hors reference, . = reference non couverte (pas 5 LDU)\n" + "\n".join(lines) + "\n")
    rb = np.array([[u, v] for u in range(-200, 220, 5) for v in range(40, 250, 5)])
    refm = np.array([ref(u + 2.5, v + 2.5) and v >= V0 - 10 for u, v in rb]); pm = np.array([(u // 5, v // 5) in allB for u, v in rb])
    rep["outline_iou_layer_B_vs_reference_lobe"] = round(float((refm & pm).sum() / max((refm | pm).sum(), 1)), 3)
    # ---- write LDraw: module alone (world frame of the head) and the list of parts
    def world(M, o, grp):
        return (np.eye(3) if grp == "base" else R_MOD @ M), O + R_MOD @ o
    L = ["0 oreille_concue_V5", "0 Name: module_oreille_V5.ldr", "0 Author: conception directe (V5), Paco 400 mm, repere de la tete"]
    steps = [("base", None), ("module", None), ("panel", "A"), ("panel", "B"), ("panel", "C")]
    for grp, layer in steps:
        if grp != "panel":
            for c, num, M, o, g, note in mod:
                if g == grp: Mw, ow = world(M, o, g); L.append(place_line(c, num, Mw, ow))
        else:
            for c, num, M, o, l_, role in panel:
                if l_ == layer: Mw, ow = world(M, o, "panel"); L.append(place_line(c, num, Mw, ow))
        L.append("0 STEP")
    open(os.path.join(out, "module_oreille_V5.ldr"), "w").write("\n".join(L) + "\n")
    # head C with its pocket (V4.1 file, everything before the turntable bases) + this module as a sub-assembly
    raw = open(os.path.expanduser("~/bench/proto/ear08/run/tete_C_avec_module.ldr")).read().splitlines()
    cut = next(n for n, l in enumerate(raw) if l.startswith("1 ") and l.split()[14] == "3680.dat")
    W = ["0 tete_C_avec_oreille_V5", "0 Name: tete_C_avec_oreille_V5.ldr", "0 Author: tete C (poche V4.1) + oreille concue a la main (V5)"]
    W += [l for l in raw[3:cut] if l.startswith("1 ") or l.startswith("0 STEP")]
    if W[-1] != "0 STEP": W.append("0 STEP")
    for c, num, M, o, g, note in mod:
        if g == "base": Mw, ow = world(M, o, g); W.append(place_line(c, num, Mw, ow))
    W += ["0 STEP", "0 BRICKIFY SUBASSEMBLY BEGIN oreille"]
    for c, num, M, o, g, note in mod:
        if g == "module": Mw, ow = world(M, o, g); W.append(place_line(c, num, Mw, ow))
    for layer in "ABC":
        for c, num, M, o, l_, role in panel:
            if l_ == layer: Mw, ow = world(M, o, "panel"); W.append(place_line(c, num, Mw, ow))
    W += ["0 BRICKIFY SUBASSEMBLY END oreille", "0 STEP"]
    open(os.path.join(out, "tete_C_avec_oreille_V5.ldr"), "w").write("\n".join(W) + "\n")
    rows = [(c, num, role, l_) for c, num, M, o, l_, role in panel] + [(c, num, note, g) for c, num, M, o, g, note in mod]
    json.dump(dict(rep, parts=[dict(colour=c, part=n, role=r, group=g) for c, n, r, g in rows]), open(os.path.join(out, "design_report.json"), "w"), indent=1)
    print(json.dumps(rep))

if __name__ == "__main__":
    main()
