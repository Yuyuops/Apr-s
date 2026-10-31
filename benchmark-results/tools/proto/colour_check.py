"""visible cells of an LDR whose colour differs from the nearest original brickify surface cell"""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.expanduser("~/bench/tools")); import partlib as PL
from scipy.spatial import cKDTree
d = np.load(sys.argv[1]); G0 = d["grid"]; S0 = d["surface"].astype(bool) & (G0 >= 0)
C = -np.ones(G0.shape, int)
for l in open(sys.argv[2]):
    t = l.split()
    if len(t) < 15 or t[0] != "1": continue
    num = t[14].replace(".dat", ""); o = np.array(t[2:5], float); M = np.array(t[5:14], float).reshape(3, 3); P = PL.part(num)
    cs = np.array([[x, y, z] for x in (P["lo"][0], P["hi"][0]) for y in (P["lo"][1], P["hi"][1]) for z in (P["lo"][2], P["hi"][2])]) @ M.T + o
    mn, mx = cs.min(0), cs.max(0)
    C[int(round(mn[0]/20)):int(round(mx[0]/20)), int(round(-mx[1]/8)):int(round(-mn[1]/8)), int(round(mn[2]/20)):int(round(mx[2]/20))] = int(t[1])
occ = C >= 0; pad = np.pad(occ, 1); nb = np.zeros(occ.shape, int)
for dx, dy, dz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
    nb += ~pad[1+dx:1+dx+occ.shape[0], 1+dy:1+dy+occ.shape[1], 1+dz:1+dz+occ.shape[2]]
surf = occ & (nb > 0); si = np.argwhere(S0); q = np.argwhere(surf); _, j = cKDTree(si).query(q)
bad = int((C[tuple(q.T)] != G0[tuple(si[j].T)]).sum())
print(json.dumps(dict(visible_cells=len(q), visible_colour_changes=bad)))
