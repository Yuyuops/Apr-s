#!/usr/bin/env python3
"""Proof that the ITALIA title and the compass rose are built from real LEGO tiles : small sea patch, LDraw + validation + render. usage: decor_patch.py OUTDIR"""
import sys, os, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, HERE)
from scene import Scene
from tiler import tile, PLATES, TILES
from decor import text_cells, compass_cells
out = sys.argv[1]; R, C = 24, 64; S = Scene(R, C); rng = random.Random(2); cells = {(r, c) for r in range(R) for c in range(C)}
for r in range(0, R, 8):
    for c in range(0, C, 8): S.add("41539", 72, r, c, 0, 0, "backing")
for (r, c, nr, nc, part, rot) in tile(cells, PLATES, rng, 2.2, 64): S.add(part, 72, r, c, 1, rot, "backing")
for (r, c, nr, nc, part, rot) in tile(cells, PLATES, rng, 2.2, 64): S.add(part, 272, r, c, 2, rot, "sea")
def lay(group, colour, region):
    for (r, c, nr, nc, part, rot) in tile(group, TILES, rng, 1.6, 8, S.stud_cells(3), 20): S.add(part, colour, r, c, 3, rot, region)
t, (h, w) = text_cells("ITALIA", 1); lay({(8 + r, 2 + c) for r, c in t}, 15, "title_tiles")
cp = compass_cells(15); ox, oy = 44, 4
for role, col in (("ring", 28), ("blade", 15), ("diag", 19), ("north", 4), ("centre", 28)): lay({(oy + r, ox + c) for (r, c), v in cp.items() if v == role}, col, "compass_" + role)
print(S.write(out, "ITALIA title and compass rose from tiles", dict(letters=len(t), compass_cells=len(cp))))
