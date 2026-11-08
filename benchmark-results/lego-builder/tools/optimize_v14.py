#!/usr/bin/env python3
"""Sprint V14 : print optimisation studies on the real V13 data.
 (1) hidden-core merge : voxels with no exposed face (all 6 neighbours occupied) are invisible once assembled ; giving them the commonest exposed colour of their layer removes colours / colour changes WITHOUT any visible change.
 (2) orientation + support experiments on the Paco head module (PrusaSlicer proxy profile A1).
usage : optimize_v14.py OUT.json [--slice]"""
import collections, json, math, os, subprocess, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / "tools"))
from lego_builder.print3d import modules, common
CAT = json.load(open(HERE.parent / "maps-engine-v03/style_fidelity_v062/part_catalog.json"))
MODELS = {"paco": HERE / "tests/data/paco_sample.ldr", "hyrule": HERE.parent / "maps-engine-v03/style_fidelity_v062/livraison_v10/hyrule_biomes/diorama.ldr"}
def stats(occ, cells):
    bylayer = collections.defaultdict(set)
    for (ix, iy, iz), c in cells.items(): bylayer[iy].add(c)
    ch = sum(max(0, len(s) - 1) for s in bylayer.values()) * 16        # 16 layers of 0.2 mm per 3.2 mm plate
    return ch, max((len(s) for s in bylayer.values()), default=0), len({c for c in cells.values()})
out = {}
for name, ldr in MODELS.items():
    parts = common.read_ldr(ldr); occ, stud, ghost, hulls = modules.voxelise(parts, CAT, True)
    xs, ys, zs = zip(*occ); x0, x1, y0, y1, z0, z1 = min(xs), max(xs) + 1, min(ys), max(ys) + 1, min(zs), max(zs) + 1; sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    nxm, nym, nzm = math.ceil(sx / 30), math.ceil(sy / 70), math.ceil(sz / 30); ex = [x0 + round(i * sx / nxm) for i in range(nxm + 1)]; ey = [y0 + round(i * sy / nym) for i in range(nym + 1)]; ez = [z0 + round(i * sz / nzm) for i in range(nzm + 1)]
    exposed = {k: any((k[0] + d[0], k[1] + d[1], k[2] + d[2]) not in occ for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))) for k in occ}
    rows = []; tot = collections.Counter()
    for a in range(nxm):
        for b in range(nym):
            for c in range(nzm):
                cells = {k: v for k, v in occ.items() if ex[a] <= k[0] < ex[a + 1] and ey[b] <= k[1] < ey[b + 1] and ez[c] <= k[2] < ez[c + 1]}
                if not cells: continue
                ch0, mx0, nc0 = stats(occ, cells)
                # merge : hidden voxels -> commonest exposed colour of their layer
                top = {}; lay = collections.defaultdict(collections.Counter)
                for k, v in cells.items():
                    if exposed[k]: lay[k[1]][v] += 1
                merged = {k: (v if exposed[k] else (lay[k[1]].most_common(1)[0][0] if lay[k[1]] else v)) for k, v in cells.items()}
                ch1, mx1, nc1 = stats(occ, merged); hidden = sum(1 for k in cells if not exposed[k])
                rows.append(dict(module=[a, b, c], voxels=len(cells), hidden_share=round(hidden / len(cells), 3), asis=dict(changes=ch0, max_colours_layer=mx0, colours=nc0), merged=dict(changes=ch1, max_colours_layer=mx1, colours=nc1)))
                tot["ch0"] += ch0; tot["ch1"] += ch1
    out[name] = dict(modules=rows, total_changes_asis=tot["ch0"], total_changes_merged=tot["ch1"], reduction=round(1 - tot["ch1"] / max(1, tot["ch0"]), 3))
    print(name, tot["ch0"], tot["ch1"], flush=True)
json.dump(out, open(sys.argv[1], "w"), indent=1)
