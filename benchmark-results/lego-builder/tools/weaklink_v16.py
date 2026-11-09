#!/usr/bin/env python3
"""Sprint V16 closure : stud-weighted weak links. The articulation count treats a 4x4 plate held by 16 studs like a piece held by 1. Here every articulation point A (cut group S, cut >= MIN parts) is scored by
  g = number of studs joining A to the NON-cut side (its clutch to the structure that reaches the baseplate) and load = mass of A + S (g).
WEAK = g <= 2 (a hand can pull it off) ; MEDIUM = 3..5 ; STRONG >= 6.   usage : weaklink_v16.py DUMP.pkl OUT.json [--min-cut 4]"""
import json, pickle, sys, collections
import numpy as np, networkx as nx
d = pickle.load(open(sys.argv[1], "rb")); out = sys.argv[2]; a = sys.argv; MIN = int(a[a.index("--min-cut") + 1]) if "--min-cut" in a else 4
P = d["parts"]; n = len(P); ground = set(d["ground"]); mass = np.array([p["mass"] for p in P]); bot = np.array([p["hi"][1] for p in P])
adj = collections.defaultdict(set); E = {}
for (i, j, area, studs) in d["edges"]: adj[i].add(j); adj[j].add(i); E[(i, j)] = len(studs); E[(j, i)] = len(studs)
G = nx.Graph(); G.add_edges_from((i, j) for i in adj for j in adj[i] if i < j); rows = []
for k in nx.articulation_points(G):
    if k in ground or bot[k] >= 0: continue
    seen = {g for g in ground if g != k}; st = list(seen)
    while st:
        u = st.pop()
        for v in adj[u]:
            if v != k and v not in seen: seen.add(v); st.append(v)
    S = [i for i in range(n) if i != k and i not in seen]
    if len(S) < MIN: continue
    g = sum(E[(k, j)] for j in adj[k] if j in seen); up = sum(E[(k, j)] for j in adj[k] if j not in seen)
    rows.append(dict(i=k, part=P[k]["num"], colour=int(P[k]["c"]), cut=len(S), load_g=round(float(mass[S].sum() + mass[k]), 1), studs_to_structure=g, studs_to_cut_group=up,
                     col=round(float((P[k]["lo"][0] + P[k]["hi"][0]) / 40), 1), row=round(float((P[k]["lo"][2] + P[k]["hi"][2]) / 40), 1), layer_plates=int(round(-P[k]["lo"][1] / 8))))
cls = lambda g: "WEAK(<=2)" if g <= 2 else ("MEDIUM(3-5)" if g <= 5 else "STRONG(>=6)")
c = collections.Counter(cls(r["studs_to_structure"]) for r in rows); res = dict(pieces=n, min_cut=MIN, critical=len(rows), by_clutch=dict(c), weak=[r for r in rows if r["studs_to_structure"] <= 2][:200],
    worst_weak=max([r["cut"] for r in rows if r["studs_to_structure"] <= 2] + [0]), min_clutch_among_cut_ge_8=min([r["studs_to_structure"] for r in rows if r["cut"] >= 8] + [999]))
json.dump(res, open(out, "w"), indent=1); print(json.dumps({k: v for k, v in res.items() if k != "weak"}))
