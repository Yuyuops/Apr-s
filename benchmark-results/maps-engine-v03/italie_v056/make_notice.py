#!/usr/bin/env python3
"""Notice PDF of the retained model : cover, composition, sector overview, one page per sector (steps by layer, part counts, BOM), monuments and finishing pages. usage: make_notice.py MODELDIR OUT.pdf"""
import csv, json, os, sys
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
D, OUT = sys.argv[1], sys.argv[2]; W, H = 1240, 1754
try: F = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", s); FB = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)
except Exception: F = FB = lambda s: ImageFont.load_default()
plan = json.load(open(D + "/assembly_plan.json")); met = json.load(open(D + "/metrics.json")); pages = []
def page(title): im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im); d.text((60, 40), title, fill="black", font=FB(34)); d.line([60, 95, W - 60, 95], fill="black", width=2); return im, d
def crop(p):
    im = Image.open(p).convert("RGB"); bb = Image.eval(im.convert("L"), lambda v: 255 if v < 250 else 0).getbbox(); return im.crop(bb) if bb else im
def paste(im, p, y, w=W - 120):
    c = crop(p); c = c.resize((w, int(c.height * w / c.width))); im.paste(c, (60, y)); return y + c.height
im, d = page("LEGO Maps - ITALIA 128 x 128 studs (V0.5.6) - notice de montage numerique")
y = paste(im, D + "/renders/full_trois_quarts.png", 130)
for i, t in enumerate(["%d pieces, %d references, champ %d x %d mm (cadre inclus : %s)" % (met["pieces"], met["references"], 1024, 1024, met["physical_size_mm"]), "Hauteur max %.1f mm. Aucune validation physique : ne pas accrocher au mur sans essai (voir PROTOCOLE_ESSAI).", "Montage strictement de bas en haut : socle 8x8 -> 2e couche decalee -> mer -> secteurs -> monuments -> titre/rose -> cadre.", "Les etapes ci-dessous suivent assembly_plan.json (%d etapes, <= 40 pieces)." % plan["step_count"]]): d.text((60, y + 30 + 36 * i), t, fill="black", font=F(22))
pages.append(im)
im, d = page("Plan : 16 secteurs 32 x 32 + cadre"); paste(im, D + "/renders/full_face.png", 130, 1000); d.text((60, 1160), "Secteurs S{ligne}{colonne}, ligne 0 = nord. Les monuments (Colisee en medaillon ouest, Pise, Vesuve) sont des sous-ensembles non decoupes.", fill="black", font=F(20)); pages.append(im)
steps = defaultdict(list)
for s in plan["steps"]: steps[s["sector"]].append(s)
bom = defaultdict(lambda: defaultdict(int))
for r in csv.DictReader(open(D + "/bom_by_sector.csv")): bom[r["sector"]][(r["part_num"], r["color_id"])] += int(r["quantity"])
for sec in ["FRAME"] + ["S%d%d" % (i, j) for i in range(4) for j in range(4)]:
    im, d = page("Secteur %s" % sec); st = steps.get(sec, []); tot = sum(bom[sec].values()); d.text((60, 115), "%d pieces, %d etapes" % (tot, len(st)), fill="black", font=F(24)); y = 170
    d.text((60, y), "Etapes (couche en plaques : nb de pieces)", fill="black", font=FB(22)); y += 36
    line = ""; 
    for s in st:
        t = "#%d L%d:%d   " % (s["step"], s["layer_plate"], s["pieces"])
        if d.textlength(line + t, font=F(19)) > W - 140: d.text((60, y), line, fill="black", font=F(19)); y += 30; line = ""
        line += t
    d.text((60, y), line, fill="black", font=F(19)); y += 60
    d.text((60, y), "Nomenclature du secteur (piece, couleur Rebrickable, quantite)", fill="black", font=FB(22)); y += 36
    items = sorted(bom[sec].items(), key=lambda kv: -kv[1]); col = 0
    for k, ((pn, c), q) in enumerate(items):
        x = 60 + (k // 38) * 400; yy = y + (k % 38) * 30
        if yy < H - 60 and x < W - 300: d.text((x, yy), "%-8s c%-4s x%d" % (pn, c, q), fill="black", font=F(19))
    pages.append(im)
for title, files in (("Colisee (medaillon ouest, variante A)", ["colisee_trois_quarts", "colisee_facade"]), ("Pise et Vesuve", ["pise", "vesuve"]), ("Alpes", ["alpes_trois_quarts", "alpes_face"]), ("Finitions : titre, rose des vents, cadre", ["titre", "rose_des_vents", "cadre_coin"])):
    im, d = page(title); y = 120
    for f in files:
        p = D + "/renders/%s.png" % f
        if os.path.exists(p): y = paste(im, p, y, 1000) + 20
    pages.append(im)
pages[0].save(OUT, save_all=True, append_images=pages[1:], resolution=150); print(len(pages), "pages")
