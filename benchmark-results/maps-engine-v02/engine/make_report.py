"""Writes results/RAPPORT_V01.md tables from the measured JSON files (no number is typed by hand). usage: python make_report.py"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maps_engine.common import ROOT
R = os.path.join(ROOT, "results"); C = json.load(open(os.path.join(R, "comparatifs", "comparaison_V0_A_B.json"))); FR = json.load(open(os.path.join(R, "controles", "fragilite_structurelle.json"))); CO = json.load(open(os.path.join(R, "controles", "coherence_ldraw_nomenclature_notice.json")))
V0 = os.path.join(ROOT, "..", "maps-engine-v0", "results")
def f(x, nd=2): return "—" if x is None else (("%." + str(nd) + "f") % x if isinstance(x, float) else str(x))
def fr(key): return FR[key]
i = C["ile"]; t = C["trois_zones"]
frag = {"V0": FR["../../maps-engine-v0/results"], "A": FR["../results/ile_temoin/A"], "B": FR["../results/ile_temoin/B"], "A48": FR["../results/ile_temoin/A_48x48"], "Anocut": FR["../results/ile_temoin/A_sans_coins_coupes"]}
fragt = {"V0": FR["../../maps-engine-v0/results/test_3_zones"], "A": FR["../results/test_3_zones/A"], "B": FR["../results/test_3_zones/B"]}
L = []
def row(label, vals): L.append("| %s | %s |" % (label, " | ".join(f(v) if not isinstance(v, str) else v for v in vals)))
def table(head, rows): L.append("| " + " | ".join(head) + " |"); L.append("|" + "---|" * len(head)); [row(a, b) for a, b in rows]; L.append("")
# --- main comparison table (island)
L.append("### Tableau comparatif demandé — île témoin (32 × 32 tenons de champ)\n")
def lisible(x): return "%d / %d paires" % (x["lisibilite"]["paires_lisibles"], x["lisibilite"]["paires_adjacentes"])
table(["Indicateur", "V0", "V0.1 A (LEGO apparent)", "V0.1 B (premium)"], [
    ("Fidélité des contours : déplacement moyen de la côte réelle (mm) / IoU terre", ("%s / %s" % (f(i["V0"]["contour_reel_terre"]["deplacement_moyen_mm"]), f(i["V0"]["contour_reel_terre"]["iou_terre"], 3)), "%s / %s" % (f(i["A"]["contour_reel_terre"]["deplacement_moyen_mm"]), f(i["A"]["contour_reel_terre"]["iou_terre"], 3)), "%s / %s" % (f(i["B"]["contour_reel_terre"]["deplacement_moyen_mm"]), f(i["B"]["contour_reel_terre"]["iou_terre"], 3)))),
    ("Classes : IoU de cellules moyen / IoU pixels moyen", tuple("%s / %s" % (f(i[k]["iou_cellules_moyen"], 3), f(i[k]["iou_pixels_moyen"], 3)) for k in ("V0", "A", "B"))),
    ("ΔE2000 moyen (valeurs réelles, pondéré surface)", tuple(i[k]["dE2000"] for k in ("V0", "A", "B"))),
    ("ΔE76 moyen (comparable aux chiffres de V0)", tuple(i[k]["dE76"] for k in ("V0", "A", "B"))),
    ("Lisibilité du relief (paires de zones adjacentes distinguables)", tuple(lisible(i[k]) for k in ("V0", "A", "B"))),
    ("Nombre de pièces (dos + relief + cadre)", tuple(i[k]["pieces"] for k in ("V0", "A", "B"))),
    ("Références (pièce × couleur)", tuple(i[k]["references"] for k in ("V0", "A", "B"))),
    ("Pièces 1×1 (part)", tuple("%d (%.1f %%)" % (i[k]["pieces_1x1"], 100 * i[k]["part_1x1"]) for k in ("V0", "A", "B"))),
    ("Pièces sur un seul tenon (dont feuilles décoratives)", tuple("%d (%d)" % (frag[k]["tenue_par_un_tenon"], frag[k]["feuilles_decoratives"]) for k in ("V0", "A", "B"))),
    ("Points d'articulation du graphe / porteuses tenues par < 4 tenons", tuple("%d / %d" % (frag[k]["points_articulation"], frag[k]["porteuses_tenues_par_moins_de_4_tenons"]) for k in ("V0", "A", "B"))),
    ("Collisions / pièces déconnectées / composantes", tuple("%s / %s / %s" % (i[k]["collisions"], i[k]["deconnectees"], i[k]["composantes"]) for k in ("V0", "A", "B"))),
    ("Épaisseur totale (mm) / tableau complet (mm)", tuple("%s / %s" % (f(i[k]["epaisseur_mm"], 1), f(i[k]["tableau_complet_mm"], 0)) for k in ("V0", "A", "B"))),
    ("Masse estimée (g, hypothèses explicites)", tuple(i[k]["masse_g"] for k in ("V0", "A", "B"))),
    ("Nombre d'étapes de notice / pièces max par étape", tuple("%s / %s" % (i[k]["etapes"], i[k]["pieces_max_par_etape"]) for k in ("V0", "A", "B"))),
    ("Qualité esthétique", ("à juger sur les rendus côte à côte", "à juger sur les rendus côte à côte", "à juger sur les rendus côte à côte"))])
L.append("### Même tableau — carte à trois zones\n")
table(["Indicateur", "V0", "V0.1 A", "V0.1 B"], [
    ("IoU de cellules / IoU pixels", tuple("%s / %s" % (f(t[k]["iou_cellules_moyen"], 3), f(t[k]["iou_pixels_moyen"], 3)) for k in ("V0", "A", "B"))),
    ("ΔE2000 / ΔE76 moyens", tuple("%s / %s" % (f(t[k]["dE2000"]), f(t[k]["dE76"])) for k in ("V0", "A", "B"))),
    ("Pièces / références / 1×1", tuple("%s / %s / %s" % (t[k]["pieces"], t[k]["references"], t[k]["pieces_1x1"]) for k in ("V0", "A", "B"))),
    ("Pièces sur un seul tenon / points d'articulation", tuple("%s / %s" % (fragt[k]["tenue_par_un_tenon"], fragt[k]["points_articulation"]) for k in ("V0", "A", "B"))),
    ("Collisions / déconnectées", tuple("%s / %s" % (t[k]["collisions"], t[k]["deconnectees"]) for k in ("V0", "A", "B"))),
    ("Épaisseur (mm) / masse (g) / étapes", tuple("%s / %s / %s" % (f(t[k]["epaisseur_mm"], 1), t[k]["masse_g"], t[k]["etapes"]) for k in ("V0", "A", "B")))])
# --- colour table per class
L.append("### Écarts de couleur par classe — avant (V0, valeurs réelles) et après (V0.1 A) ; île témoin\n")
cl = i["A"]["couleurs"]; c0 = i["V0"]["couleurs"]
table(["classe", "V0 : couleur", "ΔE2000", "ΔE76", "V0.1 : couleur", "ΔE2000", "ΔE76"], [(k, (c0[k]["lego"], f(c0[k]["dE2000"], 1), f(c0[k]["dE76"], 1), cl[k]["lego"], f(cl[k]["dE2000"], 1), f(cl[k]["dE76"], 1))) for k in cl])
# --- 32 vs 48
L.append("### Résolution : 32 × 32 contre 48 × 48 (finition A, mêmes algorithmes)\n")
table(["Indicateur", "32 × 32 (A)", "48 × 48 (A)"], [
    ("Taille du champ (mm)", ("256", "384")), ("Pièces / 1×1", ("%s / %s" % (i["A"]["pieces"], i["A"]["pieces_1x1"]), "%s / %s" % (i["A_48x48"]["pieces"], i["A_48x48"]["pieces_1x1"]))),
    ("IoU de cellules / pixels", ("%s / %s" % (f(i["A"]["iou_cellules_moyen"], 3), f(i["A"]["iou_pixels_moyen"], 3)), "%s / %s" % (f(i["A_48x48"]["iou_cellules_moyen"], 3), f(i["A_48x48"]["iou_pixels_moyen"], 3)))),
    ("Contours de toutes les classes : déplacement moyen (mm) sur la grille de classes", (f(i["A"]["deplacement_contour_grille_mm"]), f(i["A_48x48"]["deplacement_contour_grille_mm"]))),
    ("IoU de la terre (empreinte réelle des plaques, côte seule)", (f(i["A"]["contour_reel_terre"]["iou_terre"], 3), f(i["A_48x48"]["contour_reel_terre"]["iou_terre"], 3))),
    ("Surface de la rivière / de la route (rapport au source)", ("%s / %s" % (f(i["A"]["rapport_surface_riviere"]), f(i["A"]["rapport_surface_route"])), "%s / %s" % (f(i["A_48x48"]["rapport_surface_riviere"]), f(i["A_48x48"]["rapport_surface_route"])))),
    ("Masse (g) / étapes", ("%s / %s" % (i["A"]["masse_g"], i["A"]["etapes"]), "%s / %s" % (i["A_48x48"]["masse_g"], i["A_48x48"]["etapes"])))])
# --- corner cuts
L.append("### Coins coupés (plaque biseautée 2×2, géométrie existante 26601) — île témoin, finition A\n")
table(["", "sans coins coupés", "avec coins coupés (A)"], [("Plaques biseautées", (0, i["A"]["coins_coupes"])), ("Pièces / 1×1", ("%s / %s" % (i["A_sans_coins_coupes"]["pieces"], i["A_sans_coins_coupes"]["pieces_1x1"]), "%s / %s" % (i["A"]["pieces"], i["A"]["pieces_1x1"]))),
    ("Côte : déplacement moyen (mm) / max (mm) / IoU terre", tuple("%s / %s / %s" % (f(i[k]["contour_reel_terre"]["deplacement_moyen_mm"]), f(i[k]["contour_reel_terre"]["deplacement_max_mm"]), f(i[k]["contour_reel_terre"]["iou_terre"], 3)) for k in ("A_sans_coins_coupes", "A")))])
open(os.path.join(R, "tableaux_mesures.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L)[:300])
