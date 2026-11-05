#!/usr/bin/env python3
"""What do the articulation points cut off ? usage: ap_inspect.py FOLDER : histogram of (AP part type/region -> cut-off parts types/regions, number of supports of the cut parts)"""
import json, os, pickle, subprocess, sys, tempfile
from collections import Counter, defaultdict
import networkx as nx
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "20_portable_engine", "engine")); from _paths import LDRAW, RB_DB
f = sys.argv[1]; P = json.load(open(f + "/parts.json")); order = []
for y in sorted({p["y"] for p in P}): order += [p for p in P if p["y"] == y]
tmp = tempfile.mkdtemp(); pk = tmp + "/d.pkl"
subprocess.run([sys.executable, os.path.join(HERE, "..", "..", "20_portable_engine", "engine", "validate_v4.py"), "--ldr", f + "/diorama.ldr", "--ldraw", LDRAW, "--rbdb", RB_DB, "--out", tmp, "--name", "map", "--dump", pk], check=True, capture_output=True)
d = pickle.load(open(pk, "rb")); n = len(order); G = nx.Graph(); G.add_nodes_from(range(n)); ground = set(d["ground"])
for (i, j, a, st) in d["edges"]: G.add_edge(i, j)
ap = set(nx.articulation_points(G)); H0 = G
def lost(i):
    H = G.copy(); H.remove_node(i); seen = set(g for g in ground if g != i); stack = list(seen)
    while stack:
        u = stack.pop()
        for v in H[u]:
            if v not in seen: seen.add(v); stack.append(v)
    return [v for v in H if v not in seen]
cnt = Counter(); ex = []
for i in sorted(ap):
    if order[i]["y"] == 0: continue
    L = lost(i)
    if not L: continue
    o = order[i]; key = (o["region"].split("_")[0], o["part"], o["y"], "leafs" if len(L) == 1 else "casc")
    cnt[key] += 1
    if len(ex) < 12 and len(L) > 1 and o["region"].startswith("sea"): ex.append((o["part"], o["y"], [(order[v]["part"], order[v]["y"], order[v]["region"][:12]) for v in L[:6]]))
for k, v in cnt.most_common(25): print(v, k)
for e in ex: print(e)
