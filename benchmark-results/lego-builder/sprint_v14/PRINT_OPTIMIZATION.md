# Sprint V14 — Optimisation de l'impression (mesures sur les exports V13 réels)

Règle suivie : aucune optimisation n'est retenue si elle dégrade visiblement le modèle. Tranchage = PrusaSlicer, profil proxy A1 (voir `SLICING_BENCHMARK.md`) ; **aucune mesure sur imprimante réelle**.

## 0. Correction importante des supports
Trancher les corps de couleur d'un module comme objets **séparés** fait générer à chaque corps ses supports à travers ses voisins (« gcode path conflicts between b0 and b1 ») : masse de supports **surestimée**. Chaque module a donc été **fusionné en un seul solide** (union booléenne, comme un slicer multicolore voit un objet à plusieurs parties) puis tranché (`merged_supports.json`) :
| | sans supports | avec supports (45°) | supports |
|---|---|---|---|
| Paco, 8 modules | 1 084 g, 46,7 h | 1 764 g, 86,8 h | **+680 g (+63 %), +40 h** |
| Hyrule, 9 modules | 5 450 g, 123,6 h | 5 519 g, 129,6 h | **+69 g (+1 %), +6 h** |
→ le problème de supports est **réel pour Paco (formes en 3D), négligeable pour Hyrule (relief plat)**. (L'estimation V13 « 342 → 648 g » du module de tête était gonflée par le tranchage multi-objets.)

## 1. Orientations et supports (module de tête Paco, 120 × 144 × 200 mm, profil A1, objets séparés → valeurs relatives seulement)
| Orientation | sans supports | avec supports 45° | Commentaire |
|---|---|---|---|
| debout (défaut) | 18,1 h, 368 g | 36,9 h, 680 g | plots vers le haut ; 985 couches |
| couché sur le dos (x 90°) | 19,7 h, 375 g | **32,8 h, 555 g** | 720 couches ; **meilleur compromis de supports** (−18 % de masse vs debout) |
| couché sur le côté (y 90°) | 19,0 h, 372 g | 34,1 h, 579 g | plots de côté : surfaces de plots dégradées |
| retourné (x 180°) | 17,9 h, 367 g | 34,4 h, 637 g | plots vers le plateau : **inacceptable pour les plots** |
Variantes de supports (debout) : seuil 60° : sans effet (680 g) ; « buildplate only » : 588 g (−14 %) ; **organiques : 501 g (−26 %), 29,7 h** → la meilleure réduction de supports mesurée, sans changer la géométrie du modèle (les supports touchent le dessous des surplombs ; l'état de surface de ces dessous n'a pas été évalué).
**Retenu** : supports organiques (−26 %) ; l'orientation « sur le dos » est à tester physiquement (plots latéraux, déformation) avant adoption. Aucune de ces options ne modifie la forme finale.

## 2. Réduction des purges
- **Changements de couleur** (couches de 0,2 mm, n couleurs − 1 par couche) : Paco 7 990, Hyrule 4 031 pour le modèle complet.
- **Fusion du noyau caché** (voxels sans face visible → couleur dominante de leur couche ; **aucun changement visible**) : Paco −11,2 % (7 584 → 6 736), **Hyrule −29,0 %** (3 968 → 2 816). 50–75 % des voxels de Hyrule sont cachés. Le nombre de couleurs *simultanées* par couche, lui, ne baisse presque pas : **cette optimisation réduit la purge, pas le besoin d'emplacements couleur** (`hidden_core_merge.json`).
- Ordre des couleurs en serpentin (n − 1 changements par couche, pas n) : déjà supposé dans le modèle.
- Machine à têtes multiples (U1) : purge −85 % **selon le constructeur** — non mesuré ; non exploitable tant que les modules dépassent 4 couleurs.

## 3. Séparation intelligente des couleurs / découpe en petits modules
Contrainte vérifiée : A1 + AMS Lite et U1 = **4 couleurs simultanées** ; Paco 5–6 couleurs par module (jusqu'à 5 par couche), Hyrule 5–12 (jusqu'à 7 par couche). Découper en dalles plus petites (`tile_split_colours.json`) :
| Dalle | Paco : dalles / ≤ 4 couleurs par couche | Hyrule : dalles / ≤ 4 couleurs par couche | Hyrule : moy. de couleurs distinctes par dalle |
|---|---|---|---|
| 30 plots (actuel) | 3 / 67 % | 9 / 44 % | 9,6 |
| 15 plots (120 mm) | 7 / 71 % | 36 / 92 % | 7,2 |
| 10 plots (80 mm) | 10 / 80 % | 81 / **99 %** | 5,7 |
| 8 plots (64 mm) | 15 / **100 %** | 121 / 99 % | 5,1 |
→ des dalles de 8–10 plots rendent presque toutes les couches imprimables avec 4 emplacements, mais (a) il reste en moyenne > 4 couleurs distinctes par dalle (échanges de bobine manuels en cours d'impression), (b) on passe de 8–9 à 15–121 modules (joints, tenons, assemblage). **Gain non démontré** : à tester seulement si une machine à purge faible (U1) est retenue.

## 4. Modules monochromes assemblables (procédé 3)
Chaque corps de couleur est découpé en **composantes connexes** (421 pièces Paco, 594 Hyrule) imprimées à plat par couleur : **purge nulle**, supports par pièce, mais l'assemblage de pièces imbriquées sans fixation intégrée est **non résolu** (colle ou tenons à ajouter ; aucun tenon n'existe entre pièces de couleurs différentes). Temps d'intervention ≈ 8,8 h (Paco) et 13,8 h (Hyrule) **sous hypothèse de 40 s par pièce**. Une plaque Paco (101 pièces noires) fait planter PrusaSlicer (segfault) : estimée.

## 5. Conservation des courbes, pentes et détails
- Procédé 1 (briques rectangulaires) : **116 pièces Paco (3,6 %) et 515 Hyrule (4,8 %) non imprimables** → dégradation visible (coins arrondis, pentes) : **exclu** du classement.
- Procédés 2 et 3 : enveloppe convexe des pièces réelles (V13) : courbes et pentes conservées ; arches/creux remplis, plots des pentes omis.
- Fusion du noyau caché, supports organiques, dalles : aucune n'altère la surface visible.

## 6. Risques liés aux grandes pièces et aux tolérances
- Modules Hyrule jusqu'à 240 × 240 mm : marge de 10–30 mm sur 250–270 mm ; gauchissement/décollement probables (non testé) ; 1 module = 20–25 h d'impression (un échec coûte une journée).
- Tolérances : plots/tubes/douilles **non validés** (coupon non imprimé) ; un jeu inadapté invalide les procédés 1 et 3 (pièces qui ne tiennent pas) et les liaisons de modules.
- Aucune des optimisations ci-dessus ne remplace les tests physiques listés dans `FINAL_RECOMMENDATION.md`.
