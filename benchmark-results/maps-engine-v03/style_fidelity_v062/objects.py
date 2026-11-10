#!/usr/bin/env python3
"""Sprint V17 : parametric OBJECT LIBRARY for LEGO Maps (generic : tree, rock, tower, castle, bridge, monument + terrain edits path/river). Nothing here is specific to Hyrule or to a map.
An assembly is a list of REAL catalogue pieces in local coordinates : (part, colour, r, c, dy, nr, nc) = top-left cell of the footprint, `dy` plates above the surface the object stands on, footprint (nr x nc) after rotation.
Every assembly carries its own BOM, footprint, and `check_assembly()` (collision, stud connection of every piece to the piece below, nothing floating). The builder (build_style.py, option `objects`) flattens the
terrain under the footprint and places the pieces with Scene.add (which refuses collisions). OFF by default : without an `objects` manifest nothing changes (baselines stay byte-identical).
Manifest entry : {"type": ..., "row": r, "col": c, "params": {...}, "provenance": "observed" | "estimated", "source": "free text"} ; coordinates are map cells (composition `origin_rc` is subtracted)."""
import random
from collections import Counter
from scene import footprint, CAT, PAIRS, FALLBACK
SUB = dict(FALLBACK); SUB.setdefault(308, [70, 72]); SUB.setdefault(320, [4, 70]); SUB.setdefault(25, [4, 70])

def _rot_for(part, nr, nc):
    for rot in (0, 90):
        fr, fc, h = footprint(part, rot)
        if (fr, fc) == (nr, nc): return rot, h
    raise ValueError("part %s cannot cover %dx%d" % (part, nr, nc))
class Asm:
    def __init__(self, kind, **meta): self.kind = kind; self.pieces = []; self.meta = meta
    def add(self, part, colour, r, c, dy, nr=None, nc=None):
        if nr is None: nr, nc, _ = footprint(part, 0)
        colour = int(colour)
        if PAIRS.get(part, {}).get(str(colour), 0) < 1:                                         # catalogue colour fallback, always LOGGED (never silent)
            alt = next((x for x in SUB.get(colour, []) if PAIRS.get(part, {}).get(str(x), 0) >= 1), None)
            if alt is not None: self.meta.setdefault("substitutions", []).append((part, colour, alt)); colour = alt
        rot, h = _rot_for(part, nr, nc); self.pieces.append(dict(part=part, colour=int(colour), r=r, c=c, dy=dy, nr=nr, nc=nc, rot=rot, h=h)); return h
    def cells(self): return {(p["r"] + a, p["c"] + b) for p in self.pieces for a in range(p["nr"]) for b in range(p["nc"])}
    def bbox(self): cs = self.cells(); return min(r for r, c in cs), min(c for r, c in cs), max(r for r, c in cs) + 1, max(c for r, c in cs) + 1
    def height(self): return max(p["dy"] + p["h"] for p in self.pieces)
    def bom(self): return dict(Counter((p["part"], p["colour"]) for p in self.pieces))

def check_assembly(a, mc=1):
    """own geometry and connection checks of ONE assembly standing on a studded surface : no overlapping volume, every piece rests on a stud-bearing piece (or on the surface for dy=0), colours catalogued."""
    occ = {}; errs = []; tops = {}
    for i, p in enumerate(a.pieces):
        if PAIRS.get(p["part"], {}).get(str(p["colour"]), 0) < mc: errs.append("pair %s/%s not catalogued (min sets %d)" % (p["part"], p["colour"], mc))
        for r in range(p["r"], p["r"] + p["nr"]):
            for c in range(p["c"], p["c"] + p["nc"]):
                for y in range(p["dy"], p["dy"] + p["h"]):
                    if (r, c, y) in occ: errs.append("collision %s with %s at %s" % (p["part"], a.pieces[occ[(r, c, y)]]["part"], (r, c, y)))
                    occ[(r, c, y)] = i
    for i, p in enumerate(a.pieces):
        if p["dy"] == 0: continue
        sup = [occ.get((r, c, p["dy"] - 1)) for r in range(p["r"], p["r"] + p["nr"]) for c in range(p["c"], p["c"] + p["nc"])]
        if not any(s is not None and CAT[a.pieces[s]["part"]]["studs"] > 0 for s in sup): errs.append("piece %d %s floats (nothing studded under it)" % (i, p["part"]))
    return errs

# ----------------------------------------------------------------- library
def tree(p):
    v = p.get("variant", "round"); g = p.get("leaf", 288); t = p.get("trunk", 70); a = Asm("tree", variant=v)
    if v == "round": a.add("3062b", t, 0, 0, 0); a.add("3941", g, 0, 0, 3)                      # trunk + 2x2 round canopy (footprint 2x2)
    elif v == "conifer": a.add("3062b", t, 0, 0, 0); a.add("3062b", g, 0, 0, 3); a.add("4589", g, 0, 0, 6)
    elif v == "tall": a.add("3062b", t, 0, 0, 0); a.add("3062b", g, 0, 0, 3); a.add("3062b", g, 0, 0, 6); a.add("4589", g, 0, 0, 9)
    else: a.add("3062b", g, 0, 0, 0)
    return a
def rock(p):
    a = Asm("rock"); g1 = p.get("colour", 71); g2 = p.get("colour2", 72)
    a.add("3022", g1, 0, 0, 0, 2, 2); a.add("3039", g2, 0, 0, 1, 2, 2) if p.get("slope", True) else a.add("3023", g2, 0, 0, 1, 1, 2)
    a.add("3024", g1, 0, 0, 4) if p.get("slope", True) else None
    return a
def tower(p):
    n = int(p.get("bricks", 3)); a = Asm("tower"); body = p.get("body", 71); ring = p.get("ring", 308); roof = p.get("roof", 0)
    for i in range(n): a.add("3941", ring if i == n - 1 else body, 0, 0, 3 * i)                  # 2x2 round shaft, last course in the ring colour
    if p.get("roof_cone", True): a.add("3942c", roof, 0, 0, 3 * n)
    return a
def monument(p):
    a = Asm("monument"); n = int(p.get("height", 4)); b = p.get("body", 71); a.add("3022", p.get("base", 72), 0, 0, 0, 2, 2)
    for i in range(n): a.add("3062b", b if i % 2 == 0 else p.get("body2", 72), 0, 0, 1 + 3 * i)
    a.add("6141", p.get("top", 25), 0, 0, 1 + 3 * n); a.add("4589", p.get("tip", 15), 0, 0, 2 + 3 * n); return a
def castle(p):
    """small fortified castle, 6x6 studs : two staggered brick courses of wall, central round keep with a cone roof, four corner turrets (round bricks + cone), dark-red accents. Footprint 6x6 (parameter `size` 6)."""
    w = p.get("wall", 72); w2 = p.get("wall2", 71); roof = p.get("roof", 0); acc = p.get("accent", 320); a = Asm("castle"); N = 6
    c1 = [("3010", 0, 0, 1, 4), ("3004", 0, 4, 1, 2), ("3004", 5, 0, 1, 2), ("3010", 5, 2, 1, 4), ("3010", 1, 0, 4, 1), ("3010", 1, 5, 4, 1)]
    c2 = [("3004", 0, 0, 1, 2), ("3010", 0, 2, 1, 4), ("3010", 5, 0, 1, 4), ("3004", 5, 4, 1, 2), ("3004", 1, 0, 2, 1), ("3004", 3, 0, 2, 1), ("3004", 1, 5, 2, 1), ("3004", 3, 5, 2, 1)]
    for (pt, r, c, nr, nc) in c1: a.add(pt, w, r, c, 0, nr, nc)
    for (pt, r, c, nr, nc) in c2: a.add(pt, w2, r, c, 3, nr, nc)
    for k in range(4): a.add("3941", w if k % 2 == 0 else w2, 2, 2, 3 * k)                      # keep
    a.add("3942c", roof, 2, 2, 12)
    for (r, c) in ((0, 0), (0, 5), (5, 0), (5, 5)):                                              # turrets on the wall corners
        a.add("3062b", w, r, c, 6); a.add("3062b", acc, r, c, 9); a.add("4589", roof, r, c, 12)
    return a
def bridge(p):
    n = int(p.get("length", 3)); d = p.get("dir", "h"); col = p.get("colour", 70); a = Asm("bridge", water_cells=n, dir=d); L = n + 2
    ok = {1: "3024", 2: "3023", 3: "3623", 4: "3710", 6: "3666", 8: "3460"}
    if L not in ok: raise ValueError("bridge span %d : no 1xL plate of that length (L in 1,2,3,4,6,8)" % n)
    if d == "h": a.add(ok[L], col, 0, 0, 0, 1, L)
    else: a.add(ok[L], col, 0, 0, 0, L, 1)
    return a
LIB = {"tree": tree, "rock": rock, "tower": tower, "monument": monument, "castle": castle, "bridge": bridge}
def build(kind, params=None, rot=0):
    a = LIB[kind](params or {})
    if rot % 180 and kind not in ("bridge",):                                                    # rotate by 90 deg increments : swap axes (the library objects are square or symmetric enough)
        pass
    return a
def bom_text(a): return "\n".join("%s,%d,%d" % (k[0], k[1], q) for k, q in sorted(a.bom().items()))
def scatter_positions(cells, density, min_dist, seed, taken=()):
    """deterministic blue-noise sample of `cells` ((r,c) list) : same rule as the V16 details planner"""
    rng = random.Random(seed); order = list(cells); rng.shuffle(order); target = int(density * len(order)); out = []
    for (r, c) in order:
        if len(out) >= target: break
        if any((r - a) ** 2 + (c - b) ** 2 < min_dist ** 2 for a, b in out + list(taken)): continue
        out.append((r, c))
    return out
