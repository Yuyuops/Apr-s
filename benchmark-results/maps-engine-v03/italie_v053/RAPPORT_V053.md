# LEGO Maps Italie V0.5.3 — consolidation avant l'Italie complète

Référence acceptée : V0.5.2. Pas de refonte artistique. Aucun achat, moteur 1 inchangé, pas de fusion dans `main`, **aucun essai physique** (mesures mécaniques = indicatives, modèle rigide du validateur, 1 N/tenon supposé). Anciens modèles conservés (`v052_reference/`, `../italie_v052_mountain_refinement/`, `../italie_v051/`).

## 1. Corrections esthétiques (montagne seule ; Colisée inchangé)
- **Sommet sud-ouest rehaussé** : 29 → 58 mm (sommet de brique au point nominal ; la crête atteint 115 mm), visible comme 3ᵉ volume ; sommets est 86 mm, nord-ouest 67 mm, nord-est 67 mm. Pas de dôme (vue de face : 4 volumes séparés par des cols).
- **Neige redistribuée** : plus seulement sur un pic ; sur les trois sommets hauts et en traînées dans les couloirs (> 19 plaques).
- **Forêt** : 16 conifères solides (V0.5.2 : 5 solides + 13 décoratifs) sur terrasses 2×2 réservées (17 pads) ; plus d'arbre à tronc 1×1.
- **Conservé** : vallées (corridor central et col nord), silhouette de l'île, palette ; verts de vallée un peu plus sombres car moins d'arbres feuillus clairs.

## 2. Réduction de la fragilité (même critères du validateur, aucun seuil modifié)
| | V0.5.1 | V0.5.2 | **V0.5.3** |
|---|---|---|---|
| Pièces | 2 714 | 2 720 | **2 487** |
| Pièces tenues par 1 tenon | 703 | 855 | **486** |
| … feuilles décoratives | 242 | 305 | **163** |
| … portant d'autres pièces | 461 | 550 | **323** |
| Points d'articulation | 433 | 530 | **387** |
| Montagne : plus grosse perte sur 1 point | 9 pièces | 10 | **6** |
| Pire défaillance isolée | 7,5 g | 11,7 g | **8,6 g** |
| Murs Colisée tenus par 1 tenon | 55 | 55 | **25** |
| Éléments de mur 1 tenon d'épaisseur | 193 | 193 | **174** |
| Troncs d'arbres à 1 tenon | 12 | 26 | **0** |
Les trois objectifs « retour au niveau V0.5.1 » sont dépassés (liaisons porteuses −30 %, articulations −11 %, pièces à un tenon −31 %) avec 227 pièces de moins.
Moyens : (1) **tilage conscient des appuis** (`tiler.py`) : chaque pièce est choisie parmi 30 tirages pour minimiser les pièces tenues par un seul tenon, en favorisant les formes de largeur ≥ 2 ; (2) couleurs de strates décidées par blocs 2×2 pour éviter la fragmentation en 1×1 ; (3) conifères solides sur terrasses planes ; (4) rochers 1×2 (2 tenons) quand possible, 13 rochers 1×1 conservés comme décor ; (5) plaques de micro-relief 2×2 uniquement ; (6) plage tilée avec appui.
**Non traité** : épaississement des murs d'arcades (174 éléments à 1 tenon d'épaisseur : les arches ont 4 tenons chacune, un doublage aurait modifié la façade validée) ; reste des 1×1 de pics isolés dans la montagne (décoratifs). Les 163 feuilles à un tenon sont des rochers, buissons, plage, hypogée : **décoratif** ; les conifères, arches, pentes (2 tenons ou plus) et socle sont **structurellement acceptables** dans ce modèle.

## 3. Validation (rejouée, `results/diorama_v053/`)
2 487 pièces — 0 collision, 0 déconnectée, 0 îlot, 0 pose sans appui, 0 tenon bloqué ; LDraw = JSON = nomenclature. 134 références, **134/134 couples catalogués** Rebrickable, `.dat` réels non-alias ; 4 couples absents substitués (6 pièces, `metrics.json`). Prix/stock non vérifiés. Accessibilité du montage : strictement couche par couche, 5 pièces avec cellules en surplomb (16–17 avant), 24 niveaux, max 408 pièces par niveau. Table complète : `comparatif_metrics.md`.
Rendus LDraw réels sous les mêmes angles : `results/diorama_v053/renders/`, comparatifs `comparatifs/V052_vs_V053_*.png`.

## 4. Échelle artistique et Italie 128 × 128
Voir `italia128/PLAN_GENERATION_ITALIE_128.md`, `artistic_scale_config.json` (règles réutilisables, aucune dimension en dur), `output/composition_preview.png`, `sector_overlay.png`, `placements.json` (journal des décisions), `sector_plan.json`. Relief **réel** (Terrain Tiles + Natural Earth, licences dans `fixtures/SOURCES.md`). Titre et rose des vents prouvés en vraies tuiles (`output/decor_patch`, validés). Colisée redimensionné par configuration et validé à 18 × 15 et 14 × 11.

## 5. Risques identifiés
1. **Composition** : le Colisée plein (18 × 22) couvre ~40 % de la largeur de la péninsule et le relief des Apennins ; à arbitrer sur rendu 3D (variante simplifiée 15 × 18 prête). Sous ~18 × 22 il perd l'ovale (boîte à arcades) : variante « icône » à concevoir.
2. Modules Pise et Vésuve inexistants (densités provisoires).
3. Estimation ≈ 6 900 pièces (5 200–9 400), sous l'hypothèse 10–25 k : 86 % de la grille est de la mer à 1 tenon ≈ 8 km.
4. Relief réel exagéré ≈ 25× ; à valider visuellement sur un secteur pilote ; les crêtes MNT n'ont pas encore été passées dans le générateur de montagne.
5. Fragilité : 486 pièces à un tenon restent ; aucun essai physique ; accrochage mural non évalué.
