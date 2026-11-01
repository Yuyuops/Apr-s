"""Keep, in the ear sub-assembly, only the pieces linked (inside the sub-assembly) to the brackets; others are removed
and counted. usage: keep_bracket_component.py in.ldr out.ldr"""
import sys, numpy as np, networkx as nx
sys.path.insert(0, "/root/bench/tools"); import conn
src, dst = sys.argv[1:3]; lines = open(src).read().splitlines()
blk = []; inb = False
for k, l in enumerate(lines):
    if l.startswith("0 BRICKIFY SUBASSEMBLY BEGIN"): inb = True; continue
    if l.startswith("0 BRICKIFY SUBASSEMBLY END"): inb = False; continue
    t = l.split()
    if inb and t and t[0] == "1": blk.append(k)
P = []
for k in blk:
    t = lines[k].split(); o = np.array(t[2:5], float); M = np.array(t[5:14], float).reshape(3, 3); num = t[14].replace(".dat", "")
    st, rc, lo, hi = conn.world(num, M, o); P.append(dict(k=k, num=num, st=st, rc=rc, o=o))
G = nx.Graph(); G.add_nodes_from(range(len(P))); rec = {}
for i, p in enumerate(P):
    for pt, n in p["rc"]: rec.setdefault(tuple(np.round(pt).astype(int)), []).append((i, n))
for i, p in enumerate(P):
    for pt, ax in p["st"]:
        kk = np.round(pt).astype(int)
        for d in np.ndindex(3, 3, 3):
            for j, n in rec.get(tuple(kk + np.array(d) - 1), []):
                if j != i and np.dot(n, ax) < -0.9: G.add_edge(i, j)
br = [i for i, p in enumerate(P) if p["num"] in ("99780", "99781", "3832", "3679")]
keep = set().union(*[nx.node_connected_component(G, b) for b in br])
drop = {P[i]["k"] for i in range(len(P)) if i not in keep}
open(dst, "w").write("\n".join(l for k, l in enumerate(lines) if k not in drop) + "\n")
print("removed", len(drop), [P[i]["num"] for i in range(len(P)) if i not in keep])
