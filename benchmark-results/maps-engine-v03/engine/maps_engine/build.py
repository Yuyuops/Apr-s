"""V0.1 builder : class grid -> heights (declared artistic style) -> colours -> field layers (plates / smooth tiles) -> two staggered backing layers -> frame ring of bricks -> LDraw.
Coordinates : x = row, z = column in cells of a GLOBAL grid (frame included) ; the field is the n x n block at offset (m, m), m = frame width."""
import json, os
from collections import Counter
import numpy as np
from .common import STUD, PLATE, PLATES, TILES, BRICKS, KINDS, ROUND_PLATE, ROUND_TILE, CUT_CORNER_PLATE, part_for, rb_colours
from . import palette as PAL, tiling as T

POINT_CLASSES = ("village",)                                        # point features : one round 1x1 part per cell

def heights(grid, classes, style, mode):
    lv = style["levels"]; h = np.zeros(grid.shape, int)
    if mode == "2d": return h
    for i, nm in enumerate(classes): h[grid == i] = lv.get(nm, lv.get("autre", 1))
    return h
def exposed_side(h, k):
    n = h.shape[0]; e = np.zeros_like(h, bool); P = np.pad(h, 1, constant_values=-1)
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)): e |= P[1 + dx:1 + dx + n, 1 + dz:1 + dz + n] < k
    return e
def adjacency(grid, classes):
    a = set(); n = grid.shape[0]
    for r in range(n):
        for c in range(n):
            for dr, dc in ((1, 0), (0, 1)):
                if r + dr < n and c + dc < n and grid[r, c] != grid[r + dr, c + dc]: a.add(tuple(sorted((classes[grid[r, c]], classes[grid[r + dr, c + dc]]))))
    return a
def smooth_classes(grid, classes, levels, rule):
    share = {nm: float((grid == i).mean()) for i, nm in enumerate(classes)}
    return {nm for nm in classes if nm not in POINT_CLASSES and (levels[nm] <= rule.get("level_max", 1) or share[nm] >= rule.get("share_min", 0.10))}

def segments(total, first=0):
    """split `total` studs into the fewest segments of 8 / 6 / 4 / 2 (optionally starting with a segment of `first`) : every backing plate is then at least 2 wide and mostly 8 x 8"""
    best = {0: []}
    for t in range(2, total - first + 1, 2):
        cands = [best[t - s] + [s] for s in (8, 6, 4, 2) if t - s in best]
        if cands: best[t] = min(cands, key=lambda c: (len(c), -max(c)))
    rest = sorted(best.get(total - first) or [], reverse=True); return ([first] if first else []) + rest
def backing_layers(N, bc, hid, full, nowild, seed):
    """two layers of plates whose joints never coincide : layer 1 cut at 8, 16, 24... ; layer 2 shifted by 4 (or 6 / 2) ; each rectangle is one plate when that plate exists in the backing colour, else it is re-tiled"""
    s1 = segments(N)
    for first in (4, 6, 2, 0):
        s2 = segments(N, first); i1 = set(np.cumsum(s1)[:-1]); i2 = set(np.cumsum(s2)[:-1])
        if not (i1 & i2): break
    out = []
    for segs in (s1, s2):
        parts = []; r0 = 0
        for a in segs:
            c0 = 0
            for b_ in segs:
                key = (max(a, b_), min(a, b_))
                if key in PLATES and PAL.available(PLATES[key], bc): parts.append(dict(x=r0, z=c0, w=a, d=b_, colour=bc))
                else:
                    sub = np.full((a, b_), bc, int); lst = T.best_tiling(sub, np.zeros((a, b_), bool), -np.ones((a, b_), int), hid, PLATES, tries=2, seed=seed)
                    parts += [dict(x=r0 + p["x"], z=c0 + p["z"], w=p["w"], d=p["d"], colour=bc) for p in lst]
                c0 += b_
            r0 += a
        out.append(parts)
    return out

class Model:
    def __init__(self): self.parts = []; self.pid = 0
    def add(self, kind, x, z, w, d, zbot, colour, layer, region, part=None, rot=None):
        self.pid += 1; h = KINDS[kind][1] if part is None or kind in KINDS else 1
        p = dict(id=self.pid, kind=kind, x=int(x), z=int(z), w=int(w), d=int(d), zbot=int(zbot), h=h, colour=int(colour), layer=layer, region=region, part=part or part_for(kind, w, d)); p["size"] = "%dx%d" % (max(w, d), min(w, d))
        if rot: p["rot"] = rot; p["wedge"] = True
        self.parts.append(p); return p

def build(cg, style, finish="A", mode="2.5d", frame_width=None, tries=8, seed=0, contour_cut=None, smooth_set=None, frame_cap=False, improve=True, shore_band=0, mat=None):
    grid, classes, n = cg["grid"], cg["classes"], cg["grid"].shape[0]; B = finish == "B"; contour_cut = (not B) if contour_cut is None else contour_cut
    levels = {nm: style["levels"].get(nm, style["levels"].get("autre", 1)) if mode != "2d" else 0 for nm in classes}
    h = heights(grid, classes, style, mode); K = int(h.max()); m = frame_width if frame_width is not None else (2 if B else 1); N = n + 2 * m
    smooth = smooth_classes(grid, classes, levels, style.get("smooth_rule", {})) if B else {nm for nm in (smooth_set or ()) if nm in classes}      # names that the classifier did not find on this map are ignored
    from scipy import ndimage
    blob = {}
    for i, nm in enumerate(classes):
        msk = grid == i; per = max(1, int((msk ^ ndimage.binary_erosion(msk)).sum())); blob[nm] = max(1.0, min(24.0, msk.sum() / (per / 4.0)))      # typical area of one part of this class
    col, ncand, obj = PAL.assign(cg["colour"], {nm: int((grid == i).sum()) for i, nm in enumerate(classes)}, adjacency(grid, classes), levels, smooth=bool(smooth), blob=blob)
    ccode = np.array([col[nm]["code"] for nm in classes]); top_colour = ccode[grid]; fc = PAL.frame_colour(); bc = PAL.backing_colour()
    M = Model()
    # ---- backing : two staggered layers over the whole (field + frame) area, in the frame colour so that the sides read as one finished edge
    full = np.full((N, N), bc, int); nowild = np.zeros((N, N), bool); none = -np.ones((N, N), int)
    hid = lambda x, z, w, d, part: bc
    b1, b2 = backing_layers(N, bc, hid, full, nowild, seed)
    ids1 = -np.ones((N, N), int)
    for p in b1: q = M.add("plate", p["x"], p["z"], p["w"], p["d"], 0, bc, "B1", "dos"); ids1[p["x"]:p["x"] + p["w"], p["z"]:p["z"] + p["d"]] = q["id"]
    ids2 = -np.ones((N, N), int)
    for p in b2: q = M.add("plate", p["x"], p["z"], p["w"], p["d"], 1, bc, "B2", "dos"); ids2[p["x"]:p["x"] + p["w"], p["z"]:p["z"] + p["d"]] = q["id"]
    below = ids2[m:m + n, m:m + n].copy(); z0 = 2
    # ---- relief layers of the field
    for k in range(K + 1):
        top = h == k; has = h >= k; ex = exposed_side(h, k); mid = has & ~top
        fixed = -np.ones((n, n), int); wild = np.zeros((n, n), bool)
        fixed[top] = top_colour[top]; fixed[mid & ex] = top_colour[mid & ex]; wild[mid & ~ex] = True
        points = np.zeros((n, n), bool)
        for nm in POINT_CLASSES:
            if nm in classes: points |= top & (grid == classes.index(nm))
        sm = np.zeros((n, n), bool)
        for nm in smooth: sm |= top & (grid == classes.index(nm))
        if mat is not None and sm.any():                                          # smooth 'mat' : only the open water OUTSIDE the rectangle that bounds everything else (+ `mat` cells of margin) is tiled : clean straight bands of tiles around a studded window
            nz = ~np.isin(grid, [classes.index(nm) for nm in smooth]); rr, cc = np.nonzero(nz); r0, r1, c0, c1 = max(0, rr.min() - mat), min(n, rr.max() + 1 + mat), max(0, cc.min() - mat), min(n, cc.max() + 1 + mat)
            win = np.zeros((n, n), bool); win[r0:r1, c0:c1] = True; sm &= ~win
        if shore_band and sm.any():                                              # keep a studded band of `shore_band` cells along the shore : the plates under the land can then extend into it (fewer small hidden plates)
            from scipy import ndimage as _nd
            not_smooth = ~np.isin(grid, [classes.index(nm) for nm in smooth]); dist = _nd.distance_transform_cdt(~not_smooth, metric="chessboard"); sm &= dist > shore_band
        ids = -np.ones((n, n), int)
        for (r, c) in np.argwhere(points):                                     # round 1x1 marker (plate with solid stud in A, round tile in B)
            kind, part = ("tile", ROUND_TILE) if B else ("plate", ROUND_PLATE); colr = int(fixed[r, c])
            if not PAL.available(part, colr): part = ROUND_PLATE if PAL.available(ROUND_PLATE, colr) else part_for("plate", 1, 1); kind = "plate"
            q = M.add(kind, m + r, m + c, 1, 1, z0 + k, colr, "L%d" % k, classes[grid[r, c]], part=part); ids[r, c] = q["id"]
        plate_fixed = fixed.copy(); plate_fixed[sm | points] = -1
        if contour_cut:                                                                  # convex coast corners : a 2x2 wedge plate with one cut corner replaces a stair step (3 studs + a diagonal edge)
            for (r, c) in np.argwhere(top):
                for (dr, dc, rot) in ((1, 1, "1 0 0 0 1 0 0 0 1"), (1, -1, "0 0 1 0 1 0 -1 0 0"), (-1, -1, "-1 0 0 0 1 0 0 0 -1"), (-1, 1, "0 0 -1 0 1 0 1 0 0")):
                    cells = [(r, c), (r - dr, c), (r, c - dc), (r - dr, c - dc)]; outer = [(r + dr, c), (r, c + dc)]
                    if any(not (0 <= a < n and 0 <= b_ < n) for a, b_ in cells + outer): continue
                    col0 = plate_fixed[r, c]
                    if cg["frac"][r, c, grid[r, c]] > style.get("wedge_max_coverage", 0.80): continue            # cut only where the source really leaves part of the corner cell empty
                    if col0 < 0 or points[r, c] or classes[grid[r, c]] in smooth or any(plate_fixed[a, b_] != col0 or not top[a, b_] for a, b_ in cells) or any(h[a, b_] >= k for a, b_ in outer): continue
                    if not PAL.available(CUT_CORNER_PLATE, int(col0)): continue
                    r0, c0 = min(r, r - dr), min(c, c - dc); q = M.add("plate", m + r0, m + c0, 2, 2, z0 + k, int(col0), "L%d" % k, classes[grid[r, c]], part=CUT_CORNER_PLATE, rot=rot)
                    for a, b_ in cells: plate_fixed[a, b_] = -1; ids[a, b_] = q["id"]
                    break
        tile_fixed = -np.ones((n, n), int); tile_fixed[sm] = fixed[sm]
        def hidden(x, z, w, d, part, _k=k):
            cnt = Counter(top_colour[x:x + w, z:z + d].ravel().tolist())
            for c, _ in cnt.most_common():
                if PAL.available(part, int(c)): return c
            for c in (ccode.tolist() + [fc]):
                if PAL.available(part, int(c)): return c
            raise RuntimeError("no colour for a hidden part")
        pl = T.best_tiling(plate_fixed, wild, below, hidden, PLATES, tries=tries, seed=seed + 10 + k) if ((plate_fixed >= 0) | wild).any() else []
        tl = T.best_tiling(tile_fixed, np.zeros((n, n), bool), below, hidden, TILES, tries=tries, seed=seed + 50 + k, orient=16.0, seam_pen=0.3, orient_strict=True) if sm.any() else []
        pl = T.merge_small(pl, PLATES); tl = T.merge_small(tl, TILES)
        if improve: pl = T.local_improve(pl, PLATES, below, seed=seed + 300 + k, small=(3 if improve == 'weak' else 1)); tl = T.local_improve(tl, TILES, below, seed=seed + 400 + k) if tl else tl
        for kind, lst in (("plate", pl), ("tile", tl)):
            for p in lst:
                sub = grid[p["x"]:p["x"] + p["w"], p["z"]:p["z"] + p["d"]]; vis = h[p["x"]:p["x"] + p["w"], p["z"]:p["z"] + p["d"]] == k
                reg = classes[Counter((sub[vis] if vis.any() else sub).ravel().tolist()).most_common(1)[0][0]]
                q = M.add(kind, m + p["x"], m + p["z"], p["w"], p["d"], z0 + k, p["colour"], "L%d" % k, reg); ids[p["x"]:p["x"] + p["w"], p["z"]:p["z"] + p["d"]] = q["id"]
        below = ids
    top_z = z0 + K + 1                                                                      # first free plate level above the field
    # ---- frame : courses of bricks (interlocked by the same stagger rule), then plates / tiles to a finished top edge
    if m > 0:
        ring = np.ones((N, N), bool); ring[m:m + n, m:m + n] = False; frame_h = max(3, (K + 1) if B else K); nb = frame_h // 3; rest = frame_h - 3 * nb          # B : flush with the summit ; A : one plate under it (discreet, the relief stays visible from the side); nb = frame_h // 3; rest = frame_h - 3 * nb
        prev = ids2.copy(); z = z0; courses = []
        for j in range(nb):
            f = np.where(ring, fc, -1); lst = T.merge_small(T.best_tiling(f, nowild, np.where(ring, prev, -1), hid, BRICKS, tries=6, seed=seed + 100 + j, stagger=3.0, seam_pen=4.0), BRICKS)
            ids = -np.ones((N, N), int)
            for p in lst: q = M.add("brick", p["x"], p["z"], p["w"], p["d"], z, fc, "F%d" % j, "cadre"); ids[p["x"]:p["x"] + p["w"], p["z"]:p["z"] + p["d"]] = q["id"]
            prev = ids; z += 3
        for j in range(rest):
            last = (j == rest - 1) and (B or frame_cap); cat = TILES if last else PLATES; kind = "tile" if last else "plate"
            f = np.where(ring, fc, -1); lst = T.best_tiling(f, nowild, np.where(ring, prev, -1), hid, cat, tries=6, seed=seed + 200 + j, stagger=3.0, seam_pen=4.0)
            ids = -np.ones((N, N), int)
            for p in lst: q = M.add(kind, p["x"], p["z"], p["w"], p["d"], z, fc, "F%d" % (nb + j), "cadre"); ids[p["x"]:p["x"] + p["w"], p["z"]:p["z"] + p["d"]] = q["id"]
            prev = ids; z += 1
    return dict(finish_options=dict(smooth=sorted(smooth), frame_cap=bool(frame_cap or B), improve=improve), parts=M.parts, heights=h, colours=col, ncand=ncand, objective=obj, frame_colour=fc, backing_colour=bc, levels=K + 1, n=n, N=N, m=m, mode=mode, finish=finish, smooth=sorted(smooth), z0=z0, field_top=top_z)

def y_top(p): return -8 * (p["zbot"] + p["h"])

def write_ldr(model, path, name, steps=None):
    P = model["parts"]; N = model["N"]; L = ["0 %s" % name, "0 Name: %s" % os.path.basename(path), "0 Author: LEGO Maps engine 2 V0.1", "0 !LICENSE Original test map (fictional), generated file",
                                          "0 // finish %s ; field %dx%d studs + frame %d ; total %dx%d studs ; axes: LDraw x = image column (west->east), z = minus image row (north = +z), y down (relief goes up)" % (model["finish"], model["n"], model["n"], model["m"], N, N)]
    groups = [dict(title="all", parts=sorted(P, key=lambda p: (p["zbot"], p["id"])))] if steps is None else steps
    for i, st in enumerate(groups):
        L.append("0 // STEP %d : %s" % (i + 1, st["title"]))
        for p in st["parts"]:
            x = (p["z"] + p["d"] / 2) * STUD; z = -(p["x"] + p["w"] / 2) * STUD; y = y_top(p)
            rot = p.get("rot") or ("1 0 0 0 1 0 0 0 1" if p["d"] >= p["w"] else "0 0 1 0 1 0 -1 0 0")
            L.append("1 %d %g %g %g %s %s.dat" % (p["colour"], x, y, z, rot, p["part"]))
        L.append("0 STEP")
    open(path, "w").write("\n".join(L) + "\n")
