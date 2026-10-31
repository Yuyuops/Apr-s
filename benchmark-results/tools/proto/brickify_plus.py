"""Feasibility prototype (v2): brickify grid -> LEGO with shaped parts and a bond-aware plate packing.

Input: the grid of brickify's own voxeliser and colour functions (headgrid.py) plus a fine occupancy grid of the
same mesh, so the comparison with the current engine uses the same cells, colours and frame.

Stages
 0. occupancy (optional, --occupancy T): keep a brickify cell only if the mesh fills at least T of it (brickify keeps
    every cell the surface touches, which inflates thin parts); reconnect any piece cut off; cells that become visible
    take the colour of the nearest original surface cell.
 1. shaped parts: candidate placements of real parts (shapes measured from LDraw geometry, partlib.py), scored by
    the change of the fine-grid mismatch |LEGO xor mesh|; accepted greedily under support rules (a receptor on an
    occupied cell or on the support plane; nothing above a cell without stud; interior cells never taken).
 2. plates, layer by layer: largest parts produced in that colour (Rebrickable, >= MIN_SETS sets), preferring parts
    that span the seams of the layer below (running bond); caps with a flat mesh top become tiles.
 3. repair: parts not linked by studs to the support plane are re-packed locally with parts spanning a supported
    cell; floating shaped parts are turned back into plates; last resort, a 1-cell part takes a neighbour's colour.
usage: brickify_plus.py <head.npz> <outdir> <name> [--occupancy 0.5] [--no-shapes] [--no-tiles]
"""
import argparse, json, os, sqlite3, sys
from collections import Counter, defaultdict, deque
import numpy as np, networkx as nx
from scipy import ndimage
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.expanduser("~/bench/tools"))
import partlib as PL

RB = os.path.expanduser("~/bench/data/rb.db")
MIN_SETS = 20
PLATES = {(1,1):"3024",(2,1):"3023",(3,1):"3623",(4,1):"3710",(6,1):"3666",(8,1):"3460",
          (2,2):"3022",(3,2):"3021",(4,2):"3020",(6,2):"3795",(8,2):"3034",
          (4,4):"3031",(6,4):"3032",(8,4):"3035",(6,6):"3958",(8,6):"3036",(8,8):"41539"}
TILES = {(1,1):"3070b",(2,1):"3069b",(3,1):"63864",(4,1):"2431",(6,1):"6636",(2,2):"3068b"}
SHAPED_TOP = ["3040b", "3039", "11477", "15068", "54200", "85984"]
SHAPED_BOTTOM = ["3665", "3660", "24201"]
_db = None
_avail = {}

def available(num, colour):
    global _db
    key = (num, int(colour))
    if key not in _avail:
        if _db is None: _db = sqlite3.connect(RB)
        r = _db.execute("select num_sets from pcs_mat where part_num=? and color_id=?", (num, int(colour))).fetchone()
        _avail[key] = bool(r and r[0] >= MIN_SETS)
    return _avail[key]

def surface_of(occ):
    p = np.pad(occ, 1); nx_, ny_, nz_ = occ.shape; nb = np.zeros(occ.shape, int)
    for dx, dy, dz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
        nb += ~p[1+dx:1+dx+nx_, 1+dy:1+dy+ny_, 1+dz:1+dz+nz_]
    return occ & (nb > 0)

class Model:
    def __init__(self, G, F, K):
        self.G = G; self.F = F; self.K = K; self.shape = G.shape
        self.parts = []                       # dicts: num, r, x0, y0, z0, w, d, h, colour, kind
        self.owner = -np.ones(G.shape, int)

    def add(self, p):
        p = dict(p); i = len(self.parts); self.parts.append(p)
        self.owner[p["x0"]:p["x0"] + p["w"], p["y0"]:p["y0"] + p["h"], p["z0"]:p["z0"] + p["d"]] = i
        return i

    def remove(self, i):
        p = self.parts[i]
        sl = (slice(p["x0"], p["x0"] + p["w"]), slice(p["y0"], p["y0"] + p["h"]), slice(p["z0"], p["z0"] + p["d"]))
        self.owner[sl] = np.where(self.owner[sl] == i, -1, self.owner[sl]); self.parts[i] = None

    def masks(self, p):
        cells = {(x, z) for x in range(p["x0"], p["x0"] + p["w"]) for z in range(p["z0"], p["z0"] + p["d"])}
        if p["kind"] == "shaped":
            Q = PL.placed(p["num"], p["r"])
            return {(p["x0"] + i, p["z0"] + j) for i, j in Q["studs"]}, {(p["x0"] + i, p["z0"] + j) for i, j in Q["recv"]}
        return (set() if p["kind"] == "tile" else cells), cells

    def graph(self):
        Gr = nx.Graph(); M = {}
        for i, p in enumerate(self.parts):
            if p is None: continue
            Gr.add_node(i); M[i] = self.masks(p)
        for i, p in enumerate(self.parts):
            if p is None: continue
            yt = p["y0"] + p["h"]
            if yt >= self.shape[1]: continue
            for (x, z) in M[i][0]:
                q = self.owner[x, yt, z]
                if q >= 0 and self.parts[q]["y0"] == yt and (x, z) in M[q][1]:
                    if Gr.has_edge(i, q): Gr[i][q]["studs"] += 1
                    else: Gr.add_edge(i, q, studs=1)
        grounded = set()
        for i, p in enumerate(self.parts):
            if p is not None and p["y0"] == 0 and i not in grounded: grounded |= nx.node_connected_component(Gr, i)
        floating = [i for i in Gr.nodes if i not in grounded]
        return Gr, grounded, floating, M

    # ------------------------------------------------------------------ plate packing of one region in one layer
    def pack_region(self, y, region, colour, use_tiles=False, bonus=None, must=None):
        """greedy: largest parts first, + spanning the seams of the layer below, + bonus cells (a rectangle covering
        a 'must' cell and a bonus cell gets a large reward: used to tie a floating part to a supported one)."""
        NX, _, NZ = self.shape
        below = self.owner[:, y - 1, :] if y > 0 else -np.ones((NX, NZ), int)
        sx = np.zeros((NX, NZ)); sz = np.zeros((NX, NZ))
        sx[:-1, :] = (below[:-1, :] != below[1:, :]) & (below[:-1, :] >= 0) & (below[1:, :] >= 0)
        sz[:, :-1] = (below[:, :-1] != below[:, 1:]) & (below[:, :-1] >= 0) & (below[:, 1:] >= 0)
        Psx = np.pad(sx.cumsum(0).cumsum(1), ((1, 0), (1, 0))); Psz = np.pad(sz.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
        Pb = np.pad((bonus if bonus is not None else np.zeros((NX, NZ))).astype(float).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
        Pm = np.pad((must if must is not None else np.zeros((NX, NZ))).astype(float).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
        table = TILES if use_tiles else PLATES
        sizes = []
        for (L, Wd), num in table.items():
            if not available(num, colour): continue
            sizes.append((L, Wd, num, 0))
            if L != Wd: sizes.append((Wd, L, num, 1))
        if not sizes: sizes = [(1, 1, table[(1, 1)], 0)]
        free = region.copy(); pref_x = (y % 2 == 0); new = []
        box = lambda P_, xs, zs, w, d: P_[xs + w, zs + d] - P_[xs, zs + d] - P_[xs + w, zs] + P_[xs, zs]
        while free.any():
            Pf = np.pad(free.cumsum(0).cumsum(1), ((1, 0), (1, 0))); best = None
            for (w, dd, num, rot) in sizes:
                if w > NX or dd > NZ: continue
                full = (Pf[w:, dd:] - Pf[:-w, dd:] - Pf[w:, :-dd] + Pf[:-w, :-dd]) == w * dd
                if not full.any(): continue
                xs, zs = np.nonzero(full)
                seam = (box(Psx, xs, zs, w - 1, dd) if w > 1 else 0) + (box(Psz, xs, zs, w, dd - 1) if dd > 1 else 0)
                tie = (box(Pm, xs, zs, w, dd) > 0) & (box(Pb, xs, zs, w, dd) > 0)
                score = w * dd + 1.5 * seam + (0.3 if ((w >= dd) == pref_x) else 0.0) + 50.0 * tie + 0.5 * box(Pb, xs, zs, w, dd)
                i = int(np.argmax(score))
                if best is None or score[i] > best[0]: best = (score[i], xs[i], zs[i], w, dd, num, rot)
            _, x0, z0, w, dd, num, rot = best
            free[x0:x0 + w, z0:z0 + dd] = False
            new.append(self.add(dict(num=num, r=rot, x0=int(x0), y0=y, z0=int(z0), w=int(w), d=int(dd), h=1, colour=int(colour),
                                     kind="tile" if use_tiles else "plate")))
        return new

def reconnect(occ, allowed, fr):
    """add back cells (from 'allowed', along a 0-1 BFS path) until occ is one 6-connected piece"""
    lab, n = ndimage.label(occ)
    if n <= 1: return occ, 0
    sizes = ndimage.sum(occ, lab, range(1, n + 1)); main = int(np.argmax(sizes)) + 1
    added = 0
    for c in range(1, n + 1):
        if c == main: continue
        start = list(map(tuple, np.argwhere(lab == c)))
        dist = {s: 0 for s in start}; prev = {}; dq = deque(start); goal = None
        while dq:
            u = dq.popleft()
            if lab[u] == main: goal = u; break
            for dv in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
                v = (u[0] + dv[0], u[1] + dv[1], u[2] + dv[2])
                if not all(0 <= v[k] < occ.shape[k] for k in range(3)) or not (allowed[v] or occ[v]) or v in dist: continue
                cost = 0 if occ[v] else 1
                dist[v] = dist[u] + cost; prev[v] = u
                (dq.appendleft if cost == 0 else dq.append)(v)
        while goal is not None and goal in prev:
            if not occ[goal]: occ[goal] = True; added += 1
            goal = prev[goal]
    return occ, added

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("npz"); ap.add_argument("out"); ap.add_argument("name")
    ap.add_argument("--occupancy", type=float, default=0.0)
    ap.add_argument("--no-shapes", action="store_true"); ap.add_argument("--no-tiles", action="store_true")
    ap.add_argument("--min-gain", type=float, default=0.12)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    d = np.load(a.npz); G0 = d["grid"].astype(int); F = d["fine"]; K = int(d["k"]); KY = K
    NX, NY, NZ = G0.shape; log = defaultdict(int)
    fr = F.reshape(NX, K, NY, K, NZ, K).mean(axis=(1, 3, 5))
    occ0 = G0 >= 0
    # ---- stage 0: occupancy
    occ = occ0 & (fr >= a.occupancy) if a.occupancy > 0 else occ0.copy()
    occ, log["reconnect_cells"] = reconnect(occ, occ0, fr)
    G = np.where(occ, G0, -1)
    surf = surface_of(occ)
    new_vis = surf & ~d["surface"].astype(bool)
    if new_vis.any():                                   # newly visible cells: nearest original surface colour
        sidx = np.argwhere(d["surface"].astype(bool) & occ0)
        t = cKDTree(sidx); _, j = t.query(np.argwhere(new_vis))
        G[tuple(np.argwhere(new_vis).T)] = G0[tuple(sidx[j].T)]
    log["cells"] = int(occ.sum()); log["cells_brickify"] = int(occ0.sum()); log["recoloured_new_surface"] = int(new_vis.sum())
    m = Model(G, F, K); claimed = np.zeros(G.shape, bool); orig_occ = occ.copy()
    fsl = lambda x0, y0, z0, nx_, nh, nz_: (slice(x0 * K, (x0 + nx_) * K), slice(y0 * KY, (y0 + nh) * KY), slice(z0 * K, (z0 + nz_) * K))
    # ---- stage 1: shaped parts
    if not a.no_shapes:
        S = np.repeat(np.repeat(np.repeat(occ, K, 0), KY, 1), K, 2)
        cands = []
        for num in SHAPED_TOP + SHAPED_BOTTOM:
            inv = num in SHAPED_BOTTOM
            for r in range(4):
                Q = PL.placed(num, r); nx_, nh, nz_ = Q["nx"], Q["nh"], Q["nz"]; sol = Q["solid"]
                nostud = [(i, j) for i in range(nx_) for j in range(nz_) if (i, j) not in Q["studs"]]
                for x0 in range(NX - nx_ + 1):
                    for z0 in range(NZ - nz_ + 1):
                        for y0 in range(NY - nh + 1):
                            box = (slice(x0, x0 + nx_), slice(y0, y0 + nh), slice(z0, z0 + nz_))
                            bo = occ[box]
                            if not bo.any() or (bo & ~surf[box]).any(): continue
                            if any(y0 + nh < NY and occ[x0 + i, y0 + nh, z0 + j] for (i, j) in nostud): continue
                            if y0 > 0 and not any(occ[x0 + i, y0 - 1, z0 + j] for (i, j) in Q["recv"]): continue
                            if inv and y0 > 0 and all(occ[x0 + i, y0 - 1, z0 + j] for i in range(nx_) for j in range(nz_)): continue
                            fs = fsl(x0, y0, z0, nx_, nh, nz_); f = F[fs]
                            gain = (np.count_nonzero(S[fs] ^ f) - np.count_nonzero(sol ^ f)) / sol.size
                            if gain >= a.min_gain: cands.append((gain * sol.size, num, r, x0, y0, z0))
        cands.sort(key=lambda c: -c[0]); log["shape_candidates"] = len(cands)
        for _, num, r, x0, y0, z0 in cands:
            Q = PL.placed(num, r); nx_, nh, nz_ = Q["nx"], Q["nh"], Q["nz"]
            box = (slice(x0, x0 + nx_), slice(y0, y0 + nh), slice(z0, z0 + nz_))
            if claimed[box].any(): continue
            def supports(x, z):
                if y0 == 0: return True
                q = m.owner[x, y0 - 1, z]
                if claimed[x, y0 - 1, z]:
                    return q >= 0 and (x, z) in m.masks(m.parts[q])[0] and m.parts[q]["y0"] + m.parts[q]["h"] == y0
                return occ[x, y0 - 1, z]
            if not any(supports(x0 + i, z0 + j) for (i, j) in Q["recv"]): continue
            if any(y0 + nh < NY and occ[x0 + i, y0 + nh, z0 + j] for i in range(nx_) for j in range(nz_) if (i, j) not in Q["studs"]): continue
            cols = [G[tuple(c)] for c in np.argwhere(occ[box]) + [x0, y0, z0]]
            if not cols: continue
            colour = Counter(cols).most_common(1)[0][0]
            if not available(num, colour): continue
            claimed[box] = True; occ[box] = True; G[box] = colour; S[fsl(x0, y0, z0, nx_, nh, nz_)] = Q["solid"]
            m.add(dict(num=num, r=r, x0=x0, y0=y0, z0=z0, w=nx_, d=nz_, h=nh, colour=int(colour), kind="shaped"))
            log[f"shaped_{num}"] += 1
    # ---- stage 2: plates and tiles
    flat = {}
    def flat_top(y):
        if y not in flat:
            f = F[:, y * KY:(y + 1) * KY, :]; flat[y] = f[:, -1, :].reshape(NX, K, NZ, K).mean(axis=(1, 3)) > 0.75
        return flat[y]
    for y in range(NY):
        free = occ[:, y, :] & ~claimed[:, y, :]
        if not free.any(): continue
        above = occ[:, y + 1, :] if y + 1 < NY else np.zeros((NX, NZ), bool)
        tiles = (free & ~above & flat_top(y)) if not a.no_tiles else np.zeros_like(free)
        for colour in np.unique(G[:, y, :][free]):
            for ut in (False, True):
                reg = free & (G[:, y, :] == colour) & (tiles if ut else ~tiles)
                if reg.any(): m.pack_region(y, reg, int(colour), use_tiles=ut)
    # ---- stage 3: repair floating parts
    surf_now = surface_of(occ)
    for it in range(25):
        Gr, grounded, floating, M = m.graph()
        if it == 0: log["floating_before_repair"] = len(floating)
        if not floating: break
        progress = False
        for f in sorted(floating, key=lambda i: m.parts[i]["y0"] if m.parts[i] else 0):
            p = m.parts[f]
            if p is None: continue
            if p["kind"] == "shaped":        # turn the shaped part back into plates (originally occupied cells only)
                y0, h = p["y0"], p["h"]; box = (slice(p["x0"], p["x0"] + p["w"]), slice(y0, y0 + h), slice(p["z0"], p["z0"] + p["d"]))
                m.remove(f); claimed[box] = False
                keep = orig_occ[box]; occ[box] = keep
                for yy in range(y0, y0 + h):
                    reg = np.zeros((NX, NZ), bool); reg[box[0], box[2]] = keep[:, yy - y0, :]
                    if reg.any(): m.pack_region(yy, reg, p["colour"])
                log["shaped_reverted"] += 1; progress = True; continue
            y = p["y0"]; c = p["colour"]
            fmask = np.zeros((NX, NZ), bool); fmask[p["x0"]:p["x0"] + p["w"], p["z0"]:p["z0"] + p["d"]] = True
            # supported cells in this layer: a grounded part below with a stud there, or above with a receptor there
            sup = np.zeros((NX, NZ), bool)
            for (dy, which) in ((-1, 0), (1, 1)):
                yy = y + dy
                if 0 <= yy < NY:
                    for q in set(m.owner[:, yy, :][m.owner[:, yy, :] >= 0].tolist()):
                        pq = m.parts[q]
                        touches = (pq["y0"] + pq["h"] == y) if dy < 0 else (pq["y0"] == yy)
                        if q in grounded and touches:
                            for (x, z) in M[q][which]: sup[x, z] = True
            # same-colour plates of this layer around the floating part
            same = np.zeros((NX, NZ), bool)
            lay = m.owner[:, y, :]
            for q in set(lay[lay >= 0].tolist()):
                pq = m.parts[q]
                if pq["kind"] != "shaped" and pq["colour"] == c and pq["y0"] == y: same[lay == q] = True
            lab, _ = ndimage.label(same); comp = np.isin(lab, np.unique(lab[fmask & same]))
            win = ndimage.binary_dilation(fmask, iterations=4) & comp
            if not (win & sup).any():
                # bridge: the smallest plate (<= 8 cells) over occupied non-shaped cells that covers both a cell tied to
                # the floating part and a supported cell, tried in the part's own layer, then the layer above (over its
                # studs) and below (under its receptors). It takes the majority colour of the cells it covers.
                done = False
                stud_c, recv_c = M[f]
                for dy, fc in ((0, {(x, z) for x in range(p["x0"], p["x0"] + p["w"]) for z in range(p["z0"], p["z0"] + p["d"])}),
                               (p["h"], stud_c), (-1, recv_c)):
                    yy = y + dy
                    if not (0 <= yy < NY) or not fc: continue
                    lay2 = m.owner[:, yy, :]
                    occl = np.zeros((NX, NZ), bool)
                    for q in set(lay2[lay2 >= 0].tolist()):
                        if m.parts[q]["kind"] != "shaped" and m.parts[q]["y0"] == yy: occl |= (lay2 == q)
                    if dy != 0:
                        for (x, z) in list(fc):
                            q = lay2[x, z]
                            if q < 0 or not occl[x, z]: fc = fc - {(x, z)}
                    sup2 = np.zeros((NX, NZ), bool)
                    for (dd_, which) in ((-1, 0), (1, 1)):
                        y3 = yy + dd_
                        if 0 <= y3 < NY:
                            for q in set(m.owner[:, y3, :][m.owner[:, y3, :] >= 0].tolist()):
                                pq = m.parts[q]
                                touch = (pq["y0"] + pq["h"] == yy) if dd_ < 0 else (pq["y0"] == y3)
                                if q in grounded and touch:
                                    for (x, z) in M[q][which]: sup2[x, z] = True
                    best = None
                    for (fx, fz) in fc:
                        for sx_, sz_ in zip(*np.nonzero(sup2 & occl)):
                            bx0, bx1 = min(fx, sx_), max(fx, sx_) + 1; bz0, bz1 = min(fz, sz_), max(fz, sz_) + 1
                            w, dd = bx1 - bx0, bz1 - bz0; key = (max(w, dd), min(w, dd))
                            if w * dd > 8 or key not in PLATES or not occl[bx0:bx1, bz0:bz1].all(): continue
                            if best is None or w * dd < best[0]: best = (w * dd, bx0, bz0, w, dd)
                    if best is None: continue
                    _, bx0, bz0, w, dd = best; key = (max(w, dd), min(w, dd))
                    # colour that changes the fewest visible cells (a surface cell weighs 10, a hidden cell 1)
                    blk = G[bx0:bx0 + w, yy, bz0:bz0 + dd]; wgt = np.where(surf_now[bx0:bx0 + w, yy, bz0:bz0 + dd], 10, 1)
                    opts = [int(k) for k in np.unique(blk) if k >= 0 and available(PLATES[key], k)]
                    colour = min(opts, key=lambda k: int(((blk != k) * wgt).sum())) if opts else None
                    if colour is None: continue
                    victims = set(lay2[bx0:bx0 + w, bz0:bz0 + dd].ravel().tolist()); rest = []
                    for q in victims:
                        pq = m.parts[q]; rest.append((pq["colour"], pq["x0"], pq["z0"], pq["w"], pq["d"])); m.remove(q)
                    log["bridge_recoloured_cells"] += int((G[bx0:bx0 + w, yy, bz0:bz0 + dd] != colour).sum())
                    G[bx0:bx0 + w, yy, bz0:bz0 + dd] = colour
                    m.add(dict(num=PLATES[key], r=0 if w >= dd else 1, x0=int(bx0), y0=yy, z0=int(bz0), w=int(w), d=int(dd), h=1, colour=colour, kind="plate"))
                    for (c2, qx, qz, qw, qd) in rest:
                        reg = np.zeros((NX, NZ), bool); reg[qx:qx + qw, qz:qz + qd] = True; reg &= (m.owner[:, yy, :] < 0)
                        if reg.any(): m.pack_region(yy, reg, c2)
                    log["bridges"] += 1; progress = True; done = True
                    break
                continue
            freed = np.zeros((NX, NZ), bool)
            for q in set(lay[win].tolist()):
                if q >= 0 and m.parts[q] is not None:
                    pq = m.parts[q]; freed[pq["x0"]:pq["x0"] + pq["w"], pq["z0"]:pq["z0"] + pq["d"]] = True; m.remove(q)
            m.pack_region(y, freed & (m.owner[:, y, :] < 0), c, bonus=sup & freed, must=fmask)
            progress = True
        if not progress: break
    Gr, grounded, floating, M = m.graph(); log["floating_after_repair"] = len(floating)
    if os.environ.get("DEBUG_FLOAT"):
        for f in floating:
            p = m.parts[f]; info = []
            for (x, z) in sorted(M[f][0]):
                q = m.owner[x, p["y0"] + p["h"], z] if p["y0"] + p["h"] < NY else -1
                info.append(("haut", (x, z), q, m.parts[q]["kind"] + m.parts[q]["num"] if q >= 0 else None, q in grounded, (x, z) in M[q][1] if q >= 0 else None, m.parts[q]["y0"] if q >= 0 else None))
            for (x, z) in sorted(M[f][1]):
                q = m.owner[x, p["y0"] - 1, z] if p["y0"] > 0 else -1
                info.append(("bas", (x, z), q, m.parts[q]["kind"] + m.parts[q]["num"] if q >= 0 else None, q in grounded))
            print("FLOAT", f, p["num"], p["kind"], (p["x0"], p["y0"], p["z0"]), info)
    # ---- write LDraw (steps = plate layers, bottom-up)
    parts = [p for p in m.parts if p is not None]
    order = sorted(range(len(parts)), key=lambda i: (parts[i]["y0"], parts[i]["kind"] == "shaped", parts[i]["z0"], parts[i]["x0"]))
    out = [f"0 {a.name}", f"0 Name: {a.name}.ldr", "0 Author: brickify_plus prototype (feasibility study)"]; cur = None
    for i in order:
        p = parts[i]
        if cur is not None and p["y0"] != cur: out.append("0 STEP")
        cur = p["y0"]; out.append(PL.ldraw_line(p["colour"], p["num"], p["r"], p["x0"], p["y0"], p["z0"]))
    out.append("0 STEP")
    open(os.path.join(a.out, f"{a.name}.ldr"), "w").write("\n".join(out) + "\n")
    rep = dict(name=a.name, parts=len(parts), kinds=dict(Counter(p["kind"] for p in parts)),
               part_numbers=dict(Counter(p["num"] for p in parts).most_common()), settings=vars(a), **{k: int(v) for k, v in log.items()})
    json.dump(rep, open(os.path.join(a.out, f"{a.name}_report.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "part_numbers"}))

if __name__ == "__main__":
    main()
