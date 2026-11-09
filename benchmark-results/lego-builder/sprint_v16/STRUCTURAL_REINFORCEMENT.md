# Sprint V16 — Renforcement structurel

**Rappel : une validation numérique ne prouve pas la résistance physique** (`fragility.py` : pièces rigides, clutch supposé, aucun essai). Les mesures ci-dessous sont des indicateurs relatifs.

## Cause racine mesurée (V15 B)
Les 2 580 pièces à un seul tenon se décomposent en **1 552 plaques 1×1 de corps de strates**, 525 quarts-de-rond de coin, 421 tuiles 1×1, 48 ornements de cadre, 34 divers (analyse de `parts.json`). Le pire défaut isolé (45 pièces) est une plaque 6×4 de corps qui porte un sommet.

## Ce qui a été codé
1. **Pavage structurel des corps** (`surface.body_tiler = "wild"`) : cellules cachées « jokers » → une bande visible d'une cellule se prolonge dans les cellules cachées derrière elle (pièces plus grandes, ≥ 2 tenons), moteur `maps_engine.tiling` (coût d'orphelins, décalage de joints, recherche locale, fusion des petites pièces) enfin branché sur `build_style`.
2. **Tuiles de dessus qui enjambent les joints** (`surface.top_tiler = "seam"`).
3. **Plafond de taille des plaques de corps** (`body_max_area = 16`) : les grandes plaques (8×8, 6×8) étaient des points de défaillance uniques.
4. **Relief sans flèches** (`min_peak_width`) : une colonne de 1×2 plaques empilées est un point de défaillance en chaîne.
5. **Passe de renforcement mesurée** (`tools/reinforce_v16.py`, `--reinforce`) : construit, calcule les points d'articulation (graphe de joints du validateur moteur 1), re-pave en petites pièces (≤ 2×2) l'empreinte et la couche dessous des pièces dont la défaillance isole ≥ 8 pièces ; **cumulatif** (graines déterministes par couche) ; s'arrête quand le pire cas < 8 ; garde la meilleure passe. N'affecte que des plans cachés : aucune surface visible modifiée.

## Essais structurels sur les zones (V15 → options), colonne « pire » = pièces isolées par la défaillance de la pièce la plus critique (fragility.py, ordre par masse) ou analyse par nombre
| Essai | Zone A | Zone B | Zone C | Verdict |
|---|---|---|---|---|
| V15 (référence) | 2008 p., 18,5 %, porteuses 186, pire 10 | 2022 p., 18,5 %, 225, pire 14 | 1837 p., 17,9 %, 158, pire 18 | — |
| S1 pavage « joker » seul | 1568, 14,2 %, 35 | 1506, 15,0 %, 74, pire 19 | 1532, 14,3 %, 41, pire 26 | pièces −22 %, 1 tenon −4 pts ; mais **pire cas qui augmente** (grosses plaques) |
| S1b/S1c : décalage/pénalité de joints ×5, ×12 | sans effet | sans effet | sans effet | **abandonné** (aucun gain mesurable) |
| S2 : + tuiles de dessus « seam » | pire 24 | 21 | 27 | pas mieux seul |
| S3a : plafond de plaque 16 | 1859, 11,9 %, 22, pire 2 | 1692, 12,6 %, 55, pire 6 | 1695, 13,5 %, 44, pire 3 | **retenu** |
| S3b : plafond 8 | — | 1995, 10,6 %, 56, pire 7 | 2012, 10,9 %, 31, pire 3 | pas mieux, +18 % pièces, ×2,5 de temps : abandonné |
| `body_above_pen` (pénalité d'enveloppement d'un amas supérieur) | identique à sans pénalité | identique | 14 → 8 | gain sur 1 zone sur 3 : **abandonné** (option conservée, désactivée) |
| Reinforce (zones, style c4 final) | voir ci-dessous | | | **retenu** |

## Résultat final des zones (V16 = style c4 + renforcement)
| Zone | Pièces | Pièces à 1 tenon | dont feuilles décoratives | **à 1 tenon ET porteuses** | Points d'articulation | **Pire défaillance isolée (nb de pièces)** V15 → V16 | Passes (pire) | Collisions/déconnectées/îlots/non supportées |
|---|---|---|---|---|---|---|---|---|
| A | 2008 → 2315 | 18.5 % → 22.6 % | 186 → 474 | **186 → 50** | 287 → 336 | 10 → **7** | 0:12, 1:8, 2:7 | 0/0/0/0 |
| B | 2022 → 1972 | 18.5 % → 20.6 % | 150 → 372 | **225 → 34** | 304 → 300 | 14 → **8** | 0:10, 1:9, 2:8, 3:8 | 0/0/0/0 |
| C | 1837 → 1890 | 17.9 % → 18.9 % | 170 → 331 | **158 → 27** | 215 → 272 | 18 → **7** | 0:13, 1:8, 2:8, 3:7 | 0/0/0/0 |

**Lecture honnête** : (1) la part totale de pièces à un tenon **n'a pas baissé** dans les zones (18,5 → 18,9–22,6 %) : les talus, arbres, fleurs et quarts-de-rond ajoutés sont des **feuilles décoratives** à un tenon par nature ; (2) en revanche les pièces à un tenon **qui portent** d'autres pièces (le vrai risque) chutent de 186/225/158 à 50/34/27, et le pire cas isolé passe de 10/14/18 à 7/8/7 pièces ; (3) zéro collision, zéro déconnectée, zéro îlot, zéro non supportée. Les chiffres du modèle complet sont dans `FINAL_VERDICT.md`.
