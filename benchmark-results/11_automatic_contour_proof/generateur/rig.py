"""Physical test rig of the fixation alone (LEGO V6), generated from the Paco run of autogen.py.

Content (same positions as in the model, so the 3-4-5 coincidences are the real ones):
  * a base plate standing for the skull, under the seats of the lower turned plate;
  * the seats: 1x1 plates on the base (lower plate) and on 1x1 columns (upper plate);
  * the lower turned plate, the root block, the upper turned plate;
  * a 2x16 plate fixed on the upper turned plate, pointing to the ear tip: the lever where the test masses hang.
usage: rig.py <runA dir> <outdir>
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.expanduser("~/bench/tools")); sys.path.insert(0, os.path.expanduser("~/bench/proto"))
sys.path.insert(0, os.path.expanduser("~/bench/proto/ear10"))
import conn, partlib as PL, brickify_plus as BP
import design_v51 as D

def main():
    run, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    rep = json.load(open(os.path.join(run, "oreille_A_paco_report.json")))
    P1, P2 = rep["fixation"]["primary"], rep["fixation"]["secondary"]
    full = open(os.path.join(run, "tete_oreille_A_paco.ldr")).read().splitlines()
    first_step = full.index("0 STEP")
    n_seats = sum(s["seats"] for s in rep["seats"])
    seat_lines = [l for l in full[:first_step] if l.startswith("1 ")][-n_seats:]
    mod = open(os.path.join(run, "oreille_A_paco.ldr")).read().splitlines()
    groups = []; cur = []
    for l in mod:
        if l.startswith("0 STEP"): groups.append(cur); cur = []
        elif l.startswith("1 "): cur.append(l)
    base_lines, wall_lines = groups[0], groups[1]
    def mframe(l):
        t = l.split(); M = np.array(t[5:14], float).reshape(3, 3); o = np.array(t[2:5], float)
        c = D.box_corners(t[14][:-4]) @ M.T + o; m = (c - D.O) @ D.R_MOD
        return m.min(0), m.max(0)
    block = []
    for l in wall_lines:
        lo, hi = mframe(l)
        if -hi[1] >= 47 and -lo[1] <= 81 and lo[0] >= P1["xm0"] - 1 and hi[0] <= P1["xm0"] + 20 * P1["w"] + 1: block.append(l)
    L = ["0 banc_essai_fixation", "0 Name: banc_essai_fixation.ldr", "0 Author: genere depuis la fixation V6 de Paco (memes coincidences 3-4-5)"]
    # seats and supports
    seat_cells = []
    for l in seat_lines:
        t = l.split(); o = np.array(t[2:5], float)
        x, z = int(np.floor((o[0] - 10) / 20 + 0.5)), int(np.floor((o[2] - 10) / 20 + 0.5)); ytop = o[1] - 0.0
        seat_cells.append((x, z, o[1]))
    y_base_top = max(c[2] for c in seat_cells) + 8          # under the lowest seats (LDraw y down)
    xs = [c[0] for c in seat_cells]; zs = [c[1] for c in seat_cells]
    W, Lz = max(xs) - min(xs) + 1, max(zs) - min(zs) + 1
    opts = [(w, l, n) for (w, l), n in BP.PLATES.items() if BP.available(n, 0)] + [(16, 16, "91405"), (8, 16, "92438"), (6, 12, "3028"), (6, 10, "3033")]
    best = None
    for (a, b, n) in opts:
        for (ww, ll, r) in ((a, b, 0), (b, a, 1)):
            if ww >= W and ll >= Lz and (best is None or ww * ll < best[0]): best = (ww * ll, ww, ll, n, r)
    _, ww, ll, nbase, rbase = best
    Rb = np.eye(3) if rbase == 0 else PL.rot_y(1)
    P = conn.part(nbase); ext = (np.abs(np.array([P["hi"][0] - P["lo"][0], P["hi"][2] - P["lo"][2]])) / 20).round()
    if (ext[0] >= ext[1]) != (ww >= ll): Rb = PL.rot_y(1) if rbase == 0 else np.eye(3)
    L.append(D.place_line(72, nbase, Rb, D.axis_place(nbase, Rb, (20 * min(xs), y_base_top, 20 * min(zs)))))
    L.append("0 STEP")
    for (x, z, yo) in seat_cells:
        h = y_base_top - (yo + 8)                         # height to fill under the seat
        y = y_base_top
        while h >= 24: L.append(D.place_line(72, "3005", np.eye(3), D.axis_place("3005", np.eye(3), (20 * x, y - 24, 20 * z)))); y -= 24; h -= 24
        while h >= 8: L.append(D.place_line(72, "3024", np.eye(3), D.axis_place("3024", np.eye(3), (20 * x, y - 8, 20 * z)))); y -= 8; h -= 8
    L += [l.replace("1 0 ", "1 4 ", 1) for l in seat_lines]          # seats in red: the test joints
    L.append("0 STEP")
    L += base_lines[:1] + block + base_lines[1:]
    L.append("0 STEP")
    # lever: 2x16 plate on the upper turned plate (module frame), from the plate end towards the ear tip
    Pl = conn.part("4282"); Rl = np.eye(3) if (Pl["hi"][0] - Pl["lo"][0]) > (Pl["hi"][2] - Pl["lo"][2]) else PL.rot_y(1)
    x_end = P2["xm0"] + 20 * P2["w"]; lo_l = (x_end - 320, -(P2["vp"] + 8), -20)
    o_l = D.axis_place("4282", Rl, lo_l)
    L.append(D.place_line(14, "4282", D.R_MOD @ Rl, D.O + D.R_MOD @ o_l))
    L.append("0 STEP")
    open(os.path.join(out, "banc_essai_fixation.ldr"), "w").write("\n".join(L) + "\n")
    lever_arm_mm = (x_end - (x_end - 320) - 10) * 0.4
    json.dump(dict(base=nbase, base_studs=[ww, ll], seats=len(seat_cells), primary=P1, secondary=P2, lever_part="4282",
                   lever_length_studs=16, load_point_to_upper_plate_end_mm=round(lever_arm_mm, 1)), open(os.path.join(out, "banc_essai.json"), "w"), indent=1)
    print("rig", nbase, ww, ll, "seats", len(seat_cells), "block parts", len(block))

if __name__ == "__main__":
    main()
