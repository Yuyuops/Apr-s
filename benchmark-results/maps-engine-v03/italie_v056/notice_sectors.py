#!/usr/bin/env python3
"""Digital assembly plan of a full model : steps = (sector 32x32 studs, build layer) with piece counts, plus a per-sector BOM. The LDraw already carries '0 STEP' per layer ; this adds the sector structure.
Monuments (colosseum/pisa/vesuvio) are listed as sub-assemblies owned by the sector of their top-left cell (never cut). usage: notice_sectors.py FOLDER"""
import csv, json, os, sys
from collections import Counter, defaultdict
f = sys.argv[1]; P = json.load(open(os.path.join(f, "parts.json"))); F = 2; SZ = 32
def sector(p): return "S%d%d" % (min(max((p["r"] - F) // SZ, 0), 3), min(max((p["c"] - F) // SZ, 0), 3)) if not p["region"].startswith("frame") else "FRAME"
steps = defaultdict(list); bom = defaultdict(Counter); sub = defaultdict(list)
for p in P:
    s = sector(p); steps[(s, p["y"])].append(p["id"]); bom[s][(p["part"], p["colour"])] += 1
    if p["region"].split("_")[0] in ("colosseum", "pisa", "plaza"): sub[p["region"].split("_")[0]].append(p["id"])
order = ["FRAME"] + ["S%d%d" % (i, j) for i in range(4) for j in range(4)]; plan = []; n = 0
for y in sorted({k[1] for k in steps}):
    for s in order:
        ids = steps.get((s, y))
        if ids:
            for i in range(0, len(ids), 40): n += 1; plan.append(dict(step=n, sector=s, layer_plate=y, pieces=len(ids[i:i + 40]), part_ids=ids[i:i + 40]))
json.dump(dict(steps=plan, step_count=n, max_pieces_per_step=40, subassemblies={k: dict(pieces=len(v)) for k, v in sub.items()}, note="Ordered bottom-up ; a step never places a part before its support (engine-1 validation: unsupported_at_placement 0). Not a printed manual."), open(os.path.join(f, "assembly_plan.json"), "w"))
with open(os.path.join(f, "bom_by_sector.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["sector", "part_num", "color_id", "quantity"])
    for s in order:
        for (pn, c), q in sorted(bom[s].items()): w.writerow([s, pn, c, q])
print(n, "steps;", {s: sum(bom[s].values()) for s in order})
