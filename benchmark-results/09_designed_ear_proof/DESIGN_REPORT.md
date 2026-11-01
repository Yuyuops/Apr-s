# LEGO V5 : oreille conçue directement (oreille haute de Paco, 400 mm)

Point de départ : commit `d95a36a`. La conception automatique par voxels est abandonnée, comme demandé. C, D, E, V4 et V4.1 ne sont pas ré-optimisés.
Le GLB source n'a pas été modifié. Aucun service payant, aucune modification de `main`, aucune fusion, aucune application.

**Outil de conception.** Ni BrickLink Studio ni LeoCAD ne sont disponibles dans l'environnement (pas d'interface graphique). Le module est donc écrit en LDraw par programme (`scripts/design_ear.py`), mais comme une **liste explicite de pièces choisies à la main**, avec leur rotation et leur case. Le script ne cherche, n'échantillonne et n'optimise rien. Il convertit la liste en lignes LDraw et vérifie : recouvrements, tenons laissés nus, écart au contour. L'algorithme de placement voxel des itérations 06 à 08 n'est pas utilisé.

## 1. Mesure de l'oreille de référence

Source : faces sombres du GLB de référence placé dans le repère de la tête (`ref_head_frame.glb`). L'oreille haute est séparée de l'oreille basse par regroupement des faces (2 groupes). Projection dans le plan de l'oreille, repère du module V4.1 : *u* le long de la plaque des plateaux, *v* vers le haut.

| Mesure | Valeur |
|---|---|
| Forme | Palette ovale : bout libre largement arrondi, bord supérieur qui descend vers le crâne, bord inférieur presque droit |
| Longueur × hauteur du lobe | 433 × 219 LDU, soit 21,6 × 11 tenons (173 × 88 mm). Le lobe seul, hors racine, mesure environ 18 × 9 tenons. |
| Axe principal dans le plan | −19° (le bout libre est plus haut que la racine) |
| Plan de l'oreille | 52,5° autour de la verticale. Le module garde 53,13°, triangle 3-4-5 des plateaux tournants. |
| Bout libre | Demi-cercle d'environ 80 LDU de rayon, centré à *u* −100, *v* 156 |
| Bord supérieur | *v* 232 → 225 → 205 → 187 → 165 → 150 pour *u* −60 → 0 → 80 → 120 → 160 → 180 |
| Bord inférieur | *v* ≈ 55 de *u* −40 à 140, remonte à 67 en *u* −100 et 87 en *u* −140 |
| Racine | Côté crâne : le lobe bute sur la paroi de la tête vers *u* 140 à 180 |
| Épaisseur apparente | Environ 20 mm (50 à 60 LDU, courbure comprise) |

## 2. Conception

Le contour a été dessiné en premier, avec les grandes pièces dont la forme correspond, puis l'intérieur a été rempli :

- **Bout arrondi.** Une seule plaque demi-disque 4×8 (22888) de 4 tenons de rayon. Elle suit la référence à moins de 10 LDU sur presque tout le bord.
- **Bord supérieur.** Une chaîne d'ailes en escalier : aile 2×4 (41770), puis 3 ailes 2×2 (24299). Leurs pentes (0,25 puis 0,5) suivent celle du bord mesuré, qui s'accentue vers le crâne. L'écart est de moins de 6 LDU aux points mesurés.
- **Bord inférieur gauche.** Une aile 2×2 (24307).
- **Intérieur.** Plaques 4×4, 2×6, 2×4, 2×3 et 1×2.

Dans le plan de l'oreille, le module a 3 couches, soit **24 LDU (9,6 mm)** au total :

| Couche | Rôle | Pièces |
|---|---|---|
| A, côté crâne | Structure. Reçoit les 8 tenons latéraux des équerres. | 25 plaques d'une rangée (1×1 à 1×8), joints décalés par rapport à B |
| B | Contour | 6 pièces de forme (demi-disque, ailes) et 11 plaques |
| C, face extérieure | Finition : **aucun tenon visible** | 23 tuiles : 4×4, 2×6, 2×4, 2×3, 1×4, 1×2, 4 tuiles 1×1 quart de rond, 1 tuile 1×2 à bouts arrondis sur le bout arrondi |

Sur les ailes, seules les cases à tenons reçoivent une tuile. La partie biseautée reste une marche lisse, une plaque plus bas : elle se lit comme un **chanfrein de bord**.

**Remarque sur les pièces.** Les tuiles « 4×4 Corner Round » (27507) et « 2×2 Corner Round » (27925) ont d'abord été essayées. Ce sont des arcs (« macaroni »), pas des quarts de disque pleins : le rendu laissait voir les tenons. Elles ont été remplacées par des tuiles 1×1 quart de rond et des tuiles droites.

**Fixation au crâne.** Le mécanisme validé en 07 et 08 est réutilisé : bases 3680 dans la poche du crâne, dessus 3679, plaque à 53,13°. La plaque passe de 2×10 à 2×8. Le panneau ne descend plus jusqu'au crâne : c'est ce qui donnait le « talon » rectangulaire de V4.1. Un **pied court** porte le lobe :

- brique 2×4, puis plaque 2×4 ;
- dessus : plaque 1×4 côté crâne et tuile 1×4 côté extérieur ;
- **2 équerres 1×2 - 2×2 Up (99207)** dont les faces verticales (8 tenons) entrent dans la couche A.

Le lobe commence ainsi à *v* = 56 LDU, à la hauteur du bord inférieur mesuré (≈ 55). Grâce au pied, les équerres sont sur la rangée côté crâne, et la face extérieure de l'oreille tombe sur la surface extérieure du maillage (z ≈ −28 LDU). Les tenons restés visibles sur la plaque de base sont couverts de tuiles.

**Module : 79 pièces, 28 références**, dont 2 bases de plateau tournant posées dans la tête (V4.1 : 43 pièces de module et 2 cales).

## 3. Validation technique (`validation_technique.json`, `tools/validate_v2.py` sur le modèle complet réordonné)

| | Prototype C | V4.1 | **V5 conçue** |
|---|---|---|---|
| Collisions (géométrie réelle) | 0 | 0 | **0** |
| Pièces déconnectées / îlots | 0 / 0 | 0 / 0 | **0 / 0** |
| Pièces posées sans liaison dans la notice | 0 | 0 | **0** (84 étapes) |
| Tenons bouchés | 0 | 0 | **0** |
| Tenons visibles sur le module | — | nombreux (face extérieure en tenons) | **0** |
| Pivots / liaisons latérales | 0 / 0 | 2 / 33 | **2 / 82** |
| Couples pièce × couleur | 0 à vérifier | 0 à vérifier | **0 à vérifier.** Les 28 couples du module existent dans au moins 27 sets (Rebrickable, `nomenclature.csv`) ; le dessus de plateau tournant 3679 n'existe qu'en gris clair. |
| Épaisseur de l'oreille | Colonnes de voxels | 16 LDU | **24 LDU (9,6 mm)** ; référence ≈ 20 mm |
| Contour de la couche B / lobe de référence (IoU dans le plan) | — | — | **0,86**. La zone où la référence entre dans la tête n'est pas comptée comme une erreur de forme. |
| Silhouette face / profil / dessus (modèle complet, grille de 8 mm) | **0,955 / 0,958** / 0,893 | 0,896 / 0,920 / 0,890 | 0,923 / 0,939 / 0,878 |
| IoU de volume | 0,853 | 0,713 | 0,774 |
| Pire découpage de l'oreille : masse, contacts, coefficient sous le poids propre, force de décrochage au bout (indicatifs) | — | 25,1 g, 4, 5,6, 0,15 N | **37 g, 4, 3,5, 0,16 N** |

- **Silhouettes globales.** Elles restent sous C, mais nettement au-dessus de V4.1. L'oreille V5 est 2 fois plus fine que la référence, et l'espace sous le lobe est vide alors que la référence y projette la racine de l'oreille basse. Ces deux points pèsent sur l'IoU mesurée sur la grille de 8 mm, qui récompense le volume en colonnes de C.
- **Tenue.** Comme en V4.1, le point faible est la liaison oreille-tête par 2 plateaux tournants 2×2 (un pivot compté pour 1 contact). L'oreille est plus lourde : 37 g au lieu de 25 g, à cause des 3 couches. Modèle : 1,0 N par tenon (hypothèse), pièces rigides. **Ce n'est pas une mesure physique.**
- **Ordre de montage.** Calculé par `reorder_notice.py` et vérifié : aucune pièce posée dans le vide.

## 4. Constat visuel (`comparaison_ref_C_V5.png`)

Les trois versions sont rendues avec le même cadrage, les mêmes angles, la même lumière et la même échelle, en vraies pièces LDraw. Les vues de la référence et de C sont celles de l'itération 08.

| Vue | Constat |
|---|---|
| Oreille, face extérieure | **V5 meilleure.** Contour net et continu : bout en demi-disque, bord supérieur biseauté qui descend vers le crâne, bord inférieur droit. La surface est lisse (tuiles), sans escaliers ni tenons. C montre un contour en marches, une surface en tenons et en colonnes. |
| Profil, trois quarts | **V5 meilleure.** La palette est lisible et proche de la forme de référence. C reste en colonnes hérissées. |
| Oreille, face intérieure | **V5 meilleure, avec une réserve.** Contour aussi net que sur la face extérieure, dessous de plaques plat. Les creux des tenons restent visibles. |
| Face | **Équivalente ou moins bonne.** Vue presque par la tranche, l'oreille V5 (9,6 mm) paraît plus mince que la référence (≈ 20 mm). Le volume de C est plus proche. |
| Raccord au crâne | **Moins discret que voulu.** Le pied (4 tenons de large, 16 mm de haut) se voit sous le lobe, et un jour reste entre le bout du lobe et la paroi du crâne, là où la référence se fond dans la tête. Plus de talon rectangulaire, en revanche, comme en V4.1. |

**Conclusion visuelle.** Sur 4 vues sur 6, l'oreille conçue est nettement meilleure que C sans zoomer : forme, propreté de surface et contour. Elle est moins bonne de face (épaisseur) et au raccord (pied visible, jour au bout du lobe).
