"""LEGO V7 - phase 3 (end): assembly of the whole sculpture.

From the two ear modules of integrate.py: one carving of the whole-character grid (cells hit by any ear part, studs
above and below included), one brickify_plus rebuild (prototype-C settings), seats (1x1 plates) under every turned
plate where its stud falls on the grid (tiles of the body under a seat become plates), colour rule for turned plates
that reach the surface (none expected: both secondary plates are hidden), then the whole LDraw file:
body + seats, turned plates, two sub-assemblies (one per ear), ready for reorder_notice and validate_v3.
usage: assemble.py <run dir>
"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import json, os, pickle, subprocess, sys
import numpy as np
sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, ENGINE_DIR)
sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, ENGINE_DIR)
import conn
import autogen as A6
D = A6.D
BLACK = 0

def main():
    run = sys.argv[1]; P = pickle.load(open(os.path.join(run, "ears.pkl"), "rb"))
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
    G3 = G.copy(); G3[carve] = -1
    hnpz = os.path.join(run, "corps_V7.npz")
    np.savez_compressed(hnpz, grid=G3, surface=d["surface"], fine=F, k=K, neck=d["neck"], full_shape=d["full_shape"], hoff=d["hoff"])
    r = subprocess.run([sys.executable, os.path.join(ENGINE_DIR, "brickify_plus.py"), hnpz, run, "corps", "--occupancy", "0.5", "--no-shapes", "--drop-floating"],
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
    T2P = {"3070b": "3024", "3069b": "3023", "63864": "3623", "2431": "3710", "6636": "3666", "3068b": "3022", "87079": "3020"}
    swapped = 0
    for k, l in enumerate(body):
        t = l.split(); n_ = t[14][:-4]
        if n_ not in T2P: continue
        Mt = np.array(t[5:14], float).reshape(3, 3); ot = np.array(t[2:5], float); cs = D.box_corners(n_) @ Mt.T + ot
        x0, x1 = int(round(cs[:, 0].min() / 20)), int(round(cs[:, 0].max() / 20)); z0, z1 = int(round(cs[:, 2].min() / 20)), int(round(cs[:, 2].max() / 20)); yl = int(round(-cs[:, 1].max() / 8))
        if any(x0 <= x < x1 and z0 <= z < z1 and y == yl for (x, y, z) in seat_cells): t[14] = T2P[n_] + ".dat"; body[k] = " ".join(t); swapped += 1
    order = ["wall", "outer", "outer_t", "inner", "inner_t"]
    W = ["0 paco_V7_sculpture_complete", "0 Name: paco_V7.ldr", "0 Author: moteur 1 V7 (brickify_plus + generateur V6.1 + fixation 3-4-5), Paco 400 mm"]
    W += body + seats + ["0 STEP"]
    for ear, c, num, Mw, ow, g, role in parts:
        if g == "base": W.append(D.place_line(c, num, Mw, ow))
    W.append("0 STEP")
    for ear in P["ears"]:
        W.append(f"0 BRICKIFY SUBASSEMBLY BEGIN {ear}")
        for g in order:
            for e_, c, num, Mw, ow, gg, role in parts:
                if e_ == ear and gg == g: W.append(D.place_line(c, num, Mw, ow))
        W += [f"0 BRICKIFY SUBASSEMBLY END {ear}", "0 STEP"]
    open(os.path.join(run, "paco_V7.ldr"), "w").write("\n".join(W) + "\n")
    rep = dict(body=body_rep, carved_cells=int(carve.sum()), carved_protected_cells=int((carve & protect).sum()), seats=per_plate,
               body_tiles_turned_to_plates=swapped, parts_body=len(body), parts_seats=len(seats), parts_ears=len(parts),
               fixations={ear: e["rep"]["fixation"] for ear, e in P["ears"].items()}, prep=P["prep"], lower_ear_frame_shift_ldu=P["lower_shift_ldu"])
    json.dump(rep, open(os.path.join(run, "assemble_report.json"), "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in rep.items() if k not in ("fixations",)}, default=str)[:1500])

if __name__ == "__main__":
    main()
