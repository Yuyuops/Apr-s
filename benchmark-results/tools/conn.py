"""Orientation-free connection data of LDraw parts, read from the official geometry.

For a part (local LDraw frame) returns:
  body box (lo, hi) without studs, fill fraction,
  studs: list of (base point, outward unit axis) for every external stud (top studs, studs on sides, bracket studs),
  receptors: list of (point on the receiving face, outward unit normal of that face) for every cell of the underside
             that can take a stud (from partlib: the underside reaches the bottom plane in that cell).
A joint exists in a model when a stud base of part A coincides with a receptor point of part B and the stud axis is
opposite to B's receiving-face normal. Works for any 90-degree orientation (SNOT, brackets, sideways sub-assemblies).
"""
import functools, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import partlib as PL
from studrefs import refs

STUD_RE = re.compile(r"^stud(2a?|10|15|17a)?\.dat$")

@functools.lru_cache(maxsize=None)
def part(num):
    T, _ = PL.lib().geom(num + ".dat")
    V = T.reshape(-1, 3).astype(float)
    cand = []
    for b, o, M in refs(num + ".dat"):
        if not STUD_RE.match(b): continue
        ax = -M[:, 1]; s = np.linalg.norm(ax)
        if s < 1e-6: continue
        cand.append((np.array(o, float), ax / s, s))
    # remove every stud cylinder (any axis) from the body
    keep = np.ones(len(V), bool)
    for o, ax, s in cand:
        rel = V - o; along = rel @ ax; radial = np.linalg.norm(rel - np.outer(along, ax), axis=1)
        keep &= ~((radial < 6.5) & (along > -0.1) & (along < 4 * s + 0.2))
    keep = keep.reshape(-1, 3).all(axis=1).repeat(3)
    body = V[keep]; lo, hi = body.min(0), body.max(0)
    studs = []
    for o, ax, s in cand:
        tip = o + 4 * s * ax
        inside = np.all(tip > lo + 0.5) and np.all(tip < hi - 0.5)
        if inside: continue                      # inner tube, not an external stud
        # external stud: its tip stands at least 3 LDU beyond the body face it points through; the joint point is the
        # stud centre on that face (hollow studs may start inside the body)
        k = int(np.argmax(np.abs(ax)))
        if abs(ax[k]) < 0.9: continue
        face = hi[k] if ax[k] > 0 else lo[k]
        if (tip[k] - face) * np.sign(ax[k]) < 3.0: continue
        base = np.array(o, float); base[k] = face
        studs.append((tuple(np.round(base, 3)), tuple(np.round(ax, 3))))
    # receptors: lattice cells of the bottom footprint (vertices on the bottom plane y = hi[1]); for inverted parts,
    # only the cells whose underside reaches the bottom plane (partlib ray measurement)
    P = PL.part(num)
    bv = body[np.abs(body[:, 1] - hi[1]) < 0.5]
    bx0, bx1 = 20 * np.round(bv[:, 0].min() / 20 * 2) / 2, 20 * np.round(bv[:, 0].max() / 20 * 2) / 2
    bz0, bz1 = 20 * np.round(bv[:, 2].min() / 20 * 2) / 2, 20 * np.round(bv[:, 2].max() / 20 * 2) / 2
    nx_, nz_ = max(1, int(round((bx1 - bx0) / 20))), max(1, int(round((bz1 - bz0) / 20)))
    inverted = "inverted" in PL.title(num).lower()
    rec = []
    if inverted:      # partial underside: use the cells measured by vertical rays (partlib), in partlib's own box
        for (ii, jj) in P["recv"]:
            rec.append(((round(P["lo"][0] + (ii + 0.5) * 20, 3), round(hi[1], 3), round(P["lo"][2] + (jj + 0.5) * 20, 3)), (0.0, 1.0, 0.0)))
        nx_ = nz_ = 0
    for i in range(nx_):
        for j in range(nz_):
            c = (round(bx0 + (i + 0.5) * 20, 3), round(hi[1], 3), round(bz0 + (j + 0.5) * 20, 3))
            if inverted:
                ii = int((c[0] - P["lo"][0]) // 20); jj = int((c[2] - P["lo"][2]) // 20)
                if (ii, jj) not in P["recv"]: continue
            rec.append((c, (0.0, 1.0, 0.0)))
    return dict(lo=lo, hi=hi, studs=studs, receptors=rec, fill=P["fill"], solid=P["solid"], plo=P["lo"], phi=P["hi"])

def world(num, M, o):
    """studs / receptors / body box of a placed part, world LDU"""
    P = part(num); M = np.asarray(M, float).reshape(3, 3); o = np.asarray(o, float)
    st = [(M @ np.array(p) + o, M @ np.array(a)) for p, a in P["studs"]]
    rc = [(M @ np.array(p) + o, M @ np.array(n)) for p, n in P["receptors"]]
    corners = np.array([[x, y, z] for x in (P["lo"][0], P["hi"][0]) for y in (P["lo"][1], P["hi"][1]) for z in (P["lo"][2], P["hi"][2])]) @ M.T + o
    return st, rc, corners.min(0), corners.max(0)

if __name__ == "__main__":
    for n in sys.argv[1:]:
        P = part(n)
        print(n, PL.title(n)[:40], "box", np.round(P["lo"], 1).tolist(), np.round(P["hi"], 1).tolist())
        print("   studs", P["studs"]); print("   receptors", P["receptors"])
