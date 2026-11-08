#!/usr/bin/env python3
"""Writes SLICING_BENCHMARK.md and BUSINESS_COST_MODEL.md from bench.json + cost.json (Sprint V14). usage : make_reports_v14.py BENCH.json COST.json OUTDIR"""
import json, math, sys, collections
B = json.load(open(sys.argv[1])); C = json.load(open(sys.argv[2])); OUT = sys.argv[3]; A = C["assumptions"]; M = A["machines"]
H = lambda s: "%.1f h" % (s / 3600)
def sl(model, kind, prof, sup, tag=None):
    return [r for r in B["slices"] if r["model"] == model and r["kind"] == kind and r["profile"] == prof and r["supports"] == sup and r.get("seconds") is not None and (tag is None or r["tag"] == tag)]
L = []; w = L.append
w("# Sprint V14 — Benchmark de tranchage sur les exports V13 réels\n")
w("**Ce que c'est** : les vrais exports V13 (Paco : `tests/data/paco_sample.ldr`, 3 193 pièces ; Hyrule : `livraison_v10/hyrule_biomes/diorama.ldr`, 10 682 pièces, SHA = référence CI) tranchés par **PrusaSlicer 2.7.2** (seul slicer installable ici) avec des **profils proxy** par machine. **Ce n'est PAS un résultat de Bambu Studio, Creality Print ou Snapmaker Orca** : aucun profil constructeur n'était disponible (binaires et dépôts de profils inaccessibles). Les temps sont donc des estimations sous profil proxy ; seule la masse de filament de tranchage et les géométries sont directement issues des fichiers.\n")
w("## Profils proxy (identiques sauf accélération)\nBuse 0,4 ; couches 0,2 ; 3 périmètres ; remplissage 15 % ; PLA 1,24 g/cm³ ; débit max 21 mm³/s (**hypothèse commune ; seul le U1 annonce 32 mm³/s**) ; vitesses périmètre 200 / ext. 120 / remplissage 250 mm/s ; accélération A1 **10 000**, Hi **12 000**, U1 **20 000** mm/s² (valeurs constructeur vérifiées) ; plateau utile commun 250 mm (conservateur pour Hi 260 et U1 270).\n")
w("## Couverture et échantillonnage (déclarés)\n- Modules multicolores (17) : tranchés **intégralement**, avec et sans supports (supports auto 45°) sous profil A1 ; sans supports aussi sous Hi et U1.\n- Plaques monochromes (procédé 3 : 7 Paco + 43 Hyrule) : toutes tranchées sous A1 (sans/avec supports) ; Hi/U1 sur un échantillon (1 plaque sur 4) puis ratio de temps.\n- Briques individuelles : **1 plaque sur 4** tranchée sous A1 (Paco 6/21, Hyrule 33/131), 1 sur 8 pour Hi/U1 ; totaux = moyenne × nombre de plaques.\n- **1 plaque Paco monochrome (`mono_005`, 101 pièces noires) fait planter PrusaSlicer (segfault reproductible)** : estimée par ratio volume (voir `cost.json`, `crashed_plates_estimated`).\n")
for model in ("paco", "hyrule"):
    m = B["models"][model]; w("## %s\n" % model.capitalize())
    w("| Procédé | Plateaux | Temps tranché A1 | Hi | U1 | Filament tranché (g) | Remarques |\n|---|---|---|---|---|---|---|")
    P = C["products"][model]; r1 = P["A1"]["median"]["1_briques"]; r3 = P["A1"]["median"]["3_modules_monochromes"]
    def tot(kind, prof, sup=False): L2 = sl(model, kind, prof, sup); return sum(r["seconds"] for r in L2), sum(r["filament_g"] for r in L2), len(L2)
    w("| 1. Briques individuelles | %d | %.0f h | %.0f h | %.0f h | %.0f | %d/%d pièces imprimables ; 100 %% des plots à plat ; ponts sous tuiles |" % (m["bricks"]["plates"], r1["hours"] / A["reprint_factor"], P["Hi"]["median"]["1_briques"]["hours"] / A["reprint_factor"], P["U1"]["median"]["1_briques"]["hours"] / A["reprint_factor"], r1["filament_useful_g"], m["bricks"]["supported"], m["bricks"]["parts"]))
    mod = P["A1"]["median"]["2_modules_multicolores"]; w("| 2. Modules multicolores (%d) | %d | %s (+supports) | — | — | %.0f dont supports %.0f | %d colour-changes ; %d module(s) dépassent 4 couleurs par couche |" % (m["modules"]["count"], m["modules"]["count"], "voir ci-dessous", mod["filament_useful_g"] + mod["support_g"], mod["support_g"], mod["colour_changes_in_print"], mod["infeasible_modules"]))
    w("| 3. Pièces monochromes assemblées | %d | %.0f h | — | — | %.0f | %d pièces à assembler ; supports +%.0f g |" % (m["mono"]["plates"], mod and r3["hours"], r3["filament_useful_g"] + r3["support_g"], m["mono"]["pieces"], r3["support_g"]))
    w("\n### Modules (procédé 2) — mesures par module\n| Module | Couleurs | Max couleurs / couche | Changements de couleur (couches 0,2 mm) | Pièces connexes | Temps A1 sans supports | **fusionné** sans / avec supports (h) | **fusionné** g sans / avec | Avert. |\n|---|---|---|---|---|---|---|---|---|")
    for i in m["modules"]["module_list"]:
        tag = "%s_%s" % (model, i["file"].replace(".3mf", "")); a = sl(model, "mod2", "A1", False, tag); b = sl(model, "mod2", "A1", True, tag)
        mg = {r["supports"]: r for r in json.load(open(sys.argv[1].replace("bench.json", "merged_supports.json"))) if r["tag"] == tag + "_merged" and r.get("seconds")}
        if a and mg.get(True) and mg.get(False): w("| %s | %d | %d | %d | %d | %s (objets séparés) | %.1f / %.1f | %.0f / %.0f | %s |" % (i["file"], i["colours"], i["max_colours_in_layer"], i["colour_changes"], i["components"], H(a[0]["seconds"]), mg[False]["seconds"] / 3600, mg[True]["seconds"] / 3600, mg[False]["filament_g"], mg[True]["filament_g"], "; ".join(a[0]["warn"])[:60]))
    w("")
w("## Constats mesurés\n- **Aucun module ne se tranche sans avertissement de ponts/pièces flottantes.** Supports (45°) mesurés sur modules **fusionnés en un solide** (le tranchage en objets séparés surestime les supports : conflits de chemins entre corps) : Paco +63 % de masse (1 084 → 1 764 g), Hyrule +1 % (5 450 → 5 519 g).\n- **Paco : 5 à 6 couleurs par module, jusqu'à 5 simultanées dans une même couche ; Hyrule : 5 à 12 couleurs, jusqu'à 7 simultanées.** Une machine à 4 emplacements ne peut donc pas imprimer ces modules en une passe.\n- Les temps de tranchage sous profil proxy sont **≈ 3× supérieurs** aux estimations par formule de `BAMBU_EXPORT.md` (Paco briques : formule 53 h, tranché ≈ 160 h ; Hyrule : 395 h → ≈ 1 200 h).\n- Aucune différence de temps significative entre machines n'apparaît sur les plaques monochromes : sous profil proxy commun, la différence vient presque uniquement de l'accélération, et la vitesse réelle de chaque firmware **n'a pas été mesurée**.\n")
open(OUT + "/SLICING_BENCHMARK.md", "w").write("\n".join(L))
# ------------------------------------------------------------ business model
L = []; w = L.append
w("# Sprint V14 — Modèle de coût et de rentabilité\n")
w("> **Tous les prix, temps humains et purges ci-dessous sont des paramètres, pas des mesures.** Ceux marqués [V] viennent d'une page vérifiée le 2026-11-08 ; les autres sont des **hypothèses** à remplacer par des mesures (aucune imprimante n'a été achetée ni utilisée). Le classement final n'est retenu que s'il résiste à la plage bas/haut des hypothèses.\n")
w("## Hypothèses\n| Paramètre | Valeur | Statut |\n|---|---|---|")
for k, v, st in (("Prix A1 Combo", "469,95 € TTC", "[V] LDLC"), ("Prix Hi Combo", "474,90 € TTC (promos 359–370 non confirmées)", "[V partiel] PcComponentes"), ("Prix U1", "699 € TTC (page « Unavailable »)", "[V] Snapmaker EU"), ("CFS supplémentaire (Hi)", "120 € TTC l'unité, 3 unités pour 16 couleurs", "**hypothèse** : prix non vérifié"),
                 ("Filament", "%.0f € HT/kg (22 € TTC)" % A["filament_eur_kg_ht"], "hypothèse (fourchette FR 15–30 € TTC [V])"), ("Électricité", "%.2f €/kWh, %d W moyens" % (A["electricity_eur_kwh"], A["avg_power_w"]), "hypothèse (max 1 150 W [V] pour Hi/U1)"), ("Main-d'œuvre", "%d €/h" % A["human_eur_h"], "hypothèse"),
                 ("Durée de vie machine", "%d h, entretien %.2f €/h" % (A["machine_life_h"], A["maintenance_eur_h"]), "hypothèse"), ("Capacité", "%d h/mois/machine" % A["duty_h_month"], "hypothèse (≈ 70 % d'utilisation)"), ("Taux de refabrication", "+%d %%" % round((A["reprint_factor"] - 1) * 100), "hypothèse"),
                 ("Manutention", "%d min/plateau, %d min/changement de bobine" % (A["plate_handling_min"], A["spool_swap_min"]), "hypothèse"), ("Assemblage", "%d s/brique ; %d s/pièce monochrome ; %d min/module + %d min dépose des supports" % (A["brick_assembly_s"], A["piece_assembly_s"], A["module_assembly_min"], A["support_removal_min_per_module"]), "hypothèse"),
                 ("Purge par changement de couleur A1/Hi (bas–médian–haut)", "0,3 – 0,8 – 1,5 g", "**hypothèse non vérifiée** (aucun chiffre constructeur)"), ("Purge U1", "0,045 – 0,12 – 0,225 g", "affirmation constructeur « −85 % » [V page] appliquée à l'hypothèse ci-dessus : **non mesurée**"),
                 ("Durée d'un changement A1/Hi", "30 – 45 – 90 s", "hypothèse"), ("Durée d'un changement U1", "5 – 5 – 10 s", "[V] constructeur (5 s) ; non mesuré"), ("TVA", "20 % ; coûts et marges en € HT", "")):
    w("| %s | %s | %s |" % (k, v, st))
w("\n## Faisabilité des procédés selon les emplacements couleur\n| Procédé | A1 + AMS Lite (4) | Hi + CFS (4, extensible 16) | U1 (4 têtes) |\n|---|---|---|---|")
for model in ("paco", "hyrule"):
    P = C["products"][model]
    w("| %s — 2 Modules multicolores | **impossible** (%d/%d modules > 4 couleurs par couche) | possible avec 3 CFS supplémentaires | **impossible** (même limite) |" % (model.capitalize(), P["A1"]["median"]["2_modules_multicolores"]["infeasible_modules"], P["A1"]["median"]["2_modules_multicolores"]["plates"]))
w("| 1 Briques / 3 Pièces monochromes | possible | possible | possible |\n")
for model in ("paco", "hyrule"):
    P = C["products"][model]; w("## Coût complet par modèle — %s (scénario médian ; bas–haut pour les purges)\n" % model.capitalize())
    w("| Machine | Procédé | Faisable | Plateaux | Heures machine | Filament utile (g) | Supports (g) | Purge (g) | Changements | Matière € | Élec. € | Intervention (h) | Humain € | Amortissement € | **Coût complet € HT** | (bas – haut) |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for mk in ("A1", "Hi", "U1"):
        for proc in ("1_briques", "2_modules_multicolores", "3_modules_monochromes"):
            r = P[mk]["median"][proc]; lo = P[mk]["bas"][proc]["full_cost_eur"]; hi = P[mk]["haut"][proc]["full_cost_eur"]
            w("| %s | %s | %s | %s | %.0f | %.0f | %.0f | %.0f | %s | %.0f | %.0f | %.1f | %.0f | %.0f | **%.0f** | %.0f – %.0f |" % (mk, proc[2:].replace("_", " "), "oui" if r["feasible"] else "**non**", r.get("plates"), r["hours"], r["filament_useful_g"], r["support_g"], r["purge_g"], r["colour_changes_in_print"], r["material_eur"], r["electricity_eur"], r["human_h"], r["human_eur"], r["amortisation_eur"], r["full_cost_eur"], lo, hi))
    w("")
# margins / scenarios on the best FEASIBLE process per machine
PRICES = {"paco": (249, 399, 599), "hyrule": (399, 699, 999)}
w("## Marge brute (prix TTC → HT) pour le procédé faisable le moins cher de chaque machine\n**Les briques imprimées individuellement (procédé 1) sont exclues du classement** : 116 pièces Paco (3,6 %) et 515 pièces Hyrule (4,8 %) — pentes, quarts de rond, pièces spéciales — ne sont pas imprimables en briques rectangulaires, donc le modèle serait visuellement dégradé ; en outre l'emboîtement FDM n'est pas démontré.\n(les prix de vente sont des **points de test**, pas une étude de marché)\n")
best = {}
for model in ("paco", "hyrule"):
    P = C["products"][model]; w("### %s\n| Machine | Procédé retenu | Coût complet HT | Heures | " % model.capitalize() + " | ".join("Marge à %d € TTC" % p for p in PRICES[model]) + " |\n|---|---|---|---|" + "---|" * len(PRICES[model]))
    for mk in ("A1", "Hi", "U1"):
        cand = {k: v for k, v in P[mk]["median"].items() if v["feasible"] and k != "1_briques"}; k = min(cand, key=lambda x: cand[x]["full_cost_eur"]); r = cand[k]; best[(model, mk)] = (k, r)
        w("| %s | %s | %.0f € | %.0f h | " % (mk, k[2:].replace("_", " "), r["full_cost_eur"], r["hours"]) + " | ".join("%.0f € (%.0f %%)" % (p / A["vat"] - r["full_cost_eur"], 100 * (p / A["vat"] - r["full_cost_eur"]) / (p / A["vat"])) for p in PRICES[model]) + " |")
    w("")
w("## Scénarios mensuels (5 / 20 / 50 modèles vendus) — capacité machine %d h/mois\n(un « modèle vendu » = un Paco **ou** un Hyrule ; machines nécessaires = heures × (1+refabrication) / capacité)\n" % A["duty_h_month"])
w("| Produit | Machine | Procédé | N/mois | Heures requises | Machines nécessaires | Investissement HT | Marge brute mensuelle au prix médian | Retour sur investissement |\n|---|---|---|---|---|---|---|---|---|")
for model in ("paco", "hyrule"):
    for mk in ("A1", "Hi", "U1"):
        k, r = best[(model, mk)]; price = PRICES[model][1] / A["vat"]; var = r["full_cost_eur"] - r["amortisation_eur"]
        for n in (5, 20, 50):
            hrs = n * r["hours"]; nm = math.ceil(hrs / A["duty_h_month"]); cap = nm * M[mk]["price_ttc"] / A["vat"] + (nm * r.get("extra_capex_ht", 0))
            gm = n * (price - r["full_cost_eur"]); roi = (cap / (n * (price - var))) if price > var else float("inf")
            w("| %s | %s | %s | %d | %.0f h | **%d** | %.0f € | %.0f € | %s |" % (model, mk, k[2:].replace("_", " "), n, hrs, nm, cap, gm, "%.1f mois" % roi if roi < 1000 else "jamais"))
w("\n**Seuil de rentabilité (retour de l'investissement machine en 12 mois au prix médian)** : N minimal par mois = investissement / (12 × (prix HT − coût variable)). Voir colonne « Retour sur investissement » : un retour ≤ 12 mois correspond à un seuil atteint.\n")
w("## Limites\n- Les coûts humains (assemblage de 3 193 à 10 682 briques ou de 400–600 pièces) dominent plusieurs procédés ; ils reposent sur des durées **supposées**.\n- Les heures machine viennent d'un profil proxy lent : les vitesses réelles des firmwares sont inconnues, donc les capacités (machines nécessaires) peuvent être surestimées ou sous-estimées d'un facteur à mesurer.\n- Aucune compatibilité d'emboîtement FDM n'est démontrée (coupon non imprimé) : un modèle assemblé à partir de briques imprimées n'est **pas** garanti de tenir.\n")
open(OUT + "/BUSINESS_COST_MODEL.md", "w").write("\n".join(L)); print("reports ok")
