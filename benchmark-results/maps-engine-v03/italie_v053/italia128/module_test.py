#!/usr/bin/env python3
"""Proves that a monument module is resizable from the config alone : builds the Colosseum at the footprint given by the config (rows, cols), validated + rendered.
usage: module_test.py colosseum <rows> <cols> OUTDIR"""
import sys, os, json, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))
from scene import Scene
from tiler import tile, PLATES
import colosseum
kind, rows, cols, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
R, C = ((rows + 6 + 7) // 8) * 8, ((cols + 6 + 7) // 8) * 8; S = Scene(R, C); rng = random.Random(1); cells = {(r, c) for r in range(R) for c in range(C)}
for r in range(0, R, 8):
    for c in range(0, C, 8): S.add("41539", 72, r, c, 0, 0, "backing")
for (r, c, nr, nc, part, rot) in tile(cells, PLATES, rng, 2.2, 64): S.add(part, 72, r, c, 1, rot, "backing")
for (r, c, nr, nc, part, rot) in tile(cells, PLATES, rng, 2.2, 64): S.add(part, 272, r, c, 2, rot, "sea")
pm = 1; a = (cols - 2 * pm) / 2.0; b = (rows - 2 * pm) / 2.0
info = colosseum.build_colosseum(S, R // 2, C // 2, a=a - 1.2, b=b - 1.2, plaza_extra=1.2 + pm)
m = S.write(out, "Colosseum module %dx%d" % (rows, cols), dict(colosseum=info, requested_footprint=[rows, cols])); print(json.dumps(m)[:400])
