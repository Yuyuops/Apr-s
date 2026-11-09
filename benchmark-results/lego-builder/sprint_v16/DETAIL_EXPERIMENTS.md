# Sprint V16 — Expériences de détails (végétation, sols, eau et littoral)

Règles lues dans le style (`details`), **sur les classes sémantiques**, jamais sur l'image : aucune décoration au hasard (échantillonnage bleu-bruit déterministe, graine fixe, espacement minimal, cellules intérieures seulement). Code : `plan_details` / `place_details` (build_style.py) ; données : `tools/hyrule_v16_data.py`.

| Élément | Règle | Pièces | Pourquoi |
|---|---|---|---|
| Arbres | classe `forest` : sol en plaques à tenons (couleur de la classe), arbre sur ≈ 30 % des cellules, espacement ≥ 2 studs, couleurs 288/2 en alternance | brique ronde 1×1 `3062b` (3 plaques de haut) | la référence montre des arbres en pièces rondes 1×1 sur sol à tenons dans les forêts |
| Buissons | classe `grass`/`meadow` : ≈ 4 % des cellules, espacement ≥ 3 | plaque ronde `6141` vert vif sur un **patch 1×2 à tenons** (la pièce a besoin d'un tenon ET d'une plaque à 2 tenons dessous) | un détail sur une surface lisse sans tenon est refusé par le validateur (« parts without any support under them ») : constaté lors du premier essai |
| Fleurs | classe `grass`/`meadow` : ≈ 2,5 % des cellules, espacement ≥ 3,5, couleurs jaune/rouge/blanc | plaque ronde `6141` | accents de la référence (fleurs jaunes/rouges dans les plaines du nord-est) |
| Eau peu profonde | classe `shallow` (donnée) : cellules d'eau à ≤ 1,5 stud d'une terre **et** proches d'un plan d'eau large (rivières et douves étroites restent bleu foncé) ; couleur Medium Blue 73 | tuiles | gradient de profondeur sans toucher aucun contour ; **0 cellule de différence** avec le raster B après retour des classes `shallow`→`water` et `meadow`→`grass` |
| Berges | `coast_ramp` : 0,7 plaque par stud sur 4 studs ; quart-de-rond de coin conservé | `25269` + tuiles | rives en pente douce au lieu d'une marche verticale |

## Cycles
| Zone | Cycle | Défaut dominant | Modification | Résultat |
|---|---|---|---|---|
| B (plaines/forêts) | 1 | grand aplat vert uniforme | arbres + buissons | 41 détails ; validation OK ; aplat rompu (rendu `renders/cycles/d1_B_gros_plan.jpg`) | 
| B | 2 | plaine encore pauvre | + fleurs | 44 détails (3,4 → 5,8 / 100 cellules de terre), accents de couleur |
| B, C (eau) | 3 (hors limite, voir note) | **l'eau peu profonde de la 1ʳᵉ version coloriait toutes les douves et rivières en bleu pâle** : le bleu franc de la référence disparaissait (observé sur la comparaison côte à côte avec la référence) | règle `shallow` limitée aux grands plans d'eau + teinte 73 | douves et rivières redeviennent bleu foncé ; gradient seulement le long des côtes larges |
| C (littoral) | 1 | rive verticale, mer sans nuance | rampe de berge + eau peu profonde | transition mer → terre en trois teintes, bord de côte progressif |

## Mesures (zone V15 → V16)
| Zone | Pièces de détail | Détails / 100 cellules de terre | Couleurs de surface distinctes | Accord de classe (rendu vs raster) |
|---|---|---|---|---|
| A | 0 → 27 | 0 → 3,0 | 9 → 10 | 0,923 → 0,914 |
| B | 0 → 44 | 0 → 5,1 | 6 → 7 | 0,918 → 0,904 |
| C | 0 → 46 | 0 → 5,7 | 7 → 7 | 0,909 → 0,886 |
L'accord de classe baisse légèrement (≈ −1 à −2 points) parce que les arbres, talus et fleurs recouvrent des cellules de couleur de classe ; la géographie n'est pas modifiée (rasters identiques à B hors relabels).

## Limites et abandons
- Densité de détails **très inférieure** à la référence (qui compte des centaines d'éléments 1×1 par zone, bâtiments, tours, ponts) ; on s'est limité à des détails régis par une règle de classe.
- Aucun chemin ni sentier n'a été ajouté : la classe `shore` de la référence n'est pas assez fiable pour en tirer des chemins sans les inventer.
- Pas d'essai d'arbres coniques (`4589` : < 15 exemplaires par couleur) : disponibilité jugée trop faible.
