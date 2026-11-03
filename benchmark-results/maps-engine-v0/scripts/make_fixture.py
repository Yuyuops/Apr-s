#!/usr/bin/env python3
"""Generate raster test input and oracle height grid from an original synthetic map."""
from pathlib import Path
import csv
import hashlib
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
oracle = json.loads((ROOT / "fixtures/ile_temoin_oracle.json").read_text(encoding="utf-8"))
w, h = oracle["canvas_px"]
image = Image.new("RGB", (w, h), oracle["base"]["color"])
heights = Image.new("L", (w, h), oracle["base"]["height_plates"])
a, b = ImageDraw.Draw(image), ImageDraw.Draw(heights)
for item in oracle["regions"]:
    points = [tuple(p) for p in item["points"]]
    typ, colour, level = item["type"], item["color"], item["height_plates"]
    if typ == "polygon":
        a.polygon(points, fill=colour)
        if level is not None: b.polygon(points, fill=level)
    elif typ == "polyline":
        a.line(points, fill=colour, width=item["width"])
        if level is not None: b.line(points, fill=level, width=item["width"])
    elif typ == "point":
        x, y = points[0]; r = item["radius"]
        a.ellipse((x-r,y-r,x+r,y+r), fill=colour)
    else: raise ValueError(typ)
output = ROOT / "fixtures/generated"
output.mkdir(exist_ok=True)
png = output / "ile_temoin.png"
image.save(png)
oracle_csv = output / "height_levels_32.csv"
thumb = heights.resize((32,32), Image.Resampling.NEAREST)
with oracle_csv.open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    for y in range(32): writer.writerow([thumb.getpixel((x,y)) for x in range(32)])
for file in (png, oracle_csv):
    print(file.relative_to(ROOT), file.stat().st_size, hashlib.sha256(file.read_bytes()).hexdigest())
