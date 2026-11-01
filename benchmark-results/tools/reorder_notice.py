#!/usr/bin/env python3
"""Re-order the building steps of an LDraw model so that every part, when placed, connects by studs to a part
already placed (or to the support plane). Bottom-up: at each step, all placeable parts of the lowest level are
added; a part held only from above (overhang) comes right after the part it hangs from, pushed on from below.
Sub-assembly blocks (0 BRICKIFY SUBASSEMBLY ...) are kept as blocks and inserted once they can attach.
usage: reorder_notice.py <in.ldr> <out.ldr>"""
import sys, os
import numpy as np, networkx as nx
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conn

def main():
    src, dst = sys.argv[1:3]
    lines = open(src, encoding="utf-8", errors="replace").read().splitlines()
    header = [l for l in lines[:3] if l.startswith("0 ") and "STEP" not in l and "BRICKIFY" not in l]
    parts, sub = [], None
    for l in lines:
        t = l.split()
        if len(t) > 4 and t[0] == "0" and t[1] == "BRICKIFY" and t[2] == "SUBASSEMBLY":
            sub = t[4] if t[3] == "BEGIN" else None; continue
        if t and t[0] == "1" and len(t) >= 15:
            o = np.array(t[2:5], float); M = np.array(t[5:14], float).reshape(3, 3); num = t[14].lower().replace(".dat", "")
            st, rc, lo, hi = conn.world(num, M, o)
            parts.append(dict(line=l, sub=sub, studs=st, recv=rc, lo=lo, hi=hi, num=num, o=o, M=M))
    rindex = {}
    for i, p in enumerate(parts):
        for pt, n in p["recv"]: rindex.setdefault(tuple(np.round(pt).astype(int)), []).append((i, n))
    G = nx.Graph(); G.add_nodes_from(range(len(parts)))
    for i, p in enumerate(parts):
        for pt, ax in p["studs"]:
            k = np.round(pt).astype(int)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        for (j, n) in rindex.get((k[0] + dx, k[1] + dy, k[2] + dz), []):
                            if j != i and np.dot(n, ax) < -0.9: G.add_edge(i, j)
    # turntable 2x2: the top (3679) clicks on the base (3680) at the same origin, free rotation about the vertical
    for i, p in enumerate(parts):
        if p["num"] != "3679": continue
        for j, q in enumerate(parts):
            if q["num"] == "3680" and np.linalg.norm(q["o"] - p["o"]) < 1.0 and np.allclose(p["M"][1], [0, 1, 0], atol=1e-4): G.add_edge(i, j)
    base = max(p["hi"][1] for p in parts)
    blocks = {}
    for i, p in enumerate(parts):
        if p["sub"]: blocks.setdefault(p["sub"], []).append(i)
    main_parts = [i for i, p in enumerate(parts) if not p["sub"]]
    placed, steps = set(), []
    remaining = set(main_parts); pending_blocks = dict(blocks)
    while remaining or pending_blocks:
        avail = [i for i in remaining if abs(parts[i]["hi"][1] - base) < 0.5 or any(j in placed for j in G.neighbors(i))]
        if not avail:
            # attach any sub-assembly that can now connect
            done = [b for b, idx in pending_blocks.items() if any(j in placed for i in idx for j in G.neighbors(i) if j not in idx)]
            if not done:
                steps.append(("orphans", sorted(remaining) + [i for idx in pending_blocks.values() for i in idx])); break   # never dropped: left at the end, counted
            for b in done:
                steps.append(("block", b)); placed |= set(pending_blocks.pop(b))
            continue
        lvl = max(parts[i]["hi"][1] for i in avail)                     # lowest level first (LDraw y grows downward)
        batch = [i for i in avail if abs(parts[i]["hi"][1] - lvl) < 0.5]
        steps.append(("main", batch)); placed |= set(batch); remaining -= set(batch)
        done = [b for b, idx in pending_blocks.items() if any(j in placed for i in idx for j in G.neighbors(i) if j not in idx)
                and not any(any(j in remaining for j in G.neighbors(i)) and False for i in idx)]
        # sub-assemblies are attached once all main parts are placed (they hang outside the body)
    out = header[:]
    for kind, val in steps:
        if kind == "block":
            idx = blocks[val]; H = G.subgraph(idx)
            # one sub-assembly per internally connected piece, parts in breadth-first order of their joints
            for k, comp in enumerate(sorted(nx.connected_components(H), key=lambda c: min(c))):
                root = min(comp); order = list(nx.bfs_tree(H.subgraph(comp), root))
                out.append(f"0 BRICKIFY SUBASSEMBLY BEGIN {val}{'_' + str(k) if k else ''}")
                for i in order: out.append(parts[i]["line"])
                out.append(f"0 BRICKIFY SUBASSEMBLY END {val}{'_' + str(k) if k else ''}"); out.append("0 STEP")
        else:
            for i in val: out.append(parts[i]["line"])
            out.append("0 STEP")
    open(dst, "w").write("\n".join(out) + "\n")
    n_out = sum(1 for l in out if l.startswith("1 "))
    assert n_out == len(parts), f"part count changed: {n_out} != {len(parts)}"
    print(f"{dst}: {len(steps)} steps, {sum(len(v) for k, v in steps if k == 'orphans')} parts could not be ordered")

if __name__ == "__main__":
    main()
