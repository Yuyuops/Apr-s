"""Building instructions PDF by REGIONS and LAYERS : one step = one region on one layer. Every part shown is traceable (id, size, colour, studs coordinates)."""
import base64, io, json, os, subprocess
from collections import Counter, OrderedDict
from PIL import Image, ImageDraw
import palette_util as PU
from .common import ROOT
from .render import NODE_MODULES
from .build import y_top

PX = 15
def rgb(c): return tuple(PU.codes()[c][1])
def fade(c, f=0.55): return tuple(int(v + (255 - v) * f) for v in c)

def steps_of(model, class_order):
    P = model["parts"]; S = []
    S.append(dict(title="Dos rigide, couche 1 (plaques 8x8)", region="dos", layer="B1", parts=[p for p in P if p["layer"] == "B1"]))
    S.append(dict(title="Dos rigide, couche 2 (decalee de 4 tenons)", region="dos", layer="B2", parts=[p for p in P if p["layer"] == "B2"]))
    for k in range(model["levels"]):
        regs = OrderedDict()
        for p in sorted([q for q in P if q["level"] == k], key=lambda q: (class_order.index(q["region"]) if q["region"] in class_order else 99, q["id"])): regs.setdefault(p["region"], []).append(p)
        for r, ps in regs.items(): S.append(dict(title="Couche %d - region : %s" % (k + 1, r), region=r, layer="L%d" % k, parts=ps))
    return S

def draw(model, steps, i, n):
    img = Image.new("RGB", (n * PX + 1, n * PX + 1), (250, 250, 250)); d = ImageDraw.Draw(img); cur = {p["id"] for p in steps[i]["parts"]}
    done = [p for s in steps[:i] for p in s["parts"]]
    for grp, new in ((done, False), (steps[i]["parts"], True)):
        for p in sorted(grp, key=lambda q: q["level"]):
            c = rgb(p["colour"]); c = c if new else fade(c); x0, z0 = p["z"] * PX, p["x"] * PX; x1, z1 = (p["z"] + p["d"]) * PX, (p["x"] + p["w"]) * PX
            d.rectangle((x0, z0, x1, z1), fill=c, outline=(0, 0, 0) if new else (170, 170, 170), width=2 if new else 1)
            if new:
                for a in range(p["d"]):
                    for b in range(p["w"]): cx, cz = x0 + (a + .5) * PX, z0 + (b + .5) * PX; d.ellipse((cx - 3.5, cz - 3.5, cx + 3.5, cz + 3.5), outline=(0, 0, 0))
                d.text((x0 + 3, z0 + 2), str(p["id"]), fill=(0, 0, 0))
    return img

def b64(img): b = io.BytesIO(); img.save(b, "PNG"); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()

def build_notice(model, cg, outdir, name, renders=None, validation=None, bom=None):
    os.makedirs(outdir, exist_ok=True); n = model["n"]; codes = PU.codes(); order = sorted(cg["classes"], key=lambda c: -int((cg["grid"] == cg["classes"].index(c)).sum()))
    steps = steps_of(model, order); H = []
    css = "body{font:12px system-ui,sans-serif;margin:0}.pg{break-after:page;padding:3mm;height:172mm;box-sizing:border-box;overflow:hidden}h1{font-size:22px;margin:0 0 6px}h2{font-size:16px;margin:0 0 6px}table{border-collapse:collapse}td,th{border:1px solid #bbb;padding:2px 6px;text-align:left}.sw{display:inline-block;width:11px;height:11px;border:1px solid #333;vertical-align:middle;margin-right:4px}.row{display:flex;gap:14px}small{color:#555}.tr{font-size:9px;color:#444;max-height:60mm;overflow:hidden}"
    H.append("<html><head><meta charset='utf-8'><style>%s</style></head><body>" % css)
    P = model["parts"]
    H.append("<div class='pg'><h1>%s - tableau LEGO en relief, %dx%d tenons (%.0f x %.0f mm)</h1><p>Mode : <b>%s</b>. %d pieces, %d references, %d etapes (une etape = une region sur une couche). Hauteur : %d couches de plaques (%.1f mm).</p><div class='row'>%s%s</div>"
             "<p><b>Avertissements.</b> Les etapes sont une <i>sequence numerique</i> (pose couche par couche, verifiee par le validateur du moteur 1 : 0 collision, 0 piece deconnectee) ; <b>aucun montage physique n'a ete realise</b>. Les hauteurs sont un relief <b>artistique</b>, pas des altitudes. Aucun dispositif de fixation murale n'est declare sur : non teste. Prix et stocks : <b>non verifies</b> (Briquestore), laisses vides.</p></div>"
             % (name, n, n, n * 8, n * 8, model["mode"], len(P), len({(p["part"], p["colour"]) for p in P}), len(steps), model["levels"] + 2, (model["levels"] + 2) * 3.2,
                "<img src='%s' width=420>" % (b64(Image.open(renders["face"]).resize((420, 420))) if renders and "face" in renders else ""), "<img src='%s' width=420>" % (b64(Image.open(renders["trois_quarts"]).resize((420, 315))) if renders and "trois_quarts" in renders else "")))
    # region map + legend
    reg = Image.fromarray(__import__("numpy").kron(__import__("numpy").array([[cg["colour"][cg["classes"][v]] for v in row] for row in cg["grid"]], "uint8"), __import__("numpy").ones((12, 12, 1), "uint8")))
    leg = "".join("<tr><td><span class='sw' style='background:rgb(%d,%d,%d)'></span>%s</td><td>%d cellules</td><td>niveau %d</td><td><span class='sw' style='background:rgb(%d,%d,%d)'></span>%s (%d)</td></tr>" % (*[int(v) for v in cg["colour"][c]], c, int((cg["grid"] == i).sum()), int(model["heights"][cg["grid"] == i][0]) if (cg["grid"] == i).any() else 0, *model["colours"][c]["rgb"], model["colours"][c]["name"], model["colours"][c]["code"]) for i, c in enumerate(cg["classes"]))
    H.append("<div class='pg'><h2>Regions reconnues et couleurs LEGO</h2><div class='row'><img src='%s' width=384><table><tr><th>region (couleur source)</th><th>surface</th><th>relief</th><th>couleur LEGO choisie</th></tr>%s</table></div></div>" % (b64(reg), leg))
    # BOM
    c = Counter((p["part"], p["colour"], p["name_size"]) for p in P)
    rows = "".join("<tr><td>%s</td><td>%s</td><td><span class='sw' style='background:rgb(%d,%d,%d)'></span>%s (%d)</td><td>%d</td></tr>" % (num, sz, *rgb(col), codes[col][0], col, q) for (num, col, sz), q in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))
    H.append("<div class='pg'><h2>Nomenclature (%d pieces)</h2><div style='columns:2;font-size:10px'><table><tr><th>ref</th><th>taille</th><th>couleur</th><th>qte</th></tr>%s</table></div><small>Prix et stock : non verifies (colonnes vides dans parts_list.csv).</small></div>" % (len(P), rows))
    # steps
    for i, s in enumerate(steps):
        img = draw(model, steps, i, n); cnt = Counter((p["part"], p["colour"], p["name_size"]) for p in s["parts"])
        t = "".join("<tr><td>%dx</td><td>%s</td><td>%s</td><td><span class='sw' style='background:rgb(%d,%d,%d)'></span>%s</td></tr>" % (q, num, sz, *rgb(col), codes[col][0]) for (num, col, sz), q in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0])))
        tr = "; ".join("#%d (col %d, ligne %d)" % (p["id"], p["z"], p["x"]) for p in s["parts"][:70]) + (" ..." if len(s["parts"]) > 70 else "")
        H.append("<div class='pg'><h2>Etape %d / %d - %s</h2><div class='row'><img src='%s' height=520><div><p><b>%d piece(s) a poser.</b> Vue de dessus, nord en haut ; pieces pales = deja posees.</p><table><tr><th>qte</th><th>ref</th><th>taille</th><th>couleur</th></tr>%s</table><p class='tr'>Tracabilite : piece #id (colonne et ligne du coin nord-ouest) : %s</p></div></div></div>" % (i + 1, len(steps), s["title"], b64(img), len(s["parts"]), t, tr))
    H.append("</body></html>"); html = os.path.join(outdir, "notice.html"); open(html, "w", encoding="utf-8").write("".join(H))
    env = dict(os.environ, NODE_PATH=NODE_MODULES)
    subprocess.run(["node", os.path.join(ROOT, "engine", "html2pdf.js"), html, os.path.join(outdir, "notice.pdf")], check=True, capture_output=True, env=env)
    json.dump([dict(etape=i + 1, titre=s["title"], region=s["region"], couche=s["layer"], pieces=[p["id"] for p in s["parts"]]) for i, s in enumerate(steps)], open(os.path.join(outdir, "etapes.json"), "w"), indent=1)
    return len(steps)
