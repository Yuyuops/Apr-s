# Export impression 3D (expérimental) : briques individuelles et modules
Code : `lego_builder/print3d/` (`bricks.py`, `modules.py`, `common.py`, `cli.py`), validation `tests/validate_print_exports.py`, résultats `print_export_results/{paco,hyrule}/`. Commande : `python -m lego_builder.print3d.cli MODEL.ldr OUT --mode both` (dépendance : `manifold3d`, `requirements-print3d.txt`).

## Statut : NON VALIDÉ dans Bambu Studio, NON VALIDÉ physiquement
- **Validation numérique (faite, bloquante en CI)** : chaque STL et chaque corps de 3MF est un solide étanche de volume positif ; 3MF bien formés (zip, XML, indices dans les bornes) ; tout objet tient dans le plateau de 250 × 250 mm ; aucun recouvrement entre briques d'un plateau.
- **Ouverture dans Bambu Studio : non faite** (logiciel indisponible ici). Les 3MF sont du 3MF « cœur » (un objet par corps, couleur de base par objet) ; l'assignation multi-matériaux de Bambu n'est pas modélisée. **Ne pas déclarer l'export validé.**
- **Imprimante : aucune.** Les tolérances sont des **paramètres** (jeu de 0,10 mm par côté, tenons Ø 4,8 mm, parois 1,2 mm, ergots Ø 5,0 mm avec logement de +0,30 mm) à mesurer sur un échantillon de tolérances ; aucune compatibilité LEGO n'est revendiquée.
- Temps et masse : **formules**, pas de trancheur. Masse = volume du maillage × 1,24 g/cm³ (PLA supposé) = **borne haute** (remplissage plein) ; temps = volume / 8 mm³/s + 0,1 h par plateau. Pour les modules, une estimation à 30 % de remplissage effectif est donnée en plus (hypothèse, pas une mesure).

## Mode 1 : briques individuelles
Géométrie paramétrique écrite pour ce projet (aucune géométrie LEGO ni de tiers copiée) : plaques, briques et tuiles **rectangulaires** (face creuse, peau supérieure, tenons ; tubes pour 2×2 et plus). Une pièce hors de ce cas (pente, rond, coin arrondi, brique à tenons latéraux, courbe) est **déclarée non supportée**, jamais approximée. Une STL par type de brique ; plateaux 3MF par couleur, rangés en étagères (3 mm d'écart) ; un plateau = une couleur (un changement de filament par couleur).

## Mode 2 : modules imprimés
Le modèle est discrétisé sur la grille des tenons (8 × 8 mm, plaque de 3,2 mm) à partir des boîtes englobantes des pièces, découpé en modules ≤ 240 mm en plan et ≤ 224 mm de haut, reconstruit en corps pleins **par couleur**, avec tenons sur les faces supérieures exposées des pièces à tenons (les tuiles restent lisses), et **logements d'ergots** des deux côtés des coupes (ergots cylindriques à imprimer à part, non modélisés dans cet export). **Approximation assumée** : pentes, tuiles rondes et coins deviennent des blocs.

## Résultats (modèles actuels)
| | Hyrule biomes (704 × 704 × 67 mm) | Paco (272 × 280 × 397 mm) |
|---|---:|---:|
| **Briques authentiques** | 10 682 pièces, 134 réf., masse ≈ 9,2 kg (convention du validateur) | 3 193 pièces, 89 réf., ≈ 1,06 kg |
| coût d'approvisionnement | **non calculé** : aucun prix ni stock vérifié (`prices.template.csv`) | idem |
| **Briques imprimées** : pièces couvertes | 10 167 (95,2 %) ; non couvertes : 467 tuiles rondes d'angle 25269, 48 tuiles rondes 98138 | 3 077 (96,4 %) ; non couvertes : 116 (SNOT 52107, 63864, 47905, pentes, rondes…) |
| plateaux 250 × 250 | 131 (12 couleurs) | 21 (6 couleurs) |
| masse (borne haute) | 13,7 kg | 1,8 kg |
| temps machine estimé | ≈ 395 h | ≈ 53 h |
| changements de couleur | ≥ 11 (un par couleur) | ≥ 5 |
| travail manuel | 10 682 emboîtements | 3 193 emboîtements |
| **Modules imprimés** : modules | 9 (≤ 235 mm), 86 corps de couleur, 50 paires d'ergots | 8 (≤ 200 mm), 43 corps, 16 paires |
| masse borne haute / estimée à 30 % | 23,5 kg / 7,0 kg | 3,3 kg / 1,0 kg |
| temps borne haute / estimé à 30 % | 658 h / 198 h | 92 h / 28 h |
| changements de couleur (minimum, un corps par couleur et module) | 77 | 35 |
| travail manuel | ≈ 59 assemblages (modules + ergots) | ≈ 24 |
| **Modèle monté** | non évalué (aucune rentabilité démontrée) | idem |

## Lecture et risques
- **Aucune marge ni coût ne peut être donné** : prix des briques, du filament, de l'énergie, de l'amortissement et de la main-d'œuvre non vérifiés. Toute conclusion de rentabilité serait inventée.
- **Briques imprimées** : le travail manuel reste celui du kit d'origine (milliers d'emboîtements), pour plusieurs centaines d'heures machine sur Hyrule ; les pièces non couvertes (4 à 5 %) devraient être achetées ou modélisées. Risques : défauts de tolérance (emboîtement trop serré ou lâche, à mesurer), rebuts, ponts de la peau supérieure sur le creux.
- **Modules imprimés** : beaucoup moins d'assemblages mais corps pleins (matière et temps très dépendants du remplissage choisi), pas de vraies pentes, et couleurs multiples par module (changements de filament ou AMS) ; ergots à imprimer et coller ou presser. L'apparence « LEGO » se limite aux tenons.
- Dans les deux cas : validation sur une pièce d'essai de tolérances d'abord (ajustement, tenue, vieillissement), puis ouverture dans Bambu Studio.

## Verdict
**Pipeline expérimental opérationnel et validé numériquement ; NO-GO pour toute vente tant que (1) l'ouverture dans Bambu Studio, (2) un échantillon physique de tolérances et (3) les prix réels ne sont pas obtenus.**
