# LEGO V5.1 : finalisation de l'oreille conçue directement (oreille haute de Paco, 400 mm)

Point de départ : commit `e651919`, V5 (`09_designed_ear_proof/`), conservée intacte. Aucun remplissage voxel pour les surfaces de l'oreille. Le GLB source n'a pas été modifié. Aucun service payant, aucune modification de `main`, aucune fusion, aucune application.

## 1. Phase 1 : les trois réserves

### A. Épaisseur : 9,6 mm → 20,8 mm (référence ≈ 20 mm)

L'oreille devient un **sandwich** dont les deux faces sont finies. Dans le plan de l'oreille (z du module) :

| Couche | z (LDU) | Pièces |
|---|---|---|
| Face extérieure | −36 … −20 | Le contour de V5, mêmes pièces de forme (demi-disque 4×8, ailes 2×4 et 2×2), une couche de plaques et des tuiles. Tenons vers l'extérieur. |
| Âme | −20 … 0 | Mur d'un tenon d'épaisseur, monté tenons en haut. Il alterne une assise de **briques à tenons sur 2 faces opposées** (52107, 47905), qui tiennent les deux faces, et 2 plaques 1×N. Une rangée de tenons latéraux tous les 40 LDU, soit une rangée de panneau sur deux. |
| Face intérieure | 0 … 16 | **Miroir** de la face extérieure, tenons vers la tête, tuiles. La face intérieure n'a plus de fonds de pièces visibles (réserve de V4.1 et V5). |

**Épaisseur variable.** Les bords biseautés des ailes ne portent pas de tuile : le bord est plus mince (36 LDU) que le centre (52 LDU). L'âme est en retrait du contour.

**Âme allégée.** Dans les longues assises, une brique 1×2 sur deux est omise (les plaques font pont). Les extrémités restent pleines pour fermer le bord. Le dessus de chaque colonne d'âme reçoit une tuile, là où le contour la cache.

### B. Raccord au crâne : plus de pied, plus de jour

- **Le pied est supprimé.** Plus rien ne descend sous le lobe : sous le lobe, on voit la tête et l'oreille basse, comme sur la référence.
- **L'oreille entre dans le crâne par son extrémité côté tête**, comme sur la référence. Le panneau et l'âme pénètrent la surface du crâne. Les cellules de tête traversées (273, aucune des yeux ni de la bouche) sont retirées de la grille de C, puis **la tête est reconstruite** avec les réglages de C (`brickify_plus`, occupation 0,5). La surface du crâne se referme autour de l'oreille.
- **La racine de l'âme est cachée dans le crâne :** un bloc de briques 2×6 et 1×6 et une plaque 4×6, sous la surface de la tête.

### C. Tenue : plus de plateau tournant

La fixation utilise un **emboîtement direct sur la grille de la tête, grâce au triangle 3-4-5**. Une plaque tournée de 53,13° a ses tenons sur un réseau qui coïncide avec la grille de la tête **une position sur cinq** : la condition est b ≡ 3 − 3a (mod 5) sur les indices de tenon.

- Une plaque 4×6 noire (3032) est noyée dans le crâne, sous la racine, à v 40…48.
- Sous elle, aux **5 positions coïncidentes**, se trouvent 5 plaques 1×1 de la tête. Les tuiles de tête sous ces positions sont changées en plaques. Il n'y a rien entre les autres positions.
- Ce sont 5 **vrais emboîtements tenon/creux**, sans pivot.

La position de la plaque a été choisie par une recherche exhaustive sur la grille de la tête. Critères : nombre de coïncidences soutenues, plaque recouverte par la tête, distance aux yeux et à la bouche. La solution retenue a été vérifiée à l'œil.

**Hypothèses du calcul (`validate_v2.py`, inchangé) :**

- pièces rigides, 1,0 N de tenue par tenon (valeur supposée), 0,10 g par tenon × tenon × plaque ;
- poids propre, puis force au bout de chaque sous-ensemble découpé par des plans horizontaux ;
- seule la direction d'emboîtement dominante est comptée (les tenons latéraux de l'âme sont ignorés) : c'est prudent ;
- pas de frottement.

**Ce sont des indicateurs de comparaison, pas une mesure. Une validation numérique ne remplace pas un essai physique.**

## 2. Phase 2 : validation comparative (`validation_technique.json`)

| | Prototype C | V5 | **V5.1** |
|---|---|---|---|
| Collisions (géométrie réelle) | 0 | 0 | **0** |
| Pièces déconnectées / îlots / posées sans liaison | 0 / 0 / 0 | 0 / 0 / 0 | **0 / 0 / 0** (85 étapes) |
| Tenons bouchés | 0 | 0 | **0** |
| Tenons visibles sur les faces de l'oreille | — | 0 (face extérieure seulement) | **0 sur les deux faces** |
| Couples pièce × couleur (Rebrickable) | vérifiés | 28, au moins 27 sets | **29, au moins 27 sets** (`nomenclature.csv`) |
| Pièces du module | — | 79 | 142 (+ 5 plaques 1×1 dans la tête) |
| Épaisseur de l'oreille | colonnes de voxels | 9,6 mm | **20,8 mm** au centre (référence ≈ 20 mm) |
| Silhouette face / profil / dessus | **0,955 / 0,958** / 0,893 | 0,923 / 0,939 / 0,878 | **0,943 / 0,942** / 0,888 |
| IoU de volume | **0,853** | 0,774 | 0,780 |
| Liaison oreille-tête | — | 2 plateaux tournants 2×2 | **5 tenons sur une plaque noyée** |
| Pire découpage de l'oreille : masse / contacts | — | 37 g / 4 | **86,8 g / 5** |
| Coefficient sous le poids propre | — | **3,47** | 2,17 |
| Force de décrochage au bout | — | 0,16 N | **0,32 N** |

**Constat visuel** (`comparaison_ref_C_V5_V51.png`, mêmes vues, lumière et échelle ; vraies pièces LDraw ; gros plans dans `zooms/`) :

| Vue | Constat V5.1 |
|---|---|
| Face | **Amélioration visible.** L'oreille a du volume (palette épaisse) et sort du crâne sans pied. |
| Raccord au crâne | **Amélioration visible.** Plus de pied ni de plaque de base apparente, plus de jour : le lobe entre dans la tête. Il reste quelques taches noires sur le dessus du crâne, autour de la racine. Ce sont les cellules noires de C (racine de l'oreille) et 2 faces de briques à tenons latéraux visibles entre les panneaux. |
| Profil, trois quarts | Gains de V5 conservés, avec en plus le volume. |
| Face extérieure | Contour et tuiles de V5 conservés. Le lobe se fond dans la tête au lieu de s'arrêter devant. |
| Face intérieure | **Amélioration** par rapport à V5 : face tuilée, plus de fonds de pièces. |

**Défauts restants :**

1. Sur le bord supérieur, entre les deux faces, les tenons de la dernière assise d'âme dépassent de 4 LDU (1,6 mm). Ils sont visibles au ras du bord (`zooms/zoom_bord_haut_V51.png`). Il n'existe pas de brique à tenons latéraux sans tenon de dessus.
2. Sous 2 ailes du bord supérieur, l'âme dépasse la pente de quelques LDU entre les faces : il faut une rangée de tenons sous chaque aile.
3. Les ailes intérieures sont des miroirs à 2 à 5 LDU près (corps des ailes asymétriques).
4. L'oreille pèse 2,3 fois plus que V5. Le coefficient sous le poids propre baisse (3,47 → 2,17), alors que la force au bout double (0,16 → 0,32 N).
