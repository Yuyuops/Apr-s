"""V8.2: are the recoloured cells really visible from outside? Depth-buffer test (same rasteriser as visibility.py) of the exposed faces of a set of cells.
usage: cellvis.py <mesh.glb> <cells.pkl (dict recolour or list)> <post-grid.npz> <camera name> <az> <el> <out.json>"""
import json, os, pickle, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import visibility as V
V.S = 4.0
mesh, cp, npz, name, az, el, out = sys.argv[1:8]; az, el = float(az), float(el)
L = pickle.load(open(cp, "rb")); cells = list(L["recolour"].keys()) if isinstance(L, dict) and "recolour" in L else list(L)
d = np.load(npz); G = d["grid"].astype(int); F = d["fine"]; K = int(d["k"]); NX, NY, NZ = G.shape
occ = (G >= 0) & (F.reshape(NX, K, NY, K, NZ, K).mean(axis=(1, 3, 5)) >= 0.5)
if os.environ.get("ZONE"):                         # restrict to the mouth neighbourhood (cell indices): iy 74-96, ix 14-28, iz 10-30
    cells = [c for c in cells if 74 <= c[1] <= 96 and 14 <= c[0] <= 28 and 10 <= c[2] <= 30]
arr = np.array(cells); lo = (arr.min(0) - 3) * np.array([8, 3.2, 8]); hi = (arr.max(0) + 4) * np.array([8, 3.2, 8])
lo3 = np.array([lo[0], lo[1], -hi[2]]); hi3 = np.array([hi[0], hi[1], -lo[2]])
Vt, Ft, FC, FN = V.load_mesh(mesh, lo3 - 20, hi3 + 20)
cam = V.basis(az, el); c, r, u = cam
pts = []; owner = []
dirs = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
for ci, (x, y, z) in enumerate(cells):
    for dx, dy, dz in dirs:
        q = (x + dx, y + dy, z + dz)
        if 0 <= q[0] < NX and 0 <= q[1] < NY and 0 <= q[2] < NZ and occ[q]: continue
        n = np.array([dx, dy, -dz], float)                                  # mm frame: z is negated
        ctr = np.array([(x + .5) * 8, (y + .5) * 3.2, -(z + .5) * 8]) + n * np.array([4, 1.6, 4])
        t1 = np.cross(n, [0, 1, 0]) if abs(n[1]) < .5 else np.array([1, 0, 0]); t2 = np.cross(n, t1)
        ext = np.array([4, 1.6, 4])
        for a in (-.6, 0, .6):
            for b in (-.6, 0, .6):
                p = ctr + a * t1 * ext + b * t2 * ext + n * 0.3
                pts.append(p); owner.append(ci)
pts = np.array(pts); owner = np.array(owner)
cand = np.array([np.dot(((pts[i] - 0) * 0 + 1), [0, 0, 0]) for i in range(1)])  # placeholder (no-op)
pr, pu = pts @ r, pts @ u; win = (pr.min() - 4, pr.max() + 4, pu.min() - 4, pu.max() + 4)
depth, fid = V.raster(Vt, Ft, FC, FN, cam, lo3 - 20, hi3 + 20, win)
H, W = depth.shape; xi = ((pr - win[0]) * V.S).astype(int); yi = ((pu - win[2]) * V.S).astype(int)
ok = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
pd = pts @ c; hid = np.ones(len(pts), bool)
# a sample is visible if its face looks to the camera and nothing nearer covers its pixel (3x3 neighbourhood minimum of the depth map)
from scipy import ndimage
dm = ndimage.maximum_filter(depth, size=3)
facing = np.array([0.0] * len(pts))
nrm = np.repeat(np.array([[dx, dy, -dz] for (dx, dy, dz) in dirs], float), 1, axis=0)
vis = np.zeros(len(pts), bool)
for i in range(len(pts)):
    if not ok[i]: continue
    vis[i] = pd[i] >= dm[yi[i], xi[i]] - 0.8
# a face must also look towards the camera: recompute owner normal from sample offsets (cell centre -> sample)
cen = np.array([[(x + .5) * 8, (y + .5) * 3.2, -(z + .5) * 8] for (x, y, z) in cells])
nn = pts - cen[owner]; nn = nn / np.linalg.norm(nn, axis=1, keepdims=True)
front = (nn @ c) > 0.05
vis &= front
cell_vis = np.zeros(len(cells), bool); cell_vis[np.unique(owner[vis])] = True
col = {k: v for k, v in pickle.load(open(cp, "rb"))["recolour"].items() if k in set(cells)} if isinstance(L, dict) and "recolour" in L else {}
res = dict(camera=name, cellules=len(cells), visibles=int(cell_vis.sum()), cachees=int((~cell_vis).sum()))
if col:
    for k, nm in ((0, "sombre"), (4, "rouge"), (14, "peau")):
        idx = [i for i, cl in enumerate(cells) if col[cl] == k]; res[nm] = dict(total=len(idx), visibles=int(sum(cell_vis[i] for i in idx)))
json.dump(res, open(out, "w"), indent=1); print(res)
