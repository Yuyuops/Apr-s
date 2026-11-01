# Problèmes non résolus : V8.1

| # | Problème | Gravité | Cause | Correction minimale |
|---|---|---|---|---|
| 1 | **Bouche non lisible de profil gauche et de face** | Condition de la décision | **Cause non établie.** Le GLB n'est pas transparent à cet endroit : son vide n'est pas un trou traversant. Il montre à gauche un intérieur clair avec un fin liseré rouge (moins d'une cellule), que la grille reproduit mal. Les revêtements se trouvent surtout du côté de la caméra droite, à cause de la diagonale du museau (32° des axes de la grille). | D'abord mesurer, côté gauche, les cellules visibles depuis la caméra gauche dans l'encoche et leur couleur, dans le GLB et dans la grille. Ensuite : revêtir **aussi** la paroi opposée à chaque bord ouvert, quelle que soit la direction. Ne pas percer la joue sans preuve que le GLB l'exige. |
| 2 | Direction de la pente rouge à 28,5° de la normale | Faible | Un quart de tour minimum pour une pente en briques | Pente de biais (pièce tournée) ou pente fromage sur plaque tournée comme les oreilles |
| 3 | Pas de lèvre courbe ni de commissure | Moyenne (visuelle) | Pièces courbes (quart de rond, pente courbe) étudiées, non implémentées | Suivre la polyligne du bord de la cavité avec des tuiles 1×N et des quarts de rond en SNOT |
| 4 | Traits sombres isolés sur le bas du museau | Faible | Cellules du bord ouvert de la cavité | Ne revêtir que la composante principale du bord ; filtrer les cellules isolées |
| 5 | 15 colonnes sous 3 plaques de hauteur libre | Faible | Contact avec des cellules protégées ou le plancher sans marge | Autoriser le creusement du plancher d'une plaque |
| 6 | Pente rouge sur 1 tenon | Faible | Pièce 1×1 | Pente 1×2 (85984), accepter une empreinte plus large |
| 7 | Réglages à confirmer sur un autre personnage (`MIN_OPEN`, `LINING_LAYERS`, etc., plus les trois règles V8) | Méthode | Réglés en voyant Paco | Test de généralisation |
| 8 | Problèmes de V7 et V8 : mains, bords d'oreille, semelles, notice des oreilles | — | **Inchangés, hors mission** | Voir `14_facial_microdetails/PROBLEMES_NON_RESOLUS.md` |
| 9 | Aucune validation physique | — | Aucun achat autorisé | — |
