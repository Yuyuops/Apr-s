# Brickify V4.1 : correction finale de l'oreille articulée (oreille haute de Paco, 400 mm)

Point de départ : commit `2fde0a1`, module V4 (`07_articulated_ear_proof/`), mécanisme conservé : plateaux tournants 2×2 en triangle 3-4-5, plaque 2×10 à 53,13°, équerres, panneau de 2 couches.
Le GLB source n'a pas été modifié. Aucun service payant, aucune modification de `main`, aucune fusion.

## 1. Corrections appliquées (`tools/proto/ear_module_v41.py`)

| Correction demandée | Ce qui a été fait | Résultat |
|---|---|---|
| **1. Fixation intégrée au crâne** | Le niveau des plateaux n'est plus le haut de la colonne la plus haute. La recherche choisit le niveau qui minimise 4 × cales + 2 × cellules creusées, avec des cales limitées à 3 plaques. Les cellules au-dessus de ce niveau dans les 8 colonnes d'appui forment une **poche**. Le corps du module et le panneau peuvent creuser la tête : le module partout sauf à moins de 2 cellules des yeux et de la bouche, le panneau seulement à moins de 2 cellules de l'ancienne racine de l'oreille. La tête est ensuite reconstruite avec les réglages de C. | Plateaux **6 plaques plus bas** qu'en V4 (couche 26 au lieu de 32). Cales : **2 plaques au lieu de 37**. **18 cellules retirées** (13 de poche, 5 touchées par le module ou le panneau) sur 3 967. 11 pièces de tête restées flottantes après reconstruction ont été retirées (11 cellules). Plus d'effet de poteaux : l'oreille part du crâne. |
| **2. Contour de l'oreille** | Catalogue de contour élargi aux pièces existant en noir : plaques biseautées 3×8 (50304/50305) et 3×6 (54383/54384), plaque 3×3 à coin coupé (2450), coin arrondi 2×2 (79491), en plus de celles de V4. Le panneau peut entrer dans la tête près de la racine. | 8 pièces de contour biseautées ou arrondies, contre 7 en V4. Orientation conservée : 53,13° (mesuré : 52,5°). **La silhouette reste large et presque rectangulaire** : la projection de l'oreille du GLB, échantillonnée sur la grille de 8 mm des tenons, ne permet pas de placer les grandes pièces biseautées là où la feuille s'effile. Une plaque biseautée 3×8 n'est rentable que si 3 × 8 cellules suivent sa pente, ce qui n'arrive jamais ici. |
| **3. Face intérieure** | Test de faisabilité : une tuile ne se fixe que sur un tenon. Or la face intérieure du panneau est la face « dessous » (tubes), qui reçoit les tenons des équerres. Il faudrait une couche à tenons tournés vers l'intérieur, fixée par des briques à tenons sur deux faces opposées (47905, 52107, disponibles en noir), puis une couche de tuiles. | **Non appliqué.** Cela ajoute au moins 2 couches (le panneau passerait de 16 à environ 40 LDU, soit 2,5 fois son épaisseur) et environ 40 pièces. C'est l'épaississement excessif que la mission demandait d'éviter. Les tubes restent visibles sur la face intérieure (vue « oreille int. »). |

## 2. Validation (`validation_connexions.json`, `tools/validate_v2.py`)

| | Prototype C | Module V4 | **Module V4.1** |
|---|---|---|---|
| Pièces (tête + oreille) / références | 1 735 / 20 | 1 299 / 31 | **1 246 / 33** |
| Pièces du module | — | 48 (+ 37 cales) | **43 (+ 2 cales)** |
| Cellules de tête retirées | — | 0 (peau et cœur de l'oreille retirés comme en V4) | **18** (poche 13, module ou panneau 5) |
| Collisions (géométrie réelle des pièces tournées et des équerres) | 0 | 0 | **0** |
| Pièces déconnectées / îlots | 0 / 0 | 0 / 0 | **0 / 0** (1 plaque biseautée 2×2 isolée retirée de la notice) |
| Liaisons latérales / pivots | 0 / 0 | 47 / 2 | 33 / 2 (6 tenons latéraux d'équerre) |
| Pièces posées sans liaison | 0 | 0 | **0** |
| Étapes de notice | 149 | 89 | **84** |
| Couples pièce × couleur non vérifiés | 0 | 0 | **0** (53 lignes ; dessus de plateau tournant en gris clair seulement) |
| **Silhouette face / profil / dessus** | **0,955 / 0,958** / 0,893 | 0,888 / 0,930 / 0,890 | **0,896 / 0,920** / 0,890 |
| IoU de volume | 0,853 | 0,714 | 0,713 |
| Module : masse, contacts, coefficient sous le poids propre, force de décrochage au bout (indicatifs) | — | 26,5 g, 6, 30, 0,57 N | **25,1 g, 4, 5,6, 0,15 N** |
| Sous-ensembles ≥ 1 g décrochés par moins de 0,5 N | 26 | 10 | 12 |

- **Silhouettes.** Par rapport à C, elles baissent de 0,06 de face et de 0,04 de profil. **Aucun gain visuel ne compense cette baisse** (voir §3).
- **Tenue.** L'oreille est plus basse et plus proche de la tête, et ses deux plateaux reposent dans la poche. Mais elle n'a plus que 6 tenons latéraux. Le pire découpage la relie au reste par 4 contacts, contre 6 en V4.
- **Modèle de résistance.** Pièces rigides, 1,0 N par tenon (hypothèse), un pivot compté comme un seul contact, frottements ignorés. Ce sont des indicateurs de comparaison. **Rien n'est validé physiquement sans montage.**

## 3. Constat visuel (`comparaison_ref_C_V4_V41.png`, `detail_raccord_et_faces.png`)

Même cadrage, mêmes angles, même lumière et même échelle pour les quatre versions, vraies pièces LDraw.

- **Raccord au crâne : corrigé.** Les poteaux ont disparu, et l'oreille part du crâne par une courte base noire.
- **Orientation : juste** de face comme de trois quarts. C'est le seul point où le module dépasse C.
- **Silhouette de l'oreille : pas meilleure que C.** De face, de profil et sur les deux faces de l'oreille, V4.1 montre un panneau large, presque rectangulaire, avec un talon de raccord. L'oreille de C, en colonnes épaisses, garde une forme de feuille effilée plus proche de la référence sous ces mêmes angles.
- **Face intérieure : tubes visibles.**

**Conclusion : pas d'amélioration esthétique nette par rapport à C sous plusieurs angles.** La règle d'arrêt s'applique.
