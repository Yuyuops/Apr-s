# Sprint V16 — Expériences de relief (zones A, B, C ; base B V15, moteur LEGO Maps modifié par options)

Tout est reproductible avec `sprint_v16/hyrule_v16_c4.json` (style), les compositions `hyrule_v16d_zone_{A,B,C}.json`, `tools/reinforce_v16.py` et les rasters `sprint_v16/data/`. Les options du moteur sont **désactivées par défaut** (les 8 références CI sont restées identiques, voir `REGRESSION_REPORT.md`).

## Code ajouté (build_style.py)
| Option | Effet | Statut |
|---|---|---|
| `relief.smooth_height {sigma, keep, coast_min, coast_ramp, coast_width, min_peak_width}` | hauteurs lissées au pas d'1 plaque (lissage gaussien normalisé sur les terres seules), rampe de berge limitée à `coast_width` studs, **pas de flèche** plus étroite que `min_peak_width` × `min_peak_width` studs | **retenu** |
| `surface.cliff_slopes {part: 54200, min_dh: 2}` | à l'aplomb des falaises (≥ 2 plaques) la tuile est remplacée par une pente 31° dans la couleur de la cellule (talus) ; une seule falaise voisine par cellule (coins concaves exclus) | **retenu** |

## Cycles (zone A = montagnes/falaises ; critère visé : « empilement de blocs », relief plat)
| Cycle | Défaut dominant | Hypothèse | Modification | Mesure / constat | Décision |
|---|---|---|---|---|---|
| 0 (V15) | falaises de 2 à 8 plaques, aplats | — | — | 132 arêtes de falaise ≥ 2 plaques, hauteur 5–13 plaques | référence |
| 1 | blocs en escaliers de 2 plaques | lisser les hauteurs + talus aux pieds de falaise + pavage structurel | `smooth_height` σ = 1, `cliff_slopes`, `body_tiler wild` | falaises 132 → 22 ; **mais seulement 4 talus** (le lissage supprime la plupart des falaises) ; hauteur max inchangée (10 plaques) | gardé |
| 2 | relief toujours plat (amplitude) | augmenter les niveaux/gains des classes de montagne | niveaux +1 à +2, pas de gain 2 | **aucun effet** (hauteur max 10 plaques) : la rampe de berge `coast_ramp` plafonnait **toutes** les hauteurs à moins de 0,7 plaque/stud de l'eau | hypothèse non confirmée, **bug trouvé** |
| 3 | amplitude plafonnée | limiter la rampe à une ceinture de 4 studs | `coast_width = 4` | hauteur 5 → 15 plaques : relief lisible (crêtes, cratère) ; **mais** pointes de 1–2 studs = colonnes de plaques 1×2 empilées (pire défaillance 13 pièces) | gardé, défaut structurel nouveau |
| 4 (*) | colonnes minces | une pointe doit mesurer ≥ 3 × 3 studs | `min_peak_width = 3` | pire défaillance 19 → 12 puis 7 après renforcement ; relief conservé | **retenu** |
(*) **La limite de 3 cycles par zone est dépassée d'un cycle sur la zone A** (le défaut de la pointe était un défaut structurel bloquant révélé par le cycle 3) ; de même un cycle supplémentaire a corrigé la classe d'eau peu profonde sur les zones B et C (voir `DETAIL_EXPERIMENTS.md`). Je le déclare plutôt que de le masquer.

Approche abandonnée : `--flank curved|progressive` (flancs de la V0.6.2) : **aucun effet** sur les falaises terrestres du mode biomes (même modèle octet pour octet sur la zone A) ; documenté dans `ENGINE_DIAGNOSTIC.md`.

## Mesures objectives (grille gelée ; `reports/zone*_V1{5,6}_objective.json`)
| Zone | Hauteur (plaques) V15 → V16 | Arêtes de falaise ≥ 2 plaques | Talus (pente 31°) | Indice de blocs (arêtes sans talus au pied) | Gradient moyen (plaques/stud) | Pièces courbes/rondes |
|---|---|---|---|---|---|---|
| A | 5–13 → **5–18** | 132 → 194 (relief plus haut) | 0 → **115** | 1,00 → **0,62** | 0,197 → 0,779 | 118 → 342 |
| B | 5–13 → 5–17 | 68 → 68 | 0 → 49 | 1,00 → 0,90 | 0,137 → 0,382 | 95 → 246 |
| C | 5–13 → 5–16 | 141 → 97 | 0 → 56 | 1,00 → 0,70 | 0,251 → 0,452 | 116 → 226 |
**Lecture honnête** : le critère « gradient moyen (plus bas = plus lisse) » défini dans la grille gelée **empire** (0,2 → 0,8) parce qu'une pente progressive par marches d'une plaque donne plus de petites différences qu'un plateau plat bordé de falaises ; ce critère était mal choisi pour mesurer le naturel. L'indice de blocs (part de falaises sans talus) s'améliore partout. Le relief V16 est nettement plus haut (jusqu'à 18 plaques = 58 mm) et plus progressif, mais reste **par paliers de 3,2 mm** : pas de vraies pentes continues.
