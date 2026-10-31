# Comparaison visuelle : référence, C, D, E

Planches : `comparaison_C_D_E.png` (face, trois quarts, profil, fixations des oreilles, gros plan du museau), `detail_museau.png`, `detail_oreilles.png`.
Toutes les images LEGO sont calculées à partir des pièces LDraw officielles positionnées dans chaque modèle. Le cadrage, la distance, l'éclairage et la taille sont identiques. Ni retouche ni IA générative.
L'évaluation ci-dessous est la mienne. **La validation visuelle revient à l'utilisateur.**

| Critère | C (référence de travail) | D (finition des surfaces) | E (finition + oreilles SNOT) |
|---|---|---|---|
| Museau mieux défini | Terrasses de plaques à tenons ; truffe en bloc noir | **Légèrement** plus doux : 42 pentes 30° tournées vers le bas sur le dessus, tenons cachés par des tuiles. Le profil reste en terrasses, la truffe reste carrée. Différence visible au gros plan, à peine à distance. | Comme D |
| Courbes du visage plus naturelles | Non | Marginalement : surtout le dessus du crâne et du museau. Joues inchangées, car les flancs sont verticaux et non concernés. | Comme D |
| Yeux (position, orientation) | Blanc avec pupille noire, à la bonne place | Inchangés (aucune pièce de forme sur les yeux) | Inchangés |
| Oreilles moins grossières | Colonnes de plaques épaisses, contour en escalier, mais forme d'ovale reconnaissable dans les deux vues | Inchangées (tenons conservés, comme la référence) | **Plus mauvaises** : l'oreille du haut devient un panneau plat rectangulaire, percé là où les cellules sans accroche ont été retirées, et décalé de 5 colonnes. Elle est vue par la tranche de face. L'oreille du bas est amputée de 58 cellules sur 76. |
| Fixations des oreilles | Continuité de plaques avec la tête | Idem | Panneau sur 4 tenons latéraux par oreille ; quelques taches rouges et jaunes à la base |
| Amélioration visible sans zoomer | — | **Non** | **Non** (régression) |
| Verdict esthétique | Référence | **Échec** : gain trop faible pour justifier une version | **Échec** : moins beau que C |

## Pourquoi la finition change si peu

À cette échelle, une cellule mesure 8 × 8 × 3,2 mm, et le jaune n'a que 149 dessus visibles. Les escaliers les plus gênants sont sur les **flancs** (marches horizontales de 8 mm) et au bout du museau. Une pièce posée sur le dessus d'une colonne ne les touche pas.
Les pentes 45° et les courbes 2×1 et 3×1 font 2 à 3 plaques de haut et 2 à 3 tenons de long. Elles ne correspondent à aucune pente de ce visage dans la grille : les marches font 1 plaque pour 1 tenon, soit environ 22°.

## Pourquoi les oreilles SNOT échouent

Dans le modèle 3D, les oreilles sont dans un **plan vertical incliné d'environ 40°**, ce qui les rend visibles à la fois de face et de profil, comme sur la référence.
Un panneau SNOT ne se tourne que par quarts de tour : calé sur l'axe X, il est vu par la tranche de face.
De plus, l'alignement imposé (accroches tous les 5 plaques, 3 plaques pleines derrière chaque accroche) ne laisse que 4 points d'accroche par oreille sur cette tête.
Les parties de l'oreille sans accroche doivent être retirées, ce qui la déforme.
