# Décision : itération Brickify V3 (tête de Paco, 400 mm)

## Verdict : **CHANGER D'APPROCHE**

**Pour les surfaces et les détails seulement.** Le cœur volumique du prototype C reste la base :
- fidélité de volume 0,85 et silhouettes 0,96 ;
- 0 îlot, 0 collision, pièces toutes produites dans leur couleur ;
- notice réordonnée sans pose dans le vide.

## Pourquoi ni D ni E ne sont acceptables

| Critère de décision | D | E |
|---|---|---|
| Museau clairement mieux défini | Non (léger adoucissement du dessus) | Non |
| Courbes du visage plus naturelles | Marginalement | Marginalement |
| Oreilles moins grossières | Non (inchangées) | Non (régression : panneau plat, vu par la tranche de face, amputé) |
| Amélioration visible sans zoomer | Non | Non |
| 0 îlot, 0 collision, toutes les pièces raccordées | Oui | Oui, mais au prix de 13 pièces de tête et 67 cellules d'oreille **retirées** |
| Fixations critiques justifiées | Comme C (bout des oreilles à 0,04 N, indicatif) | 4 tenons latéraux par oreille ; coefficient minimal sous le poids propre de 38 à 7,3 |
| Pièces et couleurs cataloguées | Oui (34 lignes, toutes vérifiées) | Oui (44 lignes, toutes vérifiées) |
| Notice sans pose dans le vide | Oui (après réordonnancement) | Oui (après réordonnancement, 3 sous-ensembles) |
| Surcoût justifié | +29 pièces pour un gain à peine visible | Moins de pièces, mais par perte de forme (IoU de volume 0,67, silhouette de face 0,71) |

**D est un échec esthétique** : il ne dégrade rien, mais le gain ne se voit pas.
**E est un échec esthétique et un recul de fidélité.**
Conformément à la mission, je n'engage pas de troisième variante sans démonstration de faisabilité.

## Capacités qui manquent au moteur

1. **Une représentation des détails à l'échelle de la pièce, pas de la cellule.** brickify et le prototype C raisonnent en cellules de 8 × 8 × 3,2 mm.
   Une truffe ronde, un œil rond, le contour arrondi d'une oreille ou un museau effilé font 1 à 3 cellules : ils ne peuvent être que des marches.
   La finition des dessus n'agit que sur la face supérieure de chaque colonne, alors que les marches gênantes sont sur les flancs.
2. **Des liaisons à angle quelconque.** Charnières, clips sur barre, plaques tournantes, rotules. Les oreilles de la référence et du modèle 3D sont à environ 40°.
   Avec des tenons seuls, un sous-ensemble ne tourne que par quarts de tour.
3. **Le placement de grands éléments arrondis entiers**, ajustés à une forme : plaques rondes, plaques biseautées, tuiles quart de rond 2×2 et 3×3, dômes.
   Les oreilles de la référence sont de grandes plaques noires arrondies, pas un remplissage de cellules.
4. **La vérification des liaisons autres que les tenons** (clips, barres, charnières, axes). `validate_v2.py` ne connaît que tenons et points d'appui.

## Architecture alternative proposée (limitée aux surfaces et aux détails)

**Cœur volumique C** + **modules de détail ajustés** + **vérification géométrique étendue.**

1. **Segmentation des détails** à partir du GLB et de ses couleurs : oreilles, truffe, yeux, bout du museau. La segmentation des oreilles existe déjà dans `snot_ears.py`.
2. **Bibliothèque de modules LEGO paramétriques**, conçus une fois à la main en LDraw et vérifiés :
   - oreille : 2 couches de plaques arrondies ou biseautées, sur une base à charnière ;
   - œil : tuile ronde 2×2 blanche montée sur tenon latéral, avec pupille ;
   - truffe : brique ronde ou dôme 2×2 ;
   - bout de museau : pentes courbes montées de côté.

   Chaque module expose une interface d'accroche standard : briques d'accroche réservées dans le cœur avant l'empilement, comme le fait déjà `--preplaced`.
3. **Ajustement** de chaque module (taille dans un jeu discret, position, angle de charnière) sur la partie segmentée du modèle 3D, en maximisant l'IoU des silhouettes dans les vues de référence.
   **Une contrainte de lisibilité** interdit de perdre une caractéristique reconnaissable au profit du score de volume.
4. **Validation** : `validate_v2.py` étendu aux clips, barres et charnières, avec collisions sur la géométrie réelle des pièces, et pas seulement sur leurs boîtes.

## Démonstration de faisabilité préalable (avant tout développement)

- **Une seule oreille de Paco, réalisée en module à charnière, posée sur le cœur C, à 400 mm.**
- Critères de réussite :
  - mieux que C à la fois de face et de profil, sans zoomer ;
  - 0 îlot et 0 collision ;
  - liaison de l'oreille par charnière vérifiée géométriquement et au moins 8 tenons d'accroche ;
  - pièces et couleurs vérifiées.
- Si ce démonstrateur échoue, il faut envisager un moteur différent pour les détails : sculpture assistée, ou une bibliothèque de modules conçus par un designer.

## Limites rappelées

- Aucune sculpture n'est validée physiquement sans montage réel. Les newtons sont des indicateurs de comparaison.
- Rien n'est transposé au vrai Paco ni au chien gris et blanc avant la validation du moteur sur ce démonstrateur.
