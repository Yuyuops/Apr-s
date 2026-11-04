"""V0.5.6 Colosseum : three architecturally different facades on the same 20x26 oval (n=2.6).
 A  "arcades continues"     : arch bricks on straight facets, window frames on 2-stud facets, pilasters elsewhere, two stacked storeys 6 plates tall (every facet cell carries an opening)
 B  "colonnade pilier/linteau" : alternating 1-stud piers and open bays, a lintel course of plates over each storey, three storeys, no arch brick
 C  "galeries concentriques" : outer arcaded wall + ambulatory + inner arcaded wall (staggered), vault plates between storeys : the facade openings reveal the inner arcade
All : attic with window slits + cornice, stepped cavea, arena with hypogeum grid, asymmetric ruin (tiers per angle), natural-stone palette (tan / dark tan / light grey)."""
import math, random
from tiler import tile, BRICKS, PLATES
from fill import column_fill
from colosseum import oval_cells, thin_ring, runs, neighbours8, tile_cornice
TAN, DTAN, LGRAY, DGRAY = 19, 28, 71, 72
def oval_snap(cr, cc, a, b, n, s=2):
    """superellipse sampled on s x s stud blocks : the outline is a regular staircase of s-stud steps, so every facet run is a multiple of s"""
    out = set()
    for r in range(int(cr - b - 3), int(cr + b + 4)):
        for c in range(int(cc - a - 3), int(cc + a + 4)):
            y = (math.floor((r + .5 - cr) / s) + .5) * s; x = (math.floor((c + .5 - cc) / s) + .5) * s
            if (abs(x) / a) ** n + (abs(y) / b) ** n <= 1.0: out.add((r, c))
    return out
def facing(W, O):
    f = {}
    for (r, c) in W:
        vo = any((r + dr, c) not in O for dr in (-1, 1)); ho = any((r, c + dc) not in O for dc in (-1, 1)); f[(r, c)] = "H" if vo and not ho else "V" if ho and not vo else "X"
    return f
def ruin(W, cr, cc, seed, break_deg, ruin_min):
    nz = random.Random(seed + 1); T = {}
    for (r, c) in W:
        ang = math.degrees(math.atan2(r + .5 - cr, c + .5 - cc)); d = abs(((ang - break_deg + 180) % 360) - 180); s = max(0.0, 1 - d / 80.0) ** 0.8 + nz.uniform(-.12, .12); T[(r, c)] = max(ruin_min, min(4, 4 - int(round(s * 2.6))))
    return T
def piece_run(S, run, kind, y, region, colour=TAN, h=6, rest=None):
    """arcade pieces on one straight facet : 6182 arch (4) / 60592 window (2) ; leftovers go to `rest` (plain wall, tiled stud-aware per course later)"""
    i = 0; n = len(run); rot = 0 if kind == "H" else 90; cnt = dict(arch=0, window=0, wall=0)
    while i < n:
        left = n - i; r0, c0 = run[i]
        if left >= 4: S.add("6182", colour, r0, c0, y, rot, region); i += 4; cnt["arch"] += 1
        elif left >= 2: S.add("60592", colour, r0, c0, y, rot, region); i += 2; cnt["window"] += 1
        else: rest.add(run[i]); i += 1; cnt["wall"] += 1
    return cnt
def wall_courses(S, cells, y, region, rng, colour=TAN):
    """two courses of plain brick (1xN, stud-aware best-of-30 tilings, courses staggered by independent draws)"""
    for yy in (y, y + 3):
        for (r, c, nr, nc, part, rot) in tile(cells, {k: v for k, v in BRICKS.items() if k[0] == 1 and k[1] <= 4}, rng, 1.6, 4, S.stud_cells(yy), 40): S.add(part, colour, r, c, yy, rot, region)
def facade_A(S, W, face, T, tier, y, region, info, rng=None):
    rng = rng or random.Random(11); cells = {k for k in W if T[k] > tier}; used = set(); rest = set()
    for kind, along in (("H", (0, 1)), ("V", (1, 0))):
        for run in runs({k for k in cells if face[k] == kind}, along):
            cnt = piece_run(S, run, kind, y, region, rest=rest); used.update(run)
            for k, v in cnt.items(): info[k] = info.get(k, 0) + v
    rest |= cells - used; wall_courses(S, rest, y, region, rng); info["wall_cells"] = info.get("wall_cells", 0) + len(rest)
def facade_B(S, W, face, T, tier, y, region, rng, info):
    cells = {k for k in W if T[k] > tier}; piers = set(); bays = set()
    for kind, along in (("H", (0, 1)), ("V", (1, 0))):
        for run in runs({k for k in cells if face[k] == kind}, along):
            for j, k in enumerate(run): (piers if (j % 2 == 0 or j == len(run) - 1) else bays).add(k)
    piers |= cells - piers - bays
    for (r, c, nr, nc, part, rot) in tile(piers, {(1, 1): "3005", (1, 2): "3004"}, rng, 0.5, 2, S.stud_cells(y), 30): S.add(part, TAN, r, c, y, rot, region)
    info["pier"] = info.get("pier", 0) + len(piers); info["bay"] = info.get("bay", 0) + len(bays)
    for (r, c, nr, nc, part, rot) in tile(cells, {k: v for k, v in PLATES.items() if k[0] == 1}, rng, 2.0, 8, S.stud_cells(y + 3), 12): S.add(part, DTAN, r, c, y + 3, rot, region + "_lintel")
def attic(S, W, face, T, y, rng, info, region="colosseum_attic"):
    cells = {k for k in W if T[k] > 2}; gaps = set()
    for kind, along in (("H", (0, 1)), ("V", (1, 0))):
        for run in runs({k for k in cells if face[k] == kind}, along):
            for j in range(2, len(run) - 2, 3): gaps.add(run[j])
    for (r, c, nr, nc, part, rot) in tile(cells - gaps, {k: v for k, v in BRICKS.items() if k[0] == 1 and k[1] <= 4}, rng, 1.3, 4, S.stud_cells(y), 8): S.add(part, TAN, r, c, y, rot, region)
    for (r, c, nr, nc, part, rot) in tile_cornice(cells, gaps, rng, S.stud_cells(y + 3)): S.add(part, DTAN, r, c, y + 3, rot, "colosseum_cornice")
    info["windows"] = len(gaps)
def build(S, cr, cc, a, b, plaza_extra, n_oval=2.6, style="A", seed=3, break_deg=40.0, ruin_min=2, snap=0):
    rng = random.Random(seed); O = oval_snap(cr, cc, a, b, n_oval, snap) if snap else oval_cells(cr, cc, a, b, n_oval); W0 = thin_ring(O); info = dict(style=style)
    plaza = {(r, c) for (r, c) in oval_cells(cr, cc, a + plaza_extra, b + plaza_extra, 3.0) if 0 <= r < S.R and 0 <= c < S.C}
    corridor = set(); W1 = set(); inner = O - W0
    if style == "C":
        corridor = thin_ring(inner); inner2 = inner - corridor; W1 = thin_ring(inner2); inner = inner2 - W1
    I = inner; walls = W0 | W1; guide = W1 if style == "C" else W0
    column_fill(S, {k: 1 for k in plaza}, lambda r, c, y, kind: TAN if (r, c) in (O - W0) else DTAN, 3, rng, "plaza", 1.0)
    face0 = facing(W0, O); T0 = ruin(W0, cr, cc, seed, break_deg, ruin_min)
    if style == "C": face1 = facing(W1, O - W0 - corridor); T1 = ruin(W1, cr, cc, seed + 7, break_deg, ruin_min)
    if style == "A":
        facade_A(S, W0, face0, T0, 0, 4, "colosseum_facade_t0", info); facade_A(S, W0, face0, T0, 1, 10, "colosseum_facade_t1", info); attic(S, W0, face0, T0, 16, rng, info)
    elif style == "B":
        for t in range(3): facade_B(S, W0, face0, T0, t, 4 + 4 * t, "colosseum_colonnade_t%d" % t, rng, info)
        attic(S, W0, face0, T0, 16, rng, info)
    else:
        for t, (y, vy) in enumerate(((4, 10), (11, 17))):
            facade_A(S, W0, face0, T0, t, y, "colosseum_facade_t%d" % t, info); facade_A(S, W1, face1, T1, t, y, "colosseum_inner_t%d" % t, info)
            for (r, c, nr, nc, part, rot) in tile({k for k in (W0 | corridor | W1) if (T0.get(k, 4) > t if k in W0 else T1.get(k, 4) > t if k in W1 else True)}, PLATES, rng, 1.8, 12, S.stud_cells(vy), 12): S.add(part, DTAN, r, c, vy, rot, "colosseum_vault_t%d" % t)
        attic(S, W0, face0, T0, 18, rng, info)
    # cavea
    def d_in(r, c): return min(math.hypot(r - w[0], c - w[1]) for w in guide)
    heights = {}; rings = [(1.4, 14), (2.5, 12), (3.6, 10), (4.6, 8), (5.5, 6), (6.3, 4), (7.0, 2)]; top_lim = {1: 3, 2: 9, 3: 12, 4: 15}
    for (r, c) in I:
        d = d_in(r, c); h = 0
        for dist, hh in rings:
            if d <= dist: h = hh; break
        near = min(guide, key=lambda w: math.hypot(r - w[0], c - w[1])); Tg = (T1 if style == "C" else T0)[near]; lim = top_lim[Tg] if d <= 3 else 99; h = min(h, max(2, lim)) if h else 0
        if h: heights[(r, c)] = h
    def scol(r, c, y, kind):
        d = d_in(r, c)
        if style != "C" and d <= 1.5 and y < 10: return DGRAY           # dark liner behind the openings : the arcade reads as voids
        return LGRAY if int(d * 1.15) % 2 == 0 and y > 4 else TAN
    column_fill(S, heights, scol, 4, rng, "colosseum_cavea", 1.0, 8, 8)
    lines = {k for k in I if k not in heights and ((k[0] % 4 == 0 and k[1] % 2 == 0) or k[1] % 6 == 0)}
    for (r, c, nr, nc, part, rot) in tile(lines, PLATES, rng, 1.0, 4, S.stud_cells(4)): S.add(part, DGRAY, r, c, 4, rot, "colosseum_hypogeum")
    if style == "C":    # ambulatory floor stays the plaza plate ; nothing to add
        pass
    info.update(wall_cells=len(W0), inner_wall_cells=len(W1), corridor_cells=len(corridor), seat_cells=len(I), plaza_cells=len(plaza)); return info
