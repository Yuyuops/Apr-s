# LEGO Maps V0.5.1 — montagne et Colisée refaits avec des pièces LDraw réelles

Branche `research/lego-maps-italie-v05-quality-first`. Aucun achat, moteur 1 inchangé, aucune fusion dans `main`, **aucun essai physique** (tout ce qui suit est numérique : LDraw, validateur du moteur 1, rendus de la géométrie réelle des pièces).

## Ce qui a changé par rapport à V0.5
| | V0.5 | V0.5.1 |
|---|---|---|
| Diorama | 48 × 32 tenons, 707 pièces | **72 × 48 tenons (57,6 × 38,4 cm), 2 714 pièces, 138 couples pièce/couleur** |
| Placement des pièces | décalages écrits à la main (pente 3039 seulement) | **catalogue dérivé de la géométrie LDraw officielle** (`part_catalog.json`) : n'importe quelle pièce, 4 rotations, sans décalage manuel |
| Montagne | colonnes 2×2, deux sommets, brun dominant | carte de hauteurs (briques) à flancs concaves et crêtes, **337 pentes 45° réelles** (3040b/3039/3038/3037) posées sur chaque marche d'une brique, falaises, strates, neige, **27 rochers** (pente 31°, 54200), **21 arbres** (9 conifères = rond 3941 + cône 3942c, 6 feuillus), 6 buissons, plage, côte irrégulière |
| Colisée | 18 colonnes rondes + linteaux | ovale à angles arrondis, **3 niveaux d'arcades en vraies briques-arches** (6182 au rez-de-chaussée, 3659/4490 aux étages = 42 arches), **attique à fentes** + corniche, **cavea à 7 gradins concentriques**, arène avec grille d'hypogée, **côté ruiné** qui laisse voir les gradins |
| Source de pièces | — | uniquement des `.dat` réels et courants (aucun alias `~Moved`), vérifié |

Hauteur max : 12,2 cm. Les deux modules sont artistiques : relief non déduit d'un MNT, Colisée non à l'échelle d'un plan.

## Validations (rejouées par `run_all.sh`, aucun seuil modifié)
Validateur indépendant du moteur 1 (`independent_validation.json`) : **2 714 pièces — 0 collision, 0 pièce déconnectée, 0 îlot, 0 pose sans appui à l'assemblage, 0 tenon bloqué**. LDraw = JSON = nomenclature = 2 714.
Pré-contrôle interne : chaque pièce repose sur une pièce à tenons ; séquence d'assemblage couche par couche.
Références (`bom_verification.csv`) : 138/138 `.dat` présents et non-alias, 138/138 couleurs valides dans Rebrickable et LDConfig, **138/138 couples catalogués par Rebrickable** (nombre de sets indiqué). 4 couples inexistants ont été remplacés automatiquement par la couleur voisine catalogue (6 pièces : 3037/3038 en Dark Tan→Tan, 3038 Sand Green→Green, 6141 Dark Green→Green), consignés dans `metrics.json`. Prix et stock : **non vérifiés** (colonnes vides).

## Rendus réels (`results/diorama_v051/renders/`)
Géométrie des pièces LDraw rendue par three.js, couleurs Rebrickable. Vue de dessus, trois-quarts, profil, rotation 180° du diorama (`full_*`), montagne (`montagne_trois_quarts/face/sommet/flanc`), Colisée (`colisee_trois_quarts/face/facade/ruine/arene`) ; V0.5 rejoué dans `v05_reference/` ; comparatifs dans `comparatifs/`.

## Comparaison critique V0.5 / V0.5.1
**Colisée — net progrès.** V0.5 : un enclos de colonnes sans façade ; V0.5.1 se reconnaît sans légende : ovale, arcades superposées, attique, gradins, arène, ruine. Défauts restants : les arches d'étage 1×4 (3659) ne forment qu'une alvéole basse, les coins arrondis sont des escaliers de briques pleines (pas d'arches dans ces pans), la ruine est « tronquée » plutôt qu'érodée, le mur extérieur n'a qu'un tenon d'épaisseur (fragile en vrai), l'oval est un peu trop rectangulaire.
**Montagne — progrès réel mais pas encore convaincant.** Pentes, strates, neige, rochers, forêt et côte organique remplacent le tas de cubes bruns. Défauts : l'ensemble reste un **dôme à un sommet dominant** (sommets secondaires peu marqués, peu de vallées et de couloirs), la couronne de pentes à pas constant se lit comme un « anneau », les patchs Sand Green sont trop pâles, les arbres à couronne 2×2 sur un seul tenon sont décoratifs et fragiles.

## Échelle : réserve d'architecture
À 128 × 128 tenons pour l'Italie (≈ 1 050 km de large pour 1 m), 1 tenon ≈ 8 km : un Colisée de 32 tenons n'existe pas à l'échelle de la carte. Les modules servent de **monuments agrandis / encarts** ; la règle d'intégration (taille, position, exagération déclarée) est à décider avant l'Italie.

## Reproduire
`bash run_all.sh` (nécessite l'installation du moteur 1 : `20_portable_engine/scripts/install.sh`, et `LEGO_ENGINE_HOME` dans `env.sh`). Graine 7.
