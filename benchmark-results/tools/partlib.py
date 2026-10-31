"""Shape data of real LDraw parts, measured from the official geometry (no hand-made profiles).

For every part: footprint in studs (nx along local X, nz along local Z), height in plates, a fine solid mask
(K x K sub-columns per stud, KY sub-layers per plate) obtained by casting vertical rays through the part mesh,
the cells carrying a stud on top, and the cells that can receive studs from below.
LDraw local frame: -Y is up, the part origin is at the top of its body for standard bricks/plates/slopes.
"""
import functools, os, re, sys
import numpy as np, trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ldr_expand import Lib

K, KY = 4, 4                       # sub-samples per stud (x, z) and per plate (y)
LDU_STUD, LDU_PLATE = 20.0, 8.0
LDRAW = os.environ.get("LDRAW", os.path.expanduser("~/bench/ldraw-parts-library/complete/ldraw"))
_lib = None

def lib():
    global _lib
    if _lib is None: _lib = Lib(LDRAW)
    return _lib

@functools.lru_cache(maxsize=None)
def part(num, inverted=None):
    T, _ = lib().geom(num + ".dat")
    V = T.reshape(-1, 3).astype(float)
    # top studs = upright stud primitives; their cylinders are removed from the body before measuring
    from studrefs import refs
    cand = [(b, o, o[1] - 4.0 * M[1, 1]) for b, o, M in refs(num + ".dat") if re.match(r"^stud(2a?|10|15|17a)?\.dat$", b) and M[1, 1] > 0]
    keep = np.ones(len(V), bool)
    for b, o, yt in cand:                               # remove each stud cylinder (from its top yt down to its base)
        d = np.hypot(V[:, 0] - o[0], V[:, 2] - o[2])
        keep &= ~((d < 6.5) & (V[:, 1] < o[1] + 0.1) & (V[:, 1] > yt - 0.2) & (V[:, 1] < yt + 4.2))
    # also remove studs pointing sideways (studs on side, brackets): their cylinders are not part of the body box
    for b, o, M in refs(num + ".dat"):
        if not re.match(r"^stud(2a?|10|15|17a)?\.dat$", b): continue
        ax = -M[:, 1]; sc = np.linalg.norm(ax)
        if sc < 1e-6 or abs(ax[1]) / sc > 0.5: continue
        ax = ax / sc; rel = V - o; along = rel @ ax; radial = np.linalg.norm(rel - np.outer(along, ax), axis=1)
        keep &= ~((radial < 6.5) & (along > -0.1) & (along < 4 * sc + 0.2))
    keep = keep.reshape(-1, 3).all(axis=1).repeat(3)
    body = V[keep]
    lo, hi = body.min(0), body.max(0)               # y: lo = top (most negative), hi = bottom
    top_studs = [o for b, o, yt in cand if abs(yt - (lo[1] - 4.0)) < 0.6]
    nx = int(round((hi[0] - lo[0]) / LDU_STUD)); nz = int(round((hi[2] - lo[2]) / LDU_STUD))
    nh = int(round((hi[1] - lo[1]) / LDU_PLATE))
    tri_keep = keep.reshape(-1, 3).all(axis=1)
    mesh = trimesh.Trimesh(V.reshape(-1, 3, 3)[tri_keep].reshape(-1, 3), np.arange(3 * tri_keep.sum()).reshape(-1, 3), process=True)
    try:
        from trimesh.ray.ray_pyembree import RayMeshIntersector
        rays = RayMeshIntersector(mesh)
    except Exception:
        rays = mesh.ray
    # fine columns
    xs = lo[0] + (np.arange(nx * K) + 0.5) * LDU_STUD / K
    zs = lo[2] + (np.arange(nz * K) + 0.5) * LDU_STUD / K
    X, Z = np.meshgrid(xs, zs, indexing="ij")
    org_top = np.c_[X.ravel(), np.full(X.size, lo[1] - 50.0), Z.ravel()]
    org_bot = np.c_[X.ravel(), np.full(X.size, hi[1] + 50.0), Z.ravel()]
    ytop = np.full(X.size, np.nan); ybot = np.full(X.size, np.nan)
    loc, ri, _ = rays.intersects_location(org_top, np.tile([0, 1.0, 0], (X.size, 1)), multiple_hits=True)
    for r in np.unique(ri):
        hy = loc[ri == r][:, 1]; hy = hy[hy >= lo[1] - 0.01]
        if len(hy): ytop[r] = hy.min()
    loc, ri, _ = rays.intersects_location(org_bot, np.tile([0, -1.0, 0], (X.size, 1)), multiple_hits=True)
    for r in np.unique(ri):
        hy = loc[ri == r][:, 1]; hy = hy[hy <= hi[1] + 0.01]
        if len(hy): ybot[r] = hy.max()
    inv = ("inverted" in title(num).lower()) if inverted is None else inverted
    # solid from top surface down to: the part bottom (hollow standard parts count as solid), or the sloped underside
    top = np.where(np.isnan(ytop), hi[1], ytop)
    bot = np.where(np.isnan(ybot), hi[1], ybot) if inv else np.full(X.size, hi[1])
    hplates_top = (hi[1] - top) / LDU_PLATE; hplates_bot = (hi[1] - bot) / LDU_PLATE
    nyf = nh * KY
    yc = (np.arange(nyf) + 0.5) / KY                # sub-layer centres in plates above the part bottom
    solid = (yc[None, :] <= hplates_top[:, None]) & (yc[None, :] >= hplates_bot[:, None])
    solid = solid.reshape(nx * K, nz * K, nyf).transpose(0, 2, 1)   # (x, y, z), y up from bottom
    studs = {(int(np.clip((o[0] - lo[0]) // LDU_STUD, 0, nx - 1)), int(np.clip((o[2] - lo[2]) // LDU_STUD, 0, nz - 1))) for o in top_studs}
    # receptors: cells whose underside reaches the part bottom (all cells for standard parts)
    hb = hplates_bot.reshape(nx * K, nz * K)
    recv = {(i, j) for i in range(nx) for j in range(nz) if np.median(hb[i * K:(i + 1) * K, j * K:(j + 1) * K]) < 0.25}
    return dict(num=num, title=title(num), nx=nx, nz=nz, nh=nh, lo=lo, hi=hi, solid=solid, studs=frozenset(studs),
                recv=frozenset(recv), fill=float(solid.mean()))

def title(num):
    p = lib().resolve(num + ".dat")
    return open(p, encoding="utf-8", errors="replace").readline()[2:].strip()

def rot_y(r):
    """r quarter turns about the vertical axis, as an LDraw matrix (applied to local coords)."""
    c, s = [(1, 0), (0, 1), (-1, 0), (0, -1)][r % 4]
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], float)

def placed(num, r):
    """Shape of a part after r quarter turns, in grid axes (x, y-up, z)."""
    P = part(num); R = rot_y(r)
    # map local cell (i, j) -> rotated cell; do it with the corner transform
    corners = np.array([[x, z] for x in (P["lo"][0], P["hi"][0]) for z in (P["lo"][2], P["hi"][2])])
    w = np.c_[corners[:, 0], np.zeros(4), corners[:, 1]] @ R.T
    mn = w.min(0)
    def cell_map(i, j):
        c = np.array([P["lo"][0] + (i + 0.5) * LDU_STUD, 0, P["lo"][2] + (j + 0.5) * LDU_STUD]) @ R.T - mn
        return int(c[0] // LDU_STUD), int(c[2] // LDU_STUD)
    nxr, nzr = (P["nx"], P["nz"]) if r % 2 == 0 else (P["nz"], P["nx"])
    s = P["solid"]
    # rotate the fine mask with the same matrix as the LDraw line: map every fine column centre
    sol = np.zeros((nxr * K, s.shape[1], nzr * K), bool)
    for i in range(s.shape[0]):
        for j in range(s.shape[2]):
            c = np.array([P["lo"][0] + (i + 0.5) * LDU_STUD / K, 0, P["lo"][2] + (j + 0.5) * LDU_STUD / K]) @ R.T - mn
            sol[int(c[0] // (LDU_STUD / K)), :, int(c[2] // (LDU_STUD / K))] = s[i, :, j]
    studs = frozenset(cell_map(i, j) for i, j in P["studs"])
    recv = frozenset(cell_map(i, j) for i, j in P["recv"])
    return dict(num=num, r=r, nx=nxr, nz=nzr, nh=P["nh"], solid=sol, studs=studs, recv=recv, R=R, mn=mn, lo=P["lo"], hi=P["hi"])

def ldraw_line(colour, num, r, x0, y0, z0):
    """LDraw type-1 line placing the part so that its body box starts at grid cell (x0, y0, z0)."""
    Q = placed(num, r); P = part(num); R = Q["R"]
    corners = np.array([[x, y, z] for x in (P["lo"][0], P["hi"][0]) for y in (P["lo"][1], P["hi"][1]) for z in (P["lo"][2], P["hi"][2])]) @ R.T
    mn = corners.min(0)
    target = np.array([x0 * LDU_STUD, -(y0 + P["nh"]) * LDU_PLATE, z0 * LDU_STUD])
    o = target - mn
    m = " ".join(f"{v:g}" for v in R.ravel())
    return f"1 {colour} {o[0]:g} {o[1]:g} {o[2]:g} {m} {num}.dat"

if __name__ == "__main__":
    for n in sys.argv[1:]:
        P = part(n)
        prof = P["solid"].mean(axis=(2,))  # (x, y)
        print(f"{n:7s} {P['title'][:38]:38s} {P['nx']}x{P['nz']}x{P['nh']}pl fill={P['fill']:.2f} studs={sorted(P['studs'])} recv={sorted(P['recv'])}")
        colh = P["solid"].sum(axis=1) / KY      # height of solid per fine column (x, z)
        ax = 1 if P["nz"] > P["nx"] else 0
        print("        solid height along the long axis (plates):", np.round(colh.mean(axis=1 - ax), 2).tolist())
