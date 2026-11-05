#!/usr/bin/env python3
"""Extracts a stand-alone prototype (sub-assembly) from a full model : every piece intersecting the board box [r0,r1) x [c0,c1) plus the closure of the pieces that carry them
(nothing floats), re-based to its own bounding box, then written with the same joint data / validation chain. usage: extract_box.py MODELDIR OUTDIR r0 r1 c0 c1 "title" """
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import Scene
D, OUT = sys.argv[1], sys.argv[2]; r0, r1, c0, c1 = map(int, sys.argv[3:7]); title = sys.argv[7] if len(sys.argv) > 7 else "prototype"
P = json.load(open(D + "/parts.json")); sel = [p for p in P if p["r"] < r1 and p["r"] + p["nr"] > r0 and p["c"] < c1 and p["c"] + p["nc"] > c0]
byy = {}
for q in P: byy.setdefault(q["y"] + q["h"], []).append(q)
ids = {p["id"] for p in sel}; todo = list(sel)
while todo:
    p = todo.pop()
    if p["y"] == 0: continue
    for q in byy.get(p["y"], []):
        if q["id"] not in ids and q["r"] < p["r"] + p["nr"] and q["r"] + q["nr"] > p["r"] and q["c"] < p["c"] + p["nc"] and q["c"] + q["nc"] > p["c"]: ids.add(q["id"]); sel.append(q); todo.append(q)
R0, R1 = min(p["r"] for p in sel), max(p["r"] + p["nr"] for p in sel); C0, C1 = min(p["c"] for p in sel), max(p["c"] + p["nc"] for p in sel); R, C = R1 - R0, C1 - C0; S = Scene(R, C)
for p in sorted(sel, key=lambda p: (p["y"], p["id"])): S.add(p["part"], p["colour"], p["r"] - R0, p["c"] - C0, p["y"], p["rot"], p["region"], p["nr"], p["nc"], p["h"])
m = S.write(OUT, title, dict(source=os.path.basename(D.rstrip("/")), window_rows=[R0, R1], window_cols=[C0, C1], requested_box=[r0, r1, c0, c1], grid_studs=[R, C], frame_studs=0, height_plates=max(p["y"] + p["h"] for p in sel), style="premium_noyer_or_lagon_c2i (V0.8 final)"))
print(m["pieces"], "pieces", m["size_studs"], "studs")
