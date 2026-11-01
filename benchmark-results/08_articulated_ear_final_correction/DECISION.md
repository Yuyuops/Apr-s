# Décision : correction finale de l'oreille articulée (V4.1)

## Verdict : **CHANGER DE MÉTHODE**

| Critère | Résultat V4.1 |
|---|---|
| Amélioration esthétique nette par rapport à C, sous plusieurs angles | **Non.** Le raccord au crâne est corrigé (plus de poteaux) et l'orientation est juste. Mais la silhouette de l'oreille reste un panneau large et presque rectangulaire, moins proche de la référence que l'oreille de C, de face, de profil et sur ses deux faces. |
| Silhouette (référence C : 0,955 de face, 0,958 de profil) | 0,896 / 0,920. La baisse n'est pas justifiée par un gain visuel. |
| Face intérieure | Tubes toujours visibles. Les masquer avec des tuiles impose une couche à tenons inversés, soit environ 2,5 fois l'épaisseur du panneau : épaississement excessif, non appliqué. |
| Connexions, collisions, montage, catalogue | Valides : 0 collision, 0 îlot, aucune pose dans le vide, 53 couples pièce × couleur vérifiés, 18 cellules et 2 cales seulement retirées ou ajoutées. |
| Tenue indicative | En baisse par rapport à V4 : 4 contacts dans le pire découpage, 0,15 N au bout. Ce n'est pas une mesure physique. |

Conformément à la règle d'arrêt, **les optimisations de ce module s'arrêtent ici.**

## Ce qui manque à l'approche automatique

Le mécanisme (pivots 3-4-5, équerres, panneau SNOT, validation géométrique) est réalisable et vérifiable. **C'est la composition des pièces du panneau qui échoue.**

Choisir des pièces cellule par cellule, sur une silhouette échantillonnée en grille de 8 mm, ne produit pas une feuille effilée. Les grandes plaques biseautées (3×6, 3×8) et les coins arrondis ne sont rentables que si l'on conçoit d'abord le contour avec elles, en partant de la forme voulue et non de la grille.

C'est un travail de conception, pas d'échantillonnage.

## Approche proposée (non développée, en attente de décision)

**Module de détail conçu dans un logiciel LEGO/CAD, puis intégré au moteur automatique.**

1. **Conception manuelle d'une oreille de référence** dans un logiciel CAO LEGO (BrickLink Studio ou LeoCAD, en LDraw). Contour en plaques biseautées 3×8, 3×6, 2×4 et coins arrondis, deux couches, faces finies, interface d'accroche standard : 2 plateaux 3-4-5 et 4 équerres, déjà validés ici.
2. **Paramétrage limité :** 2 ou 3 tailles d'oreille conçues à la main, et un miroir gauche/droite. Le moteur choisit la taille la plus proche du GLB, la place et l'oriente avec le mécanisme existant : recherche de poche, triangle 3-4-5, équerres.
3. **Validation inchangée :** `validate_v2.py` (collisions sur géométrie réelle, pivots, liaisons latérales, notice, catalogue) et les mêmes planches comparatives.
4. **Critère d'acceptation inchangé :** mieux que C, sans zoomer, de face, de profil et sur les deux faces de l'oreille.

Rien de tout cela n'est engagé sans nouvelle décision. Rien n'est transposé au museau, aux yeux, à la queue, aux pattes ni au vrai chien.
