"""Class grid -> heights -> layers -> plates -> backing -> LDraw. Heights come from a DECLARED artistic style (styles/*.json), never from geographic data."""
import json, os
from collections import Counter
import numpy as np
from .common import PLATES, STUD, PLATE
from . import palette as PAL, tiling as T

def heights(grid, classes, style, mode):
    lv = style["levels"]; h = np.zeros(grid.shape, int)
    for i, nm in enumerate(classes):
        h[grid == i] = lv.get(nm, lv.get("autre", 1)) if mode == "2.5d" else (style.get("flat_2d_level", 1) * 0)
    return h

def exposed_side(h, k):
    """(n,n) bool : the cell has a free side at layer k (a 4-neighbour column does not reach layer k, or the board edge)"""
    n = h.shape[0]; e = np.zeros_like(h, bool); P = np.pad(h, 1, constant_values=-1)
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)): e |= P[1 + dx:1 + dx + n, 1 + dz:1 + dz + n] < k
    return e

def backing(n, colour):
    """two staggered layers of big plates (8x8 / 4x8 / 4x4), the joints of the second layer fall in the middle of the plates of the first"""
    out = []
    for gx in range(0, n, 8):
        for gz in range(0, n, 8): out.append(dict(x=gx, z=gz, w=8, d=8, colour=colour, layer="B1"))
    xs = [(0, 4)] + [(a, a + 8) for a in range(4, n - 4, 8)] + [(n - 4, n)]
    for (x0, x1) in xs:
        for (z0, z1) in xs: out.append(dict(x=x0, z=z0, w=x1 - x0, d=z1 - z0, colour=colour, layer="B2"))
    return out

def build(cg, style, mode="2.5d", seed=0, tries=8):
    grid, classes, n = cg["grid"], cg["classes"], cg["grid"].shape[0]
    col, ncand = PAL.assign(cg["colour"], {nm: int((grid == i).sum()) for i, nm in enumerate(classes)}); ccode = np.array([col[nm]["code"] for nm in classes]); top_colour = ccode[grid]
    h = heights(grid, classes, style, mode); K = int(h.max()); layers = []; below = -np.ones((n, n), int); pid = 0
    bcol = PAL.backing_colour(); parts = []
    for p in backing(n, bcol):
        pid += 1; p["id"] = pid; p["region"] = "dos"; p["level"] = -2 if p["layer"] == "B1" else -1; parts.append(p)
    back_ids = {1: [p for p in parts if p["layer"] == "B2"]}
    for k in range(K + 1):
        fixed = -np.ones((n, n), int); wild = np.zeros((n, n), bool); has = h >= k; ex = exposed_side(h, k)
        top = h == k; fixed[top] = top_colour[top]; mid = has & ~top
        fixed[mid & ex] = top_colour[mid & ex]; wild[mid & ~ex] = True
        def hidden(x, z, w, d, part, _k=k):
            cnt = Counter(top_colour[x:x + w, z:z + d].ravel().tolist())
            for c, _ in cnt.most_common():
                if PAL.available(part, int(c)): return c
            for c in (ccode.tolist() + [bcol]):
                if PAL.available(part, int(c)): return c
            raise RuntimeError("no colour for hidden plate")
        pl = T.best_tiling(fixed, wild, below, hidden, tries=tries, seed=seed + k)
        ids = -np.ones((n, n), int)
        for p in pl:
            pid += 1; p["id"] = pid; p["level"] = k; p["layer"] = "L%d" % k
            sub = grid[p["x"]:p["x"] + p["w"], p["z"]:p["z"] + p["d"]]; vis = h[p["x"]:p["x"] + p["w"], p["z"]:p["z"] + p["d"]] == k
            reg = Counter((sub[vis] if vis.any() else sub).ravel().tolist()).most_common(1)[0][0]; p["region"] = classes[reg]
            ids[p["x"]:p["x"] + p["w"], p["z"]:p["z"] + p["d"]] = pid; parts.append(p)
        layers.append(pl); below = ids
    for p in parts:
        L, S = max(p["w"], p["d"]), min(p["w"], p["d"]); p["part"] = PLATES[(L, S)]; p["name_size"] = "%dx%d" % (L, S)
    return dict(parts=parts, heights=h, colours=col, ncand=ncand, backing_colour=bcol, levels=K + 1, n=n, mode=mode)

def y_top(p):
    """LDraw y of the plate origin (top face) ; B1 sits on y=0 plane, then B2, then relief layers"""
    return -8 * (1 if p["level"] == -2 else 2 if p["level"] == -1 else 3 + p["level"])

def write_ldr(model, path, name, steps=None):
    P = model["parts"]; n = model["n"]; L = ["0 %s" % name, "0 Name: %s" % os.path.basename(path), "0 Author: LEGO Maps engine 2 V0", "0 !LICENSE Original test map (fictional), generated file",
                                          "0 // %dx%d studs, %.1f mm ; levels=%d ; mode=%s" % (n, n, n * 8, model["levels"], model["mode"])]
    order = sorted(P, key=lambda p: (p["level"], p["id"])) if steps is None else [p for st in steps for p in st["parts"]]
    cur = None
    for p in order:
        key = (p["level"], p["region"]) if steps is None else None
        if steps is not None:
            pass
        x = (p["x"] + p["w"] / 2) * STUD; z = (p["z"] + p["d"] / 2) * STUD; y = y_top(p)
        rot = "1 0 0 0 1 0 0 0 1" if p["w"] >= p["d"] else "0 0 1 0 1 0 -1 0 0"
        L.append("1 %d %g %g %g %s %s.dat" % (p["colour"], x, y, z, rot, p["part"]))
    L.append("0 STEP"); open(path, "w").write("\n".join(L) + "\n")
