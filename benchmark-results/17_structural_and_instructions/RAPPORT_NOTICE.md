# Notice V9 : sous-notices hiérarchiques contrôlées

La notice de V8.2 comptait 326 étapes, avec chaque oreille posée d'un bloc (176 et 156 pièces). Celle de V9 compte **211 étapes**, organisées en modules et sous-modules, contrôlées une par une. Elle est livrée sous trois formes : le **LDraw ordonné**, le **plan structuré** (JSON, étapes et contrôles) et les **PDF illustrés**.

| Fichier | Contenu |
|---|---|
| `modeles/paco_V9_notice.ldr` | 3 066 pièces dans l'ordre de montage, 211 `0 STEP`, un bloc `0 BRICKIFY SUBASSEMBLY` par module construit à part (bras, oreilles, détails) ; ouvrable dans Studio ou LeoCAD |
| `notice/plan_notice.json` | Chaque étape : module, section, pièces, contrôle de chaque pièce (liaisons, mouvement, dégagement, alerte) |
| `notice/etapes_notice.csv` | Tableau des 211 étapes, avec le nombre d'alertes et la direction d'emboîtement |
| `notice/arbre_notice.json` | Arbre des modules, sections, étapes et pièces |
| `notice/*.pdf` | 5 PDF, 212 pages (couverture et 211 étapes), 12,5 Mo au total |

## 1. Structure

| Module | Étapes | Pièces | Contenu |
|---|---|---|---|
| **Corps** | 124 | 2 468 | Pieds, jambes, bassin, torse, épaules, cou et tête, en place, de bas en haut (au plus 20 pièces par étape) |
| **Bras gauche** | 7 + fixation | 137 | Construit à part : la **main** (1 étape de 20 pièces), puis l'avant-bras et le bras (6 étapes) ; poussé par le bas dans les plaques d'épaule |
| **Bras droit** | 6 + fixation | 118 | Idem |
| **Oreille basse** | 23 + 5 unités + fixation | 156 | Construite à part en **unités rigides** (sous-ensembles qui s'emboîtent d'une seule translation) ; fixée sur la tête avant que la tête ne se referme |
| **Oreille haute** | 28 + 5 unités + 2 fixations | 181 | Idem (176 pièces et un groupe de 5 pièces) |
| **Détails du visage** | 4 modules | 6 | Pente rouge, 2 yeux (coupole et pupille), truffe : fixés en dernier sur leurs briques SNOT |

Les **plaques tournées de fixation des oreilles**, leurs appuis et les briques SNOT des yeux sont des pièces du corps, posées à leur couche, et les oreilles s'y accrochent.

## 2. Ce qui est contrôlé à chaque étape

1. **Liaison réelle.** Chaque pièce est jointe, par des tenons réellement engagés (même règle que `validate_v3`), à une pièce déjà posée, ou repose sur le plan d'appui, sur la table (première couche d'un module construit à part) ou sur une pièce déjà posée sans tenon (tuile).
2. **Emboîtement physique, pas seulement un graphe connecté.** La pièce recule de 4 LDU le long de l'axe de ses tenons (jeu d'emboîtement) : aucune pièce posée ne doit gêner. Elle doit ensuite pouvoir **sortir** du modèle le long d'un des six axes (elle peut glisser de côté une fois ses tenons libres) ou, pour les petites pièces, par un chemin avec virages (recherche en largeur par pas de 4 LDU).
3. **Collisions.** Pièces à angle droit sur le réseau de 4 LDU : grille d'occupation exacte. Autres pièces (oreilles, plaques tournées, plaques courbes) : points de leur volume, recouvrement si deux points sont à moins de 1,5 LDU (règle de `validate_v3`).
4. **Pièce emprisonnée.** Une pièce qui s'emboîte dans deux directions différentes sur des pièces déjà posées est refusée : elle ne pourrait pas être insérée.
5. **Sous-ensembles.** Un module construit à part est contrôlé comme un corps rigide : approche de 4 LDU, puis dégagement. L'instant d'accrochage est cherché **le plus tôt possible** : une oreille s'accroche avant que la tête ne se referme sur sa racine ; un bras s'accroche, par le bas, une fois les plaques d'épaule posées ; les détails du visage s'accrochent à la fin.
6. **Pièces suspendues.** Une pièce sans rien dessous (surplomb) est emboîtée **par le bas** après la pièce qui la tient (338 pièces). Elle est signalée sur la page.
7. **Tenue pendant le montage.** Chaque pièce posée est liée ou repose sur un appui ; 30 pièces sont « posées sur un appui sans emboîtement, verrouillées par la couche suivante ». Aucun calcul de statique n'est fait pour l'état intermédiaire.
8. **Complétude.** Les 3 066 pièces du modèle sont dans la notice, une seule fois (contrôlé).

## 3. Résultats

| Contrôle | Résultat |
|---|---|
| Pièces du corps, des bras et des détails | **Toutes insérables** (9 pièces demandent un chemin avec virages) |
| Accrochage des 2 bras, des 2 oreilles et des détails | **Possible** pour chaque module, au plus tôt |
| Collisions (`validate_v3`, notice ordonnée) | **0** |
| Pièces déconnectées / îlots / sous-ensembles non attachables | **0 / 0 / 0** |
| Pièces de la notice sans séquence d'insertion trouvée | **31, toutes dans les oreilles** (19 oreille basse, 12 oreille haute), réparties sur 14 étapes marquées « ATTENTION » dans le PDF |

**Les 31 pièces d'oreille.** Le planificateur cherche l'ordre inverse du démontage : il retire à chaque fois une unité qui peut sortir d'une seule translation. Dans chaque oreille il reste un noyau de pièces (13 pièces d'un côté) dont les liaisons s'exercent **des deux côtés** d'un même plan (en haut et en bas, plus de chaque côté de la face) : aucune unité n'en sort sans que l'autre ne le retienne. Je n'ai pas montré qu'elles sont impossibles à monter (un monteur peut incliner une pièce ou plier légèrement un contour), seulement qu'**aucune séquence de translations rigides n'a été trouvée**. Ce défaut est celui du générateur d'oreille V6.1, qui n'a jamais été contrôlé à ce niveau, et il est signalé comme tel dans le PDF.

## 4. Limites du contrôle d'accessibilité

- Il ne contrôle que des **translations rigides** : pas de rotation de la pièce pendant l'emboîtement, pas d'inclinaison ni de flexion.
- Il ne modélise **ni les doigts ni les outils** : une pièce qui passe est supposée atteignable à la main.
- Il traite **un contact à la fois** pour la direction : les cas de plusieurs directions d'emboîtement simultanées sont refusés, même si un monteur habile pourrait les contourner.
- Le jeu d'emboîtement est fixé à 4 LDU (1,6 mm), la hauteur d'un tenon.
- L'ordre des unités d'oreille est celui du démontage trouvé : d'autres ordres existent.
- Le PDF est lisible mais **n'a pas été suivi par un monteur** ; la clarté des pages n'est pas validée.

## 5. PDF

| PDF | Pages | Taille |
|---|---|---|
| `paco_V9_1a_corps_etapes_1_a_62.pdf` (couverture comprise) | 63 | 3,9 Mo |
| `paco_V9_1b_corps_etapes_63_a_fin.pdf` | 62 | 4,1 Mo |
| `paco_V9_2_bras_et_mains.pdf` | 15 | 0,9 Mo |
| `paco_V9_3_details_visage.pdf` | 8 | 0,4 Mo |
| `paco_V9_4_oreilles.pdf` | 64 | 3,2 Mo |

Chaque page porte : le numéro d'étape, le module et la section, une vue rendue avec les **vraies formes de pièces LDraw** (pièces à ajouter en couleur, pièces déjà montées en pâle), la liste des pièces à ajouter (quantité, forme, couleur), et la direction d'emboîtement. Pour un sous-ensemble ou une unité, la vue le montre **décalé le long de son emboîtement** (vue éclatée) avec la phrase « pousser vers … ». Les axes sont ceux du repère LDraw (le haut est « vers le haut »).
