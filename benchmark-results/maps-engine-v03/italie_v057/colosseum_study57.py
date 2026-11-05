#!/usr/bin/env python3
"""V0.5.7 phase 1 : Colosseum facades compared on the same sea patch. variants = A (V0.5.6 reference, 20x26), A2 (arch 1x3 on 3-stud and 5-stud facets + windows on 2-stud facets : arcade rhythm on curved stretches, 20x26), A3 (enlarged medallion 28x36 with A2).
usage: colosseum_study57.py OUTROOT [variants]"""
import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import Scene
import region, colosseum_v2
root = sys.argv[1]; V = {"A5": (20, 26, False), "A5b": (28, 36, False), "A": (20, 26, False), "A2": (20, 26, True), "A3": (28, 36, True), "A4": (24, 31, True)}
for name in (sys.argv[2].split(",") if len(sys.argv) > 2 else ["A", "A2", "A3"]):
    rows, cols, arch3 = V[name]; R, C = rows + 12, cols + 14; S = Scene(R, C); S.do_merge = True; region.base(S, R, C, random.Random(1)); a, b, pe = region.colosseum_geometry(rows, cols); colosseum_v2.ARCH3 = arch3
    info = colosseum_v2.build(S, R // 2, C // 2, a, b, pe, 2.6, "A5" if name.startswith("A5") else "A"); m = S.write(os.path.join(root, name), "colosseum " + name, dict(colosseum=info, footprint=[rows, cols])); print(name, m["pieces"], info)
