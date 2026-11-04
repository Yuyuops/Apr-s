"""V0.5.2 Alpine massif : artistic (NOT real-altitude) relief from real LEGO parts.
vs V0.5.1 : four separate summits on a rotated, embayed island ; saddles + two carved valleys ; cliff slack concentrated on the high ground ;
slope bricks only where the step is one brick (probability lower on rock so cliffs stay broken) ; snow only on the summits with LGRAY streaks ;
rock/scree/forest transitions from smooth noise + distance to rock ; no pale Sand Green ; 1-2 plate micro-relief ; sturdier 2x2 conifers (4 stud joints)."""
import random, math
import numpy as np
from scipy import ndimage
from tiler import tile, BRICKS, PLATES
GRASS, DGREEN, DGRAY, LGRAY, WHITE, TAN, DTAN, RBROWN = 2, 288, 72, 71, 15, 19, 28, 70
def fbm(shape, sigmas, weights, rng):
    out = np.zeros(shape)
    for s, w in zip(sigmas, weights):
        n = ndimage.gaussian_filter(rng.standard_normal(shape), s, mode="wrap"); n = (n - n.mean()) / (n.std() + 1e-9); out += w * n
    return out / sum(weights)
def seg_dist(r, c, pts):
    d = np.full(r.shape, 1e9)
    for (r1, c1), (r2, c2) in zip(pts[:-1], pts[1:]):
        vr, vc = r2 - r1, c2 - c1; L2 = vr * vr + vc * vc; t = np.clip(((r - r1) * vr + (c - c1) * vc) / L2, 0, 1); d = np.minimum(d, np.hypot(r - (r1 + t * vr), c - (c1 + t * vc)))
    return d
PEAKS = [(10, 9, 52, 7.0), (19, 25, 47, 7.5), (24, 11, 53, 7.5), (10, 25, 33, 6.0)]          # (row, col, plates, radius) of the four summits
VALLEYS = [[(18, 16), (24, 19), (29, 19), (36, 20)], [(15, 15), (12, 17), (6, 18), (-2, 17)]]      # carved valley axes (south valley, north gap)
def heightfield(R, C, seed):
    rng = np.random.RandomState(seed); rr, cc = np.mgrid[0:R, 0:C].astype(float)
    r = rr + 2.2 * fbm((R, C), [4, 2], [1, .5], rng); c = cc + 2.2 * fbm((R, C), [4, 2], [1, .5], rng)
    h = np.zeros((R, C))
    for pr, pc, ph, rad in PEAKS:
        d = np.hypot(r - pr, c - pc) + 1.2 * fbm((R, C), [2.0], [1], rng)        # irregular, not radial
        h = np.maximum(h, ph * np.clip(1 - d / (rad * 1.9), 0, 1) ** 1.9)
    for i, j, f in ((0, 1, .36), (0, 2, .34), (1, 3, .42), (0, 3, .4)):                  # saddles between summits (the 1-2 / 2-3 pair stays unlinked : deep valley)
        (r1, c1, h1, _), (r2, c2, h2, _) = PEAKS[i], PEAKS[j]; vr, vc = r2 - r1, c2 - c1; t = np.clip(((r - r1) * vr + (c - c1) * vc) / (vr * vr + vc * vc), 0, 1)
        dist = np.hypot(r - (r1 + t * vr), c - (c1 + t * vc)); h = np.maximum(h, (h1 + (h2 - h1) * t) * f * np.exp(-(dist / 2.0) ** 2 * .5))
    n = fbm((R, C), [2.6, 1.3], [1, .8], rng); ridge = 1 - np.abs(np.tanh(n * 1.4)); h += (ridge - .5) * 8.0 * np.clip(h / 14, 0, 1)
    h += 1.4 * fbm((R, C), [1.8], [1], rng) * (h > 3)
    valley = np.zeros((R, C))
    for ax in VALLEYS:
        ax = [(a + 1.6 * math.sin(i * 1.9), b + 1.8 * math.cos(i * 2.3)) for i, (a, b) in enumerate(ax)]; valley = np.maximum(valley, np.exp(-(seg_dist(r, c, ax) / 2.1) ** 2))
    h = h * (1 - 0.72 * valley) + 1.2 * valley
    th = math.radians(28); u = (rr - R / 2) * math.cos(th) + (cc - C / 2) * math.sin(th); v = -(rr - R / 2) * math.sin(th) + (cc - C / 2) * math.cos(th)
    dist = np.hypot(u / (R * 0.55), v / (C * 0.50)) + 0.22 * fbm((R, C), [4.0, 2.0], [1, .6], rng)
    mask = np.clip((1.0 - dist) / 0.20, 0, 1); low = 2.6 * np.clip((1.0 - dist) / 0.5, 0, 1) ** .8 + 1.1 * fbm((R, C), [2.2], [1], rng)
    h = np.maximum(h, low * (mask > 0)) * np.clip(mask * 1.7, 0, 1)
    edge = np.minimum.reduce([rr, cc, R - 1 - rr, C - 1 - cc]); h *= np.clip(edge / 2.0, 0, 1)
    return np.clip(h, 0, 53), valley, np.random.RandomState(seed + 5)
def to_bricks(h, rng):
    K = np.rint(h / 3.0).astype(int); R, C = K.shape
    hi = ndimage.gaussian_filter(h, 1.5) > 14
    cliff = ((fbm((R, C), [2.0], [1], rng) > .15) & hi).astype(int) + ((fbm((R, C), [1.4], [1], rng) > 1.0) & hi).astype(int)       # steeper drops allowed only on high ground
    for _ in range(80):
        lim = np.full((R, C), 99)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = np.zeros((R, C), int); rs, cs = slice(max(dr, 0), R + min(dr, 0)), slice(max(dc, 0), C + min(dc, 0)); rd, cd = slice(max(-dr, 0), R + min(-dr, 0)), slice(max(-dc, 0), C + min(-dc, 0)); sh[rd, cd] = K[rs, cs]
            lim = np.minimum(lim, sh + 1 + cliff)
        nk = np.minimum(K, lim)
        if (nk == K).all(): break
        K = nk
    return K
def build_mountain(S, r0, c0, R, C, seed=7, ground=3):
    rng = random.Random(seed); h, valley, nrng = heightfield(R, C, seed); K = to_bricks(h, nrng)
    for i in range(0, R - 1, 2):        # forest terraces : 2x2 flat pads on the low slopes (room for sturdy 2x2 trees, reads as terraced foothills)
        for j in range(0, C - 1, 2):
            blk = K[i:i + 2, j:j + 2]
            if blk.min() >= 1 and blk.max() <= 5 and h[i:i + 2, j:j + 2].max() < 15.0 and blk.max() - blk.min() <= 1: K[i:i + 2, j:j + 2] = int(round(blk.mean()))
    n1 = fbm((R, C), [2.4], [1], nrng); n2 = fbm((R, C), [1.4], [1], nrng); tone = fbm((R, C), [2.0], [1], nrng); streak = fbm((R, C), [2.5], [1], nrng)
    def nb4(r, c): return [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    def kk(r, c): return int(K[r, c]) if 0 <= r < R and 0 <= c < C else 0
    sea_near = ndimage.distance_transform_edt(K > 0)         # distance (cells) to the sea
    cat = np.empty((R, C), object)
    for r in range(R):
        for c in range(C):
            hh = K[r, c] * 3.0 + 1.5 * n1[r, c]
            cat[r, c] = "snow" if (hh >= 24.0 + 1.2 * n2[r, c] or (hh >= 19.0 and streak[r, c] > 1.1)) else "rock" if hh >= 15.5 + 1.8 * n2[r, c] else "grass"
    rock_d = ndimage.distance_transform_edt(cat != "rock")
    pads = set(); padrng = random.Random(seed + 77); cand = [(i, j) for i in range(1, R - 2) for j in range(1, C - 2)]; padrng.shuffle(cand); padlist = []
    for (i, j) in cand:      # forest pads : flat 2x2 terraces on the grass slopes, one per ~3 tenons, kept free of slope bricks so a solid conifer can stand on 4 studs
        cells4 = [(i + a, j + b) for a in (0, 1) for b in (0, 1)]
        if all(cat[a, b] == "grass" and K[a, b] >= 1 and rock_d[a, b] > 2.5 and h[a, b] < 17 for a, b in cells4) and not any(abs(i - a) < 3 and abs(j - b) < 3 for a, b in padlist):
            m = min(K[a, b] for a, b in cells4)
            if m >= 1 and max(K[a, b] for a, b in cells4) - m <= 1:
                for a, b in cells4: K[a, b] = m
                pads.update(cells4); padlist.append((i, j))
    def drop(r, c): return max(K[r, c] - kk(*n) for n in nb4(r, c))
    def exposed(r, c, k): return any(kk(*n) <= k for n in nb4(r, c))
    def colour(r, c, k):
        r, c, k = int(r), int(c), int(k); rg = random.Random(((r // 2) * 7919 + (c // 2) * 104729 + k * 1299709 + seed) & 0xffffffff); top = k == K[r, c] - 1; exp = exposed(r, c, k); face = exp and not top
        if not top and not exp: return DGRAY
        kind = cat[r, c]
        if face and kind == "snow" and K[r, c] - k > 1: kind = "rock"
        if face and kind == "grass" and drop(r, c) >= 2 and K[r, c] >= 3: kind = "rock"
        if kind == "snow": return LGRAY if rg.random() < (.55 if face else .22 + .25 * (streak[r, c] > .6)) else WHITE
        if kind == "rock":
            if k % 3 == 2 and rg.random() < .5: return DTAN
            if tone[r, c] > 1.1 and rg.random() < .5: return RBROWN
            return (DGRAY if tone[r, c] + .35 * rg.uniform(-1, 1) < 0 else LGRAY)
        if kind == "grass":
            if K[r, c] <= 1 and sea_near[r, c] <= 2.1 and tone[r, c] > -.2 and top: return TAN if rg.random() < .6 else DTAN       # dunes / sand at the shore
            if rock_d[r, c] <= 2.2 and rg.random() < .55: return rg.choice([DTAN, LGRAY, DGRAY, DGREEN])                            # scree skirt
            if rock_d[r, c] <= 3.6 and rg.random() < .35: return DGRAY
            meadow = valley[r, c] > .35 or K[r, c] <= 1
            return (GRASS if rg.random() < (.72 if meadow else .30) else DGREEN)
        return DGREEN
    slope_parts = {1: "3040b", 2: "3039", 3: "3038", 4: "3037"}; slopes = 0
    for k in range(int(K.max())):
        y = ground + 3 * k; mask = {(r, c) for r in range(R) for c in range(C) if K[r, c] > k}; taken = set(); slope_cells = set()
        for d, rot in (((1, 0), 0), ((-1, 0), 180), ((0, 1), 270), ((0, -1), 90)):
            cand = []
            for (r, c) in sorted(mask):
                if K[r, c] != k + 1: continue
                rr_, cc_ = r + d[0], c + d[1]
                if not (0 <= rr_ < R and 0 <= cc_ < C) or K[rr_, cc_] != k or (r, c) in taken or (rr_, cc_) in taken or (r, c) in pads or (rr_, cc_) in pads: continue
                p = .62 if cat[r, c] in ("rock", "snow") else .93
                if rng.random() < p: cand.append((r, c))
            along = (0, 1) if d[0] else (1, 0); cset = set(cand); done = set()
            for r, c in cand:
                if (r, c) in done: continue
                run = [(r, c)]
                while (run[-1][0] + along[0], run[-1][1] + along[1]) in cset and (run[-1][0] + along[0], run[-1][1] + along[1]) not in done and len(run) < 4: run.append((run[-1][0] + along[0], run[-1][1] + along[1]))
                w = len(run) if rng.random() < .65 else max(1, len(run) - rng.randint(1, 2)); run = run[:max(1, w)]; w = len(run)
                if d[0]: a0 = r if d[0] == 1 else r - 1; b0 = c; nr_, nc_ = 2, w
                else: b0 = c if d[1] == 1 else c - 1; a0 = r; nr_, nc_ = w, 2
                if not S.free(r0 + a0, c0 + b0, y, nr_, nc_, 3): continue
                S.add(slope_parts[w], colour(r, c, k), r0 + a0, c0 + b0, y, rot, "mountain_slope"); slopes += 1
                for cell in run: done.add(cell); taken.add(cell); taken.add((cell[0] + d[0], cell[1] + d[1])); slope_cells.add(cell)
        rest = mask - slope_cells; groups = {}
        for (r, c) in rest: groups.setdefault(colour(r, c, k), set()).add((r, c))
        for col, cells in groups.items():
            sup = {(a - r0, b - c0) for (a, b) in S.stud_cells(y)}
            for (r, c, nr, nc, part, rot) in tile(cells, BRICKS, rng, 1.3 if col == DGRAY else 1.0, 16 if col == DGRAY else 8, sup): S.add(part, col, r0 + r, c0 + c, y, rot, "mountain")
    info = dict(max_K=int(K.max()), max_height_mm=round(float(K.max()) * 9.6, 1), land_cells=int((K > 0).sum()), slopes=slopes, summits=[(pr, pc, round(float(K[int(pr), int(pc)]) * 9.6, 1)) for pr, pc, _, _ in PEAKS])
    info['pads'] = len(padlist); return K, cat, info, dict(pad_list=padlist, colour=colour, rock_d=rock_d, valley=valley, tone=tone)
SLIM_P = 0.0
def decorate(S, K, cat, aux, r0, c0, seed=7, ground=3, sturdy=1.0):
    rng = random.Random(seed + 11); R, C = K.shape; colour = aux["colour"]; info = dict(conifers_sturdy=0, trees_slim=0, bushes=0, boulders=0, beach_cells=0, relief_plates=0)
    nb8 = lambda r, c: [(r + i, c + j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)]
    beach = {(r, c) for r in range(R) for c in range(C) if K[r, c] == 0 and any(0 <= a < R and 0 <= b < C and K[a, b] > 0 for a in range(r - 1, r + 2) for b in range(c - 1, c + 2)) and S.free(r0 + r, c0 + c, ground, 1, 1, 1)}
    sup = {(a - r0, b - c0) for (a, b) in S.stud_cells(ground)}
    for (r, c, nr, nc, part, rot) in tile(beach, PLATES, rng, 1.6, 8, sup, 30): S.add(part, TAN if rng.random() < .75 else DTAN, r0 + r, c0 + c, ground, rot, "beach")
    info["beach_cells"] = len(beach)
    def top_ok(r, c):
        y = ground + 3 * K[r, c]; q = S.occ.get((r0 + r, c0 + c, y - 1)); return K[r, c] >= 1 and q is not None and S.parts[q - 1]["region"] == "mountain" and S.free(r0 + r, c0 + c, y, 1, 1, 1)
    # micro-relief : single 2x2 plates (4 stud joints) on flat 2x2 pads
    relief = {}; blocks = [(r, c) for r in range(1, R - 2) for c in range(1, C - 2) if all(top_ok(r + i, c + j) for i in (0, 1) for j in (0, 1)) and len({K[r + i, c + j] for i in (0, 1) for j in (0, 1)}) == 1 and all(K[a, b] <= K[r, c] for a, b in ((r - 1, c), (r + 2, c), (r, c - 1), (r, c + 2)))]
    rng.shuffle(blocks)
    for (r, c) in blocks:
        if (r, c) in relief or any(abs(r - a) < 2 and abs(c - b) < 2 for a, b in relief): continue
        if rng.random() < (.30 if cat[r, c] != "snow" else .12):
            S.add("3022", colour(r, c, K[r, c] - 1), r0 + r, c0 + c, ground + 3 * K[r, c], 0, "relief_plate"); relief[(r, c)] = 1; relief.update({(r + 1, c): 1, (r, c + 1): 1, (r + 1, c + 1): 1})
    info["relief_plates"] = len(relief) // 4
    placed = []
    for (i, j) in aux["pad_list"]:       # solid conifers on the forest pads : 2x2 round brick + 2x2 cone, 4 + 4 stud joints
        y = ground + 3 * K[i, j]
        if all(top_ok(i + a, j + b) for a in (0, 1) for b in (0, 1)) and S.free(r0 + i, c0 + j, y, 2, 2, 9):
            S.add("3941", DGREEN, r0 + i, c0 + j, y, 0, "tree_sturdy_base"); S.add("3942c", DGREEN, r0 + i, c0 + j, y + 3, 0, "tree_sturdy_cone"); placed.append((i, j)); info["conifers_sturdy"] += 1
    cells = [(r, c) for r in range(1, R - 1) for c in range(1, C - 1) if top_ok(r, c) and cat[r, c] == "grass" and aux["rock_d"][r, c] > 2.0]; rng.shuffle(cells)
    for (r, c) in cells:
        if K[r, c] > 7 or any(abs(r - a) < 2 and abs(c - b) < 2 for a, b in placed): continue
        y = ground + 3 * K[r, c]; done = False
        if rng.random() < sturdy:       # sturdy conifer : 2x2 round brick (4 stud joints) + 2x2 cone (4 stud joints), needs a 2x2 area of equal height
            for (cr, cc) in ((r, c), (r, c - 1), (r - 1, c), (r - 1, c - 1)):
                if 0 <= cr and cr + 2 <= R and 0 <= cc and cc + 2 <= C and all(K[cr + i, cc + j] == K[r, c] for i in (0, 1) for j in (0, 1)) and S.free(r0 + cr, c0 + cc, y, 2, 2, 9) and all(top_ok(cr + i, cc + j) for i in (0, 1) for j in (0, 1)):
                    S.add("3941", DGREEN, r0 + cr, c0 + cc, y, 0, "tree_sturdy_base"); S.add("3942c", DGREEN, r0 + cr, c0 + cc, y + 3, 0, "tree_sturdy_cone"); placed.append((r, c)); info["conifers_sturdy"] += 1; done = True; break
        if not done and rng.random() < SLIM_P:   # slim tree (decorative) : 1-stud trunk, 2x2 crown
            for (cr, cc) in ((r, c), (r, c - 1), (r - 1, c), (r - 1, c - 1)):
                if 0 <= cr and cr + 2 <= R and 0 <= cc and cc + 2 <= C and S.free(r0 + cr, c0 + cc, y, 2, 2, 9) and all(K[cr + i, cc + j] <= K[r, c] + 1 for i in (0, 1) for j in (0, 1)) and S.free(r0 + r, c0 + c, y, 1, 1, 3):
                    S.add("3062b", RBROWN, r0 + r, c0 + c, y, 0, "tree_slim_trunk"); S.add("3941", rng.choice([GRASS, DGREEN]), r0 + cr, c0 + cc, y + 3, 0, "tree_slim_crown"); S.add("3941", rng.choice([GRASS, DGREEN]), r0 + cr, c0 + cc, y + 6, 0, "tree_slim_crown")
                    placed.append((r, c)); info["trees_slim"] += 1; break
    for (r, c) in cells:
        y = ground + 3 * K[r, c]
        if (r, c) in placed or not S.free(r0 + r, c0 + c, y, 1, 1, 1) or (r, c) in relief: continue
        if rng.random() < .12 and top_ok(r, c): S.add("6141", rng.choice([GRASS, DGREEN]), r0 + r, c0 + c, y, 0, "bush"); info["bushes"] += 1
    rock = [(r, c) for r in range(1, R - 1) for c in range(1, C - 2) if K[r, c] >= 2 and cat[r, c] == "rock" and top_ok(r, c) and top_ok(r, c + 1) and K[r, c] == K[r, c + 1]]; rng.shuffle(rock); got = []
    for (r, c) in rock:
        y = ground + 3 * K[r, c]
        if len(got) < 24 and rng.random() < .55 and not any(abs(r - a) < 3 and abs(c - b) < 3 for a, b in got) and S.free(r0 + r, c0 + c, y, 1, 2, 2):
            S.add("85984", rng.choice([DGRAY, LGRAY, DGRAY]), r0 + r, c0 + c, y, rng.choice([0, 180]), "boulder"); got.append((r, c)); info["boulders"] += 1
    single = [(r, c) for r in range(1, R - 1) for c in range(1, C - 1) if K[r, c] >= 2 and cat[r, c] == "rock" and top_ok(r, c)]; rng.shuffle(single); n1 = 0
    for (r, c) in single:
        if n1 >= 14: break
        y = ground + 3 * K[r, c]
        if S.free(r0 + r, c0 + c, y, 1, 1, 2) and not any(abs(r - a) < 3 and abs(c - b) < 3 for a, b in got) and rng.random() < .5:
            S.add("54200", rng.choice([DGRAY, LGRAY]), r0 + r, c0 + c, y, rng.choice([0, 90, 180, 270]), "boulder_single"); got.append((r, c)); n1 += 1
    info["boulders_single_stud_decorative"] = n1
    return info
