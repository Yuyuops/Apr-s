#!/usr/bin/env python3
"""Sprint V16 closure : fix the REAL carrying weak links found by weaklink_v16.py (thin pillars of stacked 1x2 plates : every joint is a pry point, each held by 2 studs).
Three identical 1x2 plates (same colour, same footprint, 3 consecutive layers, in a chain flagged weak) are replaced by ONE 1x2 brick (3004) : identical volume and colour, two fewer joints and two fewer pieces per replacement.
Nothing else changes. usage : pillar_bricks_v16.py DUMP.pkl WEAK.json IN.ldr OUT.ldr REPORT.json   (env LEGO_ENGINE_HOME)"""
import json, pickle, sys, os, collections
import numpy as np
MAPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "maps-engine-v03", "style_fidelity_v062"); sys.path.insert(0, MAPS); from scene import PAIRS
dump, weak, fin, fout, rep = sys.argv[1:6]
d = pickle.load(open(dump, "rb")); P = d["parts"]; n = len(P); W = json.load(open(weak))["weak"]; weak_ids = {w["i"] for w in W}
key = lambda p: (p["num"], int(p["c"]), tuple(np.round(p["lo"][[0, 2]], 1)), tuple(np.round(p["hi"][[0, 2]], 1)))
for p in P: p["lo"] = np.array(p["lo"]); p["hi"] = np.array(p["hi"])
col = collections.defaultdict(list)
for i, p in enumerate(P):
    if p["num"] == "3023": col[key(p)].append(i)
used = set(); repl = []
for k, ids in col.items():
    ids = sorted(ids, key=lambda i: -P[i]["hi"][1])              # bottom first
    run = []
    for i in ids:
        if run and abs(P[i]["hi"][1] - P[run[-1]]["lo"][1]) < 1e-6: run.append(i)
        else: run = [i]
        if len(run) == 3 and any(r in weak_ids for r in run) and PAIRS.get("3004", {}).get(str(int(P[i]["c"])), 0) >= 1 and not (set(run) & used):
            repl.append(list(run)); used |= set(run); run = []
lines = open(fin).read().split("\n"); idx = [i for i, l in enumerate(lines) if l.startswith("1 ")]; assert len(idx) == n
for run in repl:
    top = run[-1]; L = lines[idx[top]].split(); L[-1] = "3004.dat"; lines[idx[top]] = " ".join(L)       # origin y = top of the highest plate = top of the brick
    for r in run[:-1]: lines[idx[r]] = None
lines = [l for l in lines if l is not None]; open(fout, "w").write("\n".join(lines))
json.dump(dict(pieces_in=n, replacements=len(repl), pieces_out=n - 2 * len(repl), weak_in=len(weak_ids), chains=[[int(x) for x in r] for r in repl]), open(rep, "w"), indent=1)
print(json.dumps(dict(replacements=len(repl), pieces_out=n - 2 * len(repl))))
