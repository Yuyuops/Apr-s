#!/usr/bin/env python3
"""Step-by-step PDF : one block per step of assembly_plan_v2.json (parts grouped by part/colour/orientation with their positions, stud counts, checks). usage: make_step_pdf.py MODELDIR OUT.pdf"""
import json, sys
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
D, OUT = sys.argv[1], sys.argv[2]; plan = json.load(open(D + "/assembly_plan_v2.json")); W, H = 1240, 1754; M = 50
F = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", s); FB = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)
pages = []; im = None; d = None; y = 0
def new(title):
    global im, d, y
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im); d.text((M, 30), title, fill="black", font=FB(28)); d.line([M, 75, W - M, 75], fill="black", width=2); y = 95; pages.append(im)
def wrap(text, font, width):
    out, line = [], ""
    for w in text.split(" "):
        if d.textlength(line + " " + w, font=font) > width: out.append(line); line = w
        else: line = (line + " " + w).strip()
    return out + [line]
LBL = "LEGO Maps " + str(plan.get("model", "modele")); new("%s - notice pas a pas (%d etapes)" % (LBL, plan["step_count"]))
for t in plan["phases"] + plan["notes"] + ["Lire : 'xN piece colour rot R' = N pieces identiques, rotation R degres ; positions (rangee,colonne,plaque) du coin NO de l'emprise ; (k) = tenons sur lesquels la piece se clipse."]:
    for ln in wrap(t, F(19), W - 2 * M): d.text((M, y), ln, fill="black", font=F(19)); y += 27
    y += 6
for s in plan["steps"]:
    groups = defaultdict(list)
    for p in s["parts"]: groups[(p["part"], p["colour_name"], p["rot"], p["name"])].append(p)
    lines = []
    for (part, col, rot, name), L in sorted(groups.items()):
        pos = " ".join("(%d,%d,%d)(%d)" % (p["row"], p["col"], p["plate_level"], p["studs_below"]) for p in L[:14]) + (" ..." if len(L) > 14 else "")
        lines += wrap("x%d %s %s rot %d  [%s]  %s" % (len(L), part, col, rot, name[:34], pos), F(15), W - 2 * M - 20)
    need = 60 + 22 * len(lines) + 20 * len(s["checks"])
    if y + need > H - M: new("%s - notice pas a pas (suite)" % LBL)
    d.rectangle([M, y, W - M, y + 38], fill=(232, 236, 244)); d.text((M + 8, y + 6), "Etape %d  |  %s %s%s  |  %d pieces" % (s["step"], s["group"], s["sector"], "" if s["level_plate"] is None else "  couche %d" % s["level_plate"], s["n_parts"]), fill="black", font=FB(20)); y += 46
    for ln in lines: d.text((M + 12, y), ln, fill="black", font=F(15)); y += 22
    for c in s["checks"]: d.text((M + 12, y), "- " + c, fill=(120, 40, 20), font=F(14)); y += 20
    y += 14
pages = [p.convert("L") for p in pages]; pages[0].save(OUT, save_all=True, append_images=pages[1:], resolution=150, quality=30); print(len(pages), "pages")
