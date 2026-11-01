# 17 : Solidité et vraie notice (LEGO V9, Paco cartoon, 400 mm)

**Verdict : CORRIGER.** Voir `VERDICT.md`.

| Fichier | Contenu |
|---|---|
| `RAPPORT_V9.md` | Contrôle de portée des modifications et ses tests, plan d'appui, diagnostic des 21 groupes fragiles, renforts, résultats, limites du modèle de résistance |
| `RAPPORT_NOTICE.md` | Notice hiérarchique : modules, contrôles à chaque étape, résultats, limites |
| `PROBLEMES_NON_RESOLUS.md` | Chaque défaut restant, avec sa cause et sa correction minimale |
| `PROTOCOLE_ESSAI_PHYSIQUE.md` | Protocole d'essai (non réalisé) et liste minimale des pièces des deux bancs V7 |
| `modeles/` | `paco_V9_notice.ldr` (ordonné, 211 étapes, blocs de sous-ensembles ; ouvrable dans Studio ou LeoCAD), `paco_V9_brut.ldr` |
| `notice/` | 5 PDF illustrés (212 pages), `plan_notice.json` (contrôles pièce par pièce), `etapes_notice.csv`, `arbre_notice.json` |
| `rapport_avant_apres/` | Les 21 groupes fragiles de V8.2 et les 8 de V9 (zone, pièces, masse, liaisons, force, risques), leur devenir, la figure, le journal des renforts |
| `comparaisons/` | GLB / V8.2 / V9 au même cadrage : personnage entier, tête et bouche ; groupes fragiles sur le modèle |
| `tests/` | 10 tests de portée (résultats), contrôle V8.2 → V9 (aucune violation) |
| `validation/` | `validate_v3` de la notice ordonnée, résultats de l'ordre du fichier, référence V8.2, classement des risques, différence de nomenclature |
| `nomenclature_complete.csv` | 3 066 pièces, 73 couples pièce × couleur, tous vérifiés (Rebrickable) |
| `bancs_essai/` | Les deux bancs de fixation d'oreille de V7 (inchangés) et la liste minimale de pièces |
| `rendus/` | Vues séparées V8.2 et V9 |
| `generateur/` | Scripts : contrôle de portée, tests, renforts, validation, diagnostic, planificateur, PDF |

Les rendus utilisent de vraies pièces LDraw (`render_ldr.js`), sans image générée par IA. Le GLB source n'est pas modifié. Les calculs mécaniques sont indicatifs. **Aucun essai physique n'a été fait.**

Reproduction (depuis `~/bench`, avec V7 à V8.2 présents) :

```
bash proto/v9/pass.sh <V8.2 notice.ldr> <groupes.json> proto/v9/a1.ldr 2 pa1 0     # R1 + R2, passe 1
bash proto/v9/pass.sh proto/v9/a1.ldr proto/v9/pa1/weak.json proto/v9/a2.ldr 4 pa2 # passe 2
venv/bin/python proto/v9/test_scope.py
venv/bin/python proto/v9/notice_plan.py proto/v9/a2.ldr proto/v9/n1
venv/bin/python proto/v9/make_notice_pdf.py proto/v9/n1_plan.json proto/v9/n1_notice.ldr proto/v9/n1_map.json proto/v9/notice paco_V9
```
