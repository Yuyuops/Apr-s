#!/usr/bin/env python3
"""Product V1 (Beagle) : the customer-facing build instructions (PDF, text-searchable, one page per step) composed from the VALIDATED engine plan and the engine's own step renders.
Nothing is re-planned here : the order of the steps, the parts of every step and the engine's insertion checks come from the engine plan (notice_plan.py, V10+) ; the step pictures are the engine's three.js renders of the real LDraw part shapes
(pale = already built, colour = to add, sub-assemblies drawn apart). This script only (1) maps plan -> real parts/colours through the LDraw file, (2) lays the pages out with correct titles (the engine's own title page says "Paco" : it is NOT used),
(3) adds cover, reading guide, full parts list with swatches, plan of the notice and finished-model pages.
usage : product_notice_v1.py PLAN.json MAP.json NOTICE.ldr STEPS_PNG_DIR CATALOGUE.csv RB.db RENDERS_DIR OUT.pdf OUT_STEPS.csv OUT_REPORT.json [--sha SHA]"""
import csv, io, json, sqlite3, sys, collections
from PIL import Image, ImageChops
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
plan_f, map_f, ldr_f, png_dir, cat_f, rb_f, ren_dir, out_pdf, out_csv, out_rep = sys.argv[1:11]; SHA = sys.argv[sys.argv.index("--sha") + 1] if "--sha" in sys.argv else ""
plan = json.load(open(plan_f))["plan"]; pos = {int(k): v for k, v in json.load(open(map_f)).items()}
lines = [l.split() for l in open(ldr_f) if l.startswith("1 ")]                      # scene index = order of the part lines
cat = {(r["part"], int(r["ldraw_colour"])): r for r in csv.DictReader(open(cat_f))}
db = sqlite3.connect(rb_f); cname = {}; crgb = {}
for (i, n, rgb) in db.execute("select id,name,rgb from colors"): cname[i] = n; crgb[i] = rgb
def pcol(s): return (s[-1][:-4], int(s[1]))
total = len(plan); W, H = A4; TOTALP = len(lines); steps = []; placed = 0; ylo = min(float(l[3]) for l in lines); layer_of = lambda y: int(round((-y) / 8.0)); NL = max(layer_of(float(l[3])) for l in lines)
for k, st in enumerate(plan):
    ps = [pcol(lines[pos[i]]) for i in st["parts"]]; c = collections.Counter(ps); ys = [layer_of(float(lines[pos[i]][3])) for i in st["parts"]]
    steps.append(dict(n=k + 1, kind=st["kind"], module=st["module"], parts=c, pieces=len(ps), layers=(min(ys), max(ys)), checks=st["checks"], attach=st.get("attach")))
def dir_words(v):                                              # Beagle : the head is on the +Z side of the LDraw file (face details have z > model centre), so +Z = front of the dog, -Z = rear
    v = [round(x, 1) for x in v]; names = {(0, 1, 0): "vers le bas", (0, -1, 0): "vers le haut (par en dessous : soutenez ou retournez le modèle)", (1, 0, 0): "vers +X du fichier LDraw", (-1, 0, 0): "vers -X du fichier LDraw", (0, 0, 1): "vers l'avant du chien (vers la tête)", (0, 0, -1): "vers l'arrière du chien (on enfonce la pièce depuis le museau, en direction de la queue)"}
    return names.get(tuple(abs(x) if x == 0 else x for x in v), "dans une direction oblique (voir l'image)")
def note(s):
    ch = s["checks"]; out = []
    if s["kind"] == "sub": return ["Construire cette pièce ou ce sous-ensemble À PART, sur la table : il ne se fixe pas encore au modèle (voir l'étape suivante)."]
    if s["kind"] == "attach":
        m = (s["attach"] or {}).get("motion")
        return ["Fixer ce sous-ensemble sur le modèle en le poussant %s (il est dessiné décalé sur l'image pour montrer le sens)." % (dir_words(m) if m else "dans le sens indiqué par l'image")]
    poses = sum(1 for c in ch if c.get("flag") == "pose"); joints = [c for c in ch if c.get("flag") != "pose"]
    if poses: out.append("%d pièce(s) se POSENT simplement sur un appui (sans emboîtement) : elles seront verrouillées par la couche suivante." % poses)
    if joints:
        dirs = collections.Counter(dir_words(c["motion"]) if c.get("motion") else "par un chemin avec virages (voir l'image)" for c in joints)
        out.append("%d pièce(s) à EMBOÎTER en les poussant %s." % (len(joints), " ; ".join("%d %s" % (n, d) if len(dirs) > 1 else d for d, n in dirs.items())))
    return out
def crop(path):
    im = Image.open(path).convert("RGB"); bg = Image.new("RGB", im.size, (255, 255, 255)); bb = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 8 else 0).getbbox()
    if bb: m = 14; bb = (max(0, bb[0] - m), max(0, bb[1] - m), min(im.width, bb[2] + m), min(im.height, bb[3] + m)); im = im.crop(bb)
    return im
def jpg(im, q=80, maxw=1300):
    if im.width > maxw: im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=q); b.seek(0); return ImageReader(b)
hexc = lambda h: tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
cv = canvas.Canvas(out_pdf, pagesize=A4); cv.setTitle("Beagle - LEGO Builder V1 - Notice de construction"); cv.setAuthor("LEGO Builder"); cv.setSubject("Beagle V1, %d pièces, %d étapes" % (TOTALP, total))
pageno = [0]
def foot(extra=""):
    pageno[0] += 1; cv.setFont("Helvetica", 7); cv.setFillGray(0.4)
    cv.drawString(36, 22, "LEGO Builder - Beagle V1 - modèle LDraw SHA-256 %s - validation numérique, pas de test physique%s" % (SHA[:12], extra)); cv.drawRightString(W - 36, 22, "page %d" % pageno[0]); cv.setFillGray(0)
def text(x, y, s, size=10, bold=False, color=None):
    cv.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    if color: cv.setFillColorRGB(*color)
    cv.drawString(x, y, s); cv.setFillGray(0)
def para(x, y, lines_, size=9.5, lead=13, width=520):
    for ln in lines_:
        words = ln.split(); cur = ""
        for w in words:
            if cv.stringWidth(cur + " " + w, "Helvetica", size) > width: text(x, y, cur, size); y -= lead; cur = w
            else: cur = (cur + " " + w).strip()
        text(x, y, cur, size); y -= lead
    return y
def swatch(x, y, ci, s=9):
    cv.setFillColorRGB(*hexc(crgb.get(ci, "888888"))); cv.setStrokeGray(0.3); cv.rect(x, y - 1, s, s, fill=1, stroke=1); cv.setFillGray(0)
total_qty = collections.Counter()
for s in steps:
    if s["kind"] != "attach":
        for k, q in s["parts"].items(): total_qty[k] += q
bom = sorted(total_qty.items(), key=lambda kv: (-kv[1], kv[0][0], kv[0][1])); rarity = {}
for (p, c), r in cat.items(): rarity[(p, c)] = int(r["sets"])
R = lambda n: Image.open("%s/%s" % (ren_dir, n)).convert("RGB")
# ---------- cover
cv.setFont("Helvetica-Bold", 30); cv.drawString(36, H - 70, "Beagle"); cv.setFont("Helvetica", 14); cv.drawString(36, H - 92, "Notice de construction - LEGO Builder V1")
im = R("Beagle_V1_trois_quarts.png"); cw = W - 72; ch = cw * im.height / im.width; cv.drawImage(jpg(im, 85, 1600), 36, H - 110 - ch, cw, ch)
y = H - 130 - ch; cv.setFont("Helvetica-Bold", 12); cv.drawString(36, y, "Ce que vous allez construire"); y -= 18
facts = ["%d pièces au total, %d références (une pièce dans une couleur), %d formes de pièces différentes, %d couleurs." % (TOTALP, len(bom), len({k[0] for k, _ in bom}), len({k[1] for k, _ in bom})), "%d étapes numérotées dans l'ordre de montage (étape 1 sur %d)." % (total, total), "Hauteur du modèle fini : 40 cm environ ; masse estimée 5,3 kg (calcul théorique, non pesé).",
         "Modèle validé NUMÉRIQUEMENT (0 collision, 0 pièce déconnectée, 0 îlot). Il n'a PAS encore été construit en vrai : si une étape vous semble ambiguë, notez le numéro d'étape.", "Fichier modèle LDraw de référence : SHA-256 %s." % SHA]
y = para(36, y, facts, 10, 14); foot()
cv.showPage()
# ---------- how to read
text(36, H - 60, "Comment lire cette notice", 20, True); y = H - 90
rd = ["Chaque page = une étape. En haut : le numéro d'étape et l'avancement (pièces déjà posées sur %d)." % TOTALP, "L'image montre le modèle en cours : les pièces PÂLES sont déjà posées ; les pièces EN COULEUR sont celles à ajouter à cette étape.",
      "La liste « Pièces à ajouter » donne la quantité, le nom de la pièce, son numéro (le même que dans la nomenclature, ex. 3024), et sa couleur avec un échantillon.", "Sous l'image, une phrase indique comment poser les pièces : « se POSENT » = simplement posées sur un appui ; « à EMBOÎTER » = à pousser sur les tenons, dans le sens indiqué.",
      "Les étapes « Construire à part » (13 petits détails du visage) se réalisent sur la table ; l'étape suivante « Fixer sur le modèle » les emboîte sur le modèle, dessiné décalé pour montrer le sens.", "L'image est cadrée sur la zone en cours : pour savoir où vous êtes dans le chien, comparez avec les vues du modèle fini (page suivante) ; l'angle de vue est le même pour toutes les étapes (proche de la vue « Trois-quarts avant » de la page des vues du modèle fini).",
      "Préparez d'abord les pièces par COULEUR puis par numéro avec la liste des pièces (pages suivantes) : les %d références sont en %d couleurs seulement." % (len(bom), len({k[1] for k, _ in bom})), "Les contrôles de la notice (emboîtement, dégagement, collisions) sont NUMÉRIQUES : aucune construction réelle n'a encore été faite."]
y = para(36, y, ["- " + r for r in rd], 10, 14.5); text(36, y - 8, "Conseil : travaillez couche par couche, vérifiez chaque étape avant de passer à la suivante.", 10, True); foot(); cv.showPage()
# ---------- parts list
def parts_page(chunk, first):
    text(36, H - 55, "Liste des pièces" + ("" if first else " (suite)"), 18, True); text(36, H - 72, "Total : %d pièces, %d références. ! = pièce/couleur présente dans 30 sets Rebrickable ou moins (à chercher en priorité). Aucun prix ni stock n'est fourni." % (TOTALP, len(bom)), 8)
    yy = H - 100; text(36, yy, "Qté", 8, True); text(78, yy, "Couleur", 8, True); text(170, yy, "N°", 8, True); text(215, yy, "Nom de la pièce", 8, True); text(470, yy, "Rareté", 8, True); yy -= 15
    for ((p, c), q) in chunk:
        swatch(36 + 0, yy, c); text(50, yy, "%d" % q, 9, True); text(78, yy, cname[c], 8.5); text(170, yy, p, 8.5); text(215, yy, cat[(p, c)]["name"].replace("  ", " "), 8.5); sets = rarity[(p, c)]
        text(470, yy, ("! rare (%d sets)" % sets) if sets <= 30 else ("peu courante (%d)" % sets if sets <= 100 else "courante"), 8, sets <= 30); yy -= 15.5
    foot(); cv.showPage()
for i in range(0, len(bom), 40): parts_page(bom[i:i + 40], i == 0)
# ---------- plan of the notice
text(36, H - 60, "Plan de la notice", 20, True); blocks = []
for s in steps:
    key = (s["kind"], s["module"] if s["kind"] != "main" else "Corps")
    if blocks and blocks[-1][0] == key and blocks[-1][2] == s["n"] - 1: blocks[-1][2] = s["n"]
    else: blocks.append([key, s["n"], s["n"]])
yy = H - 95; text(36, yy, "Étapes", 9, True); text(130, yy, "Contenu", 9, True); yy -= 14
for (kind, mod), a, b in blocks:
    lab = {"main": "Corps du chien (couche après couche, des pieds vers la tête)", "sub": "À part : " + mod, "attach": "Fixer : " + mod}[kind]
    text(36, yy, "%d" % a if a == b else "%d - %d" % (a, b), 9); text(130, yy, lab, 9); yy -= 13
    if yy < 80: foot(); cv.showPage(); yy = H - 60
foot(); cv.showPage()
# ---------- finished model views
text(36, H - 60, "Le modèle terminé : repères pour s'orienter", 18, True); gw = (W - 90) / 2; yy = H - 80
for i, (n, lab) in enumerate((("face", "Face"), ("dos", "Dos"), ("profil_gauche", "Profil gauche"), ("profil_droit", "Profil droit"), ("trois_quarts", "Trois-quarts avant"), ("trois_quarts_arriere", "Trois-quarts arrière"))):
    im = R("Beagle_V1_%s.png" % n); im = im.crop(ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).convert("L").point(lambda v: 255 if v > 8 else 0).getbbox()); r_ = min(gw / im.width, 205 / im.height); x = 36 + (i % 2) * (gw + 18); y0 = yy - 12 - (i // 2) * 238 - im.height * r_
    cv.drawImage(jpg(im, 85), x, y0, im.width * r_, im.height * r_); text(x, y0 - 12, lab, 9, True)
foot(); cv.showPage()
# ---------- step pages
rows = []; placed = 0
for s in steps:
    n = s["n"]; text(36, H - 50, "Étape %d / %d" % (n, total), 24, True)
    title = {"main": "Corps du Beagle", "sub": "Construire à part : " + s["module"], "attach": "Fixer sur le modèle : " + s["module"]}[s["kind"]]; text(36, H - 70, title, 12, True, (0.1, 0.1, 0.1))
    if s["kind"] == "main": text(36, H - 84, "Niveau d'assemblage : couche %d%s sur %d" % (s["layers"][0], "" if s["layers"][0] == s["layers"][1] else " à %d" % s["layers"][1], NL), 9, False, (0.35, 0.35, 0.35))
    if s["kind"] != "attach": placed += s["pieces"]
    bw = W - 72; cv.setStrokeGray(0.8); cv.rect(36, H - 94 - 8, bw, 8, fill=0, stroke=1); cv.setFillColorRGB(0.1, 0.4, 0.8); cv.rect(36, H - 102, bw * placed / TOTALP, 8, fill=1, stroke=0); cv.setFillGray(0)
    text(W - 36 - 150, H - 112, "pièces posées : %d / %d" % (placed, TOTALP), 8, False, (0.3, 0.3, 0.3))
    im = crop("%s/s%03d.png" % (png_dir, n)); maxw, maxh = bw, 430; r_ = min(maxw / im.width, maxh / im.height); iw, ih = im.width * r_, im.height * r_; ytop = H - 120
    cv.drawImage(jpg(im, 82, 1200), 36 + (bw - iw) / 2, ytop - ih, iw, ih); yy = ytop - max(ih, 200) - 22
    text(36, yy, "Pièces à ajouter : %d" % s["pieces"] if s["kind"] != "attach" else "Sous-ensemble à fixer : %d pièce(s)" % s["pieces"], 12, True, (0.0, 0.2, 0.6)); yy -= 16
    items = sorted(s["parts"].items(), key=lambda kv: (-kv[1], kv[0])); colx = [36, 310]; per = 12
    for j, ((p, c), q) in enumerate(items):
        x = colx[j // per] if j < 2 * per else colx[1]; y_ = yy - (j % per) * 14.5
        swatch(x, y_, c); text(x + 14, y_, "%d ×  %s  (%s)  %s" % (q, cat[(p, c)]["name"].replace("  ", " "), p, cname[c]), 8.8)
    yy -= min(len(items), per) * 14.5 + 10
    para(36, yy, note(s), 9, 12.5, bw)
    foot("  -  étape %d" % n); cv.showPage()
    rows.append(dict(etape=n, type=s["kind"], module=s["module"], pieces=s["pieces"], references=" ".join("%dx%s@%d" % (q, p, c) for (p, c), q in sorted(s["parts"].items(), key=lambda kv: (-kv[1], kv[0]))), couche_min=s["layers"][0], couche_max=s["layers"][1]))
# ---------- closing page
text(36, H - 60, "Terminé !", 26, True); im = R("Beagle_V1_trois_quarts.png"); im = im.crop(ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).convert("L").point(lambda v: 255 if v > 8 else 0).getbbox()); r_ = min((W - 72) / im.width, 420 / im.height)
cv.drawImage(jpg(im, 85), 36, H - 90 - im.height * r_, im.width * r_, im.height * r_); yy = H - 110 - im.height * r_
yy = para(36, yy, ["Comparez votre Beagle avec les vues de la page « Le modèle terminé ». Vérifiez : 4 pattes au sol, queue relevée, oreilles tombantes, détails du visage fixés (13 petits éléments).", "Total posé : %d pièces (doit être égal à %d)." % (placed, TOTALP), "Ce modèle a été validé numériquement uniquement ; merci de signaler toute étape ambiguë ou toute pièce introuvable (fiche de validation humaine fournie)."], 10.5, 15); foot(); cv.showPage()
cv.save()
with open(out_csv, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
front = 1 + 1 + (len(bom) + 39) // 40 + 1 + 1                                              # cover, reading guide, parts list pages, plan, finished views
json.dump(dict(steps=total, pieces_placed=placed, pieces_total=TOTALP, bom_lines=len(bom), front_matter_pages=front, pages=front + total + 1, layers=NL, sub_assembly_steps=sum(1 for s in steps if s["kind"] == "sub"), attach_steps=sum(1 for s in steps if s["kind"] == "attach"), main_steps=sum(1 for s in steps if s["kind"] == "main")), open(out_rep, "w"), indent=1)
print(json.dumps(json.load(open(out_rep))))
