#!/usr/bin/env python3
"""Biome class raster from a user-supplied picture (oblique render or top view) : perspective rectification of 4 measured corners + colour-rule classification. The rules are DATA (a JSON file), so the
same script reproduces any map : edit the corner points and the rules, nothing else. NO geography is created : every output pixel comes from a colour found in the picture.
usage : biomes_from_render.py SRC.jpg RULES.json OUT_codes.tif OUT_preview.jpg [--grid R C] [--px-per-stud N]
RULES.json : {"corners": [[x,y] x4 : top-left, top-right, bottom-right, bottom-left, pixels of SRC], "classes": [{"name","code","preview":[r,g,b],"hue":[min,max],"sat":[min,max],"val":[min,max],"smooth":studs,"weight":w,"min_region_studs2":n}]}"""
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage
src, rules_f, out, prev = sys.argv[1:5]; a = sys.argv; R, C = (int(a[a.index("--grid") + 1]), int(a[a.index("--grid") + 2])) if "--grid" in a else (80, 80); K = int(a[a.index("--px-per-stud") + 1]) if "--px-per-stud" in a else 12
rules = json.load(open(rules_f)); W, H = C * K, R * K; im = Image.open(src).convert("RGB")
dst = [(0, 0), (W, 0), (W, H), (0, H)]; A = []; B = []
for (x, y), (u, v) in zip(dst, rules["corners"]):
    A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u); A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
coef = np.linalg.solve(np.array(A, float), np.array(B, float)); rect = im.transform((W, H), Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)
hsv = np.asarray(rect.convert("HSV")).astype(float); h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
cls = rules["classes"]; score = np.zeros((len(cls), H, W))
for i, c in enumerate(cls):
    m = ((h >= c["hue"][0]) & (h <= c["hue"][1]) & (s >= c["sat"][0]) & (s <= c["sat"][1]) & (v >= c["val"][0]) & (v <= c["val"][1])).astype(float)
    score[i] = ndimage.gaussian_filter(m, K * c.get("smooth", 0.8)) * c.get("weight", 1.0)
best = score.argmax(axis=0); none = score.max(axis=0) < 0.04
if none.any():                                               # pixels that match no rule take the class of the nearest classified pixel
    idx = ndimage.distance_transform_edt(none, return_distances=False, return_indices=True); best = best[tuple(idx)]
for i, c in enumerate(cls):                                  # drop regions smaller than min_region_studs2 : they take the majority of their surroundings
    mn = c.get("min_region_studs2", 0)
    if mn:
        lab, n = ndimage.label(best == i); sz = ndimage.sum(best == i, lab, range(1, n + 1)); small = np.isin(lab, [j + 1 for j, z in enumerate(sz) if z < mn * K * K])
        if small.any():
            sc = score.copy(); sc[i] = -1; best = np.where(small, sc.argmax(axis=0), best)
codes = np.zeros((H, W), np.uint8); pv = np.zeros((H, W, 3), np.uint8)
for i, c in enumerate(cls): codes[best == i] = c["code"]; pv[best == i] = c["preview"]
Image.fromarray(codes).save(out, compression="tiff_lzw"); Image.fromarray(np.hstack([np.asarray(rect), pv])).save(prev, quality=85)
print({c["name"]: round(float((best == i).mean()), 3) for i, c in enumerate(cls)})
