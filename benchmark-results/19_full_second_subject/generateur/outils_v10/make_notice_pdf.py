"""LEGO V9 - illustrated notice (PDF) from the plan of notice_plan.py : one page per step, real LDraw part shapes, parts to add, new parts in colour,
parts already built pale, sub-assemblies drawn apart and exploded along their engagement direction, insertion checks of the step.
usage: make_notice_pdf.py <plan.json> <notice.ldr> <map.json> <outdir> <name>"""
import json, os, subprocess, sys
import numpy as np
from collections import Counter, defaultdict
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.expanduser("~/bench/tools"))
import partlib as PL, conn
HERE = os.path.dirname(os.path.abspath(__file__))
def font(sz, bold=False):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""), sz)
    except OSError: return ImageFont.load_default()
EXPLODE_LDU = 200.0; EXPLODE_PART = 140.0

def direction_words(v):
    v = np.asarray(v, float)
    if np.linalg.norm(v) < 0.5: return "par un chemin avec virages"
    names = {(0, -1, 0): "vers le haut", (0, 1, 0): "vers le bas", (1, 0, 0): "vers +X", (-1, 0, 0): "vers -X", (0, 0, 1): "vers +Z", (0, 0, -1): "vers -Z"}
    for k, n in names.items():
        if np.allclose(v, k, atol=0.15): return n
    return "dans la direction (%.1f ; %.1f ; %.1f)" % tuple(v)

def main():
    planf, ldr, mapf, out, name = sys.argv[1:6]; os.makedirs(out, exist_ok=True)
    D = json.load(open(planf)); plan = D["plan"]; pos = {int(k): v for k, v in json.load(open(mapf)).items()}
    ldraw = os.path.expanduser("~/bench/ldraw-parts-library/complete/ldraw")
    sj = os.path.join(out, "scene.json")
    subprocess.run([sys.executable, os.path.expanduser("~/bench/tools/ldr_expand.py"), "--ldr", ldr, "--ldraw", ldraw, "--json", sj, "--glb", os.path.join(out, "scene.glb")], check=True, capture_output=True)
    S = json.load(open(sj)); cols = S["colours"]; SP = S["parts"]
    # lo/hi (mm) of each part of the scene (box of the part), from the scene matrices
    def box_mm(k):
        p = SP[k]; num = p["p"].replace(".dat", ""); M = np.array(p["M"]).reshape(3, 3); o = np.array(p["o"])
        st, rc, lo, hi = conn.world(num, M, o)
        a = np.array([lo[0] * 0.4, -hi[1] * 0.4, -hi[2] * 0.4]); b = np.array([hi[0] * 0.4, -lo[1] * 0.4, -lo[2] * 0.4]); return a, b
    views = []; meta = []
    main_set = []; level = defaultdict(list)
    for k, st in enumerate(plan):
        parts = [pos[i] for i in st["parts"]]; label = st["module"]; top = label.split(" > ")[0]; unit = " > " in label
        items = []; offset = None
        if st["kind"] == "main":
            items = [(j, "old") for j in main_set] + [(j, "new") for j in parts]; main_set += parts
        elif st["kind"] == "sub":
            ear = label.startswith("Oreille"); new_items = []
            for idx, j in enumerate(parts):
                mo = st["checks"][idx].get("motion") if ear else None
                new_items.append((j, "new", (-np.array(mo) * EXPLODE_PART).tolist()) if mo is not None else (j, "new"))
            items = [(j, "old") for j in level[label]] + new_items; level[label] += parts
        else:
            m = st["attach"]["motion"] if st.get("attach") else None
            off = (-np.array(m) * EXPLODE_LDU).tolist() if m is not None else [0, -EXPLODE_LDU, 0]
            if unit:
                ctx = level[top]; items = [(j, "old") for j in ctx] + [(j, "new", off) for j in parts]; level[top] += parts
            else:
                items = [(j, "old") for j in main_set] + [(j, "new", off) for j in parts]; main_set += parts
        newp = [j for j in parts]
        bx = [box_mm(j) for j in newp]
        lo = np.min([b[0] for b in bx], 0); hi = np.max([b[1] for b in bx], 0)
        if st["kind"] == "attach":
            o = np.array(items[-1][2]) * 0.4 * np.array([1, -1, -1]); lo = np.minimum(lo, lo + o); hi = np.maximum(hi, hi + o)
        elif st["kind"] == "sub":
            for it_, (a_, b_) in zip([x for x in items if x[1] == "new"], bx):
                if len(it_) > 2:
                    o = np.array(it_[2]) * 0.4 * np.array([1, -1, -1]); lo = np.minimum(lo, a_ + o); hi = np.maximum(hi, b_ + o)
        if st["kind"] == "attach" and unit:
            ob = [box_mm(it_[0]) for it_ in items if it_[1] == "old"]
            if ob: lo = np.minimum(lo, np.min([b_[0] for b_ in ob], 0)); hi = np.maximum(hi, np.max([b_[1] for b_ in ob], 0))
        ctr = (lo + hi) / 2; half = np.maximum((hi - lo) / 2 + 45, 60)
        h = float(max(half)); fb = [(ctr - h).tolist(), (ctr + h).tolist()]
        views.append(dict(name="s%03d" % (k + 1), az=215, el=30, w=860, h=860, frameBox=fb, edges=True, items=items))
        meta.append(dict(i=k, label=label, kind=st["kind"], section=st["section"]))
    vf = os.path.join(out, "views.json"); json.dump(views, open(vf, "w"))
    rend = os.path.join(out, "r"); os.makedirs(rend, exist_ok=True)
    env = dict(os.environ, NODE_PATH=os.path.expanduser("~/bench/tools/node_modules"))
    if len([f for f in os.listdir(rend) if f.startswith("s") and f.endswith(".png")]) < len(views):
        subprocess.run(["node", os.path.expanduser("~/bench/tools/render_steps.js"), sj, vf, rend], check=True, capture_output=True)
    # ---------------------------------------------------------------- pages
    W, H = 1000, 1414; pages = defaultdict(list)
    def bucket(label, k):
        t = label.split(" > ")[0]
        return ("1a_corps_etapes_1_a_%d" % NCUT if k < NCUT else "1b_corps_etapes_%d_a_fin" % (NCUT + 1)) if t == "Corps" else "2_bras_et_mains" if t.startswith("Bras") else "3_details_visage" if t.startswith("Detail") else "4_oreilles"
    NCUT = sum(1 for st in plan if st["module"] == "Corps") // 2
    first_of = {}
    for k, st in enumerate(plan): first_of.setdefault(st["module"].split(" > ")[0], k + 1)
    total = len(plan)
    for k, st in enumerate(plan):
        label = st["module"]; pg = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(pg)
        title = {"main": "Corps", "sub": "Construire a part : " + label, "attach": ("Assembler l'unite : " if " > " in label else "Fixer sur le modele : ") + label}[st["kind"]]
        d.text((40, 28), "Etape %d / %d" % (k + 1, total), fill="black", font=font(34, True)); d.text((40, 76), title[:78], fill="#222", font=font(24, True))
        d.text((40, 110), st["section"], fill="#555", font=font(20))
        im = Image.open(os.path.join(rend, "s%03d.png" % (k + 1))).convert("RGB"); im.thumbnail((920, 920)); pg.paste(im, (40, 150))
        y = 1090
        # parts to add (count by part x colour) from the scene
        c2 = Counter()
        for i in st["parts"]:
            sp = SP[pos[i]]; c2[(sp["p"].replace(".dat", ""), sp["c"])] += 1
        if st["kind"] == "attach": d.text((40, y - 34), "Sous-ensemble de %d pieces a pousser %s (montre decale)" % (len(st["parts"]), direction_words(st["attach"]["motion"]) if st.get("attach") and st["attach"].get("motion") else "en place"), fill="#003d99", font=font(20, True))
        else: d.text((40, y - 34), "Pieces a ajouter : %d" % len(st["parts"]), fill="#003d99", font=font(20, True))
        x = 40
        for (num, c), n in sorted(c2.items(), key=lambda kv: -kv[1])[:14]:
            ci = cols.get(str(c), {"hex": "#888888", "name": str(c)})
            d.rectangle([x, y + 2, x + 22, y + 24], fill=ci["hex"], outline="black")
            try: nm = PL.title(num)
            except Exception: nm = num
            d.text((x + 30, y), "%dx %s (%s) %s" % (n, nm.replace("  ", " ")[:34], num, ci["name"].replace("_", " ")), fill="black", font=font(18)); y += 30
            if y > 1330 and x < 500: x = 520; y = 1090
        notes = []
        hold = [c for c in st["checks"] if c.get("tenir") or c.get("stable") is False]
        if hold: notes.append("ATTENTION : A TENIR A LA MAIN - " + (hold[0].get("tenir") or "le sous-ensemble pose n'est pas stable seul a ce stade")[:80])
        if st["kind"] == "sub" and label.startswith("Oreille") and any(c.get("sens") == "par le dessous" for c in st["checks"]):
            notes.append("Emboitement par le dessous : tenir l'oreille en l'air (ou la retourner) pour pousser la piece vers le haut")
        for j, c in enumerate(st["checks"]):
            if not c.get("ok", True): notes.append("ATTENTION : " + c.get("reason", "")[:90])
            elif c.get("reason"): notes.append(c["reason"][:90])
            if len(notes) >= 3: break
        if st["kind"] == "main" or (st["kind"] == "sub" and label.startswith("Oreille")):
            mv = [c for c in st["checks"] if c.get("motion")]
            if mv:
                dirs = Counter(direction_words([-v for v in c["motion"]]) for c in mv); notes.insert(0, "Pieces emboitees " + ", ".join(f"{v} x {k}" for k, v in dirs.items()))
        yy = 1352
        for t in list(dict.fromkeys(notes))[:2]:
            d.text((40, yy), t[:112], fill="#a00000" if t.startswith("ATT") else "#444", font=font(16)); yy += 22
        pages[bucket(label, k)].append(pg)
    # cover
    cov = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(cov)
    d.text((40, 40), "Paco cartoon 400 mm - notice V9.1", fill="black", font=font(42, True))
    d.text((40, 100), "%d pieces, %d etapes. Pieces et ordre : LDraw ordonne, formes officielles LDraw." % (len(SP), total), fill="#333", font=font(22))
    d.text((40, 135), "Chaque etape est verifiee (voir rapport) : emboitement, degagement, collisions, tenons.", fill="#333", font=font(20))
    d.text((40, 165), "Pale = deja construit ; couleur = a ajouter ; un sous-ensemble est montre decale le long de son emboitement.", fill="#333", font=font(20))
    im = Image.open(os.path.join(out, "r", "s%03d.png" % total)).convert("RGB"); im.thumbnail((900, 900)); cov.paste(im, (50, 230))
    y = 1180; d.text((40, y), "Modules (premiere etape) :", fill="#003d99", font=font(22, True)); y += 34
    for t, k in sorted(first_of.items(), key=lambda kv: kv[1])[:14]:
        d.text((60, y), "%3d  %s" % (k, t[:70]), fill="black", font=font(18)); y += 24
    covs = {}
    prec = None
    fj = os.path.join(out, "fragiles.json")
    if os.path.exists(fj):
        F = json.load(open(fj)); prec = Image.new("RGB", (W, H), "white"); dd = ImageDraw.Draw(prec); y = 40
        dd.text((40, y), F["titre"], fill="black", font=font(34, True)); y += 60
        for sect in F["sections"]:
            dd.text((40, y), sect["titre"], fill="#003d99", font=font(24, True)); y += 38
            for ln in sect["lignes"]:
                words = ln.split(); cur = ""
                for w_ in words:
                    if len(cur) + len(w_) + 1 > 92: dd.text((60, y), cur, fill="black", font=font(18)); y += 26; cur = w_
                    else: cur = (cur + " " + w_).strip()
                if cur: dd.text((60, y), cur, fill="black", font=font(18)); y += 30
            y += 18
    for b in sorted(pages):
        path = os.path.join(out, f"{name}_{b}.pdf"); pl = pages[b]
        rgb = [p.convert("RGB") for p in ([cov] + ([prec] if prec is not None else []) if b.startswith("1a") else []) + pl]
        rgb[0].save(path, save_all=True, append_images=rgb[1:], resolution=110, quality=62)
        covs[b] = (path, len(rgb), os.path.getsize(path))
    json.dump({k: dict(pdf=v[0], pages=v[1], octets=v[2]) for k, v in covs.items()}, open(os.path.join(out, "pdf_resume.json"), "w"), indent=1)
    print(json.dumps({k: (v[1], round(v[2] / 1e6, 1)) for k, v in covs.items()}))

if __name__ == "__main__":
    main()
