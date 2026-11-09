# Sprint V16 — Comparaison artistique

Grille gelée avant essais : `EVALUATION_GRID_V16_FROZEN.json` (5 critères × 5 = 25 ; solidité = critère bloquant séparé ; seuil expérimental 20/25 par zone **avec validation visuelle humaine obligatoire**). **Aucun GO artistique n'est attribué ici** : les observations ci-dessous sont celles de l'auteur technique et restent à valider par vous.

## Zones pilotes (32×32 dans B) — voir `renders/zone{A,B,C}_before_after_board.jpg` et vues `zone*_{V15,V16}_{face,trois_quarts,lateral,gros_plan}.jpg`
- **A montagnes/falaises** : reliefs jusqu'à 18 plaques, gradins progressifs, pentes inclinées (54200), flèches fines supprimées (`min_peak_width`). Gain visible vs V15 (plateaux plats).
- **B forêts/plaines** : arbres miniatures (3062b), arbustes/fleurs (6141), sols différenciés. Densité de détails encore **très inférieure** à la référence.
- **C eau/côtes** : dégradé d'eau peu profonde (couleur 73) sur les grands plans d'eau, berges étagées ; contour inchangé.
Les mesures objectives de la grille (indice de blocs en hausse) sont dans `reports/zone*_objective.json` ; la métrique « gradient moyen de hauteur » de la grille gelée se dégrade (mal spécifiée : elle récompense les surfaces plates) — signalé, non corrigé après coup.

## Hyrule complet (96×78) — `renders/full/`
`V16_face|trois_quarts|lateral|montagnes|littoral_lacs.jpg`, `compare_V15B_vs_V16_{face,trois_quarts}.jpg`, `compare_reference_V15B_V16_face.jpg` (référence LEGO tierce / V15 B / V16). Le modèle est sans titre (`--no-title`, identique aux vues V15 B) : la variante « sans titre » est donc la vue unique.
Constats : relief étagé bien plus lisible (massifs, caldeira, falaises), forêts texturées, lacs à deux tons, repères rouges/jaunes. Écarts persistants vs référence : pas de bâtiments/ponts/chemins modelés, végétation plus uniforme, pas de courbes de rivière détaillées.

**Validation humaine requise** : aucune note /25 validée n'est déclarée.
