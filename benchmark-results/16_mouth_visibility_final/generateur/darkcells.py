"""Which solid cells give the dark pixels seen in the cavity region from a camera (V8.2 model)? usage: darkcells.py <mesh> <az> <el> <pre.npz>"""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import visibility3d as V
from scipy import ndimage
mesh, az, el, pre = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
D = json.load(open("proto/v8/details.json"))["details"]; cells, occ = V.pocket_cells(pre); pk = V.keep_mouth_3d(occ, cells, D)
cav = {(x, y, z) for (x, z), ys in pk.items() for y in ys}
cdil = set((x + a, y + b, z + c) for (x, y, z) in cav for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1))
arr = np.array(sorted(cav)); lo = (arr.min(0) - 3) * np.array([8, 3.2, 8]); hi = (arr.max(0) + 4) * np.array([8, 3.2, 8]); lo3 = np.array([lo[0], lo[1], -hi[2]]); hi3 = np.array([hi[0], hi[1], -lo[2]])
Vt, Ft, FC, FN = V.load_mesh(mesh, lo3, hi3); cam = V.basis(az, el); c, r, u = cam
corners = np.array([[x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)], float)
cp = np.array([[(q[0] + cc[0]) * 8, (q[1] + cc[1]) * 3.2, -(q[2] + cc[2]) * 8] for q in cav for cc in corners]); pr, pu = cp @ r, cp @ u; win = (pr.min() - 6, pr.max() + 6, pu.min() - 6, pu.max() + 6)
depth, fid = V.raster(Vt, Ft, FC, FN, cam, lo3, hi3, win); hit = fid >= 0; ii = np.where(hit); f = fid[hit]; col = FC[f]; nrm = FN[f] * np.sign(FN[f] @ c)[:, None]
xs = (ii[1] + .5) / V.S + win[0]; ys = (ii[0] + .5) / V.S + win[2]; pts = np.outer(xs, r) + np.outer(ys, u) + np.outer(depth[hit], c)
cl = V.cell_of(pts + 1.2 * nrm); incav = np.array([tuple(t) in cdil for t in cl]); cls = V.classify_rgb(col)
dark = incav & (cls == "sombre"); inner = V.cell_of(pts - 0.8 * nrm)
d = np.load(pre); G = d["grid"]
from collections import Counter
cnt = Counter(tuple(t) for t in inner[dark]); print("pixels sombres", int(dark.sum()), "cellules distinctes", len(cnt))
dist = lambda q: min(abs(q[0] - a) + abs(q[1] - b) + abs(q[2] - cc) for (a, b, cc) in cav)
rows = []
for q, n in cnt.most_common(40):
    rows.append((q, n, int(G[q]) if all(0 <= q[i] < G.shape[i] for i in range(3)) else None, dist(q)))
print("cellule, pixels, couleur grille (pre-LCM), distance manhattan a la cavite"); [print(r) for r in rows[:25]]
print("part des pixels sombres par distance:", Counter(dist(q) for q, n in cnt.items() for _ in range(n)).most_common())

inb=np.array([all(0<=q[i]<G.shape[i] for i in range(3)) for q in map(tuple,inner[dark])])
gv=np.array([int(G[tuple(q)]) if ok else -2 for q,ok in zip(map(tuple,inner[dark]),inb)])
print("pixels sombres : cellule portee par une piece d'oreille/oeil (grille creusee, valeur -1):", round(float((gv==-1).mean()),3), "| cellule du corps noire (0):", round(float((gv==0).mean()),3), "| cellule du corps autre couleur:", round(float(((gv>0)).mean()),3))
tot=int((incav&(cls!="x")).sum()); print("part des pixels de la zone qui sont des pieces d'oreille/oeil (grille creusee):", round(float(np.mean([int(G[tuple(q)])==-1 if all(0<=q[i]<G.shape[i] for i in range(3)) else False for q in map(tuple,inner[incav])])),3), " pixels zone", int(incav.sum()))
