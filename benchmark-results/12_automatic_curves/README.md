# 12 : grands arrondis automatiques (V6.1)

Verdict : **VALIDER V6.1** (`RAPPORT_DECISION.md`), avec 3 réserves hors périmètre :

- plaque de fixation supérieure visible sur Paco ;
- fixation du Beagle non démontrée ;
- petite saillie plate à la pointe de Paco.

| Élément | Contenu |
|---|---|
| `A_comparaison_V5_V6_V61.png` | Paco : référence / V5 / V6 / V6.1, mêmes 6 vues, vraies pièces LDraw |
| `B_comparaison_V6_V61.png` | Beagle : vue du GLB / V6 / V6.1, 4 vues |
| `gros_plans/` | Bout libre de Paco (V5 / V6 / V6.1, 3 angles) ; bas et haut du Beagle (V6 / V6.1) |
| `A_contours.png`, `A_contours_bout.png`, `B_contours.png` | Contours générés (rouge) sur la silhouette extraite du GLB (gris) |
| `mesures_fidelite.json` / `.txt` | IoU GLB, IoU avec la référence manuelle, arcs, extrémités, écarts maximaux, même protocole pour toutes les versions |
| `A_paco/`, `B_beagle/` | Rapport du générateur (programme en nombres entiers, arcs, pièces), modèles `.ldr` (module ; tête + oreille ou notice), validations v3 et v2, nomenclatures |
| `rendus/` | Vues individuelles V6.1 |
| `generateur/` | `autogen61.py`, `metrics61.py`, `validate_v3.py`, `run_all.sh`, base V6 (`autogen_V6_base.py`, `contour.py`) |

Reproduire depuis `~/bench` : `bash proto/ear12/run_all.sh`. Il faut V6 (`proto/ear11/`, cibles dans `proto/ear11/targets`) et les aides de V5.1 (`proto/ear10/design_v51.py`).
