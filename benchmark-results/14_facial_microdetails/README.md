# 14 : Micro-détails du visage (LEGO V8, Paco cartoon, 400 mm)

**Verdict : CORRIGER.** Voir `VERDICT.md`.

| Fichier | Contenu |
|---|---|
| `RAPPORT_V8.md` | Analyse du GLB, générateur, intégration, évaluation visuelle, contrôles, non-régression, capacités et limites |
| `PROBLEMES_NON_RESOLUS.md` | Chaque défaut, avec sa cause et sa correction minimale |
| `visage_grand_format.png` | Visage : GLB / V7 / V8, profils et trois quarts, en grand |
| `gros_plans_visage_GLB_V7_V8.png` | 6 gros plans : profils, avant, trois quarts, bouche, oreilles |
| `comparaison_GLB_V7_V8.png` | Personnage entier : face, dos, profils, trois quarts, dessus |
| `modeles/` | `paco_V8_notice.ldr` (ordonné, pour Studio ou LeoCAD), `paco_V8_brut.ldr`, `corps_seul_V8.ldr` |
| `nomenclature_complete.csv` | 2 758 pièces, 72 couples pièce × couleur, disponibilité Rebrickable |
| `analyse/` | Détails détectés (mesures, classes, appariement) et décisions du générateur (candidats, coûts, pose) |
| `validation/` | `validate_v3` du modèle complet, rapport d'assemblage, comparaison chiffrée V7 / V8 |
| `non_regression/` | Rejeu de V6 / V6.1, script de comparaison, résultat (`nonreg.json` : aucune différence) |
| `rendus/` | Vues séparées : GLB, LEGO V7, LEGO V8 |
| `generateur/` | `detect.py`, `microdetails.py`, `assemble_v8.py`, `run_v8.sh`, `render_v8.sh`, `viewsV8.json` |

Les rendus utilisent de vraies pièces LDraw (`render_ldr.js`), sans image générée par IA. Le GLB de référence n'est pas modifié. Les calculs mécaniques sont indicatifs.

Reproduction (depuis `~/bench`, avec V7 dans `proto/v7/`) :

```
bash proto/v8/run_v8.sh
bash proto/v8/render_v8.sh
bash proto/v8/nonreg/run_nonreg.sh
```
