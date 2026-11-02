import sys, json, time
sys.path.insert(0, "/root/bench/proto/v91"); sys.path.insert(0, "/root/bench/proto/v9")
import numpy as np, networkx as nx
from collections import defaultdict, Counter
import notice_plan as N, seq as S
model = sys.argv[1]
P = N.parse(model); G = N.build_graph(P)
subs = defaultdict(list)
ALL = len(sys.argv) > 2 and sys.argv[2] == "--all"
for p in P:
    if ALL: subs["all"].append(p["i"])
    elif p["sub"]: subs[p["sub"]].append(p["i"])
out = {}
for sub, ids in subs.items():
    t = time.time()
    comps = sorted(nx.connected_components(G.subgraph(ids)), key=lambda c: -len(c))
    for ci, comp in enumerate(comps):
        comp = sorted(comp)
        M0 = P[comp[0]]["M"]
        dirs = [np.array([0, -1.0, 0]), np.array([0, 1.0, 0])]
        axes = Counter()
        for u, v, d in G.subgraph(comp).edges(data=True):
            for (pt, a, o) in d["contacts"]: axes[tuple(np.round(a, 2))] += 1
        for a in axes: dirs += [np.array(a), -np.array(a)]
        # third axis of the ear frame and global axes
        dirs += [np.array(v, float) for v in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1))]
        sq = S.Sequencer(P, G, comp, dirs)
        items, stuck = S.plan(sq, comp, prefer=lambda i: P[i]["lo"][1])
        disc = sum(1 for x in items if not x[-1])
        sl = sum(1 for x in items if x[3] is not None)
        nunits = sum(1 for x in items if x[0] == "unit")
        print(sub, "comp", ci, len(comp), "parts; top-level items", len(items), "units", nunits, "stuck", stuck, "disconnected-steps", disc, "lift-slide", sl, "%.0fs" % (time.time() - t), flush=True)
        def ser(items):
            o = []
            for x in items:
                if x[0] == "part": o.append(dict(kind="part", ids=[int(x[1])], e=None if x[2] is None else [float(v) for v in x[2]], slide=None if x[3] is None else [float(v) for v in x[3]], conn=bool(x[4])))
                else: o.append(dict(kind="unit", ids=[int(i) for i in x[1]], e=None if x[2] is None else [float(v) for v in x[2]], slide=None if x[3] is None else [float(v) for v in x[3]], conn=bool(x[5]), inside=ser(x[4])))
            return o
        out[f"{sub}:{ci}"] = dict(stuck=[int(i) for i in stuck], n=len(comp), ids=[int(i) for i in comp], order=ser(items))
json.dump(out, open(sys.argv[3] if len(sys.argv) > 3 else "/root/bench/proto/v91/seq_result.json", "w"), indent=1)
