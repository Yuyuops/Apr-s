#!/usr/bin/env python3
"""Illustrated step-by-step notice (pilot). One page per step of assembly_plan_v2.json : a real three.js render of the sub-assembly at that step (parts added by the step in their TRUE colours,
parts of earlier steps drawn in light grey as a visual aid only, later parts absent), then the table of added parts (swatch, name, colour, quantity, rotation, positions in studs from the
north-west corner of the model, 1-based) and the checks of the step. The model, BOM and colours are unchanged ; grey is a drawing convention.
usage: make_visual_notice.py MODELDIR OUT.pdf [--jobs N] [--az 20 --el 38]"""
import json, os, shutil, subprocess, sys, tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); D = sys.argv[1]; OUT = sys.argv[2]
a = sys.argv; JOBS = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 3; AZ = float(a[a.index("--az") + 1]) if "--az" in a else 20; EL = float(a[a.index("--el") + 1]) if "--el" in a else 38
sys.path.insert(0, os.path.join(HERE, "..", "..", "20_portable_engine", "engine")); from _paths import RB_DB
import sqlite3
P = json.load(open(D + "/parts.json")); plan = json.load(open(D + "/assembly_plan_v2.json")); M = json.load(open(D + "/metrics.json")); R, C = M["grid_studs"]; H = M["height_plates"] + 4
rb = {r[0]: (r[1], "#" + r[2]) for r in sqlite3.connect(RB_DB).execute("select id,name,rgb from colors")}
order = []
for y in sorted({p["y"] for p in P}): order += [p for p in P if p["y"] == y]
lines = open(D + "/diorama.ldr").read().split("\n"); idx = [i for i, l in enumerate(lines) if l.startswith("1 ")]; assert len(idx) == len(order), (len(idx), len(order))
line_of = {p["id"]: idx[k] for k, p in enumerate(order)}; steps = plan["steps"]
r0 = min(p["r"] for p in P); c0 = min(p["c"] for p in P)
work = tempfile.mkdtemp(); views = {"v": dict(box=[0, 0, R, C], h=H, az=AZ, el=EL, w=1100, hpx=760, zoom=0.85)}; vj = os.path.join(work, "views.json"); json.dump(views, open(vj, "w"))
def render(k):
    d = os.path.join(work, "s%03d" % k); os.makedirs(d, exist_ok=True); cur = set(steps[k]["part_ids"]); prev = {i for s in steps[:k] for i in s["part_ids"]}; out = list(lines[:idx[0]])
    for p in order:
        if p["id"] in cur: out.append(lines[line_of[p["id"]]])
        elif p["id"] in prev:
            t = lines[line_of[p["id"]]].split(" "); t[1] = "71"; out.append(" ".join(t))
    open(d + "/diorama.ldr", "w").write("\n".join(out) + "\n")
    cp = [p for p in order if p["id"] in cur]; ra, ca = min(p["r"] for p in cp), min(p["c"] for p in cp); rb_, cb = max(p["r"] + p["nr"] for p in cp), max(p["c"] + p["nc"] for p in cp)
    pad = 5; ra, ca, rb_, cb = ra - pad, ca - pad, rb_ + pad, cb + pad
    if rb_ - ra < 22: m = (22 - (rb_ - ra)) // 2 + 1; ra -= m; rb_ += m
    if cb - ca < 30: m = (30 - (cb - ca)) // 2 + 1; ca -= m; cb += m
    ra, ca, rb_, cb = max(ra, 0), max(ca, 0), min(rb_, R), min(cb, C); top = max(p["y"] + p["h"] for p in order if p["id"] in cur or p["id"] in prev)
    json.dump({"v": dict(box=[ra, ca, rb_, cb], h=top / 3.0 + 1, az=AZ, el=EL, w=1100, hpx=760, zoom=0.9)}, open(d + "/views.json", "w"))
    subprocess.run([sys.executable, os.path.join(HERE, "render_views.py"), d, d + "/views.json"], check=True, capture_output=True)
    img = Image.open(d + "/renders/v.png").convert("RGB"); img.load(); shutil.rmtree(d, ignore_errors=True)      # each step scene is ~50 MB : free it at once (133 steps would fill a CI runner)
    return img
with ThreadPoolExecutor(JOBS) as ex: imgs = list(ex.map(render, range(len(steps))))
W, Hh, Mg = 1240, 1754, 50; F = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", s); FB = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)
from PIL import ImageChops
def crop(g):
    bg = Image.new("RGB", g.size, (255, 255, 255)); box = ImageChops.difference(g, bg).convert("L").point(lambda v: 255 if v > 12 else 0).getbbox()
    return g.crop((max(box[0] - 12, 0), max(box[1] - 12, 0), min(box[2] + 12, g.width), min(box[3] + 12, g.height))) if box else g
pages = []
for k, s in enumerate(steps):
    im = Image.new("RGB", (W, Hh), "white"); d = ImageDraw.Draw(im); d.text((Mg, 28), "Étape %d / %d" % (k + 1, len(steps)), fill="black", font=FB(34)); d.text((Mg + 330, 38), "%d pièces ajoutées · couche plaque %s" % (s["n_parts"], s.get("level_plate", "")), fill="black", font=F(20))
    d.line([Mg, 80, W - Mg, 80], fill="black", width=2); g = crop(imgs[k]); sc = min((W - 2 * Mg) / g.width, 820 / g.height); g = g.resize((int(g.width * sc), int(g.height * sc))); im.paste(g, (Mg + (W - 2 * Mg - g.width) // 2, 95)); y = 95 + g.height + 8
    d.text((Mg, y), "Gris = pièces des étapes précédentes (aide visuelle) ; couleurs vraies = pièces à poser maintenant.", fill=(90, 90, 90), font=F(15)); y += 28
    grp = defaultdict(list)
    for p in s["parts"]: grp[(p["part"], p["name"], p["colour"], p["rot"])].append((p["row"] + 1 - (r0 - 0 if False else 0), p["col"] + 1))
    byid = {p["id"]: p for p in P}; grp = defaultdict(list)
    for pid in s["part_ids"]:
        p = byid[pid]; grp[(p["part"], p["colour"], p["rot"])].append((p["r"] - r0 + 1, p["c"] - c0 + 1))
    names = {p["part"]: p["name"] for p in s["parts"]}
    for (part, col, rot), pos in sorted(grp.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if y > Hh - 250: d.text((Mg, y), "… (suite : voir le tableau CSV de l'étape)", fill="black", font=F(16)); break
        hexc = rb.get(col, ("?", "#888888"))[1]; d.rectangle([Mg, y + 2, Mg + 26, y + 26], fill=hexc, outline="black")
        pos_txt = " ".join("(%d,%d)" % q for q in sorted(pos)[:10]) + (" …+%d" % (len(pos) - 10) if len(pos) > 10 else "")
        d.text((Mg + 36, y), "%d× %s %s · %s · rot %d°" % (len(pos), part, names.get(part, "")[:34], rb.get(col, ("?",))[0], rot), fill="black", font=FB(16)); y += 22
        d.text((Mg + 36, y), "rangée,colonne : " + pos_txt, fill=(60, 60, 60), font=F(14)); y += 22
    y = max(y + 10, Hh - 200); d.line([Mg, y - 6, W - Mg, y - 6], fill="gray", width=1)
    for c in [c for c in s["checks"] if "secteur" not in c and "jonction" not in c][:4]:      # sector/junction remarks belong to the 128-stud Italy modules (32-stud sectors) : meaningless on a sub-assembly
        d.text((Mg, y), "• " + c[:120], fill="black", font=F(14)); y += 20
    if s.get("single_stud_parts"): d.text((Mg, y), "⚠ %d pièce(s) tenue(s) par un seul tenon dans cette étape." % s["single_stud_parts"], fill=(160, 0, 0), font=FB(14))
    pages.append(im)
pages[0].save(OUT, save_all=True, append_images=pages[1:], resolution=150, quality=55); shutil.rmtree(work, ignore_errors=True); print(len(pages), "pages", os.path.getsize(OUT) // 1024, "kB")
