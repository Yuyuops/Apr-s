# 18 : oreilles : séquence de montage, renfort et notice (LEGO V9.1)

**Verdict : VALIDER AVEC RÉSERVE PHYSIQUE** (`VERDICT.md`). Aucun essai physique. Départ : commit `caef2db` (V9).

## Lire d'abord

| Fichier | Contenu |
|---|---|
| `VERDICT.md` | Verdict, critères un par un, ce qui n'est pas démontré |
| `RAPPORT_V91.md` | Synthèse, modèle complet, masse recalculée, tests |
| `RAPPORT_31_PIECES.md` | Diagnostic des 31 pièces de V9 : aucune n'est emprisonnée |
| `RAPPORT_RESISTANCE.md` | Les quatre groupes de bord d'oreille, avant / après |
| `RAPPORT_NOTICE.md` | Oreilles pièce par pièce, 338 pièces par le bas, étapes non confirmées |
| `RISQUES_RESIDUELS.md` | Liste des risques restants |
| `PROTOCOLE_ESSAI_PHYSIQUE.md` | Essais à faire (non réalisés), bancs V7 |

## Livrables

| Dossier / fichier | Contenu |
|---|---|
| `modeles/` | `paco_V91_notice.ldr` (ordonné), `paco_V91_brut.ldr`, `oreille_beagle_V91.ldr` (renfort appliqué à l'oreille du Beagle) |
| `notice/` | 5 PDF (203 pages), `plan_notice.json`, `etapes_notice.csv`, `arbre_notice.json`, `plans_oreilles.json` (séquence, orientation, contrôles par pièce), `precautions.json` |
| `nomenclature_complete.csv` | 73 références, quantités, statut du catalogue, masse du modèle |
| `generateur/` | Séquenceur, rejeu indépendant, renfort, planificateur de notice, PDF, contrôle de portée, tests, chaîne d'oreille |
| `rapport_31_pieces/` | Tableau des 31 pièces (csv, json), séquences archivées |
| `rapport_avant_apres/` | Cartes de l'oreille basse : groupes fragiles de V9, tuiles à cheval de V9.1 |
| `validation/` | Validations, rejeux, résistance avant / après, masse, pièces par le bas, Beagle |
| `tests/` | Tests de portée (16/16), rejeu V6 et V6.1 |
| `comparaisons/`, `rendus/` | Comparaisons V9 / V9.1 aux mêmes angles, rendus V9.1 |
| `bancs_essai/` | Bancs de fixation d'oreille de V7 (inchangés) |

## Reproduire (depuis `~/bench`)

```
venv/bin/python proto/v91/stitch.py <notice.ldr> <weak.json> <out.ldr> <log.json> 3          # renfort (R3)
venv/bin/python proto/v91/run_ears_v91.py <model.ldr> <ears.json>                           # orientation, séquence, rejeu
venv/bin/python proto/v91/fix_steps.py <model.ldr> <ears.json> <ears_fix.json>              # reprise des pas rejetés
venv/bin/python proto/v91/notice_plan.py <model.ldr> <prefix> --ears <ears_fix.json>        # notice
venv/bin/python proto/v91/make_notice_pdf.py <plan.json> <notice.ldr> <map.json> <out> <nom>
venv/bin/python proto/v91/test_scope_v91.py                                                 # 16 tests
bash proto/v91/ear_pipeline.sh <oreille.ldr> <dossier> <nom>                                # chaîne complète d'une oreille
```

Les dossiers 03 à 17 ne sont pas modifiés. Aucune fusion dans `main`.
