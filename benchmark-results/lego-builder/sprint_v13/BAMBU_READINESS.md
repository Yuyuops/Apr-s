# Sprint V13 — Préparation Bambu Studio : audit (B1), modules fidèles (B2), tranchage (B3)

> **Aucune validation Bambu Studio n'est revendiquée.** Bambu Studio n'est pas installable dans cet environnement (téléchargements GitHub/Bambu bloqués par le proxy, pas de paquet apt). Un tranchage indépendant a été fait avec **PrusaSlicer 2.7.2 (apt)** : il prouve qu'un second slicer importe, mesure et tranche les fichiers, **pas** que Bambu Studio ou une imprimante Bambu les accepte. Aucune fabrication n'a été lancée, rien n'a été acheté.

## B1 — Audit mesuré de `print_export_results/` (`tools/audit_print_exports.py` → `print_audit.json`)

| Point | Mesure | Verdict |
|---|---|---|
| Dimensions réelles | briques STL 0,2 mm **plus petites** que le pas nominal (1×1 : 7,8 mm pour 8 mm ; hauteur 3,2 / 9,6 mm exacte ; plot Ø 4,8 × 1,7) — tolérance 0,10 mm par côté voulue | conforme à la conception ; **ajustement réel inconnu** (B4) |
| Unités / orientation | 3MF `unit="millimeter"`, Z vers le haut, base à z = 0, volumes > 0 | OK |
| Étanchéité | tous les STL et tous les corps 3MF fermés (variété, volume > 0) | OK (validateur bloquant en CI) |
| Plateau | modules Hyrule jusqu'à 240 × 240 × 67 mm ; Paco jusqu'à 136 × 144 × 198 mm ; chaque module recentré à l'origine | tient sur 250/256 mm (marge 10–16 mm pour Hyrule ; **pas sur un plateau 180 mm**) |
| Parois / peau | paroi 1,2 mm (= 3 périmètres de 0,4), peau supérieure 1,0 mm | imprimables en 0,4 mm, sans marge |
| Zones à supports | briques : 5–10 % de la surface en surplomb > 45° ; **tuiles : ≈ 20 %** (plafond de la cavité à pont de 14–30 mm). PrusaSlicer signale « Floating bridge anchors » (+ « Long bridging extrusions » sur le module Hyrule) | **risque réel** : imprimer les tuiles **retournées** (face lisse sur le plateau, sans pont) — appliqué dans le coupon |
| Tenons de modules | **défaut trouvé** : seules les *douilles* (Ø 5,0 + 0,30 de jeu, prof. 6,5) étaient exportées, **jamais le tenon** | corrigé : `dowel_peg.stl` (Ø 5,0 × 12 mm) exporté (CI vérifie sa présence) |
| Couleurs / séparation | un corps 3MF par couleur (`basematerials`), 43 corps (Paco) / 86 (Hyrule) | affectation aux extrudeurs/AMS **non vérifiée** (dépend de l'import Bambu) |
| Approximation « blocs » | pièces non rectangulaires → boîte englobante : Hyrule **515 pièces** (467 × 25269, 48 × 98138) ; **Paco : 7 + 109 pièces absentes du catalogue (52107 ×46, 63864 ×18, 47905 ×13…) étaient purement ignorées par l'export modules** (3,4 % des pièces, trous silencieux) | corrigé en B2 |
| Estimations du dépôt | masse formule vs tranchage : plaque Paco 102,5 g vs **106,8 g** (+4 %) ✔ ; **temps** formule 3,0 h vs **15,9 h** (×5,3 trop optimiste) ✘ | les heures annoncées dans `BAMBU_EXPORT.md` sont à **multiplier par ≈ 2,5 (modules) à 5 (briques)** avec les réglages génériques ; vitesses Bambu inconnues |

## B2 — Modules fidèles aux détails LEGO (`lego_builder/print3d/shapes.py`, option `--shape-aware`)
Principe : les pièces non rectangulaires utilisent l'**enveloppe convexe de leur vraie géométrie LDraw** (plots/tubes/trous ignorés), placée à sa vraie position, découpée par le module et fusionnée au corps de sa couleur. Exacte pour pentes, cylindres, quarts de rond ; **remplit les concavités** (arches, creux) et omet leurs plots (déclaré dans `approximations`). Aucune centaine de plaques.

| Module représentatif | Blocs → formes | Preuve |
|---|---|---|
| **Paco, tête** (module 0_1_0, forme courbe) : 116 pièces recouvrent pentes/ronds/pièces absentes | volume module 796,8 → 825,2 cm³ ; Paco entier 2 635 → 2 677 cm³ (+1,6 %), 43 → 44 corps ; tranchage 342 → 368 g | `renders/paco_module_head_blocks_vs_shapes.jpg` (rendu logiciel indicatif, artefacts de tri possibles) ; 3MF `shape_aware/paco_head_module_{blocks,shapes}.3mf` |
| **Hyrule, relief/côte** (module 2_0_1, 515 tuiles rondes/quarts) | coins carrés → **courbes préservées** ; volume −0,2 % (les boîtes surestimaient) | `renders/hyrule_module_coast_blocks_vs_shapes.jpg` (haut = blocs, bas = formes) ; `shape_aware/hyrule_module_2_0_1_{blocks,shapes}.3mf` |

Validation numérique (même validateur bloquant) : Paco 8 modules / 44 corps, Hyrule 9 modules / 86 corps, tous fermés, aucun hors plateau. Limites : enveloppe convexe seulement ; les plots de pentes/tuiles rondes sont omis ; les supports peuvent doubler la masse (module Paco tête : 342 g sans supports → 648 g avec) et PrusaSlicer signale des conflits de chemins entre couleurs avec supports (corps de couleurs qui se touchent) — **non résolu**.

## B3 — Tranchage indépendant (PrusaSlicer 2.7.2, **pas Bambu Studio** ; `tools/slice_check.py`, `slicing/*.json`)
Réglages génériques : buse 0,4, couches 0,2, 3 périmètres, remplissage 15 %, PLA 1,24 g/cm³, plateau 256 mm.

| Fichier | Import / dimensions | Sans supports | Avec supports | Avertissements |
|---|---|---|---|---|
| Coupon de tolérance (22 pièces) | OK, manifold | 2 h 29, 20,5 g, 60 couches | — | « Floating bridge anchors » |
| Plaque Paco (26 briques) | OK | 15 h 54, 106,8 g, 25 couches | identique | ponts |
| Module Paco tête (blocs) | OK | 1 j 4 h, 341,8 g, 985 couches | 1 j 22 h, 648 g | conflits de chemins entre couleurs (supports) |
| Module Paco tête (formes) | OK | 1 j 6 h, 367,6 g | 2 j 2 h, 679,5 g | idem |
| Module Hyrule 0_0_0 (232 mm) | OK | 2 j 6 h, 699,8 g, 304 couches | 2 j 7 h, 712 g | ponts longs |

**Procédure Bambu Studio (à faire par un humain, ~15 min)** : (1) importer `tolerance_coupon_plate.3mf` puis un module 3MF ; accepter « multi-parties » ; (2) vérifier dimensions (X/Y/Z) = valeurs de `coupon.json` ; (3) profil du modèle d'imprimante réel, PLA, 0,2 mm, supports auto désactivés d'abord ; (4) Slice → noter temps, masse, nombre de changements de filament, avertissements ; (5) exporter la capture du rapport ; (6) répéter avec supports « arbre ». **Statut : Bambu Studio = BLOCKED (intervention humaine)**.
