#!/usr/bin/env python3
"""[fast variant : identical output, no per-node graph copy] Indicative fragility audit of a diorama (NOT a physical proof) from the engine-1 joint graph (validate_v4 dump) : stud joints per part, single-stud parts split into
decorative leaves vs load-carrying, articulation points, and the mass (0.10 g per stud*stud*plate, same convention as the validator) cut off from the base if one part fails.
usage: fragility.py FOLDER"""
import json, os, pickle, subprocess, sys, tempfile
from collections import Counter, defaultdict
import networkx as nx
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "20_portable_engine", "engine"))
from _paths import LDRAW, RB_DB
folder = sys.argv[1]; P = json.load(open(os.path.join(folder, "parts.json")))
order = []                                   # LDR emission order = layers ascending, then id : maps validator index -> parts.json record
for y in sorted({p["y"] for p in P}): order += [p for p in P if p["y"] == y]
tmp = tempfile.mkdtemp(); pk = os.path.join(tmp, "d.pkl")
subprocess.run([sys.executable, os.path.join(HERE, "..", "..", "20_portable_engine", "engine", "validate_v4.py"), "--ldr", os.path.join(folder, "diorama.ldr"), "--ldraw", LDRAW, "--rbdb", RB_DB, "--out", tmp, "--name", "map", "--dump", pk], check=True, capture_output=True)
d = pickle.load(open(pk, "rb")); assert len(d["parts"]) == len(order), (len(d["parts"]), len(order))
n = len(order); G = nx.Graph(); G.add_nodes_from(range(n)); joints = Counter(); dj = Counter(); up = defaultdict(set); down = defaultdict(set)
for (i, j, area, studs) in d["edges"]:
    k = len(studs); joints[i] += k; joints[j] += k; G.add_edge(i, j, w=k)
    lo, hi = (i, j) if order[i]["y"] < order[j]["y"] else (j, i); up[lo].add(hi); down[hi].add(lo); dj[hi] += k
mass = [0.1 * o["nr"] * o["nc"] * o["h"] for o in order]; ground = set(d["ground"])
def fam(o):
    r = o["region"]
    for k in ("tree_sturdy", "tree_slim", "bush", "boulder", "relief_plate", "beach", "colosseum_arcade", "colosseum_wall", "colosseum_attic", "colosseum_cornice", "colosseum_cavea", "colosseum_hypogeum", "plaza", "mountain_slope", "mountain", "backing", "sea"):
        if r.startswith(k): return k
    return r
def subtree_mass(i):          # mass of parts that lose every path to the base if part i is removed (BFS that skips i : no graph copy -> same result, much faster)
    seen = {g for g in ground if g != i}; stack = list(seen)
    while stack:
        u = stack.pop()
        for v in G._adj[u]:
            if v != i and v not in seen: seen.add(v); stack.append(v)
    lost = [v for v in range(n) if v != i and v not in seen]; return len(lost), sum(mass[v] for v in lost)
single = [i for i in range(n) if dj[i] == 1 and order[i]["y"] > 0]; fams = defaultdict(lambda: Counter())
for i in range(n):
    f = fam(order[i]); fams[f]["parts"] += 1
    if order[i]["y"] > 0 and dj[i] == 1:
        fams[f]["hangs_by_one_stud"] += 1
        if up[i]: fams[f]["hangs_by_one_stud_and_carries"] += 1
        else: fams[f]["hangs_by_one_stud_decorative_leaf"] += 1
    if order[i]["y"] > 0 and dj[i] == 2: fams[f]["hangs_by_two_studs"] += 1
ap = set(nx.articulation_points(G)); rows = []
for i in sorted(ap):
    if order[i]["y"] == 0: continue
    c, m = subtree_mass(i)
    if c: rows.append((fam(order[i]), order[i]["id"], c, round(m, 1), joints[i]))
rows.sort(key=lambda x: -x[3]); byfam = defaultdict(lambda: [0, 0, 0.0])
for f, pid, c, m, jn in rows: byfam[f][0] += 1; byfam[f][1] = max(byfam[f][1], c); byfam[f][2] = max(byfam[f][2], m)
leaf_rows = [r for r in rows if r[2] == 1]; casc = [r for r in rows if r[2] >= 2]
def fclass(f): return "sea" if f in ("sea", "sea_tiles", "backing") else "mountain" if f.startswith("mountain") or f in ("tree_sturdy", "relief_plate", "bush", "boulder", "boulder_single", "beach") else "colosseum" if f.startswith("colosseum") or f == "plaza" else "other"
cls = defaultdict(lambda: dict(ap=0, leaf=0, cascade=0, max_mass=0.0))
for f, pid, c, m, jn in rows:
    k = fclass(f); cls[k]["ap"] += 1; cls[k]["leaf" if c == 1 else "cascade"] += 1; cls[k]["max_mass"] = max(cls[k]["max_mass"], m)
thin = [o for o in order if o["part"] in ("3004", "3005", "3010", "3622", "3009", "3659", "4490", "6182") and min(o["nr"], o["nc"]) == 1 and fam(o) in ("colosseum_wall", "colosseum_arcade", "colosseum_attic")]
res = dict(note="indicative only : rigid parts, 1.0 N clutch per stud assumed by the validator, NO physical test", parts=n, joints_total=sum(joints.values()) // 2, parts_hanging_by_one_stud=len(single),
           one_stud_decorative_leaves=sum(1 for i in single if not up[i]), one_stud_and_carrying=sum(1 for i in single if up[i]),
           articulation_points_with_loss=len(rows), worst_single_failure=dict(family=rows[0][0], part_id=rows[0][1], parts_cut_off=rows[0][2], mass_cut_off_g=rows[0][3]) if rows else None,
           families={f: dict(v) for f, v in sorted(fams.items())}, failure_by_family={f: dict(articulation_points=v[0], max_parts_cut_off=v[1], max_mass_cut_off_g=round(v[2], 1)) for f, v in sorted(byfam.items())},
           colosseum_one_stud_thick_wall_pieces=len(thin), ap_leaf_isolating_one_part=len(leaf_rows), ap_cascade_two_or_more=len(casc), ap_cascade_mass_sum_g=round(sum(r[3] for r in casc), 1), ap_by_class={k: v for k, v in cls.items()}, worst_10=[dict(family=r[0], parts_cut_off=r[2], mass_g=r[3]) for r in rows[:10]], total_mass_g=round(sum(mass), 1))
json.dump([dict(id=order[i]["id"], studs_below=int(dj[i]), carries=len(up[i])) for i in range(n)], open(os.path.join(folder, "joints_per_part.json"), "w"))
json.dump(res, open(os.path.join(folder, "fragility.json"), "w"), indent=1); print(json.dumps(res)[:3000])
