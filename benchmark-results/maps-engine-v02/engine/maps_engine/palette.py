"""Colour choice (V0.1). Real LEGO colour values (Rebrickable), NON-injective assignment under legibility constraints.
Objective for a class -> colour assignment :  sum_i w_i * dE(source_i, colour_i)            fidelity (w_i = sqrt of the surface)
                                             + LEG * sum over adjacent pairs of the contrast shortfall   legibility
                                             + REF * (number of distinct colours)                          references
Two classes may share a colour when their levels differ (a step of height makes them readable) or when they are not adjacent, or when the source itself shows them as one colour.
Colours must exist (>= MIN_SETS Rebrickable sets) for the core plates, and for the tiles when a smooth finish is requested : a technical existence proxy, NOT a seller stock."""
import sqlite3, itertools
import numpy as np
from .common import lab, rb_colours, PLATES, TILES, dE2000
from _paths import RB_DB

MIN_SETS = 20; LEG = 1.0; REF = 1.0; TOPK = 9; PIECE = 1.2      # PIECE : cost of one extra part, in the units of the fidelity term (weighted dE)
CORE = ["3024", "3023", "3022", "3020", "3710"]; CORE_TILE = ["3070b", "3069b", "3068b", "87079"]
EXCLUDE = ("chrome", "metallic", "pearl", "glitter", "speckle", "milky", "glow", "opal", "rubber", "flat_silver", "flat_gold", "trans", "satin")
_db = None; _cache = {}
def sets(part, colour):
    global _db
    if _db is None: _db = sqlite3.connect(RB_DB)
    k = (part, colour)
    if k not in _cache:
        r = _db.execute("select num_sets from pcs_mat where part_num=? and color_id=?", (part, colour)).fetchone(); _cache[k] = int(r[0]) if r else 0
    return _cache[k]
def available(part, colour): return sets(part, colour) >= MIN_SETS

def _norm(s): return s.lower().replace("_", "").replace(" ", "").replace("-", "").replace("grey", "gray")
def candidates(smooth=False):
    """Rebrickable colour id == LDraw colour code is relied upon by the LDraw file (`1 <code> ...`) : colours whose NAMES differ between the two catalogues (e.g. 326) are excluded"""
    import palette_util as PU
    ld = PU.codes(); out = {}
    for c, v in rb_colours().items():
        if v["trans"] or v["name"].lower().startswith(EXCLUDE) or c > 1000 or c < 0: continue
        if c not in ld or _norm(ld[c][0]) != _norm(v["name"]): continue
        if all(available(p, c) for p in CORE) and (not smooth or all(available(p, c) for p in CORE_TILE)): out[c] = dict(name=v["name"], rgb=np.array(v["rgb"], float))
    return out

def required_contrast(src_a, src_b, level_a, level_b):
    d = float(dE2000(lab(src_a), lab(src_b)))
    if d < 4: return 0.0                                              # the source itself shows one colour (a lake and its river) : keep one colour
    req = min(0.75 * d, 16.0)
    return req * (0.5 if level_a != level_b else 1.0)                  # a step of height already separates two levels

def effective_area(code, smooth=False):
    """largest rectangle (in studs) that exists as a plate (or tile) in this colour, capped at 24 : a colour whose big plates do not exist costs many more parts"""
    cat = TILES if smooth else PLATES; return min(24, max([a * b for (a, b), p in cat.items() if available(p, code)] or [1]))

def assign(class_colours, weights, adjacency, levels, smooth=False, injective=False, blob=None):
    """class_colours {name: rgb} ; weights {name: cells} ; adjacency set of (a, b) ; levels {name: relief level} -> {name: dict(code, name, rgb, dE, ...)}, n candidates, objective"""
    cand = candidates(smooth); codes = sorted(cand); names = list(class_colours); CL = lab(np.array([cand[c]["rgb"] for c in codes])); SL = {n: lab(np.array(class_colours[n], float)) for n in names}
    D = {n: dE2000(CL, SL[n][None, :]) for n in names}; D76 = {n: np.linalg.norm(CL - SL[n], axis=1) for n in names}; w = {n: np.sqrt(max(1.0, weights.get(n, 1))) for n in names}
    EFF = np.array([effective_area(c, smooth) for c in codes], float); blob = blob or {}
    P = {n: weights.get(n, 1) / np.minimum(EFF, max(1.0, blob.get(n, 24.0))) for n in names}                  # estimated number of parts of class n in each candidate colour
    top = {n: list(np.argsort(D[n] + PIECE * P[n] / w[n])[:TOPK]) for n in names}
    pairs = [(a, b, required_contrast(class_colours[a], class_colours[b], levels[a], levels[b])) for a, b in adjacency if a in D and b in D]
    def cost(asg):
        c = sum(w[n] * D[n][asg[n]] + PIECE * P[n][asg[n]] for n in names)
        for a, b, req in pairs:
            gap = float(dE2000(CL[asg[a]], CL[asg[b]])); c += LEG * (w[a] + w[b]) / 2 * max(0.0, req - gap)
        c += REF * len(set(asg.values()))
        if injective and len(set(asg.values())) < len(names): c += 1e6
        return c
    best = None
    for start in range(6):
        rng = np.random.default_rng(start); asg = {n: (top[n][0] if start == 0 else top[n][int(rng.integers(0, min(4, TOPK)))]) for n in names}; cur = cost(asg)
        improved = True
        while improved:
            improved = False
            for n in names:
                for j in top[n]:
                    if j == asg[n]: continue
                    old = asg[n]; asg[n] = j; c = cost(asg)
                    if c < cur - 1e-9: cur = c; improved = True
                    else: asg[n] = old
        if best is None or cur < best[0]: best = (cur, dict(asg))
    cur, asg = best; res = {}
    for n in names:
        j = asg[n]; res[n] = dict(code=int(codes[j]), name=cand[codes[j]]["name"], rgb=[int(v) for v in cand[codes[j]]["rgb"]], dE00=round(float(D[n][j]), 1), dE76=round(float(D76[n][j]), 1), nearest_dE=round(float(D[n].min()), 1), nearest=cand[codes[int(D[n].argmin())]]["name"],
                      pieces_estimees=round(float(P[n][j]), 1), plus_grande_plaque_studs=int(EFF[j]),
                      alternatives=[dict(name=cand[codes[a]]["name"], dE00=round(float(D[n][a]), 1), dE76=round(float(D76[n][a]), 1), pieces_estimees=round(float(P[n][a]), 1)) for a in top[n][:4]])
    return res, len(cand), round(float(cur), 1)

def frame_colour(kinds_needed=("brick", "tile")):
    """a dark, neutral or brown frame / side colour that exists for plates, bricks and tiles"""
    rb = rb_colours(); order = [70, 0, 72]
    for c in order:
        if c in rb and all(available(p, c) for p in ("3004", "3001", "3003", "3009", "3008", "3020", "3022", "3795", "3068b", "87079", "69729")): return c
    raise RuntimeError("no frame colour")

def backing_colour():
    """colour of the two backing layers : the first neutral dark colour in which the big plates (8x8, 4x8, 4x4, 2x8) exist, so that the backing is made of few large plates (a backing in a colour without big plates degrades into 2x1 / 3x1 plates)"""
    for c in (72, 0, 71):
        if all(available(x, c) for x in ("41539", "3035", "3031", "3034")): return c
    raise RuntimeError("no backing colour with big plates")
