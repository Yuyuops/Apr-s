# 13 : Preuve de sculpture complète automatique (LEGO V7, Paco cartoon, 400 mm)

**Verdict : INTÉGRATION PARTIELLE.** Voir `VERDICT.md`.

| Fichier | Contenu |
|---|---|
| `RAPPORT_INTEGRATION.md` | Phases 1 à 6 : audit, segmentation, construction, constructibilité, évaluation visuelle |
| `PROBLEMES_NON_RESOLUS.md` | Chaque échec, avec sa cause et sa correction minimale |
| `PROTOCOLE_ESSAI_FIXATIONS.md` | Essai physique minimal des deux fixations (non exécuté, aucun achat) |
| `comparaison_GLB_LEGO_V7.png` | GLB et LEGO côte à côte : face, dos, profils, trois quarts, dessus |
| `gros_plans_GLB_LEGO_V7.png` | Gros plans de la tête, des oreilles, des mains et des pieds |
| `notice_avancement.png` | Montage à 25, 50, 75 et 100 % |
| `modeles/` | `paco_V7_notice.ldr` (ordonné, à ouvrir dans Studio ou LeoCAD), `paco_V7_brut.ldr`, `corps_seul.ldr` |
| `nomenclature_complete.csv`, `notice_etapes.csv` | 2 773 pièces, 331 étapes |
| `segmentation.json` | Zones, mesures, décision et confiance |
| `validation/` | `validate_v3`, bilan mécanique, rapport d'assemblage |
| `bancs_essai/` | Deux bancs LDraw avec leurs nomenclatures et validations |
| `rendus/` | Rendus séparés : GLB, LEGO, étapes de notice |
| `code/` | Scripts V7, ainsi que `autogen.py` modifié et ses différences |

Les rendus utilisent de vraies pièces LDraw (`render_ldr.js`), sans image générée par IA. Le GLB de référence n'est pas modifié. Les calculs mécaniques sont indicatifs.

Reproduction (depuis `~/bench`) : `fullgrid.py` → `segment.py` → `integrate.py run` → `assemble.py run` → `run_check.sh` → `rig_v7.py`.
