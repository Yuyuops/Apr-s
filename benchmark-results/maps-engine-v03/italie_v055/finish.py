"""Finishing layers of the full model : decorative frame, smooth sea (tiles, depth-graded blues), ITALIA title and compass rose (tiles)."""
import random
import numpy as np
from scipy import ndimage
from tiler import tile, BRICKS, TILES
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "italia"))
from decor import text_cells, compass_cells
RBROWN, DTAN, TAN, WHITE, RED = 70, 28, 19, 15, 4
def frame(S, R, C, f, rng, layers=3):
    """ring of f studs around the f..f+R, f..f+C field : brown bricks (stud-aware tiling, joints staggered per layer) + dark-tan tile cap"""
    ring = {(r, c) for r in range(R + 2 * f) for c in range(C + 2 * f) if r < f or c < f or r >= R + f or c >= C + f}
    for k in range(layers):
        y = 3 + 3 * k
        for (r, c, nr, nc, part, rot) in tile(ring, BRICKS, rng, 1.6, 12, S.stud_cells(y), 4): S.add(part, RBROWN, r, c, y, rot, "frame")
    y = 3 + 3 * layers
    for (r, c, nr, nc, part, rot) in tile(ring, TILES, rng, 1.8, 8, S.stud_cells(y), 3): S.add(part, DTAN, r, c, y, rot, "frame_cap")
    return len(ring)
def decor(S, zones, f, rng):
    """zones = {'title': {row, col, text}, 'compass': {row, col, d}} in FIELD coordinates (frame offset added here)"""
    n0 = len(S.parts)
    def lay(group, colour, region):
        for (r, c, nr, nc, part, rot) in tile(group, TILES, rng, 1.6, 8, S.stud_cells(3), 6): S.add(part, colour, r, c, 3, rot, region)
    if "title" in zones:
        z = zones["title"]; t, _ = text_cells(z["text"], 1); lay({(z["row"] + r + f, z["col"] + c + f) for r, c in t}, WHITE, "title_ITALIA")
    if "compass" in zones:
        z = zones["compass"]; cp = compass_cells(z["d"])
        for role, col in (("ring", DTAN), ("blade", WHITE), ("diag", TAN), ("north", RED), ("centre", DTAN)): lay({(z["row"] + r + f, z["col"] + c + f) for (r, c), v in cp.items() if v == role}, col, "compass_" + role)
    return len(S.parts) - n0
def sea_tiles(S, R, C, f, land_dist, rng):
    """smooth sea : tiles on every free sea cell of the field, colour graded by distance to the coast (dark azure shallows -> blue -> deep dark blue), dithered at the boundaries"""
    free = {(r + f, c + f) for r in range(R) for c in range(C) if S.free(r + f, c + f, 3, 1, 1, 1)}
    groups = {}
    for (r, c) in free:
        d = land_dist[r - f, c - f] + rng.uniform(-0.8, 0.8); col = 321 if d <= 1.6 else 1 if d <= 4.2 else 272; groups.setdefault(col, set()).add((r, c))
    n = 0
    for col, cells in groups.items():
        for (r, c, nr, nc, part, rot) in tile(cells, TILES, rng, 1.8, 16, S.stud_cells(3), 2): S.add(part, col, r, c, 3, rot, "sea_tiles"); n += 1
    return n

def leader(S, cells, f, rng, colour=DTAN):
    """thin causeway of tiles from an off-shore medallion to the true position of the monument (cartographic leader line)"""
    group = {(r + f, c + f) for (r, c) in cells if S.free(r + f, c + f, 3, 1, 1, 1)}
    n = 0
    for (r, c, nr, nc, part, rot) in tile(group, TILES, rng, 2.0, 8, S.stud_cells(3), 6): S.add(part, colour, r, c, 3, rot, "leader_causeway"); n += 1
    return n
