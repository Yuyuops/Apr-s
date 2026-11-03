# VERDICT MAPS V0.2 : **GARDER A** (finition A corrigée), hybride non adoptée

## Décision technique
| Critère (île témoin, 32×32) | A V0.1 (référence a28527e) | **A corrigée V0.2** | Hybride (mat 1) |
|---|---|---|---|
| Pièces | 221 | **224** (+3) | 257 (+36, +16 %) |
| Collisions / déconnectées | 0 / 0 | 0 / 0 | 0 / 0 |
| Porteuses faibles (< 4 tenons) | 13 | **12** (objectif ≤ 13 atteint) | 11 |
| … dont critiques (seul appui d'une pièce portée) | 3 | **0** | 2 |
| Pièces sur un seul tenon | 15 (12 feuilles décoratives) | 15 (13 feuilles) | 16 |
| Points d'articulation (pièce dont la perte isole une pièce) | 28 | **23** | 36 |
| Pièces 1×1 | 15 (6,8 %) | 15 (6,7 %) | 16 (6,2 %) |
| Étapes de notice | 23 | 22 | 25 |

Trois zones : A V0.1 167 pièces / 0 critique ; A corrigée 166 / 0 ; hybride 203 (+22 %) / 1 critique.

## Décision visuelle
Côte à côte (`results/comparatifs/`) : l'hybride apporte un passe-partout de tuiles lisses (mer) autour de l'île et un bleu de rivière plus vif. Le gain esthétique est modeste, le contour de l'île et les couleurs sont inchangés, et il coûte +16 à +22 % de pièces, +8 points d'articulation et deux porteuses critiques. Les variantes à tuiles lisses sur les terres (bandes littorales) ont été écartées : plus chargées, plus fragiles.
Règle de la mission : « si l'hybride n'apporte pas de gain convaincant, conserver A » → **A conservée**. L'hybride reste livrée comme variante optionnelle, non recommandée.

## Corrections apportées à A (aucune pièce visible supplémentaire de façon significative)
1. pénalité d'alignement des joints (seam_pen 4,0) ;
2. ré-pavage local autour des petites pièces (`local_improve`) ;
3. chape de tuiles sur le cadre (hauteur K plates).
Résultat mesuré : 3 porteuses critiques → 0, points d'articulation 28 → 23, +3 pièces.
Limite : « zéro collision » et « zéro pièce déconnectée » ne prouvent pas la solidité ; aucune charge réelle n'a été testée.

## Généralisation (3ᵉ carte : Écosse / nord de l'Angleterre / Irlande du Nord, Natural Earth, domaine public)
Premier résultat conservé tel quel (`results/ecosse/A_32`), moteur gelé avant l'essai (`GEL_MOTEUR.md`, empreintes SHA‑256).
- Fidélité : mer IoU 0,91, terre 0,73, relief (massif) 0,72, Irlande 0,78 ; déplacement moyen du trait de côte 2,4 mm sur 256 mm.
- Points faibles réels : rivière/route fines (IoU 0,04 et 0,20 malgré un rappel de 0,86), petites îles perdues, 13 % de 1×1 (40 pièces), Irlande étiquetée « forêt » (sémantique par famille de couleur), inscription illisible à 32×32 (classe « autre »).
- Structure : 44 porteuses faibles dont **17 critiques** (21 en hybride) : le réglage de A ne se généralise pas sur un relief plus fragmenté. À corriger avant tout usage mural ; aucune sécurité de fixation n'est déclarée.
- Altitude : relief **artistique** (niveaux déclarés par classe), pas une altitude réelle ; la source ne contient aucune donnée d'élévation. Aucun terrain inventé.

## 32×32 contre 48×48 (Écosse)
| | 32×32 | 48×48 |
|---|---|---|
| Pièces | 301 | 487 (+62 %) |
| Dimension | 256 mm | 384 mm |
| Masse estimée (±30 %) | 902 g | 1 930 g (×2,1) |
| Étapes (≤ 20 pièces) | 24 | 36 |
| Pièces 1×1 | 40 (13,3 %) | 51 (10,5 %) |
| IoU terre / route / ville | 0,73 / 0,20 / 0,24 | 0,80 / 0,28 / 0,38 |
| Déplacement côte | 2,4 mm | 2,0 mm |
| Porteuses critiques | 17 | 19 |
Le 48×48 améliore nettement les détails fins mais coûte presque le double en masse ; il ne règle pas la fragilité structurelle. 32×32 suffit pour la lecture générale, 48×48 pour routes et villes.

## Décision
**GARDER A**, en version corrigée V0.2. Ne pas adopter l'hybride. Chantier ouvert avant de viser des cartes plus complexes : porteuses critiques et 1×1 sur reliefs fragmentés (pas de nouvelle option esthétique).
Contraintes tenues : aucun achat, pas de fusion dans main, moteur 1 et anciens résultats intacts, aucun GLB modifié, prix/stock Briquestore vides (non vérifiés), aucune validation physique prétendue.
