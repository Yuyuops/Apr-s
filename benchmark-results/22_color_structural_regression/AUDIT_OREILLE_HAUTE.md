# Audit géométrique de l'oreille haute de Paco (aucun déplacement)

Outil : `engine/ear_diagnosis.py`. Segmentation identique des deux côtés : les cellules étiquetées « oreille_haute » (+1 cellule) sélectionnent les triangles du GLB (tous les sommets dans la zone, toutes couleurs, 15 400 triangles échantillonnés) et les pièces du sous-ensemble `V7_oreille_haute` du LEGO (nuages « tout », « zone » = points dans les cellules étiquetées, « visible » = points exposés). Mesures : centroïde, axes principaux (longueur, largeur, épaisseur), normale, racine (extrémité de l'axe principal la plus proche de la tête), pointe, contour sur le plan principal du GLB (raster 4 mm) et IoU en place / centroïdes superposés / axes et centroïdes superposés. Règle de conclusion écrite dans l'outil (non réglée par sujet) ; elle porte sur le nuage « zone » (le nuage « visible » ne compte que ≈ 1 300 points et n'est que rapporté).

| Oreille haute (nuage « zone ») | GLB | V11 | V12.1 A | V12.1 B |
|---|---|---|---|---|
| Écart de centroïde | — | 8,6 mm | 6,1 mm | 8,0 mm |
| Écart de normale | — | 1,1° | 2,2° | 1,2° |
| Longueur | 128–133 mm | 118,4 | 118,5 | 118,4 |
| Largeur | 70 mm | 56,1 (−20 %) | 55,1 (−21 %) | 56,1 |
| Épaisseur | 18,4–18,9 mm | 16,4 (−13 %) | 15,8 (−14 %) | 16,4 |
| Aire du contour | ≈ 96–100 cm² | 66,2 (−34 %) | 66,7 (−31 %) | 68,6 |
| IoU contour en place | | 0,661 | 0,696 | 0,691 |
| IoU centroïdes superposés | | 0,622 | 0,666 | 0,638 |
| Écart de racine / de pointe | | 20,9 / 27,9 mm | 17,2 / 22,3 mm | 19,8 / 28,0 mm |
| Longueur du sous-ensemble entier (racine enterrée incluse) | | 201,7 mm | 201,7 mm | 201,7 mm |

Constats :
1. **Le centre et l'orientation sont corrects** (centroïde 6–9 mm, normale 1–2°). Superposer les centroïdes **n'améliore pas** le contour (gain IoU −0,03 à −0,05 ; seuil de preuve +0,15) : le décalage restant n'est pas un défaut de position.
2. **La forme diffère** : la partie du module qui figure l'oreille est plus étroite de 20 %, plus mince de 13–14 %, d'aire −31 à −34 % (empilement de plaques 8 × 20 LDU contre une oreille amincie et incurvée). L'écart de forme calculé est 0,30–0,34 (≥ 0,25).
3. **L'écart de dénivelé et de pointe de V11/V12 vient en grande partie du volume de racine** : le sous-ensemble entier mesure 201,7 mm contre 128–133 mm pour l'oreille du GLB ; ses 70 mm excédentaires (bloc de fixation et plaques tournées) décalent le centroïde et la pointe du nuage « tout » (pointe : 65 mm). Les 24 mm de pointe plus haute de V12 sont donc un artefact de la définition « tout », non un défaut de position.
4. Les écarts de 14–25 mm de V12 sur le nuage « visible » étaient un artefact d'échantillonnage (≈ 1 300 points exposés, surface partielle).

**Conclusion : différence de forme / d'épaisseur (largeur −20 %, épaisseur −13 %), avec en plus un volume de racine qui n'a pas d'équivalent dans le GLB. Aucune erreur de placement n'est démontrée ; aucune correction de position n'est proposée, et aucune oreille n'a été déplacée ni symétrisée.** L'oreille basse (nuage « zone ») : centroïde 4,2 mm, normale 2,2°, IoU 0,81 ; diagnostic « information insuffisante » (aucun écart ne se sépare) : elle est bien placée.
Limite : le GLB n'a pas d'oreille isolée ; la sélection par segmentation inclut les triangles de la peau voisine (toutes couleurs) dans la dilatation d'une cellule, ce qui peut gonfler la largeur du GLB de quelques millimètres.
