"""Randomised greedy rectangle tiler : covers a set of cells with real LEGO bricks/plates/tiles of one colour, staggering joints (random choice, biased to big pieces)."""
import random
BRICKS = {(1, 1): "3005", (1, 2): "3004", (1, 3): "3622", (1, 4): "3010", (1, 6): "3009", (1, 8): "3008", (2, 2): "3003", (2, 3): "3002", (2, 4): "3001", (2, 6): "2456", (2, 8): "3007"}
PLATES = {(1, 1): "3024", (1, 2): "3023", (1, 3): "3623", (1, 4): "3710", (1, 6): "3666", (1, 8): "3460", (2, 2): "3022", (2, 3): "3021", (2, 4): "3020", (2, 6): "3795", (2, 8): "3034",
          (4, 4): "3031", (4, 6): "3032", (4, 8): "3035", (6, 6): "3958", (6, 8): "3036", (8, 8): "41539"}
TILES = {(1, 1): "3070b", (1, 2): "3069b", (1, 4): "2431", (2, 2): "3068b"}
def _tile_once(cells, table, rng, bias=1.4, max_area=64, support=None):
    """cells: set of (r,c). returns list of (r, c, nr, nc, part, rot) with rot 0 when nc>=nr else 90 (square: 0)"""
    cells = set(cells); left = set(cells); out = []
    shapes = [(a, b) for (a, b) in table] + [(b, a) for (a, b) in table if a != b]
    for r, c in sorted(cells):
        if (r, c) not in left: continue
        fits = []
        for nr, nc in shapes:
            if nr * nc > max_area: continue
            if all((r + i, c + j) in left for i in range(nr) for j in range(nc)): fits.append((nr, nc))
        if support is None: w = [(nr * nc) ** bias for nr, nc in fits]
        else:       # stud joints = footprint cells over a stud below : avoid pieces hanging by one stud, prefer 2-wide shapes
            w = []
            for nr, nc in fits:
                j = sum(1 for i in range(nr) for jj in range(nc) if (r + i, c + jj) in support); a = nr * nc
                w.append((a ** bias) * (1.0 if j >= 3 or j == a else 0.5 if j == 2 else 0.04) * (1.6 if min(nr, nc) >= 2 else 1.0))
        nr, nc = rng.choices(fits, w)[0]
        for i in range(nr):
            for j in range(nc): left.discard((r + i, c + j))
        key = (min(nr, nc), max(nr, nc)); out.append((r, c, nr, nc, table[key], 0 if nc >= nr else 90))
    return out

def score(out, support):
    sc = 0.05 * len(out)
    for (r, c, nr, nc, part, rot) in out:
        j = nr * nc if support is None else sum(1 for i in range(nr) for jj in range(nc) if (r + i, c + jj) in support)
        sc += 3.0 if j <= 1 else 0.3 if j == 2 else 0.0
    return sc
def tile(cells, table, rng, bias=1.4, max_area=64, support=None, tries=30):
    """best of `tries` random tilings : fewest pieces that hang by one stud (support = cells carrying a stud below)"""
    best = None
    for _ in range(tries if support is not None else 1):
        out = _tile_once(cells, table, rng, bias, max_area, support); sc = score(out, support)
        if best is None or sc < best[0]: best = (sc, out)
    return best[1]
