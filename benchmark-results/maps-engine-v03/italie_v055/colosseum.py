"""V0.5.1 Colosseum module : oval three-tier arcade built with real arch bricks (1x4 / 1x3), attic with window slits, cornice, cavea (stepped seating),
arena with hypogeum grid and a ruined side. Footprint is parametric (independent of any pixel data)."""
import math, random
from tiler import tile, BRICKS, PLATES
from fill import column_fill
TAN, DTAN, LGRAY, DGRAY, RBROWN, WHITE = 19, 28, 71, 72, 70, 15
def oval_cells(cr, cc, a, b, n=3.9):
    out = set()
    for r in range(int(cr - b - 3), int(cr + b + 4)):
        for c in range(int(cc - a - 3), int(cc + a + 4)):
            x, y = c + .5 - cc, r + .5 - cr
            if (abs(x) / a) ** n + (abs(y) / b) ** n <= 1.0: out.add((r, c))
    return out
def neighbours8(r, c): return [(r + i, c + j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)]
def runs(cells, along):
    """maximal runs of consecutive cells along (dr,dc)"""
    cells = set(cells); seen = set(); out = []
    for cell in sorted(cells):
        if cell in seen: continue
        if (cell[0] - along[0], cell[1] - along[1]) in cells: continue
        run = [cell]
        while (run[-1][0] + along[0], run[-1][1] + along[1]) in cells: run.append((run[-1][0] + along[0], run[-1][1] + along[1]))
        seen.update(run); out.append(run)
    return out
def thin_ring(O):
    """1-stud thick, 4-connected boundary ring of the oval (diagonal steps closed by an elbow cell)"""
    n4 = lambda r, c: [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]
    B = {k for k in O if any(n not in O for n in n4(*k))}
    for (r, c) in sorted(B):
        for dr, dc in ((1, 1), (1, -1)):
            q = (r + dr, c + dc)
            if q in B and (r + dr, c) not in B and (r, c + dc) not in B:
                for e in ((r + dr, c), (r, c + dc)):
                    if e in O: B.add(e); break
    return B
def split_arches(L, only4=False):
    """length L -> list of piece lengths using 4 (arch 1x4, 2-stud opening) and 3 (arch 1x3, 1-stud opening) : maximal number of 4s, remainder 1-2 left to plain bricks"""
    best = None
    for a in range(L // 4, -1, -1):
        for b in (range((L - 4 * a) // 3, -1, -1) if not only4 else [0]):
            left = L - 4 * a - 3 * b
            if best is None or (left, -a) < (best[0], -best[1]): best = (left, a, b)
    left, a, b = best; seq = [4] * a + [3] * b
    return seq, left
def build_colosseum(S, cr, cc, a=13, b=11, seed=3, break_deg=40.0, plaza_extra=2.4, n_oval=3.9, gaps=False, ruin_min=2):
    rng = random.Random(seed); O = oval_cells(cr, cc, a, b, n_oval); W = thin_ring(O); I = O - W
    plaza = {(r, c) for (r, c) in oval_cells(cr, cc, a + plaza_extra, b + plaza_extra, 3.0) if 0 <= r < S.R and 0 <= c < S.C}
    arena_d = lambda r, c: min(math.hypot(r - w[0], c - w[1]) for w in W)
    # plaza + arena floor (plates at y = 3)
    ground = {k: 1 for k in plaza}
    def gcol(r, c, y, kind): return TAN if (r, c) in I else DTAN
    column_fill(S, ground, gcol, 3, rng, "plaza", 1.0)
    # ---- ruin profile : tiers kept per wall cell (4 = intact incl. attic)
    def ang(r, c): return math.degrees(math.atan2(r + .5 - cr, c + .5 - cc))
    nz = random.Random(seed + 1); T = {}
    for (r, c) in W:
        d = abs(((ang(r, c) - break_deg + 180) % 360) - 180); s = max(0.0, 1 - d / 80.0) ** 0.8 + nz.uniform(-.12, .12)
        T[(r, c)] = max(ruin_min, min(4, 4 - int(round(s * 2.6))))
    # smooth the ruin so that a tier never hangs over a missing neighbour by more than one tier (ragged but physical)
    for _ in range(4):
        for (r, c) in W:
            m = max(T.get(n, 0) for n in neighbours8(r, c) if n in W); T[(r, c)] = min(T[(r, c)], m + 1) if False else T[(r, c)]
    face = {}
    for (r, c) in W:
        vo = any((r + dr, c) not in O for dr in (-1, 1)); ho = any((r, c + dc) not in O for dc in (-1, 1))
        face[(r, c)] = "H" if vo and not ho else "V" if ho and not vo else "X"
    info = dict(wall_cells=len(W), seat_cells=len(I), arches=0)
    ytier = [4, 10, 13, 16]; ARCH = {0: ('6182', None), 1: ('3659', '4490'), 2: ('3659', '4490')}
    for t in range(4):
        y = ytier[t]; cells = {k for k in W if T[k] > t}
        if t < 3:
            used = set()
            for kind, along, rot in (("H", (0, 1), 0), ("V", (1, 0), 90)):
                sub = {k for k in cells if face[k] == kind}
                for run in runs(sub, along):
                    seq, left = split_arches(len(run), t == 0); i = 0
                    # centre the plain-brick remainder at the run ends
                    off = left // 2 if left else 0; i = off
                    for L in seq:
                        seg = run[i:i + L]; i += L
                        part = ARCH[t][0] if L == 4 else ARCH[t][1]
                        r0, c0 = seg[0]; nr, nc = (1, L) if kind == "H" else (L, 1)
                        S.add(part, TAN, r0, c0, y, rot, "colosseum_arcade_t%d" % t); used.update(seg); info["arches"] += 1
            rest = cells - used
            if gaps and t == 0:      # arcade rhythm on the curved, non-arch stretches : every other plain wall cell left open (bridged by the next tier / cornice)
                ring = [k for k in rest if sum(((k[0] + dr, k[1] + dc) in W) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))) >= 2]
                opens = {k for k in ring if (k[0] + 2 * k[1]) % 4 == 0 and not any(((k[0] + dr, k[1] + dc) in used) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
                rest = rest - opens; info["openings"] = info.get("openings", 0) + len(opens)
            for yy in ((y, y + 3) if t == 0 else (y,)):
                for (r, c, nr, nc, part, rot) in tile(rest, {k: v for k, v in BRICKS.items() if k[0] <= 2 and k[1] <= 4}, rng, 1.2, 8, S.stud_cells(yy)): S.add(part, TAN, r, c, yy, rot, "colosseum_wall_t%d" % t)
        else:   # attic : brick wall with window slits (every third cell empty inside straight runs), bridged by the cornice
            gaps = set()
            for kind, along in (("H", (0, 1)), ("V", (1, 0))):
                sub = {k for k in cells if face[k] == kind}
                for run in runs(sub, along):
                    for j in range(2, len(run) - 2, 3): gaps.add(run[j])
            solid = cells - gaps
            for (r, c, nr, nc, part, rot) in tile(solid, {k: v for k, v in BRICKS.items() if k[0] == 1 and k[1] <= 4}, rng, 1.3, 4, S.stud_cells(y)): S.add(part, TAN, r, c, y, rot, "colosseum_attic")
            info["windows"] = len(gaps)
            # cornice ring : plates 1 plate high, long pieces so that every slit is bridged
            for _ in range(60):
                trial = tile(cells, {k: v for k, v in PLATES.items() if k[0] == 1 and k[1] >= 2}, random.Random(rng.random()), 1.6, 8) if False else None
                break
            cor = tile_cornice(cells, gaps, rng, S.stud_cells(19))
            for (r, c, nr, nc, part, rot) in cor: S.add(part, DTAN, r, c, 19, rot, "colosseum_cornice")
    # ---- cavea : concentric stepped seating rising to the wall, then arena floor
    heights = {}; rings = [(1.4, 14), (2.5, 12), (3.6, 10), (4.6, 8), (5.5, 6), (6.3, 4), (7.0, 2)]
    for (r, c) in I:
        d = arena_d(r, c); h = 0
        for dist, hh in rings:
            if d <= dist: h = hh; break
        # follow the ruin : seats are cut where the outer wall is low
        near = min(W, key=lambda w: math.hypot(r - w[0], c - w[1])); lim = {1: 3, 2: 9, 3: 12, 4: 15}[T[near]] if d <= 3 else 99
        h = min(h, max(2, lim)) if h else 0
        if h: heights[(r, c)] = h
    def scol(r, c, y, kind):
        d = arena_d(r, c); return LGRAY if int(d * 1.15) % 2 == 0 and y > 4 else TAN
    column_fill(S, heights, scol, 4, rng, "colosseum_cavea", 1.0, 8, 8)
    # arena : hypogeum grid of low walls
    arena = [(r, c) for (r, c) in I if (r, c) not in heights]; ar = set(arena)
    lines = {k for k in ar if (k[0] % 4 == 0 and k[1] % 2 == 0) or k[1] % 6 == 0}
    for (r, c, nr, nc, part, rot) in tile(lines, PLATES, rng, 1.0, 4, S.stud_cells(4)): S.add(part, DGRAY, r, c, 4, rot, "colosseum_hypogeum")
    info["plaza_cells"] = len(plaza); return info
def tile_cornice(cells, gaps, rng, sup=None):
    from tiler import PLATES as P
    table = {k: v for k, v in P.items() if k[0] == 1 and k[1] >= 2}
    for attempt in range(400):
        r = random.Random(rng.random()); out = tile_try(cells, table, r, sup)
        if out and all(not (set((rr + i, cc + j) for i in range(nr) for j in range(nc)) <= gaps) for (rr, cc, nr, nc, part, rot) in out): return out
    raise ValueError("cornice tiling failed")
def tile_try(cells, table, r, sup=None):
    allowed = dict(table); allowed[(1, 1)] = "3024"
    return tile(cells, allowed, r, 2.0, 8, sup)
