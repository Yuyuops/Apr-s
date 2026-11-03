"""Layer tiling : cover the cells of a layer with really existing parts (plates, tiles or bricks), trading piece count, 1x1 share, orphan cells and seam stagger against the layer below."""
import numpy as np
from . import palette as PAL

def _ps(a):
    p = np.zeros((a.shape[0] + 1, a.shape[1] + 1), int); p[1:, 1:] = a.cumsum(0).cumsum(1); return p
def _feasible(ok, w, d):
    p = _ps(ok.astype(int)); n0, n1 = ok.shape; f = np.zeros_like(ok)
    if w > n0 or d > n1: return f
    s = p[w:, d:] - p[:-w, d:] - p[w:, :-d] + p[:-w, :-d]; f[:n0 - w + 1, :n1 - d + 1] = s == w * d; return f

def _orphans(fixed, wild, free, x, z, w, d):
    n0, n1 = fixed.shape; F = free.copy(); F[x:x + w, z:z + d] = False; cnt = 0; ring = set()
    for a in range(x, x + w): ring.update(((a, z - 1), (a, z + d)))
    for b in range(z, z + d): ring.update(((x - 1, b), (x + w, b)))
    for (a, b) in ring:
        if not (0 <= a < n0 and 0 <= b < n1) or not F[a, b]: continue
        ok = False
        for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p, q = a + da, b + db
            if 0 <= p < n0 and 0 <= q < n1 and F[p, q] and (fixed[p, q] == fixed[a, b] or wild[p, q] or wild[a, b]) and (fixed[p, q] >= 0 or wild[p, q]) and (fixed[a, b] >= 0 or wild[a, b]): ok = True; break
        if not ok: cnt += 1
    return cnt

def _seam_arrays(below):
    n0, n1 = below.shape; H = np.zeros((n0, n1), int); V = np.zeros((n0, n1), int)
    H[:, :-1] = (below[:, :-1] != below[:, 1:]) & (below[:, :-1] >= 0) & (below[:, 1:] >= 0); V[:-1, :] = (below[:-1, :] != below[1:, :]) & (below[:-1, :] >= 0) & (below[1:, :] >= 0); return H, V
def _aligned(H, V, x, z, w, d):
    n0, n1 = H.shape; c = 0
    if z > 0: c += H[x:x + w, z - 1].sum()
    if z + d - 1 < n1 - 1: c += H[x:x + w, z + d - 1].sum()
    if x > 0: c += V[x - 1, z:z + d].sum()
    if x + w - 1 < n0 - 1: c += V[x + w - 1, z:z + d].sum()
    return int(c)

DEFAULTS = dict(orphan_cost=60.0, seam_pen=4.0)      # measured on the island : fewest lonely 1x1 plates, seams still staggered (see RAPPORT)
def tile_layer(fixed, wild, below, rng, hidden_colour_of, catalog, jitter=0.0, stagger=2.0, allowed=None, orphan_cost=None, orphan_tiers=3, seam_pen=None, orient=0.0, orient_strict=False):
    orphan_cost = DEFAULTS["orphan_cost"] if orphan_cost is None else orphan_cost; seam_pen = DEFAULTS["seam_pen"] if seam_pen is None else seam_pen
    """fixed (n,m) colour or -1 ; wild (n,m) bool = hidden cell that may take any colour ; below (n,m) id of the part under each cell (-1 none) ; catalog {(long,short): part}.
    returns [dict(x, z, w, d, colour, wild_only)]  (x = row, w = extent in rows ; z = column, d = extent in columns)"""
    covered = (fixed < 0) & ~wild; parts = []; colours = sorted(set(fixed[fixed >= 0].tolist())); allowed = allowed or PAL.available
    sizes = sorted(catalog, key=lambda s: -s[0] * s[1]); H, V = _seam_arrays(below)
    while not covered.all():
        cands = []
        for g in colours + [None]:
            ok = ~covered & (((fixed == g) | wild) if g is not None else wild)
            if not ok.any(): continue
            for (L, S) in sizes:
                if g is not None and not allowed(catalog[(L, S)], g): continue
                for (w, d) in ((L, S), (S, L)) if L != S else ((L, S),):
                    f = _feasible(ok, w, d)
                    if f.any(): cands.append((w * d, g, w, d, f))
        if not cands: raise RuntimeError("cannot cover the layer")
        if orient_strict:                                                      # smooth finish : tiles run along the columns (like planks) unless a cell cannot be reached that way
            hz = [c for c in cands if c[3] >= c[2]]
            if hz: cands = hz
        areas = sorted({c[0] for c in cands}, reverse=True)[:orphan_tiers]; best = None; free_now = ~covered
        for area, g, w, d, f in cands:
            if area not in areas: continue
            for x, z in np.argwhere(f):
                u = len(set(below[x:x + w, z:z + d].ravel().tolist()) - {-1})
                sc = area * 10.0 + stagger * min(u, 3) + rng.random() * jitter - orphan_cost * _orphans(fixed, wild, free_now, x, z, w, d) - seam_pen * _aligned(H, V, x, z, w, d) + (orient if d > w else 0.0)
                if best is None or sc > best[0]: best = (sc, g, x, z, w, d)
        _, g, x, z, w, d = best
        if g is None: g = hidden_colour_of(x, z, w, d, catalog[(max(w, d), min(w, d))])
        parts.append(dict(x=int(x), z=int(z), w=int(w), d=int(d), colour=int(g), wild_only=bool((fixed[x:x + w, z:z + d] < 0).all())))
        covered[x:x + w, z:z + d] = True
    return parts

def best_tiling(fixed, wild, below, hidden_colour_of, catalog, tries=8, seed=0, allowed=None, **kw):
    rng = np.random.default_rng(seed); best = None
    for t in range(tries):
        pl = tile_layer(fixed, wild, below, rng, hidden_colour_of, catalog, jitter=0.0 if t == 0 else 6.0, allowed=allowed, **kw)
        H, V = _seam_arrays(below); key = (len(pl), sum(1 for p in pl if p["w"] * p["d"] == 1), sum(_aligned(H, V, p["x"], p["z"], p["w"], p["d"]) for p in pl))
        if best is None or key < best[0]: best = (key, pl)
    return best[1]

def merge_small(parts, catalog, allowed=None, max_small=2):
    """merge a 1x1 / 1x2 part with an adjacent part of the same colour when their union is a rectangle that exists as a part : fewer parts, fewer lonely 1-stud contacts (same footprint, same colours)"""
    allowed = allowed or PAL.available; parts = [dict(p) for p in parts]; changed = True
    while changed:
        changed = False
        parts.sort(key=lambda p: p["w"] * p["d"])
        for i, a in enumerate(parts):
            if a["w"] * a["d"] > max_small: break
            for j, b in enumerate(parts):
                if i == j: continue
                if a.get("wild_only"): colour = b["colour"]                                    # a hidden part may take the colour of its neighbour
                elif b.get("wild_only") or a["colour"] == b["colour"]: colour = a["colour"]
                else: continue
                x0 = min(a["x"], b["x"]); z0 = min(a["z"], b["z"]); x1 = max(a["x"] + a["w"], b["x"] + b["w"]); z1 = max(a["z"] + a["d"], b["z"] + b["d"]); w, d = x1 - x0, z1 - z0
                if w * d != a["w"] * a["d"] + b["w"] * b["d"]: continue                      # union must be a full rectangle (no overlap, no hole)
                key = (max(w, d), min(w, d))
                if key not in catalog or not allowed(catalog[key], colour): continue
                parts[j] = dict(x=x0, z=z0, w=w, d=d, colour=colour, wild_only=a.get("wild_only", False) and b.get("wild_only", False)); parts.pop(i); changed = True; break
            if changed: break
    return parts

def local_improve(parts, catalog, below, tries=60, seed=0, window=2, max_cells=60, allowed=None, small=1):
    """local search on a finished layer : around every 1x1 part, the neighbouring parts of the same colour (or hidden ones) are re-tiled many times with random tie-breaks ; the new tiling is kept when it has fewer 1x1 parts, or as many 1x1 parts and fewer parts. Footprint and colours of the visible cells never change."""
    allowed = allowed or PAL.available; rng = np.random.default_rng(seed); parts = [dict(p) for p in parts]
    n0 = max(p["x"] + p["w"] for p in parts) if parts else 0; n1 = max(p["z"] + p["d"] for p in parts) if parts else 0; n0 = max(n0, below.shape[0]); n1 = max(n1, below.shape[1])
    changed = True; guard = 0
    while changed and guard < 4:
        changed = False; guard += 1
        for p in [q for q in parts if q["w"] * q["d"] <= small]:
            if p not in parts: continue
            grp = [q for q in parts if q is p or (not (q["x"] > p["x"] + window or q["x"] + q["w"] < p["x"] - window or q["z"] > p["z"] + window or q["z"] + q["d"] < p["z"] - window) and (q["colour"] == p["colour"] or q.get("wild_only") or p.get("wild_only")))]
            cells = sum(q["w"] * q["d"] for q in grp)
            if len(grp) < 2 or cells > max_cells: continue
            x0 = min(q["x"] for q in grp); z0 = min(q["z"] for q in grp); x1 = max(q["x"] + q["w"] for q in grp); z1 = max(q["z"] + q["d"] for q in grp)
            fixed = -np.ones((x1 - x0, z1 - z0), int); wild = np.zeros_like(fixed, bool); colour_at = np.zeros_like(fixed)
            for q in grp:
                sl = (slice(q["x"] - x0, q["x"] - x0 + q["w"]), slice(q["z"] - z0, q["z"] - z0 + q["d"])); colour_at[sl] = q["colour"]
                if q.get("wild_only"): wild[sl] = True
                else: fixed[sl] = q["colour"]
            bl = below[x0:x1, z0:z1] if below.shape[0] >= x1 and below.shape[1] >= z1 else -np.ones(fixed.shape, int)
            old = (sum(1 for q in grp if q["w"] * q["d"] <= small), len(grp)); best = None
            hid = lambda x, z, w, d, part: int(np.bincount(colour_at[x:x + w, z:z + d].ravel()).argmax())
            for t in range(tries):
                try: cand = tile_layer(fixed, wild, bl, rng, hid, catalog, jitter=0.0 if t == 0 else 12.0, allowed=allowed)
                except RuntimeError: continue
                key = (sum(1 for c in cand if c["w"] * c["d"] <= small), len(cand))
                if key < (best[0] if best else old) : best = (key, cand)
            if best is not None:
                for q in grp: parts.remove(q)
                parts += [dict(x=c["x"] + x0, z=c["z"] + z0, w=c["w"], d=c["d"], colour=c["colour"], wild_only=c["wild_only"]) for c in best[1]]; changed = True
    return parts
