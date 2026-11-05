#!/usr/bin/env python3
"""Selection sheet : real catalogue photos with name, id, sets, status. usage: sheet.py THEME -> results/THEME_selection.png (contact sheet of the candidates found by search.py)"""
import json, os, sys, textwrap
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); theme = sys.argv[1]; d = json.load(open(os.path.join(HERE, "results", theme + "_candidates.json")))
F = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", s); FB = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)
C = d["candidates"]; cols = 4; cw, ch = 330, 400; rows = max(1, -(-len(C) // cols)); W = cols * cw + 20; H = rows * ch + 90
im = Image.new("RGB", (W, H), "white"); dr = ImageDraw.Draw(im); dr.text((10, 8), "%s : %s" % (d["label"], d["verdict"]), fill="black", font=FB(22))
dr.text((10, 40), "Source : catalogue Rebrickable (instantane local). BrickLink / site LEGO non consultables (HTTP %s / %s). Disponibilite : non verifiee. Prix : aucun." % (d["sources"]["bricklink"]["http"], d["sources"]["lego_official"]["http"]), fill=(90, 30, 30), font=F(13))
if not C: dr.text((10, 80), "Aucune figurine verifiee", fill="black", font=FB(28))
for i, c in enumerate(C):
    x, y = 10 + (i % cols) * cw, 70 + (i // cols) * ch; dr.rectangle([x, y, x + cw - 10, y + ch - 10], outline=(180, 180, 180))
    if c.get("image_file") and os.path.exists(os.path.join(HERE, c["image_file"])):
        p = Image.open(os.path.join(HERE, c["image_file"])).convert("RGB"); p.thumbnail((cw - 30, 210)); im.paste(p, (x + 10, y + 8))
    else: dr.text((x + 20, y + 90), "image non disponible", fill=(150, 0, 0), font=F(14))
    t = 228; dr.text((x + 8, y + t), "%s [%s]" % (c["fig_num"], c["relevance"]), fill="black", font=FB(13)); t += 18
    for ln in textwrap.wrap(c["name"], 40)[:3]: dr.text((x + 8, y + t), ln, fill="black", font=F(13)); t += 16
    dr.text((x + 8, y + t), "pieces : %s | sets : %s" % (c["parts"], ", ".join(s["set_num"] for s in c["sets"][:3])), fill=(60, 60, 60), font=F(12)); t += 16
    dr.text((x + 8, y + t), "disponibilite : non verifie | prix : -", fill=(60, 60, 60), font=F(12)); t += 16
    dr.text((x + 8, y + t), "3D : non integre (aucun modele)", fill=(120, 40, 20), font=F(12))
im.save(os.path.join(HERE, "results", theme + "_selection.png")); print(theme, im.size)
