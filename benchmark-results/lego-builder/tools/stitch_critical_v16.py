#!/usr/bin/env python3
"""Sprint V16 closure : repair REAL carrying weaknesses without touching the visible surface.
A critical piece = an articulation point (hidden single-plate-thick strata piece) whose removal cuts >= MIN parts off the baseplate. It is split in two plates of the SAME colour along a seam chosen so the pieces above
straddle the seam : the union of the geometry is identical (nothing visible changes, same colour), the weight no longer hangs on one piece. Candidates are evaluated on the real joint graph (studs are assigned to the side where they are) ; a split is kept only if it
strictly reduces the worst cut of the two halves. Pure post-processing of an LDraw file ; no engine change.
usage : stitch_critical_v16.py DUMP.pkl IN.ldr OUT.ldr REPORT.json [--min-cut 4]   (env LEGO_ENGINE_HOME for the availability table)"""
import json, os, pickle, sys, collections
import numpy as np
E1 = os.environ["LEGO_ENGINE_HOME"]; MAPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "maps-engine-v03", "style_fidelity_v062")
sys.path.insert(0, MAPS); from tiler import PLATES; from scene import PAIRS
a = sys.argv[1:]; dump, ldr_in, ldr_out, rep = a[:4]; MIN = int(a[a.index("--min-cut") + 1]) if "--min-cut" in a else 4
d = pickle.load(open(dump, "rb")); P = d["parts"]; n = len(P); ground = set(d["ground"])
lo = np.array([p["lo"] for p in P]); hi = np.array([p["hi"] for p in P]); num = [p["num"] for p in P]; bot = hi[:, 1]
adj = collections.defaultdict(set); E = collections.defaultdict(dict)
for (i, j, area, studs) in d["edges"]: adj[i].add(j); adj[j].add(i); E[i][j] = studs; E[j][i] = studs
CAT = {v: k for k, v in PLATES.items()}
def cut(adjf, k, N):
    seen = {g for g in ground if g != k}; st = list(seen)
    while st:
        u = st.pop()
        for v in adjf(u):
            if v != k and v not in seen: seen.add(v); st.append(v)
    return N - 1 - len(seen) if k < N else None
# only the pieces that matter : articulation points with a real cut
import networkx as nx
G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from((i, j) for i in adj for j in adj[i] if i < j)
crit = []
for k in nx.articulation_points(G):
    if k in ground or bot[k] >= 0 or num[k] + ".dat" == "" : continue
    c = cut(lambda u: adj[u], k, n)
    if c >= MIN: crit.append((c, k))
crit.sort(reverse=True); fixes = {}; skipped = collections.Counter()
for c0, k in crit:
    if num[k] not in CAT or int(round(hi[k, 1] - lo[k, 1])) != 8: skipped["not a one-plate catalogued plate"] += 1; continue
    col = int(P[k]["c"]); nx_ = int(round((hi[k, 0] - lo[k, 0]) / 20)); nz_ = int(round((hi[k, 2] - lo[k, 2]) / 20)); best = None
    for axis, size in ((0, nx_), (2, nz_)):
        for s in range(1, size):
            dims = [(s, nz_), (size - s, nz_)] if axis == 0 else [(nx_, s), (nx_, size - s)]
            parts = [PLATES.get((max(w, dd), min(w, dd))) for (w, dd) in dims]
            if None in parts or any(PAIRS.get(p, {}).get(str(col), 0) < 1 for p in parts): continue
            cutpos = lo[k, axis] + 20 * s; side = {}
            for nb, studs in E[k].items():
                for (pos, nrm) in studs: side.setdefault(nb, set()).add(0 if pos[axis] < cutpos else 1)
            A1, A2 = n, n + 1                                       # virtual ids
            def adjf(u, side=side, k=k, A1=A1, A2=A2):
                if u == A1: return [nb for nb, sd in side.items() if 0 in sd]
                if u == A2: return [nb for nb, sd in side.items() if 1 in sd]
                r = set(adj[u]); 
                if k in r:
                    r.discard(k); sd = side.get(u, set())
                    if 0 in sd: r.add(A1)
                    if 1 in sd: r.add(A2)
                return r
            # removal of each half : count parts cut off (graph has n+2 ids, k left isolated and unreachable -> excluded)
            def cutv(x):
                seen = {g for g in ground}; st = list(seen)
                while st:
                    u = st.pop()
                    for v in adjf(u):
                        if v != x and v not in seen: seen.add(v); st.append(v)
                return (n + 2) - 1 - 1 - len(seen - {k}) if False else sum(1 for q in list(range(n)) + [A1, A2] if q not in (k, x) and q not in seen)
            c1, c2 = cutv(A1), cutv(A2); sc = max(c1, c2)
            if best is None or (sc, c1 + c2) < best[:2]: best = (sc, c1 + c2, axis, s, parts, dims)
    if best and best[0] < c0: fixes[k] = dict(before=c0, after=best[0], axis="x" if best[2] == 0 else "z", seam_studs=best[3], part=num[k], colour=col, parts=best[4], dims=best[5])
    else: skipped["no split reduces the cut"] += 1
# ---- rewrite the LDraw file : parts are in the same order as the dump
lines = open(ldr_in).read().split("\n"); idx = [i for i, l in enumerate(lines) if l.startswith("1 ")]; assert len(idx) == n, (len(idx), n)
R90 = "0 0 1 0 1 0 -1 0 0"
for k, f in fixes.items():
    L = lines[idx[k]].split(); col = L[1]; ox, oy, oz = float(L[2]), float(L[3]), float(L[4]); axis = 0 if f["axis"] == "x" else 2; new = []
    x0, x1, z0, z1 = lo[k, 0], hi[k, 0], lo[k, 2], hi[k, 2]; s = f["seam_studs"] * 20
    boxes = [(x0, x0 + s, z0, z1), (x0 + s, x1, z0, z1)] if axis == 0 else [(x0, x1, z0, z0 + s), (x0, x1, z0 + s, z1)]
    for (bx0, bx1, bz0, bz1), part in zip(boxes, f["parts"]):
        wx, wz = (bx1 - bx0) / 20, (bz1 - bz0) / 20; M = "1 0 0 0 1 0 0 0 1" if wx >= wz else R90
        new.append("1 %s %g %g %g %s %s.dat" % (col, (bx0 + bx1) / 2, oy, (bz0 + bz1) / 2, M, part))
    lines[idx[k]] = "\n".join(new)
open(ldr_out, "w").write("\n".join(lines))
json.dump(dict(pieces_in=n, critical_min_cut=MIN, critical_found=len(crit), fixed=len(fixes), skipped=dict(skipped), pieces_out=n + len(fixes), fixes={str(k): v for k, v in fixes.items()}), open(rep, "w"), indent=1)
print(json.dumps(dict(critical_found=len(crit), fixed=len(fixes), skipped=dict(skipped), pieces_out=n + len(fixes))))
