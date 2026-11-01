"""LEGO V8: assembly of the whole sculpture = V7 assembly (unchanged ears, same carving rule, same brickify_plus
settings) + the micro-detail parts of microdetails.py (their cells carved, their voxel colours cleared, body tiles under
their mounting cells turned to plates).

V7 docstring follows.

From the two ear modules of integrate.py: one carving of the whole-character grid (cells hit by any ear part, studs
above and below included), one brickify_plus rebuild (prototype-C settings), seats (1x1 plates) under every turned
plate where its stud falls on the grid (tiles of the body under a seat become plates), colour rule for turned plates
that reach the surface (none expected: both secondary plates are hidden), then the whole LDraw file:
body + seats, turned plates, two sub-assemblies (one per ear), ready for reorder_notice and validate_v3.
usage: assemble_v81.py <V7 run dir (ears.pkl)> <microdetails.pkl> <out dir> <details.json> <variant A|B|none>
(V8.1: the V8 assembly, then the lines-and-cavities module lcm.py applied to the carved grid before the single brickify_plus rebuild)
"""
import json, os, pickle, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.expanduser("~/bench/tools")); sys.path.insert(0, os.path.expanduser("~/bench/proto"))
sys.path.insert(0, os.path.expanduser("~/bench/proto/ear11")); sys.path.insert(0, os.path.expanduser("~/bench/proto/ear12"))
import conn
import autogen as A6
D = A6.D
BLACK = 0

def main():
    run7, mdp, run = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(run, exist_ok=True)
    details, variant = sys.argv[4], sys.argv[5]
    P = pickle.load(open(os.path.join(run7, "ears.pkl"), "rb")); MD = pickle.load(open(mdp, "rb"))
    R = np.array(P["R"]); npz2 = P["npz2"]
    d = np.load(npz2); G = d["grid"].astype(int); F = d["fine"]; K = int(d["k"]); NX, NY, NZ = G.shape
    occ = (G >= 0) & (F.reshape(NX, K, NY, K, NZ, K).mean(axis=(1, 3, 5)) >= 0.5); protect = d["protect"].astype(bool)
    parts = []                      # (ear, colour, num, Mw, ow, group, role)
    for ear, e in P["ears"].items():
        O = np.array(e["O"])
        for c, num, M, o, g, role in e["mod"]: parts.append((ear, c, num, R @ M, O + R @ o, g, role))
    carve = np.zeros(G.shape, bool)
    for ear, c, num, Mw, ow, g, role in parts:
        pts = conn.solid_points(num) @ Mw.T + ow
        for dy in (-4.5, 0.0, 4.5):
            q = pts + np.array([0, dy, 0])
            ix = np.floor(q[:, 0] / 20).astype(int); iy = np.floor(-q[:, 1] / 8).astype(int); iz = np.floor(q[:, 2] / 20).astype(int)
            ok = (ix >= 0) & (ix < NX) & (iy >= 0) & (iy < NY) & (iz >= 0) & (iz < NZ); carve[ix[ok], iy[ok], iz[ok]] = True
    carve &= occ
    n_carve_ears = int(carve.sum())
    md_carve = np.zeros(G.shape, bool)
    for c in MD["carve"]: md_carve[tuple(c)] = True
    md_carve &= occ
    G3 = G.copy()
    for c, col in MD["recolour"].items(): G3[tuple(c)] = col
    carve |= md_carve
    G3[carve] = -1
    hnpz = os.path.join(run, "corps_V81.npz")
    pre = os.path.join(run, "pre_lcm.npz")
    np.savez_compressed(pre, grid=G3, surface=d["surface"], fine=F, k=K, neck=d["neck"], full_shape=d["full_shape"], hoff=d["hoff"])
    LCM = dict(recolour={}, carve=[], parts=[])
    if variant != "none":
        sys.path.insert(0, os.path.expanduser("~/bench/proto/v8")); import lcm
        lcm.run(pre, details, run, variant); LCM = pickle.load(open(os.path.join(run, "lcm_%s.pkl" % variant), "rb"))
        for c, col in LCM["recolour"].items(): G3[tuple(c)] = col
        for c in LCM["carve"]: G3[tuple(c)] = -1
    np.savez_compressed(hnpz, grid=G3, surface=d["surface"], fine=F, k=K, neck=d["neck"], full_shape=d["full_shape"], hoff=d["hoff"])
    r = subprocess.run([sys.executable, os.path.expanduser("~/bench/proto/brickify_plus.py"), hnpz, run, "corps", "--occupancy", "0.5", "--no-shapes", "--drop-floating"],
                       check=True, capture_output=True, text=True)
    body_rep = {k: v for k, v in json.loads(r.stdout.strip().splitlines()[-1]).items() if k not in ("settings", "part_numbers")}
    body = [l for l in open(os.path.join(run, "corps.ldr")).read().splitlines() if l.startswith("1 ")]
    Hocc = np.zeros(G.shape, bool); Hcol = -np.ones(G.shape, int)
    for l in body:
        t = l.split(); Mt = np.array(t[5:14], float).reshape(3, 3); ot = np.array(t[2:5], float); cs = D.box_corners(t[14][:-4]) @ Mt.T + ot
        sl = (slice(int(round(cs[:, 0].min() / 20)), int(round(cs[:, 0].max() / 20))), slice(int(round(-cs[:, 1].max() / 8)), int(round(-cs[:, 1].min() / 8))),
              slice(int(round(cs[:, 2].min() / 20)), int(round(cs[:, 2].max() / 20))))
        Hocc[sl] = True; Hcol[sl] = int(t[1])
    seats = []; seat_cells = []; per_plate = []
    for ear, c, num, Mw, ow, g, role in parts:
        if g != "base": continue
        bottom_y = (D.box_corners(num) @ Mw.T + ow)[:, 1].max(); layer = int(round(-bottom_y / 8)) - 1
        n_ok = 0
        for p, a in conn.part(num)["studs"]:
            s = Mw @ np.array(p) + ow; x, z = int(np.floor(s[0] / 20)), int(np.floor(s[2] / 20))
            if abs(s[0] - (20 * x + 10)) > 0.5 or abs(s[2] - (20 * z + 10)) > 0.5: continue
            if not (0 <= layer - 1 and layer < NY) or Hocc[x, layer, z] or not Hocc[x, layer - 1, z]: continue
            col = Hcol[x, layer - 1, z] if Hcol[x, layer - 1, z] >= 0 else BLACK
            seats.append(D.place_line(col, "3024", np.eye(3), D.axis_place("3024", np.eye(3), (20 * x, -8 * (layer + 1), 20 * z))))
            seat_cells.append((x, layer - 1, z)); Hocc[x, layer, z] = True; n_ok += 1
        per_plate.append(dict(oreille=ear, plaque=role, appuis=n_ok))
    MDP = MD["parts"] + LCM["parts"]
    for q in MDP:
        if q["role"] in ("snot", "incrustation"):
            Mq = np.array(q["R"]); oq = np.array(q["o"]); cs = D.box_corners(q["num"]) @ Mq.T + oq
            yl = int(round(-cs[:, 1].max() / 8)) - 1
            for x in range(int(round(cs[:, 0].min() / 20)), int(round(cs[:, 0].max() / 20))):
                for z in range(int(round(cs[:, 2].min() / 20)), int(round(cs[:, 2].max() / 20))): seat_cells.append((x, yl, z))
    T2P = {"3070b": "3024", "3069b": "3023", "63864": "3623", "2431": "3710", "6636": "3666", "3068b": "3022", "87079": "3020"}
    swapped = 0
    for k, l in enumerate(body):
        t = l.split(); n_ = t[14][:-4]
        if n_ not in T2P: continue
        Mt = np.array(t[5:14], float).reshape(3, 3); ot = np.array(t[2:5], float); cs = D.box_corners(n_) @ Mt.T + ot
        x0, x1 = int(round(cs[:, 0].min() / 20)), int(round(cs[:, 0].max() / 20)); z0, z1 = int(round(cs[:, 2].min() / 20)), int(round(cs[:, 2].max() / 20)); yl = int(round(-cs[:, 1].max() / 8))
        if any(x0 <= x < x1 and z0 <= z < z1 and y == yl for (x, y, z) in seat_cells): t[14] = T2P[n_] + ".dat"; body[k] = " ".join(t); swapped += 1
    order = ["wall", "outer", "outer_t", "inner", "inner_t"]
    W = ["0 paco_V81_sculpture_complete", "0 Name: paco_V81.ldr", "0 Author: moteur 1 V8.1 (V8 + module lignes et cavites), Paco 400 mm"]
    W += body + seats
    for q in MDP:
        if q["role"] in ("snot", "incrustation"): W.append(D.place_line(q["colour"], q["num"], np.array(q["R"]), np.array(q["o"])))
    W += ["0 STEP"]
    for q in MDP:
        if q["role"] not in ("snot", "incrustation"): W.append(D.place_line(q["colour"], q["num"], np.array(q["R"]), np.array(q["o"])))
    W += ["0 STEP"]
    for ear, c, num, Mw, ow, g, role in parts:
        if g == "base": W.append(D.place_line(c, num, Mw, ow))
    W.append("0 STEP")
    for ear in P["ears"]:
        W.append(f"0 BRICKIFY SUBASSEMBLY BEGIN {ear}")
        for g in order:
            for e_, c, num, Mw, ow, gg, role in parts:
                if e_ == ear and gg == g: W.append(D.place_line(c, num, Mw, ow))
        W += [f"0 BRICKIFY SUBASSEMBLY END {ear}", "0 STEP"]
    open(os.path.join(run, "paco_V81.ldr"), "w").write("\n".join(W) + "\n")
    rep = dict(body=body_rep, carved_cells=int(carve.sum()), carved_cells_ears=n_carve_ears, carved_cells_microdetails=int((md_carve & ~np.zeros_like(md_carve)).sum()),
               recoloured_cells=len(MD["recolour"]), parts_microdetails=len(MD["parts"]), parts_lcm=len(LCM["parts"]), cells_lcm_recoloured=len(LCM["recolour"]), cells_lcm_carved=len(LCM["carve"]), carved_protected_cells=int((carve & protect).sum()), seats=per_plate,
               body_tiles_turned_to_plates=swapped, parts_body=len(body), parts_seats=len(seats), parts_ears=len(parts),
               fixations={ear: e["rep"]["fixation"] for ear, e in P["ears"].items()}, prep=P["prep"], lower_ear_frame_shift_ldu=P["lower_shift_ldu"])
    json.dump(rep, open(os.path.join(run, "assemble_report.json"), "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in rep.items() if k not in ("fixations",)}, default=str)[:1500])

if __name__ == "__main__":
    main()
