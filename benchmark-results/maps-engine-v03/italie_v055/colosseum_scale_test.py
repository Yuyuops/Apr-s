#!/usr/bin/env python3
"""Where does the oval stay legible ? builds the Colosseum alone on sea for several footprints / oval exponents. usage: colosseum_scale_test.py OUTROOT"""
import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import Scene
import region, colosseum
root = sys.argv[1]
for name, rows, cols, n, gaps in (("20x26_n2.6", 20, 26, 2.6, True), ("22x28_n2.8", 22, 28, 2.8, True), ("24x30_n3.0", 24, 30, 3.0, True), ("26x32_n3.2", 26, 32, 3.2, False)):
    R, C = ((rows + 8 + 7) // 8) * 8, ((cols + 8 + 7) // 8) * 8; a, b, pe = region.colosseum_geometry(rows, cols)
    for g in ((gaps, False) if gaps else (False,)):
        try:
            S = Scene(R, C); region.base(S, R, C, random.Random(1)); info = colosseum.build_colosseum(S, R // 2, C // 2, a=a, b=b, plaza_extra=pe, n_oval=n, gaps=g); m = S.write(os.path.join(root, name), "colosseum " + name, dict(colosseum=info, gaps=g)); print(name, m["pieces"], "gaps", g, info); break
        except ValueError as e: print(name, "gaps", g, "failed:", str(e)[:60])
