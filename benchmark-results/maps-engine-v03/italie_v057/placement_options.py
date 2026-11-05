#!/usr/bin/env python3
"""Colosseum placement policies on the real 128x128 geography, measured : land-priority (>=70 % land), sea-podium (>=40 %), offshore medallion (<=25 % land, nearest to Rome).
Draws the three options on the land mask and reports masked land cells, relief levels hidden, displacement from the true position. usage: placement_options.py OUTDIR"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "italia")); import geo
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
land = np.load(os.path.join(HERE, "italia/output/land_128.npy")); lev = np.load(os.path.join(HERE, "italia/output/levels_128.npy")); ar, ac = geo.to_grid(12.4924, 41.8902); rows, cols = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (22, 28)
FORBID = [(33, 43, 41, 51), (62, 74, 69, 82)]   # (row0,row1,col0,col1) : Pisa tower plaza + Vesuvius cone footprints with margin
from scipy import ndimage
ALL = land
PADLAND = ndimage.binary_dilation(ALL, iterations=3)
def find(lo, hi, maxshift=40, margin=False):
    best = None
    for r in range(3, 128 - rows - 3):
        for c in range(3, 128 - cols - 3):
            frac = land[r:r + rows, c:c + cols].mean(); sh = math.hypot(r + rows / 2 - ar, c + cols / 2 - ac)
            if any(r < b and r + rows > a and c < d_ and c + cols > c0_ for (a, b, c0_, d_) in FORBID): continue
            if margin and c > int(os.environ.get('OFFSHORE_COLMAX', '999')): continue
            if margin and PADLAND[r:r + rows, c:c + cols].any(): continue
            if lo <= frac <= hi and sh <= maxshift and (best is None or sh < best[0]): best = (sh, r, c, frac)
    return best
res = {}
for name, (lo, hi) in (("land_priority", (.7, 1.0)), ("sea_podium", (.4, 1.0)), ("offshore_medallion", (0.0, .04))):
    b = find(lo, hi, 60 if name == "offshore_medallion" else 40, margin=(name == "offshore_medallion")); sh, r, c, frac = b; blk = land[r:r + rows, c:c + cols]; res[name] = dict(row=r, col=c, shift_studs=round(sh, 1), land_cells_covered=int(blk.sum()), land_fraction=round(float(frac), 2), relief_levels_hidden=int(sum(max(int(v) - 1, 0) for v in lev[r:r + rows, c:c + cols][blk])), distance_km=round(sh * 8, 0))
im = Image.new("RGB", (128 * 8, 128 * 8)); d = ImageDraw.Draw(im)
for r in range(128):
    for c in range(128): d.rectangle([c * 8, r * 8, c * 8 + 7, r * 8 + 7], fill=(36, 99, 158) if not land[r, c] else (90, 140, 80) if lev[r, c] < 4 else (150, 125, 85))
cols_ = {"land_priority": (220, 40, 40), "sea_podium": (240, 160, 20), "offshore_medallion": (255, 255, 255)}
for k, v in res.items(): d.rectangle([v["col"] * 8, v["row"] * 8, (v["col"] + cols) * 8, (v["row"] + rows) * 8], outline=cols_[k], width=3); d.text((v["col"] * 8 + 4, v["row"] * 8 + 4), k, fill=cols_[k])
d.ellipse([ac * 8 - 5, ar * 8 - 5, ac * 8 + 5, ar * 8 + 5], fill=(0, 0, 0)); d.text((ac * 8 + 8, ar * 8 - 6), "Roma (position vraie)", fill=(0, 0, 0))
im.save(os.path.join(out, "placement_options.png")); json.dump(res, open(os.path.join(out, "placement_options.json"), "w"), indent=1); print(json.dumps(res))
