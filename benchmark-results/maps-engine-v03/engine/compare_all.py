"""Builds results/comparatifs : V0 / A / B tables (island and three-zone map), contour error of the real footprint, side-by-side images. usage: python compare_all.py"""
import json, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageChops
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maps_engine import compare as K, evaluate as E, render as R, common
from maps_engine.common import ROOT, dE2000, lab

RES = os.path.join(ROOT, "results"); OUT = os.path.join(RES, "comparatifs"); os.makedirs(OUT, exist_ok=True); V0 = K.V0
ORACLE = os.path.join(ROOT, "..", "maps-engine-v0", "fixtures", "ile_temoin_oracle.json")
def crop(p, pad=12):
    im = Image.open(p).convert("RGB"); bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox(); return im.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), min(im.width, bb[2] + pad), min(im.height, bb[3] + pad))) if bb else im
def sheet(items, W, path, cols=None):
    ims = []
    for title, p in items:
        im = crop(p) if p.endswith(".png") else Image.open(p); im = im.resize((W, int(im.height * W / im.width))); c = Image.new("RGB", (W, im.height + 26), "white"); c.paste(im, (0, 26)); ImageDraw.Draw(c).text((6, 6), title, fill="black"); ims.append(c)
    cols = cols or len(ims); rows = [ims[i:i + cols] for i in range(0, len(ims), cols)]; H = sum(max(i.height for i in r) for r in rows); S = Image.new("RGB", (W * cols, H), "white"); y = 0
    for r in rows:
        for k, i in enumerate(r): S.paste(i, (k * W, y))
        y += max(i.height for i in r)
    S.save(path); return S.size

# ---- V0 re-rendered with the REAL colour values (V0 files are only read)
v0r = os.path.join(OUT, "V0_couleurs_reelles")
if not os.path.exists(os.path.join(v0r, "face.png")):
    R.render_all(os.path.join(V0, "map.ldr"), v0r, N=32, height_plates=8, zooms={"village": (10, 14, 26, 28)}, w=1200); import shutil; shutil.rmtree(os.path.join(v0r, "_scene"), ignore_errors=True)

res = {}
for ile, label in (("ile_temoin", "ile"), ("test_3_zones", "trois_zones")):
    runs = {"V0": V0 if ile == "ile_temoin" else os.path.join(V0, "test_3_zones"), "A": os.path.join(RES, ile, "A"), "B": os.path.join(RES, ile, "B")}
    if ile == "ile_temoin": runs.update({"A_sans_coins_coupes": os.path.join(RES, ile, "A_sans_coins_coupes"), "A_48x48": os.path.join(RES, ile, "A_48x48")})
    out = {}
    for k, d in runs.items():
        if k == "V0":
            gen = json.load(open(os.path.join(d, "generation.json"))); val = json.load(open(os.path.join(d, "validation", "validation_resume.json"))); m1, m2 = val["moteur1"], val["moteur2"]; steps = json.load(open(os.path.join(d, "etapes.json"))); P = K.v0_parts()
            from maps_engine import validate as Vd
            import json as _j
            Pm = json.load(open(os.path.join(d, "parts.json"))); parts = [dict(part=p["part"], w=p["w"], d=p["d"], h=1, layer=p["layer"], size=p["name_size"]) for p in Pm]; mass, _ = Vd.mass_g(parts)
            R0 = json.load(open(os.path.join(d, "classes_hauteurs.json")))
            row = dict(nom="V0", pieces=gen["pieces"], references=gen["references"], pieces_1x1=gen["pieces_1x1"], part_1x1=gen["part_1x1_share"], couches_de_plaques=len(m2["pieces_par_niveau"]), epaisseur_mm=m2["dimensions_mm"]["hauteur"], masse_g=round(mass), pieces_sur_un_seul_tenon=m2["plaques_attachees_par_1_tenon"], points_articulation=m2["points_d_articulation"],
                       collisions=m1["collisions"], deconnectees=m1["disconnected_parts"], composantes=m2["graphe_pieces"]["composantes"], liaisons=m1["joints"], tenons_engages=m1["studs_engaged"], coupe_noyau_tenons=m2["noyau_dos_et_niveau_mer"]["coupe_minimale_tenons"], etapes=len(steps), pieces_max_par_etape=max(len(s["pieces"]) for s in steps), coins_coupes=0,
                       tableau_complet_mm=256.0, lisibilite=K.class_legibility({**R0, "lego_colours": {nm: dict(v, rgb=list(common.rb_colours()[v["code"]]["rgb"])) for nm, v in R0["lego_colours"].items()}}))
        else: row = K.summarize(d, k); R0 = json.load(open(os.path.join(d, "classes_hauteurs.json")))
        # colour fidelity against the REAL colour values (V0 re-measured), fidelity of classes
        if ile == "ile_temoin":
            Rm = dict(R0)
            if k == "V0": Rm["lego_colours"] = {nm: dict(v, rgb=list(common.rb_colours()[v["code"]]["rgb"])) for nm, v in R0["lego_colours"].items()}
            ev = E.evaluate_from = E.evaluate(os.path.join(d, "classes_hauteurs.json") if k != "V0" else os.path.join(d, "classes_hauteurs.json"), ORACLE, None) if k != "V0" else None
            if k == "V0":
                tmp = os.path.join(OUT, "_v0_real.json"); json.dump(Rm, open(tmp, "w")); ev = E.evaluate(tmp, ORACLE, None); os.remove(tmp)
            row.update(iou_cellules_moyen=ev["iou_cellules_moyen"], iou_pixels_moyen=ev["iou_pixels_moyen"], dE76=ev["dE76_moyen_pondere_surface"], dE2000=ev["dE2000_moyen_pondere_surface"], hauteurs_identiques=ev["hauteurs"]["cellules_identiques"], deplacement_contour_grille_mm=ev["deplacement_contour_moyen_mm"],
                       rapport_surface_riviere=ev["classes"]["riviere"]["rapport_surface_moteur_sur_oracle"], rapport_surface_route=ev["classes"]["route"]["rapport_surface_moteur_sur_oracle"], composantes_riviere=ev["composantes_connexes_8"]["riviere"]["moteur"], classes=ev["classes"], couleurs=ev["couleurs_reelles"])
            P = json.load(open(os.path.join(d, "parts.json"))); m = 0 if k == "V0" else json.load(open(os.path.join(d, "classes_hauteurs.json")))["frame_width"]; nn = 32 if k != "A_48x48" else 48
            if k == "V0": P = [dict(p, x=p["z"], z=p["x"]) if False else p for p in P]
            mask = K.footprint_mask(P, m, nn, "L1"); g = np.array(json.load(open(os.path.join(d, "classes_hauteurs.json")))["grid"]); cl = json.load(open(os.path.join(d, "classes_hauteurs.json")))["classes"]; wc = np.isin(np.array(cl, dtype=object)[g], ["lac", "riviere"]); row["contour_reel_terre"] = K.land_contour_error(mask, ORACLE, wc)
        else:
            ref = {"mer": "#315c9c", "terre": "#e6d1a2", "foret": "#568451"}
            png = os.path.join(d, "input.png") if k != "V0" else os.path.join(d, "input.png")
            Rm = dict(R0)
            if k == "V0": Rm["lego_colours"] = {nm: dict(v, rgb=list(common.rb_colours()[v["code"]]["rgb"])) for nm, v in R0["lego_colours"].items()}
            tmp = os.path.join(OUT, "_r.json"); json.dump(Rm, open(tmp, "w")); ev = E.evaluate_by_source_colours(tmp, png, ref); os.remove(tmp)
            row.update(iou_cellules_moyen=ev["iou_cellules_moyen"], iou_pixels_moyen=ev["iou_pixels_moyen"], dE76=ev["dE76_moyen_pondere_surface"], dE2000=ev["dE2000_moyen_pondere_surface"], couleurs=ev["couleurs_reelles"], classes=ev["classes"])
        out[k] = row
    res[label] = out
json.dump(res, open(os.path.join(OUT, "comparaison_V0_A_B.json"), "w"), indent=1, ensure_ascii=False, default=str)
# ---- side-by-side sheets
src = os.path.join(RES, "ile_temoin", "A", "input.png")
for kind in ("face", "trois_quarts"):
    sheet([("Source", src), ("V0 (rendu d'origine, couleurs LDraw)", os.path.join(V0, "renders", kind + ".png")), ("V0 (memes pieces, couleurs reelles)", os.path.join(v0r, kind + ".png")), ("V0.1 A : LEGO apparent", os.path.join(RES, "ile_temoin", "A", "renders", kind + ".png")), ("V0.1 B : tableau premium", os.path.join(RES, "ile_temoin", "B", "renders", kind + ".png"))], 560, os.path.join(OUT, "cote_a_cote_%s.png" % kind), cols=5)
sheet([("V0.1 A : LEGO apparent", os.path.join(RES, "ile_temoin", "A", "renders", "face.png")), ("V0.1 B : tableau premium", os.path.join(RES, "ile_temoin", "B", "renders", "face.png"))], 900, os.path.join(OUT, "A_vs_B_dessus.png"))
sheet([("V0.1 A : LEGO apparent", os.path.join(RES, "ile_temoin", "A", "renders", "trois_quarts.png")), ("V0.1 B : tableau premium", os.path.join(RES, "ile_temoin", "B", "renders", "trois_quarts.png"))], 900, os.path.join(OUT, "A_vs_B_trois_quarts.png"))
sheet([("V0.1 A : profil", os.path.join(RES, "ile_temoin", "A", "renders", "profil.png")), ("V0.1 B : profil", os.path.join(RES, "ile_temoin", "B", "renders", "profil.png"))], 1200, os.path.join(OUT, "A_vs_B_profil.png"), cols=1)
for z in ("village", "sommet", "lac"):
    sheet([("A : %s (dessus)" % z, os.path.join(RES, "ile_temoin", "A", "renders", "zoom_%s.png" % z)), ("B : %s (dessus)" % z, os.path.join(RES, "ile_temoin", "B", "renders", "zoom_%s.png" % z)), ("A : %s (relief)" % z, os.path.join(RES, "ile_temoin", "A", "renders", "zoom_%s_relief.png" % z)), ("B : %s (relief)" % z, os.path.join(RES, "ile_temoin", "B", "renders", "zoom_%s_relief.png" % z))], 700, os.path.join(OUT, "gros_plan_%s_A_vs_B.png" % z), cols=2)
sheet([("V0.1 A sans coins coupes", os.path.join(RES, "ile_temoin", "A_sans_coins_coupes", "renders", "face.png")) if os.path.exists(os.path.join(RES, "ile_temoin", "A_sans_coins_coupes", "renders", "face.png")) else ("A", os.path.join(RES, "ile_temoin", "A", "renders", "face.png")), ("V0.1 A (coins coupes)", os.path.join(RES, "ile_temoin", "A", "renders", "face.png")), ("A 48 x 48", os.path.join(RES, "ile_temoin", "A_48x48", "renders", "face.png"))], 640, os.path.join(OUT, "resolution_32_cut_vs_48.png"))
print("done", list(res["ile"]))
