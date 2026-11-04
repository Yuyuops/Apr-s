#!/usr/bin/env python3
"""V0.5.5 chantier B : Colosseum variants on the real Tuscany-Rome terrain (rows 32..96, cols 32..96 of the Italia grid). Placement by the config rules (land fraction, shift),
measured masking / relief disturbance / displacement. usage: colosseum_variants.py OUTROOT"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "italia"))
import geo, region, colosseum
out = sys.argv[1]; ROW0, COL0, R, C = 32, 32, 64, 64
land = np.load(os.path.join(HERE, "italia/output/land_128.npy")); lev = np.load(os.path.join(HERE, "italia/output/levels_128.npy"))
ar, ac = geo.to_grid(12.4924, 41.8902)
def place(rows, cols, minland=.85, maxshift=10):
    best = None
    for dr in range(-maxshift, maxshift + 1):
        for dc in range(-maxshift, maxshift + 1):
            sh = math.hypot(dr, dc)
            if sh > maxshift: continue
            r = int(round(ar + dr - rows / 2)); c = int(round(ac + dc - cols / 2)); frac = land[r:r + rows, c:c + cols].mean()
            if frac >= minland and (best is None or sh < best[0]): best = (sh, r, c, frac)
    return best
res = {}
VAR = sys.argv[2].split(",") if len(sys.argv) > 2 else ["full", "simplified", "icon"]; LADDER = {"icon28_sea": (.4, .3), "icon28": (.85, .7, .55)}
for variant in VAR:
    vkey = variant.replace("_sea", "")
    rows, cols = region.COL_VARIANTS[vkey]["scale"]; p = None
    for ml in LADDER.get(variant, (.85, .7, .55)):
        p = place(rows, cols, ml)
        if p: break
    sh, r, c, frac = p; a, b, pe = region.colosseum_geometry(rows, cols); cells = colosseum.oval_cells(rows // 2, cols // 2, a + pe, b + pe, 3.0)
    gl = [(r + rr, c + cc) for rr, cc in cells]; covered = [(x, y) for x, y in gl if 0 <= x < 128 and 0 <= y < 128 and land[x, y]]; rowband = land[int(round(ar)) - 1:int(round(ar)) + 2, :].any(axis=0); w_pen = int(rowband[int(ac) - 30:int(ac) + 30].sum())
    res[variant] = dict(footprint=[rows, cols], placed_row=r, placed_col=c, shift_studs=round(sh, 1), min_land_fraction_used=ml, land_cells_covered=len(covered), peninsula_width_at_rome_studs=w_pen, share_of_local_width_covered=round(min(1.0, cols / max(w_pen, 1)), 2), relief_levels_removed=int(sum(max(int(lev[x, y]) - 1, 0) for x, y in covered)), plaza_oval_cells=len(cells))
    S, met, F = region.build_region(os.path.join(out, variant), ROW0, COL0, R, C, [dict(type="colosseum", variant=vkey, row=r - ROW0 + ROW0, col=c, footprint=[rows, cols])], title="Tuscany-Rome " + variant)
    res[variant]["pieces"] = met["pieces"]; res[variant]["modules"] = met["modules"]; print(variant, json.dumps(res[variant])[:300])
if len(VAR) == 3 or "--nomon" in sys.argv: S, met, F = region.build_region(os.path.join(out, "no_monument"), ROW0, COL0, R, C, [], title="Tuscany-Rome terrain only"); res["no_monument"] = dict(pieces=met["pieces"])
json.dump(res, open(os.path.join(out, "variants_metrics_%s.json" % "_".join(VAR)), "w"), indent=1)
