#!/usr/bin/env python3
"""Sprint V16 closure : classify the pieces connected by ONE stud into three risk classes with the SAME definitions on any model (needs the validate_v4 --dump pickle).
 C1 carrying            : one stud down AND removing it cuts >= 1 piece off the baseplate.
 C2 decorative captured : one stud down, nothing is cut off, and no side neighbour column is lower than its top (flush : it can only be lifted vertically).
 C3 decorative exposed  : one stud down, nothing is cut off, at least one side faces a lower surface (protrudes by >= 1 plate : can be knocked or pulled sideways).
usage : structural_classify_v16.py DUMP.pkl OUT.json   (units : LDU ; stud = 20, plate = 8)"""
import json, pickle, sys, collections
import numpy as np
d = pickle.load(open(sys.argv[1], "rb")); out = sys.argv[2]
P = d["parts"]; n = len(P); ground = set(d["ground"])
lo = np.array([p["lo"] for p in P]); hi = np.array([p["hi"] for p in P]); mass = np.array([p["mass"] for p in P]); num = [p["num"] for p in P]
top = lo[:, 1]; bot = hi[:, 1]                                   # y points down : top is the smaller value
down = collections.Counter(); up = collections.Counter(); adj = collections.defaultdict(list)
for (i, j, area, studs) in d["edges"]:
    adj[i].append(j); adj[j].append(i)
    a, b = (i, j) if bot[i] > bot[j] else (j, i)                  # a = lower piece
    down[b] += len(studs); up[a] += 1
x0 = min(lo[:, 0].min(), 0); z0 = lo[:, 2].min()
def cells(i):
    return [(x, z) for x in range(int(round((lo[i, 0] - x0) / 20)), int(round((hi[i, 0] - x0) / 20))) for z in range(int(round((lo[i, 2] - z0) / 20)), int(round((hi[i, 2] - z0) / 20)))]
surf = {}
for i in range(n):
    for c in cells(i): surf[c] = min(surf.get(c, 1e9), top[i])    # highest surface of the column
def cut_if_removed(k):
    seen = {g for g in ground if g != k}; st = list(seen)
    while st:
        u = st.pop()
        for v in adj[u]:
            if v != k and v not in seen: seen.add(v); st.append(v)
    return [i for i in range(n) if i != k and i not in seen]
rows = []
for i in range(n):
    if i in ground or down[i] != 1 or bot[i] >= 0: continue       # bot >= 0 = baseplate layer
    cut = cut_if_removed(i) if up[i] else []
    own = set(cells(i)); ring = {(x + dx, z + dz) for (x, z) in own for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))} - own
    protrude = max([(surf.get(c, -1e9) * -1 + top[i]) * -1 for c in ring if c in surf] + [0])   # plates (LDU) by which this piece rises above the lowest side column
    protrude = max([(surf[c] - top[i]) for c in ring if c in surf] + [0])
    cls = "C1_carrying" if cut else ("C3_decorative_exposed" if protrude >= 8 else "C2_decorative_captured")
    cx = (lo[i, 0] + hi[i, 0]) / 2 / 20 - x0 / 20; cz = (lo[i, 2] + hi[i, 2]) / 2 / 20 - z0 / 20
    rows.append(dict(i=i, part=num[i], colour=int(P[i]["c"]), cls=cls, cut=len(cut), cut_mass_g=round(float(mass[cut].sum()), 1) if cut else 0.0, col=round(float(cx), 1), row=round(float(cz), 1), layer_plates=int(round(-top[i] / 8)), protrude_plates=round(protrude / 8, 1)))
import networkx as nx
G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from((i, j) for (i, j, a, st) in d["edges"])
art = [i for i in nx.articulation_points(G) if i not in ground and bot[i] < 0]; worst = []
for k in art:
    c = cut_if_removed(k)
    if c: worst.append((len(c), num[k], int(P[k]["c"]), k, round(float(mass[c].sum()), 1)))
worst.sort(reverse=True)
res = dict(pieces=n, one_stud=len(rows), articulation_points=len(art), worst_isolated_failure_parts=worst[0][0] if worst else 0, articulation_cut_ge_8=sum(1 for w in worst if w[0] >= 8), articulation_cut_ge_4=sum(1 for w in worst if w[0] >= 4), worst10=worst[:10]); by = collections.defaultdict(list)
for r in rows: by[r["cls"]].append(r)
res["classes"] = {}
for k in ("C1_carrying", "C2_decorative_captured", "C3_decorative_exposed"):
    L = by.get(k, [])
    res["classes"][k] = dict(count=len(L), pct_of_pieces=round(100 * len(L) / n, 2), pct_of_one_stud=round(100 * len(L) / max(1, len(rows)), 1), parts=collections.Counter(r["part"] for r in L).most_common(8),
        max_cut=max([r["cut"] for r in L] + [0]), cut_ge_4=sum(1 for r in L if r["cut"] >= 4), cut_ge_8=sum(1 for r in L if r["cut"] >= 8), cut_mass_g_total=round(sum(r["cut_mass_g"] for r in L), 1))
res["rows"] = rows
json.dump(res, open(out, "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "rows"}))
