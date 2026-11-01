"""LEGO V6: automatic ear generator (contour -> real LEGO parts).

Input : a silhouette raster (5 LDU) in a panel frame (u, v up), from contour.py, and optionally a head grid + frame
        for the fixation (Paco).
Output: an LDraw module (outer face, inner face, core, tiles) and, with a head, the head rebuilt around it with the
        two turned-plate fixations; JSON report.
Nothing in this file is specific to a model: no list of part positions. Steps:
  1. contour analysis (contour.analyse): slopes and arcs of the boundary;
  2. catalogue of real shaped plates (wings, half disc, quarter rounds, cut corners), each with its slanted/curved edge;
  3. candidates: every catalogue part x rotation x stud position whose slanted/curved edge lies on the target boundary
     (distance transform), scored by the gain over plain stud cells (agreement - 2 x excess), with the assembly
     constraint "one full cell on a core joint row" (the sandwich core holds the faces every other row);
  4. selection: greedy by gain without shared cells, run for several settings; the layout with the best outline IoU
     against the target is kept (all settings are reported);
  5. interior: largest rectangles first, each covering a joint row;
  6. V5.1 rules: tiles on every stud (quarter-round tiles where a stud cell corner is outside the part), mirrored inner
     face, core courses, cap tiles; with a head: search of two turned plates whose studs fall on the head grid (3-4-5
     rotation), root block, carving and rebuild of the head, seats.
usage: autogen.py <target_name> <outdir> [--head]
"""
import json, os, subprocess, sys
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.expanduser("~/bench/tools")); sys.path.insert(0, os.path.expanduser("~/bench/proto"))
sys.path.insert(0, os.path.expanduser("~/bench/proto/ear10")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conn, partlib as PL
import brickify_plus as BP
import design_v51 as D            # geometric helpers of V5.1 (outer_piece, mirror_piece, footprint, wall pieces)
import contour as CT

BLACK = 0
V0 = D.V0                          # rows k: v 12+20k .. 32+20k; core side studs on even rows (v = 22 + 40 n)
D.MIRROR.update({"43722": "43723", "43723": "43722", "78443": "78444", "78444": "78443", "54383": "54384", "54384": "54383",
                 "50304": "50305", "50305": "50304", "47397": "47398", "47398": "47397"})
SHAPED = ["24299", "24307", "43722", "43723", "41769", "41770", "78443", "78444", "54383", "54384", "50304", "50305",
          "22888", "30565", "30357", "2450", "6003"]
TILE_RECT = {(1, 1): "3070b", (2, 1): "3069b", (3, 1): "63864", (4, 1): "2431", (6, 1): "6636", (2, 2): "3068b",
             (3, 2): "26603", (4, 2): "87079", (6, 2): "69729", (4, 4): "1751"}
TILE_1xN = {1: "3070b", 2: "3069b", 3: "63864", 4: "2431", 6: "6636"}

# ---------------------------------------------------------------- footprints at 4 LDU (5 pixels per stud)
_FPC = {}
def fp4(num, M, o):
    """real solid of a placed part projected on the panel (4 LDU pixels); the 5 LDU solid samples are closed so the
    footprint has no aliasing holes"""
    key = (num, tuple(np.round(M, 3).ravel()), tuple(np.round(o, 2)))
    if key in _FPC: return _FPC[key]
    F = D.footprint(num, M, o, res=4)
    a = np.array(sorted(F)); lo = a.min(0) - 2
    img = np.zeros(tuple(a.max(0) - lo + 3), bool); img[tuple((a - lo).T)] = True
    img = ndimage.binary_closing(img, structure=np.ones((3, 3)), iterations=1); img = ndimage.binary_fill_holes(img)
    out = {(int(x + lo[0]), int(y + lo[1])) for x, y in np.argwhere(img)}
    _FPC[key] = out; return out

# ---------------------------------------------------------------- catalogue
def catalogue():
    cat = []
    for num in SHAPED:
        if not BP.available(num, BLACK): continue
        for r in range(4):
            M, o = D.outer_piece(num, r, 0, 0, "P")
            F = fp4(num, M, o)
            Fa = np.array(sorted(F))
            if any(np.array_equal(Fa, c["F"]) for c in cat if c["num"] == num): continue      # symmetric turns
            Fs = set(F); lo = Fa.min(0); hi = Fa.max(0)
            Bd = [p for p in F if any((p[0] + dx, p[1] + dy) not in Fs for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
            edge = np.array([p for p in Bd if lo[0] < p[0] < hi[0] and lo[1] < p[1] < hi[1]] or
                            [p for p in Bd if not (p[0] in (lo[0], hi[0]) or p[1] in (lo[1], hi[1]))] or [[0, 0]])
            cells = {}
            for (a, b) in F: cells[(a // 4, b // 4)] = cells.get((a // 4, b // 4), 0) + 1
            full = [c for c, n in cells.items() if n >= 16]
            # vertical position of a cell relative to the row grid: rows are v = V0 + 20 k -> pixel b // 4 is not k
            cat.append(dict(num=num, r=r, F=Fa, edge=edge, M=M, o=o))
    return cat

def cell_of_pixel(a, b):
    """stud cell (i, k) of an absolute 5-LDU pixel (a, b)"""
    return (a * 4) // 20, (b * 4 - V0) // 20

# ---------------------------------------------------------------- layout search
def layout(T, ia0, ib0, cat, gain_min, tol, fill_thr, plates_ok=True):
    """T: target raster (pixels a = ia0.., b = ib0..). Returns list of (num, r, i0, k0, role)."""
    NA, NB = T.shape
    Tset = {(ia0 + a, ib0 + b) for a, b in np.argwhere(T)}
    Bt = T & ~ndimage.binary_erosion(T); dist = ndimage.distance_transform_edt(~Bt)
    # cell coverage
    cov = {}
    for (a, b) in Tset:
        c = cell_of_pixel(a, b); cov[c] = cov.get(c, 0) + 1
    def cell_pixels(i, k):
        a0 = 5 * i; b0 = (V0 + 20 * k) // 4
        return {(a0 + x, b0 + y) for x in range(5) for y in range(5)}
    plain_cells = {c for c, n in cov.items() if n >= 13}
    cands = []
    imin = min(c[0] for c in cov) - 2; imax = max(c[0] for c in cov) + 2
    kmin = min(c[1] for c in cov) - 2; kmax = max(c[1] for c in cov) + 2
    for it in cat:
        for i0 in range(imin, imax + 1):
            for k0 in range(kmin, kmax + 1):
                da = 5 * i0; db = 5 * k0
                F = it["F"] + [da, db]
                e = it["edge"] + [da, db]
                ea = e[:, 0] - ia0; eb = e[:, 1] - ib0
                if (ea < 0).any() or (eb < 0).any() or (ea >= NA).any() or (eb >= NB).any(): continue
                de = dist[ea, eb]
                if de.mean() > tol or (de <= tol + 1).mean() < 0.7: continue          # slanted/curved edge on the contour
                Fs = {tuple(p) for p in F}
                agree = len(Fs & Tset); extra = len(Fs) - agree
                cells = {}
                for p in Fs: c = cell_of_pixel(*p); cells[c] = cells.get(c, 0) + 1
                P = set().union(*[cell_pixels(*c) for c in cells if c in plain_cells]) if any(c in plain_cells for c in cells) else set()
                plain = len(P & Tset) - 2 * len(P - Tset)
                gain = (agree - 2 * extra) - plain
                full_even = [c for c, n in cells.items() if n >= 25 and c[1] % 2 == 0]
                # the validator treats right-angle parts as their bounding box: the whole box is claimed
                c_lo = cell_of_pixel(*F.min(0)); c_hi = cell_of_pixel(*F.max(0))
                box = {(x, y) for x in range(c_lo[0], c_hi[0] + 1) for y in range(c_lo[1], c_hi[1] + 1)}
                # target area left empty inside the claimed box (no other part may go there): counted against the part
                boxpix = set().union(*[cell_pixels(*c) for c in box])
                hole = len((boxpix & Tset) - Fs)
                gain -= 2 * hole
                if gain >= gain_min and full_even:
                    cands.append((gain, it["num"], it["r"], i0, k0, frozenset(box), Fs))
    cands.sort(key=lambda c: -c[0])
    claimed = set(); chosen = []; usedpix = set()
    for gain, num, r, i0, k0, cells, Fs in cands:
        if cells & claimed: continue
        claimed |= cells; usedpix |= Fs; chosen.append((num, r, int(i0), int(k0), f"forme {num} (gain {gain})"))
    # interior: largest rectangles, each covering an even (joint) row
    free = {c for c, n in cov.items() if n >= fill_thr * 25} - claimed
    sizes = []
    for (L, W), num in BP.PLATES.items():
        if BP.available(num, BLACK):
            sizes.append((L, W, num, 0))
            if L != W: sizes.append((W, L, num, 1))
    sizes.sort(key=lambda s: -s[0] * s[1])
    free0 = set(free); best_pack = None
    orders = [lambda c: (c[1], c[0]), lambda c: (-c[1], c[0]), lambda c: (c[1], -c[0]), lambda c: (-c[1], -c[0])]
    for key in orders:                      # 4 scan orders: keep the packing that leaves the fewest empty cells
        free = set(free0); rects_ = []
        while True:
            best = None
            for (w, h, num, rr) in sizes:
                for (i, k) in sorted(free, key=key):
                    blk = {(i + x, k + y) for x in range(w) for y in range(h)}
                    if not blk <= free: continue
                    if h == 1 and k % 2: continue
                    best = (w, h, num, rr, i, k, blk); break
                if best: break
            if not best: break
            w, h, num, rr, i, k, blk = best; free -= blk
            rects_.append((num, 0 if w >= h else 1, int(i), int(k), f"plaque {w}x{h}"))
        sc = (len(free), len(rects_))
        if best_pack is None or sc < best_pack[0]: best_pack = (sc, rects_, set(free))
    _, rects, free = best_pack
    dropped = len(free)
    return chosen, rects, dropped

def outline_iou(pieces, Tref_set, exclude=None):
    fp = set()
    for num, r, i0, k0, role in pieces:
        M, o = D.outer_piece(num, r, i0, k0, "P"); fp |= fp4(num, M, o)
    if exclude is not None: fp = {p for p in fp if p not in exclude}; Tref_set = {p for p in Tref_set if p not in exclude}
    return len(fp & Tref_set) / max(len(fp | Tref_set), 1), fp

# ---------------------------------------------------------------- tiles (rules)
def tiles_for(num, r, i0, k0, role):
    w_h = None
    for (L, W), n in BP.PLATES.items():
        if n == num: w_h = (L, W) if r == 0 else (W, L)
    if w_h and (w_h in TILE_RECT or (w_h[1], w_h[0]) in TILE_RECT):
        if w_h in TILE_RECT: return [(TILE_RECT[w_h], 0, i0, k0, "tuile " + role)]
        return [(TILE_RECT[(w_h[1], w_h[0])], 1, i0, k0, "tuile " + role)]
    M, o = D.outer_piece(num, r, i0, k0, "P"); F = fp4(num, M, o)
    st = D.studs_dir(num, M, o, -1)
    cells = sorted({(int(round(p[0] - 10)) // 20, int(round(-p[1] - 10 - V0)) // 20) for p in st})
    out = []; plain = []
    for (i, k) in cells:
        a0 = 5 * i; b0 = (V0 + 20 * k) // 4
        corners = {(0, 0): (a0, b0), (1, 0): (a0 + 4, b0), (0, 1): (a0, b0 + 4), (1, 1): (a0 + 4, b0 + 4)}
        outc = [c for c, p in corners.items() if p not in F]
        if len(outc) == 1:
            rr = {(0, 0): 1, (0, 1): 2, (1, 0): 0, (1, 1): 3}[outc[0]]
            out.append(("25269", rr, i, k, "tuile quart de rond sur " + role))
        else: plain.append((i, k))
    def runs(cells_, horiz):
        s = set(cells_); res = []
        key = (lambda c: (c[1], c[0])) if horiz else (lambda c: (c[0], c[1]))
        for c in sorted(s, key=key):
            if c not in s: continue
            n = 1
            while (c[0] + n, c[1]) in s if horiz else (c[0], c[1] + n) in s: n += 1
            while n:
                m = max(x for x in TILE_1xN if x <= n)
                res.append((TILE_1xN[m], 0 if horiz else 1, c[0], c[1], "tuile sur " + role))
                for j in range(m): s.discard((c[0] + j, c[1]) if horiz else (c[0], c[1] + j))
                c = (c[0] + m, c[1]) if horiz else (c[0], c[1] + m); n -= m
        return res
    a, b = runs(plain, True), runs(plain, False)
    return out + (a if len(a) <= len(b) else b)

# ---------------------------------------------------------------- fixation search (head grid)
def plate_seats(occ, E, R, O, xm0, zm0, w, l, vp, forbid=None, above=36.5):
    coin = []; expo = 0; bad = False
    for a in range(w):
        for b in range(l):
            xm = xm0 + 10 + 20 * a; zm = zm0 + 10 + 20 * b
            def cw(v_):
                p = O + R @ np.array([xm, -v_, zm]); return int(np.floor(p[0] / 20)), int(np.floor(-p[1] / 8)), int(np.floor(p[2] / 20))
            x, y, z = cw(vp - 4); xs, ys, zs = cw(vp - 12)
            NX, NY, NZ = occ.shape
            if not (0 <= x < NX and 0 <= z < NZ and 0 <= ys - 1 < NY): bad = True; continue
            if E[x, y, z] or E[xs, ys, zs]: bad = True
            if not occ[x, y + 1:, z].any(): expo += 1
            w_ = O + R @ np.array([xm, 0, zm])
            if (abs((w_[0] - 10) / 20 - round((w_[0] - 10) / 20)) < .01 and abs((w_[2] - 10) / 20 - round((w_[2] - 10) / 20)) < .01
                    and occ[xs, ys, zs] and occ[xs, ys - 1, zs] and not (forbid and forbid(xm, zm))):
                coin.append((xm, zm))
    # the plate and the root block above it (up to v + 40) are carved with a 4.5 LDU margin: no eye or mouth cell inside
    xs_ = np.arange(xm0 + 2.5, xm0 + 20 * w, 5.0); zs_ = np.arange(zm0 + 2.5, zm0 + 20 * l, 5.0); vs_ = np.arange(vp - 12.5, vp + above, 4.0)
    g = np.stack(np.meshgrid(xs_, -vs_, zs_, indexing="ij"), -1).reshape(-1, 3) @ R.T + O
    ix = np.floor(g[:, 0] / 20).astype(int); iy = np.floor(-g[:, 1] / 8).astype(int); iz = np.floor(g[:, 2] / 20).astype(int)
    NX, NY, NZ = occ.shape; ok = (ix >= 0) & (ix < NX) & (iy >= 0) & (iy < NY) & (iz >= 0) & (iz < NZ)
    if E[ix[ok], iy[ok], iz[ok]].any(): bad = True
    return coin, expo, bad

def find_fixation(occ, E, R, O, lobe_cells):
    """two turned plates: primary at v 40..48 (under a root block), secondary at v 80..88 resting on the block plate,
    each with its own seats in the head. Chosen by: most supported coincident studs, no exposure, near the lobe."""
    sizes = [(6, 4, "3032"), (4, 4, "3031"), (8, 4, "3035"), (6, 2, "3795"), (4, 2, "3020"), (8, 2, "3034")]
    best = None
    imax_lobe = max(i for i, k in lobe_cells)
    for (w, l, num) in sizes:
        for xm0 in range(0, 341, 20):
            for zm0 in range(-20 * l, 1, 20):
                if not (zm0 <= -20 and zm0 + 20 * l >= 0): continue
                if xm0 > 20 * (imax_lobe + 3): continue              # must reach the lobe through the root
                coin, expo, bad = plate_seats(occ, E, R, O, xm0, zm0, w, l, 48)
                if bad or expo or len(coin) < 2: continue
                sc = (len(coin), -xm0)
                if best is None or sc > best[0]: best = (sc, dict(num=num, w=w, l=l, xm0=xm0, zm0=zm0, vp=48, coin=coin))
    if best is None: return None, None
    P1 = best[1]
    inP1 = lambda xm, zm: P1["xm0"] <= xm < P1["xm0"] + 20 * P1["w"] and P1["zm0"] <= zm < P1["zm0"] + 20 * P1["l"]
    # seats of the secondary plate: outside the root block and away from the core row (their skull cells must survive
    # the carving of the block and of the core root)
    near_block = lambda xm, zm: ((P1["xm0"] - 20 <= xm < P1["xm0"] + 20 * P1["w"] + 20 and P1["zm0"] - 20 <= zm < P1["zm0"] + 20 * P1["l"] + 20)
                                 or abs(zm + 10) < 30)
    best2 = None
    # tier 1: hidden plate, seats >= 30 LDU from the core row; tier 2 (fallback): seats >= 20 LDU, up to 6 visible cells
    for tier, marg, max_expo in ((1, 30, 1), (2, 20, 6)):
        nb = lambda xm, zm, m=marg: ((P1["xm0"] - 20 <= xm < P1["xm0"] + 20 * P1["w"] + 20 and P1["zm0"] - 20 <= zm < P1["zm0"] + 20 * P1["l"] + 20)
                                     or abs(zm + 10) < m)
        for vp2 in (88, 128):
            for (w, l, num) in sizes:
                for xm0 in range(P1["xm0"] - 120, P1["xm0"] + 20 * P1["w"] + 61, 20):
                    for zm0 in range(-20 * l, 1, 20):
                        if not (zm0 <= -20 and zm0 + 20 * l >= 0): continue
                        over = sum(1 for a in range(w) for b in range(l) if inP1(xm0 + 10 + 20 * a, zm0 + 10 + 20 * b))
                        if vp2 == 88 and over < 2: continue                       # rests on the block plate (connection)
                        coin, expo, bad = plate_seats(occ, E, R, O, xm0, zm0, w, l, vp2, forbid=nb, above=4.5)
                        if bad or expo > max_expo or len(coin) < 2: continue
                        sc = (len(coin), -expo, -vp2, -w * l)
                        if best2 is None or sc > best2[0]: best2 = (sc, dict(num=num, w=w, l=l, xm0=xm0, zm0=zm0, vp=vp2, coin=coin, tier=tier, exposed_cells=expo))
        if best2: break
    return P1, (best2[1] if best2 else None)

# ---------------------------------------------------------------- core courses (rule of V5.1, height taken from the outline)
def wall_courses(cells_ok, vstart, vtop, must=frozenset()):
    """courses from v = 8: [SNOT bricks 24][plate 8][plate 8] ... ; cells_ok(i, v0, v1) says if a wall cell may exist"""
    parts = []; v = vstart; n = 0
    while v < vtop:
        for kind, h in (("snot", 24), ("plate", 8), ("plate", 8)):
            if v + h > vtop: break
            row = [i for i in range(-20, 30) if cells_ok(i, v, v + h)]
            runs = []
            for i in row:
                if runs and runs[-1][1] == i - 1: runs[-1][1] = i
                else: runs.append([i, i])
            for a, b in runs:
                L = b - a + 1; i = a
                if kind == "snot":
                    seq = [2] * (L // 2) + ([1] if L % 2 else [])
                    if n % 2 and L >= 3: seq = [1] + [2] * ((L - 1) // 2) + ([1] if (L - 1) % 2 else [])
                    for k_, w in enumerate(seq):
                        # hollow core: inside long runs, every other 1x2 brick is left out (the plate courses bridge it);
                        # the run ends stay closed (rim) and every brick under a panel joint row is kept by the checks
                        if (D.SPARSE and 0 < k_ < len(seq) - 1 and k_ % 2 == 1 and w == 2 and not (D.BLOCK_X[0] - 40 <= 20 * i)
                                and not any((i + dx, (v + 4 - V0) // 20) in must for dx in (0, 1))): i += w; continue
                        parts.append(("52107" if w == 2 else "47905", i, w, v, h)); i += w
                else:
                    off = (n + (1 if v % 16 else 0)) % 3
                    seq = []; rem = L
                    first = min(rem, [2, 3, 1][off]); seq.append(first); rem -= first
                    while rem > 0:
                        w = 8 if rem >= 8 else (6 if rem >= 6 else (4 if rem >= 4 else rem)); seq.append(w); rem -= w
                    for w in seq:
                        parts.append(({1: "3024", 2: "3023", 3: "3623", 4: "3710", 5: "3710", 6: "3666", 8: "3460"}[w] if w != 5 else "3710", i, w if w != 5 else 4, v, h)); i += (w if w != 5 else 4)
                        if w == 5: parts.append(("3024", i, 1, v, h)); i += 1
            v += h
        n += 1
    return parts


# ---------------------------------------------------------------- build
def build(target, outdir, use_head):
    os.makedirs(outdir, exist_ok=True)
    tdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "targets")
    S = np.load(os.path.join(tdir, f"{target}_silhouette.npy")); meta = json.load(open(os.path.join(tdir, f"{target}_contour.json")))
    ia0, ib0 = int(round(meta["u0"] / 4)), int(round(meta["v0"] / 4))
    feats, summ, _ = CT.analyse(S, meta["u0"], meta["v0"])
    Tset = {(ia0 + a, ib0 + b) for a, b in np.argwhere(S)}
    head = None
    if use_head:
        d0 = np.load(D.HEAD_NPZ); G0 = d0["grid"]; F0 = d0["fine"]; K0 = int(d0["k"]); NX, NY, NZ = G0.shape
        occ0 = (G0 >= 0) & (F0.reshape(NX, K0, NY, K0, NZ, K0).mean(axis=(1, 3, 5)) >= 0.5)
        E = (G0 == 15) | (G0 == 4)                                  # eye and mouth cells: never touched
        head = (occ0, E)
        E2 = ndimage.binary_dilation(E, iterations=2)
        # pixels of the panel slab inside the skull: the panel may enter the skull there (root), within 2 cells of the ear
        inside = set()
        for (a, b) in {(a, b) for a in range(ia0 - 12, ia0 + S.shape[0] + 12) for b in range(ib0 - 12, ib0 + S.shape[1] + 12)}:
            ok = True
            for zm in (-34, -10, 14):
                w = D.O + D.R_MOD @ np.array([a * 4 + 2.0, -(b * 4 + 2.0), zm]); x, y, z = int(np.floor(w[0] / 20)), int(np.floor(-w[1] / 8)), int(np.floor(w[2] / 20))
                if not (0 <= x < NX and 0 <= y < NY and 0 <= z < NZ and occ0[x, y, z]) or E2[x, y, z]: ok = False; break
            if ok: inside.add((a, b))
        E1 = ndimage.binary_dilation(E, iterations=1)
        def forbidden(a, b):
            for zm in (-34, -22, -10, 2, 14):
                for du in (0.5, 3.5):
                    for dv in (0.5, 3.5):
                        w = D.O + D.R_MOD @ np.array([a * 4 + du, -(b * 4 + dv), zm]); x, y, z = int(np.floor(w[0] / 20)), int(np.floor(-w[1] / 8)), int(np.floor(w[2] / 20))
                        if 0 <= x < NX and 0 <= y < NY and 0 <= z < NZ and E1[x, y, z]: return True
            return False
        forb = {p for p in Tset if forbidden(*p)}
        Tset_gen = Tset - forb
        P1_, P2_ = find_fixation(occ0, E, D.R_MOD, D.O, {cell_of_pixel(a, b) for (a, b) in Tset})
        fix_early = dict(primary=P1_, secondary=P2_)
        def in_fix(a, b):
            u, v = a * 4 + 2, b * 4 + 2
            for P, v0_, v1_, zlo, zhi in ((P1_, 36, 84, None, None), (P2_, (P2_ or {}).get("vp", 88) - 32, (P2_ or {}).get("vp", 88) + 4, None, None)):
                if not P: continue
                if not (P["xm0"] - 4 <= u < P["xm0"] + 20 * P["w"] + 4 and v0_ <= v < v1_): continue
                z0, z1 = P["zm0"], P["zm0"] + 20 * P["l"]
                if z0 < -20 or z1 > 0: return True          # the plate reaches under a face of the panel
            return False
        forb |= {p for p in Tset if in_fix(*p)}
        forb |= {p for p in Tset if p[1] * 4 < 52}            # the core starts on the turned plate (v 48): no face below
        Tset_gen = Tset - forb
        Tm = np.zeros((S.shape[0] + 24, S.shape[1] + 24), bool)
        for (a, b) in Tset_gen: Tm[a - ia0 + 12, b - ib0 + 12] = True
        near = ndimage.binary_dilation(Tm, iterations=10)
        inside = {p for p in inside if not in_fix(*p) and p[1] * 4 >= 52}
        globals()["LAST_EXCLUDED"] = set(inside) | set(forb)       # (read by V6.1 only; no effect on V6)
        Text = set(Tset_gen) | {(a, b) for (a, b) in inside if 0 <= a - ia0 + 12 < Tm.shape[0] and 0 <= b - ib0 + 12 < Tm.shape[1] and near[a - ia0 + 12, b - ib0 + 12]}
        ia0e, ib0e = ia0 - 12, ib0 - 12
        Te = np.zeros_like(Tm)
        for (a, b) in Text: Te[a - ia0e, b - ib0e] = True
    else:
        inside = set(); Te = S; ia0e, ib0e = ia0, ib0
        globals()["LAST_EXCLUDED"] = set()
    cat = catalogue()
    runs = []
    for gmin in (4, 8, 16):
        for tol in (1.5, 2.5):
            for fthr in (0.5, 0.6):
                shaped, rects, dropped = layout(Te, ia0e, ib0e, cat, gmin, tol, fthr)
                iou, _ = outline_iou(shaped + rects, Tset, exclude=inside)
                runs.append(dict(gain_min=gmin, tol_px=tol, fill_thr=fthr, shaped=len(shaped), rects=len(rects), dropped_cells=dropped, iou=round(iou, 4),
                                 _layout=(shaped, rects)))
    best = max(runs, key=lambda r: (r["iou"], -r["shaped"] - r["rects"]))
    shaped, rects = best["_layout"]
    OUTER = [(n, r, i, k, "S%d %s" % (j + 1, role)) for j, (n, r, i, k, role) in enumerate(shaped)] + \
            [(n, r, i, k, "P%d %s" % (j + 1, role)) for j, (n, r, i, k, role) in enumerate(rects)]
    mod = []
    for num, r, i0, k0, role in OUTER:
        M, o = D.outer_piece(num, r, i0, k0, "P"); mod.append((BLACK, num, M, o, "outer", role))
        for t in tiles_for(num, r, i0, k0, role.split()[0]):
            M2, o2 = D.outer_piece(t[0], t[1], t[2], t[3], "T"); mod.append((BLACK, t[0], M2, o2, "outer_t", t[4]))
    for c, num, M, o, g, role in list(mod):
        n2, M2, o2 = D.mirror_piece(num, M, o, 0.0 if g == "outer" else 8.0)
        mod.append((BLACK, n2, M2, o2, "inner" if g == "outer" else "inner_t", "face interieure : " + role))
    fp = set().union(*[fp4(num, M, o) for c, num, M, o, g, r in mod if g == "outer"])
    # close the joints between neighbouring plates (the solid samples stop 1 LDU short of each face)
    fa = np.array(sorted(fp)); flo = fa.min(0) - 2; img = np.zeros(tuple(fa.max(0) - flo + 3), bool); img[tuple((fa - flo).T)] = True
    img = ndimage.binary_closing(img, structure=np.ones((3, 3)), iterations=1)
    fp_wall = {(int(x + flo[0]), int(y + flo[1])) for x, y in np.argwhere(img)}
    lobe_cells = {cell_of_pixel(a, b) for (a, b) in Tset}
    vmin = min(b for a, b in fp) * 4; vstart = V0 - 4 + 40 * int(np.floor((vmin - (V0 - 4)) / 40))
    fix = {}
    if use_head:
        fix = fix_early
        vstart = 48
    D.V_PLATE = vstart
    plates = [p for p in (fix.get("primary"), fix.get("secondary")) if p]
    P1 = fix.get("primary"); P2 = fix.get("secondary")
    def in_p(p, i, zrow=True): return p and p["xm0"] <= 20 * i < p["xm0"] + 20 * p["w"]
    def in_skull(i, v0, v1):
        if not use_head: return False
        occ0 = head[0]; NX, NY, NZ = occ0.shape
        for xm in (20 * i + 1, 20 * i + 19):
            for v in (v0 + 1, v1 - 1):
                w = D.O + D.R_MOD @ np.array([xm, -v, -10.0]); x, y, z = int(np.floor(w[0] / 20)), int(np.floor(-w[1] / 8)), int(np.floor(w[2] / 20))
                if not (0 <= x < NX and 0 <= y < NY and 0 <= z < NZ and occ0[x, y, z]): return False
        return True
    def cells_ok(i, v0, v1):
        if P1 and in_p(P1, i) and v0 >= 72 and v1 <= 80: return False                       # block plate
        if P2 and in_p(P2, i) and v0 >= P2["vp"] - 8 and v1 <= P2["vp"]: return False       # secondary plate
        if P2 and P2["vp"] > 88 and P2["xm0"] - 20 <= 20 * i < P2["xm0"] + 20 * P2["w"] and v0 >= 48 and v1 <= P2["vp"] - 8: return True   # core under it
        if P1 and P1["xm0"] - 40 <= 20 * i < P1["xm0"] + 20 * P1["w"] and v0 >= 48 and v1 <= 88: return True   # root
        snot = v1 - v0 == 24
        top = v1 - 16 if (v1 >= vtop_ - 4 or snot) else v1 + 7
        bot = v0 + 4 if snot else max(v0, vstart + 4)       # side-stud course: only its joint row has to be under the faces
        lobe = all((a, b) in fp_wall for a in range(5 * i, 5 * i + 5) for b in range(bot // 4, top // 4 + 1))
        return lobe
    D.BLOCK_X = (P1["xm0"], P1["xm0"] + 20 * P1["w"]) if P1 else (10 ** 6, 10 ** 6)
    old_vp = D.V_PLATE
    vtop_ = 4 * max(b for a, b in fp) + 4
    must = set()            # joint cells of narrow face pieces: the hollow core keeps its bricks there
    for c, num, M, o, g, role in mod:
        if g != "outer": continue
        cells = {}
        for p in fp4(num, M, o): cc = cell_of_pixel(*p); cells[cc] = cells.get(cc, 0) + 1
        je = [cc for cc, n in cells.items() if n >= 25 and cc[1] % 2 == 0]
        if len(je) <= 3: must |= set(je)
    for num, i, w, v, h in wall_courses(cells_ok, vstart, vtop_, frozenset(must)):
        M, o = D.wall_piece(num, i, w, v, h); mod.append((BLACK, num, M, o, "wall", "ame : " + PL.title(num)))
    def axis_part(num, lo):
        P = conn.part(num); R = np.eye(3) if (P["hi"][0] - P["lo"][0]) >= (P["hi"][2] - P["lo"][2]) else PL.rot_y(1)
        return R, D.axis_place(num, R, lo)
    if P1:
        # root block (rule): bricks on the primary plate rows other than the core row, then a plate like the primary
        rows = [P1["zm0"] + 20 * b for b in range(P1["l"]) if not (-20 <= P1["zm0"] + 20 * b < 0)]
        bricks = {(1, 6): "3009", (2, 6): "2456", (1, 4): "3010", (2, 4): "3001", (1, 8): "3008", (2, 8): "3007", (1, 2): "3004", (2, 2): "3003"}
        j = 0
        while j < len(rows):
            if j + 1 < len(rows) and rows[j + 1] == rows[j] + 20 and (2, P1["w"]) in bricks:
                num = bricks[(2, P1["w"])]; M, o = axis_part(num, (P1["xm0"], -72, rows[j])); j += 2
            else:
                num = bricks[(1, P1["w"])]; M, o = axis_part(num, (P1["xm0"], -72, rows[j])); j += 1
            mod.append((BLACK, num, M, o, "wall", "bloc de racine : " + PL.title(num)))
        M, o = axis_part(P1["num"], (P1["xm0"], -80, P1["zm0"])); mod.append((BLACK, P1["num"], M, o, "wall", "bloc de racine : plaque"))
        M, o = axis_part(P1["num"], (P1["xm0"], -48, P1["zm0"])); mod.append((BLACK, P1["num"], M, o, "base", "plaque tournee 1 (v 40..48)"))
    if P2:
        M, o = axis_part(P2["num"], (P2["xm0"], -P2["vp"], P2["zm0"])); mod.append((BLACK, P2["num"], M, o, "base", "plaque tournee 2 (v %d..%d)" % (P2["vp"] - 8, P2["vp"])))
    # cap tiles on the top of each core column, where the outline hides them
    REC_ALL = np.array([M @ np.array(rc[0]) + o for c, num, M, o, g, role in mod for rc in conn.part(num)["receptors"]])
    caps = []
    for c, num, M, o, g, role in list(mod):
        if g != "wall" or "bloc" in role: continue
        for (p, a) in conn.part(num)["studs"]:
            w = M @ np.array(p) + o; ax = M @ np.array(a)
            if ax[1] < -0.9 and np.linalg.norm(REC_ALL - w, axis=1).min() > 2 and w[0] < D.BLOCK_X[0]: caps.append((round(w[0] - 10), round(-w[1])))
    coltop = {}
    for x0, vt in caps: coltop[x0] = max(coltop.get(x0, -1e9), vt)
    for (x0, vt) in sorted({(x0, vt) for x0, vt in caps if vt == coltop[x0] and
                            all((a, b) in fp_wall for a in range(int(x0) // 4, int(x0) // 4 + 5) for b in range(int(vt) // 4, (int(vt) + 7) // 4 + 1))}):
        Mt = np.eye(3); mod.append((BLACK, "3070b", Mt, D.axis_place("3070b", Mt, (x0, -(vt + 8), D.Z_WALL[0])), "wall", "ame : tuile de fermeture"))
    # connectivity filter: parts not linked (stud in anti-stud) to the core are removed with their twins, and counted
    def links(mod_):
        st = []; rc = []
        for k, (c, num, M, o, g, role) in enumerate(mod_):
            st += [(k, M @ np.array(p) + o) for p, a in conn.part(num)["studs"]]
            rc += [(k, M @ np.array(r_[0]) + o) for r_ in conn.part(num)["receptors"]]
        S_ = np.array([x for k, x in st]); ks = np.array([k for k, x in st]); adj = {k: set() for k in range(len(mod_))}
        for k, x in rc:
            j = np.nonzero(np.linalg.norm(S_ - x, axis=1) < 1.5)[0]
            for jj in j:
                if ks[jj] != k: adj[k].add(int(ks[jj])); adj[int(ks[jj])].add(k)
        return adj
    removed = 0
    for _ in range(3):
        adj = links(mod)
        seed = [k for k, x in enumerate(mod) if x[4] in ("base", "wall")]
        if not seed: break
        lowest = max((mod[k][3] @ np.zeros(3) + mod[k][3])[1] for k in seed)
        roots = [k for k in seed if mod[k][4] == "base"] or [k for k in seed if abs(mod[k][3][1] - lowest) < 1e-6]
        seen = set(roots); stack = list(roots)
        while stack:
            k = stack.pop()
            for j in adj[k]:
                if j not in seen: seen.add(j); stack.append(j)
        if len(seen) == len(mod): break
        removed += len(mod) - len(seen); mod = [x for k, x in enumerate(mod) if k in seen]
    rep = dict(target=target, contour=summ, parts_removed_unlinked=removed, settings_tried=[{k: v for k, v in r.items() if k != "_layout"} for r in runs],
               chosen={k: v for k, v in best.items() if k != "_layout"}, outer_layout=[list(p) for p in OUTER], fixation=fix)
    # reference metrics on the same footing as V5 (Paco: outline IoU against the V5 reference lobe, outside the skull)
    return mod, rep, fp, Tset, inside

def write(mod, rep, outdir, name, use_head):
    order = [("base", 0), ("wall", 0), ("outer", 0), ("outer_t", 0), ("inner", 0), ("inner_t", 0)]
    if use_head:
        world = lambda M, o: (D.R_MOD @ M, D.O + D.R_MOD @ o)
    else:
        world = lambda M, o: (M, o + np.array([0.0, 0.0, 0.0]))
    L = [f"0 {name}", f"0 Name: {name}.ldr", "0 Author: generateur automatique V6 (contour -> pieces)"]
    for g, _ in order:
        for c, num, M, o, gg, role in mod:
            if gg == g: Mw, ow = world(M, o); L.append(D.place_line(c, num, Mw, ow))
        L.append("0 STEP")
    open(os.path.join(outdir, f"{name}.ldr"), "w").write("\n".join(L) + "\n")
    if not use_head: return rep
    # head: carving, rebuild, seats (rules of V5.1)
    d = np.load(D.HEAD_NPZ); G = d["grid"].astype(int); F = d["fine"]; K = int(d["k"]); NX, NY, NZ = G.shape
    occ = (G >= 0) & (F.reshape(NX, K, NY, K, NZ, K).mean(axis=(1, 3, 5)) >= 0.5); eyes = (G == 15) | (G == 4)
    carve = np.zeros(G.shape, bool)
    for c, num, M, o, g, role in mod:
        Mw, ow = world(M, o); pts = conn.solid_points(num) @ Mw.T + ow
        for dy in (-4.5, 0.0, 4.5):
            q = pts + np.array([0, dy, 0])
            ix = np.floor(q[:, 0] / 20).astype(int); iy = np.floor(-q[:, 1] / 8).astype(int); iz = np.floor(q[:, 2] / 20).astype(int)
            ok = (ix >= 0) & (ix < NX) & (iy >= 0) & (iy < NY) & (iz >= 0) & (iz < NZ); carve[ix[ok], iy[ok], iz[ok]] = True
    carve &= occ
    G3 = G.copy(); G3[carve] = -1; hnpz = os.path.join(outdir, "head_C_V6.npz")
    np.savez_compressed(hnpz, grid=G3, surface=d["surface"], fine=F, k=K, neck=d["neck"], full_shape=d["full_shape"], hoff=d["hoff"])
    r = subprocess.run([sys.executable, os.path.expanduser("~/bench/proto/brickify_plus.py"), hnpz, outdir, "head_C", "--occupancy", "0.5", "--no-shapes", "--drop-floating"],
                       check=True, capture_output=True, text=True)
    head = [l for l in open(os.path.join(outdir, "head_C.ldr")).read().splitlines() if l.startswith("1 ")]
    Hocc = np.zeros(G.shape, bool)
    for l in head:
        t = l.split(); Mt = np.array(t[5:14], float).reshape(3, 3); ot = np.array(t[2:5], float); cs = D.box_corners(t[14][:-4]) @ Mt.T + ot
        Hocc[int(round(cs[:, 0].min() / 20)):int(round(cs[:, 0].max() / 20)), int(round(-cs[:, 1].max() / 8)):int(round(-cs[:, 1].min() / 8)),
             int(round(cs[:, 2].min() / 20)):int(round(cs[:, 2].max() / 20))] = True
    seats = []; seat_cells = []; per_plate = []
    for c, num, M, o, g, role in mod:
        if g != "base": continue
        Mw, ow = world(M, o); bottom_y = (D.box_corners(num) @ Mw.T + ow)[:, 1].max(); layer = int(round(-bottom_y / 8)) - 1
        st = [Mw @ np.array(p) + ow for p, a in conn.part(num)["studs"]]; n_ok = 0
        for s in st:
            x, z = int(np.floor(s[0] / 20)), int(np.floor(s[2] / 20))
            if abs(s[0] - (20 * x + 10)) > 0.5 or abs(s[2] - (20 * z + 10)) > 0.5: continue
            if Hocc[x, layer, z] or not Hocc[x, layer - 1, z]: continue
            seats.append(D.place_line(BLACK, "3024", np.eye(3), D.axis_place("3024", np.eye(3), (20 * x, -8 * (layer + 1), 20 * z))))
            seat_cells.append((x, layer - 1, z)); Hocc[x, layer, z] = True; n_ok += 1
        per_plate.append(dict(plate=role, seats=n_ok))
    T2P = {"3070b": "3024", "3069b": "3023", "63864": "3623", "2431": "3710", "6636": "3666", "3068b": "3022", "87079": "3020"}
    for k, l in enumerate(head):
        t = l.split(); n_ = t[14][:-4]
        if n_ not in T2P: continue
        Mt = np.array(t[5:14], float).reshape(3, 3); ot = np.array(t[2:5], float); cs = D.box_corners(n_) @ Mt.T + ot
        x0, x1 = int(round(cs[:, 0].min() / 20)), int(round(cs[:, 0].max() / 20)); z0, z1 = int(round(cs[:, 2].min() / 20)), int(round(cs[:, 2].max() / 20)); yl = int(round(-cs[:, 1].max() / 8))
        if any(x0 <= x < x1 and z0 <= z < z1 and y == yl for (x, y, z) in seat_cells): t[14] = T2P[n_] + ".dat"; head[k] = " ".join(t)
    W = [f"0 tete_{name}", f"0 Name: tete_{name}.ldr", "0 Author: tete C reconstruite + oreille generee (V6)"] + head + seats + ["0 STEP"]
    for c, num, M, o, gg, role in mod:
        if gg == "base": Mw, ow = world(M, o); W.append(D.place_line(c, num, Mw, ow))
    W += ["0 STEP", "0 BRICKIFY SUBASSEMBLY BEGIN oreille"]
    for g, _ in order[1:]:
        for c, num, M, o, gg, role in mod:
            if gg == g: Mw, ow = world(M, o); W.append(D.place_line(c, num, Mw, ow))
    W += ["0 BRICKIFY SUBASSEMBLY END oreille", "0 STEP"]
    open(os.path.join(outdir, f"tete_{name}.ldr"), "w").write("\n".join(W) + "\n")
    rep.update(carved_cells=int(carve.sum()), carved_eye_or_mouth=int((carve & eyes).sum()), seats=per_plate)
    return rep

def main():
    target, outdir = sys.argv[1], sys.argv[2]; use_head = "--head" in sys.argv
    mod, rep, fp, Tset, inside = build(target, outdir, use_head)
    name = f"oreille_{target}"
    rep = write(mod, rep, outdir, name, use_head)
    # outline IoU against the target, and for Paco against the V5 reference (same definition as in 09)
    iou_t = len(fp & Tset) / len(fp | Tset)
    fpo = {p for p in fp if p not in inside}; To = {p for p in Tset if p not in inside}
    rep["outline_iou_vs_target"] = round(iou_t, 4); rep["outline_iou_vs_target_outside_skull"] = round(len(fpo & To) / max(len(fpo | To), 1), 4)
    if target.startswith("A"):
        S = np.load(os.path.expanduser("~/bench/proto/ear09/sil_mesh.npy")); sj = json.load(open(os.path.expanduser("~/bench/proto/ear09/sil_mesh.json")))
        ref = {(int(np.floor((sj["u0"] + 2.5 * (a + 0.5)) / 4)), int(np.floor((sj["v0"] + 2.5 * (b + 0.5)) / 4))) for a, b in np.argwhere(S)}   # 2.5 -> 4 LDU
        ref = {p for p in ref if p[1] * 4 >= 46}
        fpr = {p for p in fp if p[1] * 4 >= 46 and p not in inside}; refo = {p for p in ref if p not in inside}
        rep["outline_iou_vs_V5_reference_lobe_outside_skull"] = round(len(fpr & refo) / len(fpr | refo), 4)
        for nm, lst in (("V5_manuel", None), ("V51_manuel", D.OUTER)):
            if lst is None:
                sys.path.insert(0, os.path.expanduser("~/bench/proto/ear09")); import design_ear as D5
                fp5 = set().union(*[fp4(n, *D5.panel_piece(n, r, i, k, "B")) for n, r, i, k, _ in D5.LAYER_B])
            else:
                fp5 = set().union(*[fp4(n, *D.outer_piece(n, r, i, k, "P")) for n, r, i, k, _ in lst])
            f5 = {p for p in fp5 if p[1] * 4 >= 46 and p not in inside}
            rep[f"outline_iou_{nm}_same_definition"] = round(len(f5 & refo) / len(f5 | refo), 4)
    rep["parts_by_group"] = {g: sum(1 for x in mod if x[4] == g) for g in ("base", "wall", "outer", "outer_t", "inner", "inner_t")}
    json.dump(dict(rep, parts=[dict(part=n, colour=c, group=g, role=r) for c, n, M, o, g, r in mod]), open(os.path.join(outdir, f"{name}_report.json"), "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in rep.items() if k not in ("settings_tried", "outer_layout", "contour")}, default=str))

if __name__ == "__main__":
    main()
