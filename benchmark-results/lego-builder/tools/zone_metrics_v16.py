#!/usr/bin/env python3
"""Sprint V16 objective measures of one pilot zone from the generated model (parts.json) and the zone raster + style : class agreement, block index, height gradient, slope/curved pieces, detail density, colours, piece mix.
usage : zone_metrics_v16.py WORKDIR ZONE_CLASSES.npy STYLE.json CLASS_NAMES_JSON OUT.json"""
import collections, json, sys
import numpy as np
w, npy, style, names_json, out = sys.argv[1:6]; F = 4
P = json.load(open(w + "/parts.json")); Z = np.load(npy); st = json.load(open(style)); names = json.load(open(names_json)); R, C = Z.shape
surf = -np.ones((R, C), int); top_colour = -np.ones((R, C), int); slope_cell = np.zeros((R, C), bool); detail_cells = 0
SLOPE = {"54200", "85984", "11477", "15068"}; CURVE = SLOPE | {"25269", "3062b", "6141", "98138", "4073"}
reg = collections.Counter(); curved = 0; slopes = 0; details = 0
for p in P:
    reg[p["region"]] += 1
    if p["part"] in SLOPE: slopes += 1
    if p["part"] in CURVE: curved += 1
    if p["region"].startswith("detail"): details += 1; continue
    if p["region"] in ("frame", "backing", "frame_cap", "frame_ornament") or p["y"] < 2: continue
    for r in range(p["r"], p["r"] + p["nr"]):
        for c in range(p["c"], p["c"] + p["nc"]):
            rr, cc = r - F, c - F
            if 0 <= rr < R and 0 <= cc < C:
                top = p["y"] + p["h"]
                if top > surf[rr, cc]: surf[rr, cc] = top; top_colour[rr, cc] = p["colour"]
                if p["region"] == "cliff_slope": slope_cell[rr, cc] = True
water = np.array([bool(st["biomes"][names[int(k)]].get("water")) for k in Z.ravel()]).reshape(Z.shape); land = ~water
expected = np.array([st["biomes"][names[int(k)]]["top"] for k in Z.ravel()]).reshape(Z.shape); agree = float((top_colour == expected)[surf >= 0].mean())
# gradient and cliff edges over land-land neighbour pairs
dh = []; cliff = 0; cliff_slope = 0
for dr, dc in ((0, 1), (1, 0)):
    a = surf[:R - dr, :R - dc if False else C - dc] if False else None
for r in range(R):
    for c in range(C):
        if not land[r, c]: continue
        for dr, dc in ((0, 1), (1, 0)):
            r2, c2 = r + dr, c + dc
            if r2 < R and c2 < C and land[r2, c2]:
                d = abs(int(surf[r, c]) - int(surf[r2, c2])); dh.append(d)
                if d >= 2:
                    cliff += 1; lo = (r, c) if surf[r, c] < surf[r2, c2] else (r2, c2)
                    if slope_cell[lo]: cliff_slope += 1
top_cols = {int(x) for x in top_colour[surf >= 0].ravel()}; n_land = int(land.sum())
res = dict(pieces=len(P), class_agreement=round(agree, 3), mean_height_gradient_plates_per_stud=round(float(np.mean(dh)), 3) if dh else None, cliff_edges_ge2_plates=cliff, cliff_edges_with_slope_at_foot=cliff_slope, block_index=round(1 - cliff_slope / cliff, 3) if cliff else None,
           slope_pieces=slopes, curved_or_round_pieces=curved, detail_pieces=details, detail_per_100_land_cells=round(100 * details / max(1, n_land), 1), distinct_surface_colours=len(top_cols), height_range_plates=[int(surf[surf >= 0].min()), int(surf.max())], region_mix=dict(reg.most_common(10)))
json.dump(res, open(out, "w"), indent=1); print(json.dumps(res))
