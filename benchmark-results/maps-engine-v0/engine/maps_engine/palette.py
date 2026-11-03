"""LEGO colour choice by colorimetric proximity to the source, restricted to colours in which the plates really exist (>= MIN_SETS Rebrickable sets per part : a technical existence proxy, NOT a seller stock)."""
import sqlite3
import numpy as np
from scipy.optimize import linear_sum_assignment
from .common import lab, PLATES
import palette_util as PU
from _paths import RB_DB

MIN_SETS = 20
CORE = ["3024", "3023", "3022", "3020", "3710"]
EXCLUDE = ("trans", "chrome", "glitter", "pearl", "metal", "opal", "speckle", "milky", "glow", "flat_silver", "flat_gold", "rubber", "very_light_bluish")
_db = None
_cache = {}
def sets(part, colour):
    global _db
    if _db is None: _db = sqlite3.connect(RB_DB)
    k = (part, colour)
    if k not in _cache:
        r = _db.execute("select num_sets from pcs_mat where part_num=? and color_id=?", (part, colour)).fetchone(); _cache[k] = int(r[0]) if r else 0
    return _cache[k]
def available(part, colour): return sets(part, colour) >= MIN_SETS

def candidates():
    codes = PU.codes(); out = {}
    for c, (name, rgb) in codes.items():
        if c >= 512 or name.lower().startswith(EXCLUDE): continue
        if all(available(p, c) for p in CORE): out[c] = dict(name=name, rgb=np.array(rgb, float))
    return out

def assign(class_colours, weights=None):
    """injective assignment class -> LEGO colour minimising the area-weighted (sqrt of the cell count) Delta E (CIE76) ; two different classes never share a colour"""
    cand = candidates(); codes = sorted(cand); names = list(class_colours)
    C = np.array([[np.linalg.norm(lab(class_colours[n]) - lab(cand[c]["rgb"])) for c in codes] for n in names])
    w = np.array([np.sqrt(max(1.0, (weights or {}).get(n, 1.0))) for n in names]); r, c = linear_sum_assignment(C * w[:, None]); res = {}
    for i, j in zip(r, c): res[names[i]] = dict(code=codes[j], name=cand[codes[j]]["name"], rgb=[int(v) for v in cand[codes[j]]["rgb"]], dE=round(float(C[i, j]), 1),
                                                   nearest_free_dE=round(float(C[i].min()), 1))
    return res, len(cand)

def backing_colour():
    for c in (72, 71, 0, 85, 308):
        if all(available(p, c) for p in ("41539", "3035", "3031")): return c
    raise RuntimeError("no backing colour with 8x8 / 4x8 / 4x4 plates")
