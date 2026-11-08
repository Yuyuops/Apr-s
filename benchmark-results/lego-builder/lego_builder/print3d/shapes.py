"""B2 (Sprint V13) : shape-aware modules. Non-rectangular parts (slopes, round tiles, quarter rounds, cones...) are NOT replaced by their bounding box any more : the convex hull of the real LDraw part
geometry (studs, tubes and holes ignored) is placed at its real position and merged into the module body. Convex hull = exact for slopes, cylinders, quarter rounds, wedges ; it FILLS concavities
(arches, hollow parts), which is declared. EXPERIMENTAL : nothing here is validated in Bambu Studio or on a printer."""
import os
from functools import lru_cache
from pathlib import Path
import numpy as np
import manifold3d as M
from .common import LDU
_SKIP = ("stud", "box", "peghole", "connhole", "axlehol", "ring", "stug")        # primitives that are studs / tubes / holes (not part of the outer volume)
def _ldraw_root():
    r = os.environ.get("LEGO_LDRAW") or str(Path(os.environ.get("LEGO_DEPS", "")) / "ldraw-parts-library" / "complete" / "ldraw")
    return Path(r)
@lru_cache(maxsize=None)
def _find(name):
    root = _ldraw_root(); n = name.lower().replace("\\", "/")
    for d in ("parts", "p", "parts/s", "p/48", "p/8"):
        f = root / d / n
        if f.exists(): return f
    return None
@lru_cache(maxsize=None)
def part_points(part, depth=0):
    """vertices (LDU, LDraw axes) of the part outer geometry (triangles / quads, sub-files recursively, stud primitives skipped)."""
    f = _find(part if part.endswith(".dat") else part + ".dat"); pts = []
    if f is None or depth > 8: return np.zeros((0, 3))
    for l in open(f, errors="replace"):
        t = l.split()
        if not t: continue
        if t[0] in ("3", "4"):
            n = 3 if t[0] == "3" else 4; pts.append(np.array([float(x) for x in t[2:2 + 3 * n]]).reshape(n, 3))
        elif t[0] == "1" and len(t) >= 15:
            sub = t[14].lower().replace("\\", "/")
            if any(sub.split("/")[-1].startswith(s) or sub.split("/")[-1].startswith("4-4" + s) for s in _SKIP) or sub.split("/")[-1].startswith(("stud", "2-4", "1-4")) and "cyli" in sub and False: continue
            m = np.array([float(x) for x in t[5:14]]).reshape(3, 3); o = np.array([float(x) for x in t[2:5]]); sp = part_points(sub, depth + 1)
            if len(sp): pts.append(sp @ m.T + o)
    return np.vstack(pts) if pts else np.zeros((0, 3))
def hull_body(part, pos, rot, P):
    """Manifold of the convex hull of the placed part, in module coordinates (mm) : X = x*0.4, Y = z*0.4, Z = -y*0.4 (LDraw y is down)."""
    pts = part_points(part)
    if len(pts) < 4: return None
    w = pts @ np.asarray(rot).T + np.asarray(pos); w = np.stack([w[:, 0] * LDU, w[:, 2] * LDU, -w[:, 1] * LDU], 1)
    try:
        h = M.Manifold.hull_points(w.astype(float))
    except Exception: return None
    return h if h.volume() > 1.0 else None
