"""Building instructions PDF (V0.1) : three sections (backing, relief by region and layer, frame), steps of at most MAX_STEP parts, every part traceable (id, size, colour, studs coordinates)."""
import base64, io, json, os, subprocess
from collections import Counter, OrderedDict
from PIL import Image, ImageDraw
from .common import ROOT, rb_colours
from .render import NODE_MODULES

MAX_STEP = 20; PX = 11
def rgb(c): return tuple(rb_colours()[c]["rgb"])
def fade(c, f=0.6): return tuple(int(v + (255 - v) * f) for v in c)

def chunks(parts, size=MAX_STEP):
    parts = sorted(parts, key=lambda p: (p["x"] // 8, p["z"], p["x"]))
    for i in range(0, len(parts), size): yield parts[i:i + size]

def steps_of(model, class_order):
    P = model["parts"]; S = []
    for layer, title in (("B1", "Dos rigide, couche 1"), ("B2", "Dos rigide, couche 2 (joints decales)")):
        ps = [p for p in P if p["layer"] == layer]; cs = list(chunks(ps))
        for j, c in enumerate(cs): S.append(dict(section="Dos", title="%s%s" % (title, " (partie %d/%d)" % (j + 1, len(cs)) if len(cs) > 1 else ""), region="dos", layer=layer, parts=c))
    for k in range(model["levels"]):
        regs = OrderedDict()
        for p in sorted([q for q in P if q["layer"] == "L%d" % k], key=lambda q: (class_order.index(q["region"]) if q["region"] in class_order else 99, q["id"])): regs.setdefault(p["region"], []).append(p)
        for r, ps in regs.items():
            cs = list(chunks(ps))
            for j, c in enumerate(cs): S.append(dict(section="Relief", title="Couche %d - region : %s%s" % (k + 1, r, " (partie %d/%d)" % (j + 1, len(cs)) if len(cs) > 1 else ""), region=r, layer="L%d" % k, parts=c))
    fl = sorted({p["layer"] for p in P if p["layer"].startswith("F")}, key=lambda s: int(s[1:]))
    for layer in fl:
        ps = [p for p in P if p["layer"] == layer]; cs = list(chunks(ps))
        for j, c in enumerate(cs): S.append(dict(section="Cadre", title="Cadre, rang %d%s" % (int(layer[1:]) + 1, " (partie %d/%d)" % (j + 1, len(cs)) if len(cs) > 1 else ""), region="cadre", layer=layer, parts=c))
    return S

def draw(model, steps, i, px=PX, crop=None):
    N = model["N"]; img = Image.new("RGB", (N * px + 1, N * px + 1), (248, 248, 248)); d = ImageDraw.Draw(img); done = [p for s in steps[:i] for p in s["parts"]]
    for grp, new in ((sorted(done, key=lambda q: q["zbot"]), False), (steps[i]["parts"], True)):
        for p in grp:
            c = rgb(p["colour"]); c = c if new else fade(c); x0, z0 = p["z"] * px, p["x"] * px; x1, z1 = (p["z"] + p["d"]) * px, (p["x"] + p["w"]) * px
            d.rectangle((x0, z0, x1, z1), fill=c, outline=(0, 0, 0) if new else (175, 175, 175), width=2 if new else 1)
            if new and px >= 14 and p["kind"] != "tile":
                for a in range(p["d"]):
                    for b in range(p["w"]): cx, cz = x0 + (a + .5) * px, z0 + (b + .5) * px; d.ellipse((cx - px * .3, cz - px * .3, cx + px * .3, cz + px * .3), outline=(0, 0, 0))
            if new and px >= 14: d.text((x0 + 3, z0 + 2), str(p["id"]), fill=(0, 0, 0))
    if crop: img = img.crop(crop)
    return img

def b64(img): b = io.BytesIO(); img.save(b, "PNG"); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()

def build_notice(model, cg, outdir, name, renders=None, extra=None):
    os.makedirs(outdir, exist_ok=True); N = model["N"]; rb = rb_colours(); P = model["parts"]; import numpy as np
    order = sorted(cg["classes"], key=lambda c: -int((cg["grid"] == cg["classes"].index(c)).sum())); steps = steps_of(model, order); H = []
    css = "body{font:12px system-ui,sans-serif;margin:0}.pg{break-after:page;padding:3mm;height:172mm;box-sizing:border-box;overflow:hidden}h1{font-size:22px;margin:0 0 6px}h2{font-size:16px;margin:0 0 6px}table{border-collapse:collapse}td,th{border:1px solid #bbb;padding:2px 6px;text-align:left}.sw{display:inline-block;width:11px;height:11px;border:1px solid #333;vertical-align:middle;margin-right:4px}.row{display:flex;gap:14px}small{color:#555}.tr{font-size:9px;color:#444;max-height:40mm;overflow:hidden}.sec{background:#222;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px}"
    H.append("<html><head><meta charset='utf-8'><style>%s</style></head><body>" % css)
    cover_imgs = "".join("<img src='%s' width=%d>" % (b64(Image.open(renders[k]).resize((w, int(Image.open(renders[k]).height * w / Image.open(renders[k]).width)))), w) for k, w in (("face", 400), ("trois_quarts", 460)) if renders and k in renders)
    H.append("<div class='pg'><h1>%s - tableau LEGO en relief, finition %s</h1><p>Champ cartographique <b>%d x %d tenons (%.0f x %.0f mm)</b>, cadre de %d tenon(s) : tableau complet %d x %d tenons (%.0f mm), epaisseur %.1f mm. <b>%d pieces</b>, %d references, <b>%d etapes</b> de %d pieces au plus, en trois sections : <span class='sec'>Dos</span> <span class='sec'>Relief</span> <span class='sec'>Cadre</span>.</p><div class='row'>%s</div>"
             "<p><b>Avertissements.</b> Sequence de montage <i>numerique</i> (pose couche par couche, verifiee : 0 collision, 0 piece deconnectee) ; <b>aucun montage physique n'a ete realise</b>. Relief <b>artistique</b>, pas des altitudes. Masse estimee %s g (hypotheses dans validation). Aucune fixation murale n'est declaree sure : non testee. Prix et stocks : <b>non verifies</b> (Briquestore), laisses vides.</p></div>"
             % (name, model["finish"], model["n"], model["n"], model["n"] * 8, model["n"] * 8, model["m"], N, N, N * 8, (max(p["zbot"] + p["h"] for p in P)) * 3.2, len(P), len({(p["part"], p["colour"]) for p in P}), len(steps), MAX_STEP, cover_imgs, (extra or {}).get("masse", "?")))
    reg = Image.fromarray(np.kron(np.array([[cg["colour"][cg["classes"][v]] for v in row] for row in cg["grid"]], "uint8"), np.ones((12, 12, 1), "uint8")))
    leg = "".join("<tr><td><span class='sw' style='background:rgb(%d,%d,%d)'></span>%s</td><td>%d cellules</td><td>niveau %d</td><td><span class='sw' style='background:rgb(%d,%d,%d)'></span>%s (%d)</td><td>%.1f / %.1f</td></tr>" % (*[int(v) for v in cg["colour"][c]], c, int((cg["grid"] == i).sum()), int(model["heights"][cg["grid"] == i][0]) if (cg["grid"] == i).any() else 0, *model["colours"][c]["rgb"], model["colours"][c]["name"], model["colours"][c]["code"], model["colours"][c]["dE00"], model["colours"][c]["dE76"]) for i, c in enumerate(cg["classes"]))
    H.append("<div class='pg'><h2>Regions reconnues et couleurs LEGO (valeurs reelles)</h2><div class='row'><img src='%s' width=384><table><tr><th>region (couleur source)</th><th>surface</th><th>relief</th><th>couleur LEGO</th><th>dE2000 / dE76</th></tr>%s</table></div></div>" % (b64(reg), leg))
    c = Counter((p["part"], p["colour"], p["size"], p["kind"], p["layer"][0]) for p in P)
    rows = "".join("<tr><td>%s</td><td>%s %s</td><td><span class='sw' style='background:rgb(%d,%d,%d)'></span>%s (%d)</td><td>%s</td><td>%d</td></tr>" % (num, sz, kind, *rgb(col), rb[col]["name"], col, {"B": "dos", "L": "relief", "F": "cadre"}[sec], q) for (num, col, sz, kind, sec), q in sorted(c.items(), key=lambda kv: ({"B": 0, "L": 1, "F": 2}[kv[0][4]], -kv[1], kv[0])))
    H.append("<div class='pg'><h2>Nomenclature (%d pieces)</h2><div style='columns:2;font-size:9px'><table><tr><th>ref</th><th>taille / type</th><th>couleur</th><th>section</th><th>qte</th></tr>%s</table></div><small>Prix et stock : non verifies (colonnes vides dans parts_list.csv).</small></div>" % (len(P), rows))
    for i, s in enumerate(steps):
        full = draw(model, steps, i); ps = s["parts"]; x0 = min(p["z"] for p in ps); x1 = max(p["z"] + p["d"] for p in ps); z0 = min(p["x"] for p in ps); z1 = max(p["x"] + p["w"] for p in ps)
        cx, cz = (x0 + x1) / 2, (z0 + z1) / 2; half = max(8, (max(x1 - x0, z1 - z0)) / 2 + 2); zoom = draw(model, steps, i, px=26, crop=(int(max(0, cx - half) * 26), int(max(0, cz - half) * 26), int(min(N, cx + half) * 26), int(min(N, cz + half) * 26)))
        cnt = Counter((p["part"], p["colour"], p["size"], p["kind"]) for p in ps)
        t = "".join("<tr><td>%dx</td><td>%s</td><td>%s %s</td><td><span class='sw' style='background:rgb(%d,%d,%d)'></span>%s</td></tr>" % (q, num, sz, kind, *rgb(col), rb[col]["name"]) for (num, col, sz, kind), q in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0])))
        tr = "; ".join("#%d (col %d, ligne %d)" % (p["id"], p["z"], p["x"]) for p in ps)
        H.append("<div class='pg'><span class='sec'>%s</span> <b style='font-size:16px'>Etape %d / %d - %s</b><div class='row' style='margin-top:6px'><div><img src='%s' height=330><br><small>Vue d'ensemble</small></div><div><img src='%s' height=330><br><small>Gros plan : pieces a poser en couleur, deja posees en pale</small></div><div><p><b>%d piece(s).</b></p><table><tr><th>qte</th><th>ref</th><th>taille</th><th>couleur</th></tr>%s</table></div></div><p class='tr'>Tracabilite : %s</p></div>" % (s["section"], i + 1, len(steps), s["title"], b64(full), b64(zoom), len(ps), t, tr))
    H.append("</body></html>"); html = os.path.join(outdir, "notice.html"); open(html, "w", encoding="utf-8").write("".join(H))
    subprocess.run(["node", os.path.join(ROOT, "engine", "html2pdf.js"), html, os.path.join(outdir, "notice.pdf")], check=True, capture_output=True, env=dict(os.environ, NODE_PATH=NODE_MODULES))
    json.dump([dict(etape=i + 1, section=s["section"], titre=s["title"], region=s["region"], couche=s["layer"], pieces=[p["id"] for p in s["parts"]]) for i, s in enumerate(steps)], open(os.path.join(outdir, "etapes.json"), "w"), indent=1)
    os.remove(html); return steps
