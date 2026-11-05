"""Seam-crossing base : the three hidden layers under the model (y=2 sea plates, y=1 and y=0 backing) are tiled AFTER everything above exists, choosing plates whose seams cut through the pieces above, so that
every multi-stud piece above rests on >= 2 plates (no piece depends on a single plate) and every plate carries several pieces. Best-of-N randomised greedy tilings scored by the number of
pieces above that still have a single owner. Real catalogue plates only (tiler.PLATES), colours : y=2 sea blue 272, y=1/y=0 dark bluish grey 72."""
import random
from tiler import PLATES
SHAPES = sorted({(a, b) for (a, b) in PLATES} | {(b, a) for (a, b) in PLATES if a != b})
BIAS2 = 2.8; PLATE_COST = 0.02; BIAS = 1.2; PEN = 0.12; MAXA = 32
SMALL = [s for s in SHAPES if s[0] * s[1] <= 32]
def layer_map(S, y):
    """cell -> id of the piece occupying plane y (any piece), for pieces above"""
    m = {}
    for p in S.parts:
        if p["y"] == y + 1:
            for r in range(p["r"], p["r"] + p["nr"]):
                for c in range(p["c"], p["c"] + p["nc"]): m[(r, c)] = p["id"]
    return m
def one_try(R, C, above, area_of, rng, max_area):
    left = [[True] * C for _ in range(R)]; out = []
    for r in range(R):
        for c in range(C):
            if not left[r][c]: continue
            fits = []
            for nr, nc in SHAPES:
                if nr * nc > max_area or r + nr > R or c + nc > C: continue
                if all(left[r + i][c + j] for i in range(nr) for j in range(nc)):
                    ids = {above.get((r + i, c + j)) for i in range(nr) for j in range(nc)}; ids.discard(None)
                    fits.append((nr, nc, ids))
            if not fits: nr, nc, ids = 1, 1, set(); fits = [(1, 1, set())]
            w = []
            for nr, nc, ids in fits:
                a = nr * nc; cont = sum(1 for pid in ids if area_of[pid] >= 2 and bbox[pid][0] >= r and bbox[pid][1] >= c and bbox[pid][2] <= r + nr and bbox[pid][3] <= c + nc)
                ones = sum(1 for pid in ids if area_of[pid] == 1)
                w.append((a ** (BIAS2 if ones else BIAS)) * (PEN ** cont) * (1.0 if len(ids) >= 2 or not ids else 0.4))
            nr, nc, ids = rng.choices(fits, w)[0]
            for i in range(nr):
                for j in range(nc): left[r + i][c + j] = False
            out.append((r, c, nr, nc))
    return out
bbox = {}; above_cells = None
def score(plates, above, area_of):
    owners = {}
    for (r, c, nr, nc) in plates:
        ids = {above.get((r + i, c + j)) for i in range(nr) for j in range(nc)}; ids.discard(None)
        for pid in ids: owners.setdefault(pid, set()).add((r, c))
    sole_plates = {next(iter(o)) for pid, o in owners.items() if len(o) == 1}
    multi_single = sum(1 for pid, o in owners.items() if len(o) == 1 and area_of[pid] >= 2)
    return len(sole_plates) + 0.5 * multi_single
def fit_layer(S, y, colour, region, R, C, rng, tries=12, max_area=None):
    max_area = max_area or MAXA
    global bbox
    above = layer_map(S, y); area_of = {p["id"]: p["nr"] * p["nc"] for p in S.parts if p["y"] == y + 1}
    bbox = {p["id"]: (p["r"], p["c"], p["r"] + p["nr"], p["c"] + p["nc"]) for p in S.parts if p["y"] == y + 1}
    best = None
    for _ in range(tries):
        t = one_try(R, C, above, area_of, rng, max_area); sc = score(t, above, area_of) + PLATE_COST * len(t)
        if best is None or sc < best[0]: best = (sc, t)
    for (r, c, nr, nc) in best[1]: S.add(PLATES[(min(nr, nc), max(nr, nc))], colour, r, c, y, 0 if nc >= nr else 90, region)
    return dict(layer=y, plates=len(best[1]), single_owner_pieces_above=int(best[0]))
def build_base(S, R, C, rng, tries=12):
    info = [fit_layer(S, 2, 272, "sea", R, C, rng, tries), fit_layer(S, 1, 72, "backing", R, C, rng, tries), fit_layer(S, 0, 72, "backing", R, C, rng, tries)]
    return info
