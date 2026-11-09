#!/usr/bin/env python3
"""Sprint V15 comparison boards. usage : compose_v15.py OUTDIR REFERENCE.png WORKROOT TAG:R:C [TAG:R:C ...]   (WORKROOT/TAG/renders/*.png ; frame = 4 studs)"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
out = Path(sys.argv[1]); ref = Image.open(sys.argv[2]).convert("RGB").crop((40, 56, 1168, 972)); root = Path(sys.argv[3]); specs = [s.split(":") for s in sys.argv[4:]]; out.mkdir(parents=True, exist_ok=True)
def interior(img, R, C, F=4):
    a = np.asarray(img.convert("RGB")).astype(float); ys, xs = np.where(a.mean(2) < 100); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return img.crop((int(x0 + F * (x1 - x0) / (C + 2 * F)), int(y0 + F * (y1 - y0) / (R + 2 * F)), int(x1 - F * (x1 - x0) / (C + 2 * F)), int(y1 - F * (y1 - y0) / (R + 2 * F)))).convert("RGB")
def label(im, text):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, im.width, 26), fill=(255, 255, 255)); d.text((8, 6), text, fill=(0, 0, 0)); return im
def fit(im, w): return im.resize((w, int(w * im.height / im.width)), Image.LANCZOS)
tiles = {"Reference (third-party LEGO model)": fit(ref, 1100)}; names = {"A": "A - V14 current pipeline", "B": "B - need-guided", "C": "C - hybrid", "C2": "C2 - hybrid, massif relief", "C3": "C3 - hybrid, calmer palette"}
for tag, R, C in specs:
    f = root / tag / "renders" / "face.png"
    if f.exists(): tiles[names.get(tag, tag)] = fit(interior(Image.open(f), int(R), int(C)), 1100)
    full = Image.open(f).convert("RGB") if f.exists() else None
H = max(t.height for t in tiles.values()) + 28; keys = list(tiles)
def board(sel, name):
    W = Image.new("RGB", (1100 * len(sel), H), "white")
    for i, k in enumerate(sel): W.paste(label(tiles[k].copy(), k), (1100 * i, 0)) if False else W.paste(tiles[k], (1100 * i, 28)); ImageDraw.Draw(W).text((1100 * i + 8, 8), k, fill=(0, 0, 0))
    W.save(out / name, quality=90)
board(keys, "compare_all_vs_reference.jpg"); ref_k = keys[0]; a_k = [k for k in keys if k.startswith("A")]
for k in keys[1:]:
    board([ref_k, k], "compare_%s_vs_reference.jpg" % k.split(" ")[0]);
    if a_k and k != a_k[0]: board([a_k[0], k], "compare_%s_vs_V14.jpg" % k.split(" ")[0])
print(sorted(p.name for p in out.glob("*.jpg")))
