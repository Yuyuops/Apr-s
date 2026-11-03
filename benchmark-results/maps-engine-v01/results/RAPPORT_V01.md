# RAPPORT V0.1 — du prototype au tableau décoratif

Branche `research/lego-maps-v0-20261103`, base V0 = commit 2456d1a (dossier `maps-engine-v0/`, **non modifié**) ; moteur 1 (`20_portable_engine`) en lecture seule. Moteur : `engine/maps_engine/` (copie évoluée du moteur 2 V0), relancer tout avec `run_all.sh`. Toutes les valeurs ci-dessous sont **calculées par le code à partir des fichiers de sortie** (`results/tableaux_mesures.md` est généré par `engine/make_report.py`). Aucun prix, stock ni essai physique n'est inventé.

**Ce rapport ne recommande pas de finition** : la demande est de comparer A et B côte à côte avant de choisir ; la comparaison visuelle est dans `results/comparatifs/` (images ci-dessous) et la décision revient à l'utilisateur.

## 0. Résultat en quelques lignes
* **Découverte qui change les mesures de V0** : V0 choisissait et mesurait ses couleurs avec les valeurs de `LDConfig.ldr` (bibliothèque LDraw installée), qui diffèrent des vraies couleurs LEGO (Tan : #B0A06F contre #E4CD9E ; Sand Green #708E7C contre #A0BCAC ; Blue #1E5AA8 contre #0055BF…). Mesuré avec les valeurs réelles (table `colors` du catalogue technique), V0 a un ΔE2000 de **4,21** (ΔE76 : 16,16), pas 12,95. V0.1 utilise partout les valeurs réelles (choix, mesure, rendus, viewer).
* **Couleurs** : choix non injectif sous contrainte de lisibilité. ΔE2000 4,21 → **3,49** (A) / 3,54 (B). Gains nets sur forêt (22,7 → 8,0), sommet (20,4 → 8,2), colline, village ; mer et terre étaient déjà bonnes. 13 / 13 paires de zones adjacentes restent distinguables.
* **Contours et relief** : à 32 × 32 le contour de la côte ne progresse que légèrement (déplacement moyen 1,64 → 1,49 mm avec 18 plaques biseautées) ; la limite de résolution persiste, et la rivière et la route restent plus larges qu'à la source (surface × 2,26 et × 1,74). 48 × 48 : IoU de cellules 0,905 → 0,952, déplacement des contours 1,89 → 1,21 mm, pour 393 pièces et 384 mm de côté.
* **Finitions** : A (tenons apparents, cadre 1 tenon, 221 pièces) et B (tuiles lisses sur les grands aplats, cadre de 2 tenons arasé au sommet, 365 pièces) générées automatiquement, avec rendus, viewer, notice et nomenclature.
* **Structure** : 0 collision, 0 pièce déconnectée, 1 composante pour tous les modèles ; mais **plus de pièces tenues par un seul tenon que V0** (9 → 15 en A, 23 en B) et B ajoute des porteuses faiblement tenues (10 → 42) : limites listées au § 5.
* **Prix et stocks** : inconnus (Briquestore répond 202, inexploitable par machine ; aucune valeur inventée).

## 1. Phase 1 — audit visuel de V0
Voir `audit_v0/AUDIT_VISUEL_V0.md` et `audit_v0/V0_source_vs_rendu.png` (diagnostic établi avant toute modification : couleurs, contours 0,7–2,3 mm moyens et 5–7 mm maximum, rivière et route 2,3 × et 1,7 × trop larges, relief peu lisible, aucun cadre, tenons partout, 9 plaques sur un seul tenon, étapes de 5 à 43 pièces).

## 2. Phases 2 à 8 — mesures

### Tableau comparatif demandé — île témoin (32 × 32 tenons de champ)

| Indicateur | V0 | V0.1 A (LEGO apparent) | V0.1 B (premium) |
|---|---|---|---|
| Fidélité des contours : déplacement moyen de la côte réelle (mm) / IoU terre | 1.64 / 0.961 | 1.49 / 0.966 | 1.64 / 0.961 |
| Classes : IoU de cellules moyen / IoU pixels moyen | 0.905 / 0.671 | 0.905 / 0.671 | 0.905 / 0.671 |
| ΔE2000 moyen (valeurs réelles, pondéré surface) | 4.21 | 3.49 | 3.54 |
| ΔE76 moyen (comparable aux chiffres de V0) | 16.16 | 15.25 | 15.13 |
| Lisibilité du relief (paires de zones adjacentes distinguables) | 13 / 13 paires | 13 / 13 paires | 13 / 13 paires |
| Nombre de pièces (dos + relief + cadre) | 153 | 221 | 365 |
| Références (pièce × couleur) | 53 | 66 | 70 |
| Pièces 1×1 (part) | 9 (5.9 %) | 15 (6.8 %) | 23 (6.3 %) |
| Pièces sur un seul tenon (dont feuilles décoratives) | 9 (8) | 15 (12) | 23 (16) |
| Points d'articulation du graphe / porteuses tenues par < 4 tenons | 25 / 10 | 28 / 13 | 51 / 42 |
| Collisions / pièces déconnectées / composantes | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 0 / 1 |
| Épaisseur totale (mm) / tableau complet (mm) | 22.4 / 256 | 22.4 / 272 | 22.4 / 288 |
| Masse estimée (g, hypothèses explicites) | 785 | 954.00 | 1194.00 |
| Nombre d'étapes de notice / pièces max par étape | 15 / 43 | 23 / 20 | 32 / 20 |
| Qualité esthétique | à juger sur les rendus côte à côte | à juger sur les rendus côte à côte | à juger sur les rendus côte à côte |

### Même tableau — carte à trois zones

| Indicateur | V0 | V0.1 A | V0.1 B |
|---|---|---|---|
| IoU de cellules / IoU pixels | 1.000 / 0.931 | 1.000 / 0.931 | 1.000 / 0.931 |
| ΔE2000 / ΔE76 moyens | 5.29 / 18.41 | 3.80 / 16.50 | 3.80 / 16.50 |
| Pièces / références / 1×1 | 119 / 36 / 2 | 167 / 42 / 1 | 258 / 50 / 7 |
| Pièces sur un seul tenon / points d'articulation | 2 / 13 | 1 / 18 | 7 / 26 |
| Collisions / déconnectées | 0 / 0 | 0 / 0 | 0 / 0 |
| Épaisseur (mm) / masse (g) / étapes | 16.0 / 781 / 8 | 16.0 / 921.0 / 13 | 16.0 / 1073.0 / 18 |

### Écarts de couleur par classe — avant (V0, valeurs réelles) et après (V0.1 A) ; île témoin

| classe | V0 : couleur | ΔE2000 | ΔE76 | V0.1 : couleur | ΔE2000 | ΔE76 |
|---|---|---|---|---|---|---|
| colline | Dark_Tan | 9.7 | 16.0 | Medium_Nougat | 5.4 | 6.7 |
| foret | Sand_Green | 22.7 | 32.2 | Green | 8.0 | 13.4 |
| lac | Dark_Azure | 7.6 | 14.7 | Medium_Blue | 6.0 | 18.3 |
| mer | Blue | 4.7 | 26.3 | Blue | 4.7 | 26.3 |
| riviere | Medium_Blue | 6.0 | 18.3 | Medium_Blue | 6.0 | 18.3 |
| route | Medium_Nougat | 2.2 | 3.9 | Medium_Nougat | 2.2 | 3.9 |
| sommet | Light_Bluish_Grey | 20.4 | 30.1 | Tan | 8.2 | 11.4 |
| terre | Tan | 1.1 | 1.5 | Tan | 1.1 | 1.5 |
| village | Dark_Orange | 15.0 | 26.0 | Red | 8.9 | 34.9 |

### Résolution : 32 × 32 contre 48 × 48 (finition A, mêmes algorithmes)

| Indicateur | 32 × 32 (A) | 48 × 48 (A) |
|---|---|---|
| Taille du champ (mm) | 256 | 384 |
| Pièces / 1×1 | 221 / 15 | 393 / 33 |
| IoU de cellules / pixels | 0.905 / 0.671 | 0.952 / 0.767 |
| Contours de toutes les classes : déplacement moyen (mm) sur la grille de classes | 1.89 | 1.21 |
| IoU de la terre (empreinte réelle des plaques, côte seule) | 0.966 | 0.970 |
| Surface de la rivière / de la route (rapport au source) | 2.26 / 1.74 | 1.72 / 1.64 |
| Masse (g) / étapes | 954.0 / 23 | 2019.0 / 31 |

### Coins coupés (plaque biseautée 2×2, géométrie existante 26601) — île témoin, finition A

|  | sans coins coupés | avec coins coupés (A) |
|---|---|---|
| Plaques biseautées | 0 | 18 |
| Pièces / 1×1 | 202 / 11 | 221 / 15 |
| Côte : déplacement moyen (mm) / max (mm) / IoU terre | 1.64 / 5.32 / 0.961 | 1.49 / 4.95 / 0.966 |


Notes de lecture :
* ΔE2000 est la métrique d'optimisation et de lecture perceptive ; ΔE76 est donnée pour la comparabilité avec V0. La mer (Blue, ΔE76 26 mais ΔE2000 4,7) et le village (Red, ΔE76 35 mais ΔE2000 8,9) dominent ΔE76 sans que l'écart visuel soit grand : le meilleur candidat reste le plus proche au sens ΔE2000.
* « Lisibilité du relief » = part des paires de classes adjacentes qui restent distinguables : contraste ΔE2000 ≥ 8, ou marche de hauteur ≥ 2 plaques, ou marche ≥ 1 avec contraste ≥ 4, ou source déjà d'une seule couleur (un lac et sa rivière, ΔE source < 4). Colline et route, sommet et terre partagent désormais une couleur ; ils ne sont pas adjacents ou diffèrent en hauteur.
* Contours : « déplacement de la côte réelle » est mesuré sur l'empreinte réelle des plaques de la couche de terre, plaques biseautées comprises (triangle de coupe d'un tenon de côté), lacs et rivières comptés comme terre des deux côtés. Les finitions A et B ont les mêmes classes (mêmes IoU) : seul le biseautage des coins (A) modifie l'empreinte.
* La masse suppose l'ABS à 1,05 g/cm³ × volume des boîtes × taux de remplissage de la géométrie LDraw, tenons non comptés : ±30 % plausible. Elle n'est pas mesurée.
* Les « étapes » sont une séquence numérique ; aucun montage physique n'a été fait.

## 3. Ce que chaque amélioration a coûté (île témoin)
* **Cadre** (A : 1 tenon, rangs de briques + plaques, arasé 1 plaque sous le sommet ; B : 2 tenons, briques + tuiles de finition, arasé au sommet) : 33 pièces en A, 66 en B ; dos et cadre sont posés sur deux couches de plaques décalées (jamais de joints alignés, B1→B2 = 0 %) dont le tracé est calculé par segments (8 tenons, puis 6 / 4 / 2 pour le reste) pour que le dos reste fait de grandes plaques (plaques 8×8 en majorité, bandes 8×2, 8×4, 8×6 sur les bords). Le cadre se pose sur le dos par ses tenons et se soulève d'un bloc ; **non éprouvé physiquement**.
* **Plaques biseautées** (A seulement) : 18 plaques 2×2 à coin coupé (réf. 26601), posées uniquement là où la source laisse ≥ 30 % de la cellule d'angle vide : +19 pièces (202 → 221), +4 pièces de 1×1 (11 → 15), contour 1,64 → 1,49 mm. Gain visuel net en gros plan, gain métrique modeste : **choix esthétique, non d'exactitude**.
* **Tuiles lisses** (B) : les plus grandes tuiles existantes font 2×6, donc les grands aplats demandent beaucoup plus de pièces qu'avec des plaques 8×8 : 365 pièces (+139 % contre V0), 1 194 g (+52 %), 70 références ; en contrepartie surface lisse, côtés finis, aucun tenon sur la mer, la terre, le lac, la rivière et la route.

## 4. Détails fins (Phase 3)
* **Village** : pièce ronde 1×1 (plaque 6141 en A, tuile ronde 98138 en B), niveau + 1 plaque, conservé ; **lac** : même bleu que sa rivière (source ΔE < 4), un niveau sous la terre ; **route** : continuité conservée (1 composante), partage la couleur de la colline (non adjacentes).
* **Limite documentée** : à 32 × 32 une cellule fait 8 mm ; la rivière et la route de la source font ≈ 4,5 et 5 mm de large. Aucune pièce existante ne permet d'en faire une ligne de moins d'un tenon sans décentrer les pièces (plaques à tenon décentré, non testées : elles ajouteraient une pièce par cellule de ligne pour un gain inférieur à la résolution). À 48 × 48 (5,3 mm par tenon) le rapport de surface passe de 2,26 à 1,72 (rivière) et de 1,74 à 1,64 (route).

## 5. Structure et constructibilité (Phase 5)
* **Calcul** : voir `results/controles/` — `coherence_ldraw_nomenclature_notice.json` (LDraw = nomenclature = étapes, chaque pièce exactement une fois), `fragilite_structurelle.json`, `charge_murale_etude_*.json`, et pour chaque sortie `validation/` (validateur du moteur 1 + contrôles du moteur 2 : couverture des couches, appui, graphe, joints, coupe minimale).
* **Résultats** : 0 collision, 0 pièce déconnectée, 1 composante connexe pour les six sorties. Pièces tenues par un seul tenon : V0 9, A 15 (12 feuilles décoratives qui ne portent rien), B 23 (16 feuilles) ; points d'articulation 25 / 28 / 51 ; pièces portant d'autres pièces avec moins de 4 tenons 10 / 13 / 42.
* **Lecture honnête** : A reste proche de V0 sur la structure mais **n'améliore pas** le critère « pièces sur un seul tenon » (il augmente de 6, dont 4 dus aux plaques biseautées) ; B est nettement plus fragile (les tuiles demandent des plaques porteuses petites). Je n'ai pas pu réduire ces chiffres sans changer la carte (une 1×1 isolée sur un tenon est inévitable tant que la cellule garde sa couleur). Pistes : fusion colorée de cellules isolées (coût de fidélité), pavage dédié des couches basses, plaques de jonction invisibles sous les tuiles.
* **Dos** : deux couches de plaques (la seconde décalée de 4 tenons, jamais de joint aligné). Coupe minimale du noyau dos + cadre : 2 tenons, due à une unique plaque feuille, pas à la structure d'ensemble.
* **Fixation murale** : étude de répartition seulement (`charge_murale_etude_*.json`) : le tableau se suspend par son dos ; l'interface la plus chargée a 1 156 tenons pour 6,9 N de poids (A) avec l'hypothèse non mesurée de 1 N par tenon. **Rien n'est déclaré sûr** : le glissement, les chocs, le fluage du frottement et le moment dû à l'épaisseur ne sont pas modélisés ; aucun essai physique n'a été réalisé.

## 6. Notice et visualisation (Phase 7)
`notice.pdf` : couverture et avertissements, régions et couleurs, nomenclature, puis des étapes de **20 pièces au plus** en trois sections — Dos (rangées de plaques 8×8…), Relief (couche par région, avec gros plan en plus de la vue d'ensemble), Cadre (rangs de briques). A : 23 étapes, 26 pages ; B : 32 étapes, 35 pages. `viewer.html` (autonome) : rotation, zoom, curseur de couches, filtres dos / relief / cadre, filtre de région, **clic sur une pièce = référence, couleur, section, région, identifiant et position** (testé sans erreur de console par navigateur sans interface). Un PDF illustré ne prouve pas un montage physique.

## 7. Approvisionnement (Phase 9)
Toutes les paires pièce × couleur existent dans le catalogue technique avec au moins 22 sets (Rebrickable, `parts_list.csv`) ; ce n'est **pas un stock**. Références plus rares signalées : tuile 2×6 Blue (23 sets) en B, plaque 6×10 Blue (3033, 47 sets) en A. Briquestore (seule source commerciale autorisée) : une requête le 2026-11-03, HTTP 202, inventaire non vérifiable par machine ; **prix, stock et date de vérification restent vides** ; aucune commande n'est réalisable sur cette base ; aucun achat.

## 8. Ce qui reste non résolu
Contours à la résolution de 8 mm ; rivière et route trop larges ; village en ΔE76 élevé ; pièces uniques sur un tenon ; B structurellement plus faible ; qualité esthétique non mesurable (comparaison humaine nécessaire) ; aucune fixation murale validée ; prix et stock inconnus ; une seule carte avec relief et une carte très simple.
