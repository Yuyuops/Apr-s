"""Layer tiling : cover the cells of a layer with really existing plates, trading piece count, 1x1 share and stagger of the seams against the layer below."""
import numpy as np
from .common import PLATES
from . import palette as PAL

SIZES = sorted(PLATES, key=lambda s: -s[0] * s[1])             # (long, short)

def _ps(a):
    p = np.zeros((a.shape[0] + 1, a.shape[1] + 1), int); p[1:, 1:] = a.cumsum(0).cumsum(1); return p
def _feasible(ok, w, d):
    """feasible[x, z] : the w x d rectangle (x extent w, z extent d) with its corner at (x, z) lies fully on True cells"""
    p = _ps(ok.astype(int)); n0, n1 = ok.shape; f = np.zeros_like(ok)
    if w > n0 or d > n1: return f
    s = p[w:, d:] - p[:-w, d:] - p[w:, :-d] + p[:-w, :-d]; f[:n0 - w + 1, :n1 - d + 1] = s == w * d; return f

def tile_layer(fixed, wild, below, rng, hidden_colour_of, jitter=0.0, stagger=2.0, allowed=None):
    """fixed (n,n) LEGO colour or -1 ; wild (n,n) bool = hidden cell that may take any colour ; below (n,n) id of the plate under every cell (-1 : none).
    returns list of dict(x, z, w, d, colour, wild_only)"""
    n = fixed.shape[0]; covered = (fixed < 0) & ~wild; plates = []
    colours = sorted(set(fixed[fixed >= 0].tolist()))
    allowed = allowed or PAL.available
    while not covered.all():
        cands = []                                              # (area, g, w, d, feasible mask)
        for g in colours + [None]:
            ok = ~covered & (((fixed == g) | wild) if g is not None else wild)
            if not ok.any(): continue
            for (L, S) in SIZES:
                if g is not None and not allowed(PLATES[(L, S)], g): continue
                for (w, d) in ((L, S), (S, L)) if L != S else ((L, S),):
                    f = _feasible(ok, w, d)
                    if f.any(): cands.append((w * d, g, w, d, f))
        if not cands: raise RuntimeError("cannot cover the layer")
        amax = max(c[0] for c in cands); best = None
        for area, g, w, d, f in cands:
            if area != amax: continue
            for x, z in np.argwhere(f):
                u = len(set(below[x:x + w, z:z + d].ravel().tolist()) - {-1}); sc = stagger * min(u, 3) + (rng.random() * jitter)
                if best is None or sc > best[0]: best = (sc, g, x, z, w, d, None)
        if best is None: raise RuntimeError("cannot cover the layer")
        _, g, x, z, w, d, ok = best
        if g is None:
            g = hidden_colour_of(x, z, w, d, PLATES[(max(w, d), min(w, d))])
        plates.append(dict(x=int(x), z=int(z), w=int(w), d=int(d), colour=int(g), wild_only=bool((fixed[x:x + w, z:z + d] < 0).all())))
        covered[x:x + w, z:z + d] = True
    return plates

def best_tiling(fixed, wild, below, hidden_colour_of, tries=8, seed=0):
    rng = np.random.default_rng(seed); best = None
    for t in range(tries):
        pl = tile_layer(fixed, wild, below, rng, hidden_colour_of, jitter=0.0 if t == 0 else 6.0)
        key = (len(pl), sum(1 for p in pl if p["w"] * p["d"] == 1))
        if best is None or key < best[0]: best = (key, pl)
    return best[1]
