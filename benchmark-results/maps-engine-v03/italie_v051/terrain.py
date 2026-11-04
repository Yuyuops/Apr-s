"""V0.5.1 Alpine module : artistic (NOT real-altitude) relief built from real LEGO parts.
Heightfield (bricks) -> nested brick layers tiled per colour -> 45-degree slope bricks bridging every 1-brick step -> rock/snow/grass colouring
-> 1-plate relief skin, scree, boulders, shrubs, conifers and broadleaf trees. Everything deterministic from the seed."""
import random, math
import numpy as np
from scipy import ndimage
from tiler import tile, BRICKS, PLATES
GRASS, DGREEN, DGRAY, LGRAY, WHITE, TAN, DTAN, RBROWN, BLACK, OLIVE = 2, 288, 72, 71, 15, 19, 28, 70, 0, 378
def fbm(shape, sigmas, weights, rng):
    out = np.zeros(shape)
    for s, w in zip(sigmas, weights):
        n = ndimage.gaussian_filter(rng.standard_normal(shape), s, mode="wrap"); n = (n - n.mean()) / (n.std() + 1e-9); out += w * n
    out /= sum(weights); return out
def heightfield(R, C, seed=7):
    rng = np.random.RandomState(seed); rr, cc = np.mgrid[0:R, 0:C].astype(float)
    wr = fbm((R, C), [4, 2], [1, .5], rng) * 2.4; wc = fbm((R, C), [4, 2], [1, .5], rng) * 2.4
    r, c = rr + wr, cc + wc
    peaks = [(R * .46, C * .50, 43, 12.0), (R * .66, C * .24, 33, 8.5), (R * .27, C * .73, 31, 8.5), (R * .75, C * .72, 20, 7.0), (R * .20, C * .26, 19, 6.5), (R * .60, C * .70, 25, 6.5)]
    h = np.zeros((R, C))
    for pr, pc, ph, rad in peaks:                                   # concave 'horn' flanks : steep near the summit, gentle at the foot
        d = np.hypot(r - pr, c - pc); h = np.maximum(h, ph * np.clip(1 - d / (rad * 2.0), 0, 1) ** 2.0)
    links = [(0, 1), (0, 2), (0, 5), (2, 5), (1, 4), (3, 5), (0, 4)]
    for i, j in links:                                              # crest lines between summits
        (r1, c1, h1, _), (r2, c2, h2, _) = peaks[i], peaks[j]; vr, vc = r2 - r1, c2 - c1; L2 = vr * vr + vc * vc
        t = np.clip(((r - r1) * vr + (c - c1) * vc) / L2, 0, 1); dist = np.hypot(r - (r1 + t * vr), c - (c1 + t * vc))
        h = np.maximum(h, (h1 + (h2 - h1) * t) * 0.48 * np.exp(-(dist / 2.1) ** 2 * 0.5) * (0.85 + 0.15 * t))
    n = fbm((R, C), [3.0, 1.5], [1, .7], rng); ridge = 1 - np.abs(np.tanh(n * 1.3)); h += (ridge - 0.55) * 9.0 * np.clip(h / 12, 0, 1)
    h += 1.6 * fbm((R, C), [2.0], [1], rng) * (h > 3)
    dist = np.hypot((rr - R * 0.5) / (R * 0.52), (cc - C * 0.5) / (C * 0.52)) + 0.20 * fbm((R, C), [4.5, 2.2], [1, .6], rng)
    mask = np.clip((1.0 - dist) / 0.22, 0, 1)
    low = 3.2 * np.clip((1.0 - dist) / 0.5, 0, 1) ** 0.8 + 1.2 * fbm((R, C), [2.5], [1], rng)    # lowland / foothills
    h = np.maximum(h, low * (mask > 0)) * np.clip(mask * 1.6, 0, 1)
    edge = np.minimum.reduce([rr, cc, R - 1 - rr, C - 1 - cc]); h *= np.clip(edge / 2.0, 0, 1)
    return np.clip(h, 0, 34), rng
def to_bricks(h, rng):
    K = np.rint(h / 3.0).astype(int); R, C = K.shape
    cliff = (fbm((R, C), [2.2], [1], rng) > 0.75).astype(int) + (fbm((R, C), [1.5], [1], rng) > 1.35).astype(int)   # cells allowed a steeper (cliff) drop
    for _ in range(80):
        lim = np.full((R, C), 99)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = np.full((R, C), 0); rs, cs = slice(max(dr, 0), R + min(dr, 0)), slice(max(dc, 0), C + min(dc, 0))
            rd, cd = slice(max(-dr, 0), R + min(-dr, 0)), slice(max(-dc, 0), C + min(-dc, 0)); sh[rd, cd] = K[rs, cs]
            lim = np.minimum(lim, sh + 1 + cliff)
        nk = np.minimum(K, lim)
        if (nk == K).all(): break
        K = nk
    return K, cliff
def layout_surface(K, rng, ROWS, COLS):
    """category of each cell : snow / rock / grass / sand-free ; patchy via smooth noise"""
    R, C = K.shape; n1 = fbm((R, C), [2.5], [1], rng); n2 = fbm((R, C), [1.3], [1], rng); Ht = K * 3.0
    cat = np.empty((R, C), object)
    for r in range(R):
        for c in range(C):
            h = Ht[r, c] + 1.5 * n1[r, c]
            cat[r, c] = "snow" if h >= 25.0 + 1.5 * n2[r, c] else "rock" if h >= 13.5 + 1.8 * n2[r, c] else "grass"
    return cat
def pick(options, rng):
    return rng.choices([o for o, w in options], [w for o, w in options])[0]
def colour_for(kind, rng, tone, k=0, exposed_face=False):
    """tone : smooth noise at the cell (coherent patches), rng : rare per-cell variation"""
    flip = rng.random() < 0.13
    if kind == "snow": return LGRAY if (exposed_face and rng.random() < 0.45) else WHITE
    if kind == "rock":
        if k % 4 == 3 and rng.random() < .55: return DTAN
        if tone > 1.0 and rng.random() < .75: return RBROWN
        return (DGRAY if tone < 0 else LGRAY) if not flip else (LGRAY if tone < 0 else DGRAY)
    if kind == "olive": return OLIVE
    return (GRASS if tone > 0.25 else DGREEN) if not flip else (DGREEN if tone > 0.25 else GRASS)
def build_mountain(S, r0, c0, R, C, seed=7, ground=3):
    rng = random.Random(seed); h, nrng = heightfield(R, C, seed); K, cliff = to_bricks(h, nrng); cat = layout_surface(K, nrng, R, C)
    tone = fbm((R, C), [1.8], [1], nrng); info = dict(max_K=int(K.max()), max_height_mm=round(float(K.max()) * 9.6, 1), land_cells=int((K > 0).sum()))
    def drop(r, c):
        d = 0
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc; kn = K[rr, cc] if 0 <= rr < R and 0 <= cc < C else 0
            d = max(d, K[r, c] - kn)
        return d
    def lowest_nb(r, c, k):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc; kn = K[rr, cc] if 0 <= rr < R and 0 <= cc < C else 0
            if kn <= k: return True
        return False
    def cell_colour(r, c, k):
        """colour of the brick of cell (r,c) at layer k (k = K-1 is the top brick)"""
        top = k == K[r, c] - 1; exposed = lowest_nb(r, c, k)
        if not top and not exposed: return DGRAY
        kind = cat[r, c]; face = exposed and not top
        if face:
            if drop(r, c) >= 2 and kind == "grass" and K[r, c] >= 3: kind = "rock"
            elif kind == "snow" and (K[r, c] - k) > 1: kind = "rock"
        if kind == "grass" and top and K[r, c] >= 3 and any(cat[min(R - 1, max(0, r + dr)), min(C - 1, max(0, c + dc))] == "rock" for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))): kind = "olive"
        return colour_for(kind, random.Random((r * 7919 + c * 104729 + k * 1299709 + seed) & 0xffffffff), tone[r, c], k, face)
    # fixed per-cell/colour decision (reproducible : python hash of ints is stable)
    slope_parts = {1: "3040b", 2: "3039", 3: "3038", 4: "3037"}
    used_total = 0; slopes = 0
    for k in range(int(K.max())):
        y = ground + 3 * k
        mask = {(r, c) for r in range(R) for c in range(C) if K[r, c] > k}
        taken = set(); slope_cells = set()
        # slope bridging : A has its top brick on layer k, B (neighbour) tops at layer k-1 or is sea (k = 0)
        for d, rot in (((1, 0), 0), ((-1, 0), 180), ((0, 1), 270), ((0, -1), 90)):
            cand = [(r, c) for (r, c) in sorted(mask) if K[r, c] == k + 1 and 0 <= r + d[0] < R and 0 <= c + d[1] < C and K[r + d[0], c + d[1]] == k and rng.random() < 0.92]
            along = (0, 1) if d[0] else (1, 0)
            cand = [(r, c) for (r, c) in cand if (r, c) not in taken and (r + d[0], c + d[1]) not in taken]
            cset = set(cand); done = set()
            for r, c in cand:
                if (r, c) in done: continue
                run = [(r, c)]
                while True:
                    nr_, nc_ = run[-1][0] + along[0], run[-1][1] + along[1]
                    if (nr_, nc_) in cset and (nr_, nc_) not in done and len(run) < 4: run.append((nr_, nc_))
                    else: break
                w = len(run) if rng.random() < .8 else max(1, len(run) - rng.randint(0, 1)); run = run[:w]
                col = cell_colour(r, c, k)
                if d[0]: rr0 = r if d[0] == 1 else r - 1; cc0 = c; nrr, ncc = 2, w
                else: cc0 = c if d[1] == 1 else c - 1; rr0 = r; nrr, ncc = w, 2
                if not S.free(r0 + rr0, c0 + cc0, y, nrr, ncc, 3): continue
                S.add(slope_parts[w], col, r0 + rr0, c0 + cc0, y, rot, "mountain_slope"); slopes += 1
                for cell in run: done.add(cell); taken.add(cell); taken.add((cell[0] + d[0], cell[1] + d[1])); slope_cells.add(cell)
        rest = mask - slope_cells; groups = {}
        for (r, c) in rest: groups.setdefault(cell_colour(r, c, k), set()).add((r, c))
        for col, cells in groups.items():
            for (r, c, nr, nc, part, rot) in tile(cells, BRICKS, rng, 1.3 if col == DGRAY else 1.0, 16 if col == DGRAY else 8):
                S.add(part, col, r0 + r, c0 + c, y, rot, "mountain")
    info["slopes"] = slopes
    return K, cat, info

def decorate(S, K, cat, r0, c0, seed=7, ground=3, trees=True):
    rng = random.Random(seed + 11); R, C = K.shape; info = dict(trees=0, conifers=0, bushes=0, boulders=0, beach_cells=0)
    nb8 = lambda r, c: [(r + i, c + j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)]
    # beach : tan plates around the land (free cells only)
    beach = {(r, c) for r in range(R) for c in range(C) if K[r, c] == 0 and any(0 <= a < R and 0 <= b < C and K[a, b] > 0 for a, b in nb8(r, c)) and S.free(r0 + r, c0 + c, ground, 1, 1, 1)}
    for (r, c, nr, nc, part, rot) in tile(beach, PLATES, rng, 1.0, 4): S.add(part, TAN, r0 + r, c0 + c, ground, rot, "beach")
    info["beach_cells"] = len(beach)
    def exposed_top(r, c):
        y = ground + 3 * K[r, c]; q = S.occ.get((r0 + r, c0 + c, y - 1))
        return q is not None and S.parts[q - 1]["region"] == "mountain" and S.free(r0 + r, c0 + c, y, 1, 1, 1)
    cells = [(r, c) for r in range(1, R - 1) for c in range(1, C - 1) if K[r, c] >= 1 and cat[r, c] in ("grass",) and exposed_top(r, c)]
    rng.shuffle(cells); placed = []
    if trees:
        for (r, c) in cells:
            if K[r, c] > 5 or any(abs(r - a) < 3 and abs(c - b) < 3 for a, b in placed): continue
            y = ground + 3 * K[r, c]; conifer = K[r, c] >= 3 or rng.random() < .45; h2 = 6 if conifer else 3
            for (cr, cc) in ((r, c), (r, c - 1), (r - 1, c), (r - 1, c - 1)):    # try the four 2x2 crowns containing the trunk cell
                if not (0 <= cr and cr + 2 <= R and 0 <= cc and cc + 2 <= C): continue
                if S.free(r0 + cr, c0 + cc, y, 2, 2, 3 + 3 + h2) and all(K[cr + i, cc + j] <= K[r, c] + 1 for i in (0, 1) for j in (0, 1)) and S.free(r0 + r, c0 + c, y, 1, 1, 3):
                    S.add("3062b", RBROWN, r0 + r, c0 + c, y, 0, "tree_trunk")
                    for i in (0, 1):
                        for j in (0, 1):
                            pass
                    # the crown base must sit one brick above the neighbours : it is free by the check above
                    S.add("3941", DGREEN if conifer else GRASS, r0 + cr, c0 + cc, y + 3, 0, "tree_crown")
                    if conifer: S.add("3942c", DGREEN, r0 + cr, c0 + cc, y + 6, 0, "tree_cone")
                    else: S.add("3941", GRASS if rng.random() < .5 else DGREEN, r0 + cr, c0 + cc, y + 6, 0, "tree_crown")
                    placed.append((r, c)); info["trees"] += 1; info["conifers"] += int(conifer); break
    # bushes (round plates) and boulders (30-degree slopes) on free exposed tops
    for (r, c) in cells:
        y = ground + 3 * K[r, c]
        if not S.free(r0 + r, c0 + c, y, 1, 1, 1) or (r, c) in placed: continue
        if rng.random() < .09: S.add("6141", rng.choice([GRASS, DGREEN]), r0 + r, c0 + c, y, 0, "bush"); info["bushes"] += 1
    rock_cells = [(r, c) for r in range(1, R - 1) for c in range(1, C - 1) if K[r, c] >= 2 and cat[r, c] in ("rock", "snow") and exposed_top(r, c)]
    rng.shuffle(rock_cells)
    for (r, c) in rock_cells[:70]:
        y = ground + 3 * K[r, c]
        if S.free(r0 + r, c0 + c, y, 1, 1, 2) and rng.random() < .55:
            S.add("54200", rng.choice([DGRAY, LGRAY, DGRAY]), r0 + r, c0 + c, y, rng.choice([0, 90, 180, 270]), "boulder"); info["boulders"] += 1
    return info
