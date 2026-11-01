# Brickify V4 : démonstrateur d'oreille articulée (oreille haute de Paco, 400 mm)

Dépôt `Yuyuops/Apr-s`, branche `research/lego-brickify-benchmark`, à partir du commit `49b2265`. Résultats antérieurs intacts.
Rien n'est fusionné dans `main`. Aucun service payant, aucune commande, aucun déploiement. Le GLB source n'a pas été modifié.

## 1. Étude préalable

- **Itération 06 relue.** Elle concluait qu'il fallait des modules de détail, des liaisons à angle quelconque et un validateur étendu (`06_head_surface_optimization/DECISION.md`). Le prototype C est repris tel quel : même grille, même empilement, sortie reproductible.
- **Oreille haute dans le GLB** (segmentation de l'itération 06, puis ajustement d'un plan sur les voxels fins de sa peau noire) :
  - plan vertical de normale (−0,79 ; 0 ; 0,61), soit **52,5°** par rapport à l'axe X dans le plan horizontal ;
  - environ 18 × 12 tenons (145 × 96 mm) ;
  - forme de feuille, attachée à l'arrière haut du crâne, dont le dessus est arrondi à cet endroit.
- **Pièces étudiées** (couleur vérifiée dans Rebrickable, `nomenclature.csv`) :

| Famille | Retenue | Constat |
|---|---|---|
| Plateau tournant 2×2 (3680 base, 3679 dessus) | **Oui** | Pivot vertical à angle libre. La base existe en noir (597 sets). **Le dessus n'existe qu'en gris clair (776 sets)** : il est utilisé dans cette couleur, et caché sous la plaque. |
| Charnière plate 1×4 (2429/2430) | Non | Pratiquement pas produite (1 set par couleur). |
| Équerres 99780 (Up), 99781 (Down), 44728 (1×2 − 2×2 Down) | 99780 et 99781 | La 44728 descend 16 LDU sous le dessus de la tête et entrait en collision avec les cales et les bases (vérifié). |
| Plaques biseautées 2×2, 2×3, 2×4 ; plaque 3×3 à coin arrondi (30357) ; plaque 4×4 à coin arrondi (30565) | Ajustées automatiquement sur la silhouette | 6 plaques biseautées et 1 coin arrondi retenus. La 30565 n'a jamais apporté de gain. |
| Clips et barres, tuiles courbes | Non | Pas nécessaires pour ce mécanisme. Le validateur n'a été étendu qu'aux mécanismes utilisés, comme demandé. |

## 2. Module retenu (`module_oreille.ldr`, 48 pièces)

```
tête C (dessus du crâne, colonnes mises à niveau par 37 plaques 1x1 noires)
  └─ 2 × plateau tournant 2x2, base 3680 (4 tenons chacun, alignée sur la grille)
       └─ 2 × dessus 3679 (pivot vertical, angle libre)
            └─ plaque 2x10 (3832) : les deux pivots sont à 3 x 4 tenons l'un de l'autre, donc à 5 tenons le long de
               la plaque (triangle 3-4-5). La plaque se pose sur les deux pivots et fixe l'angle à 53,13 deg.
                 ├─ 1 équerre 99781 (Down) : 2 tenons latéraux à la hauteur -14
                 └─ 3 équerres 99780 (Up) sur une plaque 1x2 de rehausse : 2 tenons latéraux chacune, à -34
                      └─ panneau d'oreille, 2 couches de plaques noires dans le plan de l'oreille :
                         couche intérieure (16 plaques) sur les 8 tenons latéraux ;
                         couche extérieure (20 pièces dont 7 biseautées ou arrondies), joints décalés, tenons vers l'extérieur
```

- **Orientation obtenue : 53,13°**, contre 52,5° mesurés, soit 0,6° d'écart. Le triangle 3-4-5 impose cet angle, et il est vérifiable géométriquement : les tenons du dessus des plateaux tombent exactement dans les points d'appui de la plaque tournée.
- **Position.** Le plan du panneau est imposé par les équerres. La recherche le place à **25 LDU (1,2 tenon) en dehors** du plan de l'oreille du GLB, sans toucher la tête.
- **Silhouette.** Projection du GLB sur le plan du panneau, en cellules de 20 × 20 LDU gardées à partir de 60 % de couverture.
  - Pièces de contour ajustées sur la silhouette fine (5 LDU).
  - 11 cellules retirées parce qu'elles touchaient la tête.
  - 4 pièces sans liaison élaguées.
- **Tête.** Grille C sans la peau de l'oreille haute (441 cellules) ni son cœur jaune (615 cellules), empilée avec les réglages de C.
  - 9 pièces restées flottantes ont été retirées (`--drop-floating`).
  - 2 tuiles placées sous les plateaux ont été remplacées par des plaques de même taille.

## 3. Validation (`validation_connexions.json`, `tools/validate_v2.py`, indépendant du générateur)

Mécanismes ajoutés au validateur, et seulement ceux-là :
- **Liaison pivot.** Le dessus 3679 est reconnu sur une base 3680 s'il a la même origine et ne tourne qu'autour de la verticale. C'est le seul chevauchement de volume autorisé.
- **Points d'appui des équerres « Down ».** Ils sont sous leur plaque horizontale.
- **Tenons latéraux et pièces à angle quelconque.** Correspondance tenon/point d'appui en 3D, à 1 LDU près.
- **Collisions sur la géométrie réelle** pour les pièces tournées et les équerres. On utilise des points à au moins 1 LDU à l'intérieur de chaque pièce (volume mesuré par rayons, ou deux plaques pour une équerre), testés contre les boîtes exactes des pièces alignées et, par proximité, entre eux.

| | Prototype C | Tête C + module | Module seul |
|---|---|---|---|
| Pièces / références | 1 735 / 20 | 1 299 / 31 | 48 / 22 |
| Collisions (pièces alignées : boîtes ; tournées et équerres : géométrie réelle) | 0 | **0** | **0** |
| Tenons bloqués | 0 | 0 | 0 |
| Pièces déconnectées / îlots | 0 / 0 | **0 / 0** | 0 / 0 |
| Liaisons latérales / pivots | 0 / 0 | 47 / 2 | 47 / 2 |
| Pièces posées sans liaison (notice réordonnée) | 0 | **0** | 0 |
| Étapes de notice | 149 | 89 | 31 |
| Couples pièce × couleur non vérifiés | 0 | 0 | 0 |
| IoU de volume / silhouettes face, profil, dessus | 0,853 / 0,955 ; 0,958 ; 0,893 | **0,714 / 0,888 ; 0,930 ; 0,890** | — |
| Coefficient minimal sous le poids propre (indicatif) | 38,2 | 24,5 | — |
| Module entier (26,5 g) : contacts, coefficient sous le poids propre, force de décrochage au bout | — | 6 contacts, 30, **0,57 N** | — |
| Sous-ensembles ≥ 1 g décrochés par moins de 0,5 N | 26 | 10 | — |

Le point le plus faible de la tête (0,04 N) reste le bout de **l'oreille basse en voxels**, héritée de C et non traitée ici.

**Modèle de résistance et limites.**
- Pièces rigides, **1,0 N par tenon** à l'arrachement (hypothèse prudente), compression libre.
- Le pivot d'un plateau tournant compte pour **un seul** contact, faute de donnée fiable sur sa tenue.
- Masse : 0,10 g par tenon × tenon × plaque de matière.
- Non modélisés : frottements, jeu des pivots, fatigue.
- **Ce sont des indicateurs de comparaison, pas des résistances garanties. Rien n'est validé physiquement sans montage réel.**

## 4. Constat visuel (`reference_vs_C_vs_module.png`, `detail_fixation.png`)

- **Ce qui progresse.**
  - L'angle de l'oreille est juste : en vue de fixation et de trois quarts, elle part dans la même direction que sur la référence.
  - C'est une oreille plate en plaques noires à tenons, comme sur la référence, au lieu d'un empilement de colonnes épaisses.
- **Ce qui reste insuffisant.**
  1. **L'oreille semble posée sur des poteaux.** À la base de l'oreille, le crâne est arrondi et plus bas que le panneau. Les 37 plaques de cale forment des colonnes noires visibles, et l'oreille ne rejoint pas la tête.
  2. **Silhouette trop épaisse et carrée** du côté de la tête. Elle est échantillonnée en cellules de 8 mm, avec seulement 7 pièces de contour. La pointe est arrondie, mais la feuille n'est pas effilée comme sur la référence.
  3. **De profil, on voit le dessous des plaques** (tubes) de la face intérieure.
  4. **Les chiffres le confirment.** La fidélité de silhouette est inférieure à C : 0,888 contre 0,955 de face. Le cœur de l'oreille voxel a été retiré, et le panneau, fin, est décalé de 1,2 tenon.
