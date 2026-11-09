# Sprint V16 — Diagnostic du moteur LEGO Maps avant modification

Fichiers lus : `maps-engine-v03/style_fidelity_v062/{build_style.py, tiler.py, scene.py, fragility.py, decor.py}`, `maps-engine-v03/engine/maps_engine/tiling.py`, `lego-builder/tests/check_regression.py`. Mesures sur le modèle V15 B (12 543 pièces) et sur les trois zones. Tests de non-régression existants : `tests/check_regression.py maps|sculpture|glb` (SHA-256 bloquants, `ci/reference_hashes.json`), `tests/test_unit.py`, `check_render.py --no-render` (validateur indépendant), `verify_bom.py`, `fragility.py`, workflows CI `lego-maps-v09-deliverables` et `lego-builder-regression`.

| # | Sujet | Ce que fait réellement le code (fonctions) | Limite constatée | Risque de régression |
|---|---|---|---|---|
| 1 | **Génération des hauteurs** | `Builder.make_levels_biomes` : niveau constant par classe (`biomes[nom].level`) + gain par distance au bord de la classe (`gain.step/max`) ; strates de 2 plaques (`strata_thickness_plates`) | relief en **escaliers de 2 plaques** aux frontières de classes ; aucun lissage ; falaises de 2 à 8 plaques → « empilement de blocs » (zone A : 132 arêtes de falaise ≥ 2 plaques) | partagé par toutes les cartes à biomes (Hyrule V14/V15) |
| 2 | **Sélection et orientation des pentes** | `plan_flanks` / `place_flanks` (pièces courbes 11477/15068 ou plaques progressives) ; convention d'orientation `scene.LOW_DIR` | les flancs ne s'appliquent qu'aux cellules **non sujet** (mer/étranger) avec marche de 1 niveau : **aucun effet sur les falaises terrestres en mode biomes** (vérifié : `--flank curved` et `progressive` donnent exactement le même modèle que `vertical` sur la zone A de V15) ; V15 utilisait de toute façon `--flank vertical` | risque faible si l'option reste désactivée |
| 3 | **Pièces courbes** | `place_top` + `corner_rot` : coins convexes de la surface arrondis par la tuile quart-de-rond `25269` (`surface.round_corners`) | seul usage de pièces courbes ; chaque quart-de-rond est une pièce à 1 tenon (feuille décorative, 525 dans V15 B) | — |
| 4 | **Transitions entre biomes** | frontières nettes de classes ; couleur de paroi par classe (`biomes[nom].wall`), `hidden_wall` neutre pour les plans cachés | aucun dégradé ; l'eau est un aplat de niveau 1 (pas de profondeur) | — |
| 5 | **Petits éléments** | `decor.py` (texte, filets, médaillons) ; module `figures/` (arbres, rochers) propre aux cartes à figures (Italie) ; **rien en mode biomes** | aucune végétation ni détail dans Hyrule V15 | — |
| 6 | **Supports structurels** | corps de strates pavés par `tiler.tile` (glouton aléatoire, 8 essais, critère « tenons sous la pièce ») ; **le pavage évolué `maps_engine.tiling.tile_layer` (coût d'orphelins, décalage de joints, recherche locale, fusion des petites pièces) existe mais n'est pas branché sur `build_style`** | dans V15 B, **1 552 des 2 580 pièces à un tenon sont des plaques 1×1 de corps** (`strata_body 3024`) ; 525 quarts-de-rond, 421 tuiles 1×1, 48 ornements | forte : `build_style` produit les 8 références CI ; toute modification doit rester **désactivée par défaut** |
| 7 | **Connexions** | joints calculés par le validateur moteur 1 (`validate_v4 --dump`), `Scene.merge_pass` fusionne des pièces voisines | les cellules cachées (derrière un voisin plus haut) reçoivent un gris neutre mais ne sont pas utilisées pour **allonger** les bandes visibles d'une cellule → bandes 1 × N et 1×1 | — |
| 8 | **Estimation de la fragilité** | `fragility.py` : pièces à un tenon (feuille décorative / porteuse), points d'articulation, masse coupée | indicatif, aucune force physique ; **le pire défaut isolé de V15 B (45 pièces) est une plaque de corps qui porte un sommet** ; une plaque unique sous un pic est un point de défaillance unique | — |

## Constats chiffrés (V15 B complet, `sprint_v15/builds/B/fragility.json`)
- Pièces à 1 tenon : **2 580 = 20,6 %**, dont 1 584 porteuses ; pire défaillance isolée : **45 pièces** (`strata_body` 521).
- Relief : 2 plaques par niveau, pas de lissage ; couleurs de parois par classe.

## Stratégie retenue (modulaire, activée par configuration, **désactivée par défaut**)
1. `surface.body_tiler = "wild"` : pavage des corps avec cellules cachées « jokers » + `tile_layer`/`local_improve`/`merge_small` du moteur.
2. `surface.top_tiler = "seam"` : tuiles de dessus qui enjambent les joints du dessous.
3. `surface.body_max_area` : plafond de taille des plaques de corps (grosses plaques = points de défaillance uniques).
4. `relief.smooth_height` : hauteurs lissées au pas d'1 plaque (+ `coast_ramp`).
5. `surface.cliff_slopes` : talus (pente 31°, `54200`) au pied des falaises.
6. `details` : règles de végétation déterministes (arbres `3062b`, buissons/fleurs `6141`) sur classes sémantiques.
7. `tools/reinforce_v16.py` + `--reinforce` : passe de renforcement mesurée (points d'articulation → re-pavage en petites pièces des plans cachés, cumulatif).
8. Données : classe `shallow` (eau peu profonde) calculée sans déplacer aucun contour (`tools/hyrule_v16_data.py`, vérifié : 0 cellule de différence avec le raster B après relabel).
