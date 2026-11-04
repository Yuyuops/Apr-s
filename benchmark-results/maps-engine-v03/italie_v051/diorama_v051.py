#!/usr/bin/env python3
"""V0.5.1 diorama : Alpine module + Colosseum module on the real-part scene kit. Run: diorama_v051.py --out DIR [--no-trees]"""
import argparse, json, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import Scene
from tiler import tile, PLATES
import terrain, colosseum
ROWS, COLS = 48, 72
BLUE, DGRAY = 272, 72
GROUND = 3
def base(S, rng):
    cells = {(r, c) for r in range(ROWS) for c in range(COLS)}
    for r in range(0, ROWS, 8):
        for c in range(0, COLS, 8): S.add("41539", DGRAY, r, c, 0, 0, "backing")
    for (r, c, nr, nc, part, rot) in tile(cells, PLATES, rng, 2.2, 64): S.add(part, DGRAY, r, c, 1, rot, "backing")
    for (r, c, nr, nc, part, rot) in tile(cells, PLATES, rng, 2.2, 64): S.add(part, BLUE, r, c, 2, rot, "sea")
def build(out, seed=7):
    rng = random.Random(seed); S = Scene(ROWS, COLS); base(S, rng); extra = {}
    K, cat, info = terrain.build_mountain(S, 7, 2, 34, 32, seed); extra["mountain"] = info; extra["mountain_deco"] = terrain.decorate(S, K, cat, 7, 2, seed)
    extra["colosseum"] = colosseum.build_colosseum(S, 24, 53, a=16, b=13)
    m = S.write(out, "LEGO Maps V0.5.1 Alpine module and Colosseum", extra); print(json.dumps(m)); return S
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="results/diorama"); ap.add_argument("--seed", type=int, default=7); a = ap.parse_args(); build(a.out, a.seed)
