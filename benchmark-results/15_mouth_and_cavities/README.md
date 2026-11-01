# 15 : Bouche et cavités (LEGO V8.1, Paco cartoon, 400 mm)

**Verdict : CORRIGER SOUS CONDITION.** Voir `VERDICT.md`.

| Fichier | Contenu |
|---|---|
| `RAPPORT_V81.md` | Analyse de la bouche du GLB, module générique, résultat, évaluation visuelle, contrôles, non-régression |
| `CAPACITES_GENERIQUES.md` | Ce qui est automatique et générique, pièces étudiées, limites, réglages à confirmer |
| `NOUVEAUX_POINTS_FAIBLES.md` | Bilan des sous-ensembles fragiles, V8 contre V8.1 |
| `PROBLEMES_NON_RESOLUS.md` | Chaque défaut, avec sa cause et sa correction minimale |
| `comparaisons/bouche_GLB_V7_V8_V81.png` | Gros plans de la bouche : gauche, droite, dessous, deux trois quarts |
| `comparaisons/tete_taille_normale_GLB_V7_V8_V81.png` | Tête à taille normale : profils et trois quarts |
| `comparaisons/personnage_taille_normale_GLB_V7_V8_V81.png` | Personnage entier : profils et face |
| `comparaisons/variantes_A_B.png` | Relief réduit (A) contre cavité ouverte (B) |
| `comparaisons/montage_bouche_*.png` | Gros plans du montage (couches 78 à 92), V8 contre V8.1 |
| `modeles/` | `paco_V81_notice.ldr` (ordonné, pour Studio ou LeoCAD), `paco_V81_brut.ldr`, `corps_seul_V81.ldr`, variante A |
| `nomenclature_complete.csv` | 2 796 pièces, 74 couples pièce × couleur, disponibilité Rebrickable |
| `analyse/` | Coupes et silhouettes du GLB, décisions du module (variantes A et B) |
| `validation/` | `validate_v3` (V8.1, variante A, référence V8), comparaison chiffrée, mesures de la zone de la bouche, différence de nomenclature |
| `non_regression/` | Rejeu de V6 / V6.1 (aucune différence) |
| `rendus/` | Vues séparées : GLB, V7, V8, V8.1 B, variante A, montage |
| `generateur/` | `lcm.py` (module), `assemble_v81.py`, `run_v81.sh`, `render_v81.sh`, `mouth_metrics.py`, etc. |

Les rendus utilisent de vraies pièces LDraw (`render_ldr.js`), sans image générée par IA. Le GLB source n'est pas modifié. Les calculs mécaniques sont indicatifs.

Reproduction (depuis `~/bench`, avec V7 et V8 dans `proto/v7/` et `proto/v8/`) : `bash proto/v81/run_v81.sh B`.
