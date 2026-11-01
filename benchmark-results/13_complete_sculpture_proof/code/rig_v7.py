"""LEGO V7: physical test rigs of the critical fixations (one per ear), generated from the assembled model.

For each ear: its two turned plates, its root block, the 1x1 seats at the exact positions of the model (3-4-5
coincidences), columns of 1x1 bricks/plates down to a common base plate standing for the head, and a 2x16 lever on
the upper turned plate pointing towards the ear tip (the test masses hang at its end).
usage: rig_v7.py <run dir> <outdir>
"""
import json, os, pickle, sys
import numpy as np
sys.path.insert(0, os.path.expanduser("~/bench/tools")); sys.path.insert(0, os.path.expanduser("~/bench/proto"))
sys.path.insert(0, os.path.expanduser("~/bench/proto/ear10"))
import conn, partlib as PL, brickify_plus as BP
import design_v51 as D

def main():
    run, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    P = pickle.load(open(os.path.join(run, "ears.pkl"), "rb")); R = np.array(P["R"])
    rep = json.load(open(os.path.join(run, "assemble_report.json")))
    lines = open(os.path.join(run, "paco_V7.ldr")).read().splitlines()
    first = lines.index("0 STEP")
    n_seats = sum(s["appuis"] for s in rep["seats"])
    seats = [l for l in lines[:first] if l.startswith("1 ")][-n_seats:]
    summary = {}
    for ear, e in P["ears"].items():
        O = np.array(e["O"]); fix = e["rep"]["fixation"]; P1, P2 = fix["primary"], fix["secondary"]
        plates = [(c, n, R @ M, O + R @ o) for c, n, M, o, g, role in e["mod"] if g == "base"]
        block = [(c, n, R @ M, O + R @ o) for c, n, M, o, g, role in e["mod"] if g == "wall" and "bloc" in role]
        # seats of this ear: under one of its plates
        mine = []
        for l in seats:
            t = l.split(); so = np.array(t[2:5], float)
            for c, n, Mw, ow in plates:
                cs = D.box_corners(n) @ Mw.T + ow
                if cs[:, 0].min() - 20 <= so[0] <= cs[:, 0].max() + 20 and cs[:, 2].min() - 20 <= so[2] <= cs[:, 2].max() + 20 and abs(so[1] - cs[:, 1].max()) < 17: mine.append(so); break
        L = [f"0 banc_essai_{ear}", f"0 Name: banc_essai_{ear}.ldr", "0 Author: genere depuis le modele V7 (memes coincidences 3-4-5)"]
        y_base = max(s[1] for s in mine) + 8                                   # top of the base plate (LDraw y down)
        xs = [int(round((s[0] - 10) / 20)) for s in mine]; zs = [int(round((s[2] - 10) / 20)) for s in mine]
        W, Lz = max(xs) - min(xs) + 1, max(zs) - min(zs) + 1
        opts = [(w, l, n) for (w, l), n in BP.PLATES.items() if BP.available(n, 72)] + [(16, 16, "91405"), (8, 16, "92438"), (6, 12, "3028"), (6, 10, "3033")]
        best = None
        for (a, b, n) in opts:
            for (ww, ll) in ((a, b), (b, a)):
                if ww >= W and ll >= Lz and (best is None or ww * ll < best[0]): best = (ww * ll, ww, ll, n)
        _, ww, ll, nb = best
        Pb = conn.part(nb); along_x = (Pb["hi"][0] - Pb["lo"][0]) >= (Pb["hi"][2] - Pb["lo"][2])
        Rb = np.eye(3) if (along_x == (ww >= ll)) else PL.rot_y(1)
        L.append(D.place_line(72, nb, Rb, D.axis_place(nb, Rb, (20 * min(xs), y_base, 20 * min(zs))))); L.append("0 STEP")
        for s, x, z in zip(mine, xs, zs):
            h = y_base - (s[1] + 8); y = y_base
            while h >= 24: L.append(D.place_line(72, "3005", np.eye(3), D.axis_place("3005", np.eye(3), (20 * x, y - 24, 20 * z)))); y -= 24; h -= 24
            while h >= 8: L.append(D.place_line(72, "3024", np.eye(3), D.axis_place("3024", np.eye(3), (20 * x, y - 8, 20 * z)))); y -= 8; h -= 8
            L.append(D.place_line(4, "3024", np.eye(3), s))                   # the test joint, red
        L.append("0 STEP")
        for c, n, Mw, ow in plates[:1] + block + plates[1:]: L.append(D.place_line(0, n, Mw, ow))
        L.append("0 STEP")
        top = max(plates, key=lambda p: -(D.box_corners(p[1]) @ p[2].T + p[3])[:, 1].min())   # highest plate
        Pl = conn.part("4282"); Rl = np.eye(3) if (Pl["hi"][0] - Pl["lo"][0]) > (Pl["hi"][2] - Pl["lo"][2]) else PL.rot_y(1)
        Ptop = P2 if P2 and P2["vp"] >= P1["vp"] else P1
        x_end = Ptop["xm0"] + 20 * Ptop["w"]
        o_l = D.axis_place("4282", Rl, (x_end - 320, -(Ptop["vp"] + 8), -20))
        L.append(D.place_line(14, "4282", R @ Rl, O + R @ o_l)); L.append("0 STEP")
        open(os.path.join(out, f"banc_essai_{ear}.ldr"), "w").write("\n".join(L) + "\n")
        summary[ear] = dict(base=nb, base_studs=[ww, ll], test_joints=len(mine), primary=P1, secondary=P2, lever="4282 (2x16)", load_arm_mm=round((320 - 10) * 0.4, 1))
    json.dump(summary, open(os.path.join(out, "bancs_essai.json"), "w"), indent=1)
    print(json.dumps({k: (v["base"], v["test_joints"]) for k, v in summary.items()}))

if __name__ == "__main__":
    main()
