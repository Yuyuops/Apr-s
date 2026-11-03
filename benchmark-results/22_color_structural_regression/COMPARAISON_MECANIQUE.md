# Comparaison mécanique et colorimétrique V11 / V12 / V12.1

Même validateur, mêmes seuils, même base Rebrickable de référence ; V11 revalidé avec la méthode courante (Beagle : valeurs archivées retrouvées ; Paco : rejeu à palette figée octet pour octet identique à V9.1).

## Beagle
| | V11 | V12 | **V12.1** |
|---|---|---|---|
| Pièces | 11111 | 10498 | 10567 |
| Types de pièces | 24 | 24 | 23 |
| Liaisons (paires de pièces) | 21091 | 20440 | 20594 |
| dont à un seul tenon | 10420 | 9520 | 9715 |
| Collisions | 0 | 0 | 0 |
| Pièces déconnectées | 0 | 0 | 0 |
| Pièces sans appui à la pose | 0 | 0 | 0 |
| Cas de stabilité évalués | 2285 | 2055 | 2016 |
| Cas < 0,5 N | 10 | 32 | 0 |
| Cas < 2 N | 65 | 99 | 62 |
| Groupes fragiles distincts | 10 | 32 | 0 |
| FS gravité minimal | 38.23 | 15.79 | 43.25 |
| Force de bout minimale (N) | 0.1 | 0.06 | 0.52 |
| Étapes LDraw (0 STEP, notice plate) | 593 | 602 | 544 |
| ΔE moyen / médian | 17.1 / 15.6 | 14.7 / 13.3 | **14.7 / 13.3** |
| Cellules parasites | 195 | 31 | 30 |
| Sans correspondance catalogue | 0 | 31 | 31 |
| IoU silhouette | 0.998 | 0.998 | 0.998 |

Surfaces exposées : 0 cellule d'occupation et 0 cellule exposée modifiée par le renfort (243 cellules cachées recolorées) ; la réparation de couleur est inchangée (1 cellule exposée de différence avec V12, parasites 31 → 30).

## Paco
| | V11 | V12 | **V12.1 option A** (palette V12) | **V12.1 option B** (palette V11 + réparation) |
|---|---|---|---|---|
| Pièces | 3098 | 3193 | 3193 | 3102 |
| Liaisons | 4899 | 4954 | 4954 | 4902 |
| dont à un seul tenon | 2933 | 2995 | 2995 | 2934 |
| Collisions | 0 | 0 | 0 | 0 |
| Pièces déconnectées | 0 | 0 | 0 | 0 |
| Cas évalués | 1026 | 1083 | 1083 | 1023 |
| Cas < 0,5 N | 7 | 8 | 8 | 6 |
| Cas < 2 N | 48 | 51 | 51 | 45 |
| Groupes fragiles distincts | 7 | 8 | 8 | 6 |
| FS gravité minimal | 11.15 | 9.82 | 9.82 | 11.15 |
| Force de bout minimale (N) | 0.19 | 0.19 | 0.19 | 0.17 |
| Étapes LDraw (notice plate) | 289 | 371 | 371 | 289 |
| ΔE moyen / médian | 20.4 / 12.9 | 15.5 / 12.5 | 15.5 / 12.5 | 16.4 / 12.6 |
| Cellules parasites | 369 | 114 | 114 | 101 |
| Sans correspondance catalogue | 467 | 182 | 182 | 467 |
| IoU silhouette | 0.867 | 0.867 | 0.867 | 0.867 |
| Cellules d'oreille parasites (fixations) | 106 | 20 | 20 | 17 |
| Fixations : pièces de contact tête (basse / haute) ; chemins disjoints | 8 / 7 ; 1 / 1 | 8 / 7 ; 1 / 1 | 8 / 7 ; 1 / 1 | 8 / 7 ; 1 / 1 |
| Couples pièce×couleur du catalogue vérifiés | — | 89 / 89 | 89 / 89 | 74 / 74 |

Groupes fragiles de Paco restants (option A) : museau 7 pièces 2 tenons 0,19 N ; bas du torse 8 pièces 0,26 N ; bas du torse 9 pièces 0,26 N ; 9 pièces 3 tenons 0,33 N (rouge/jaune) ; 3 pièces 2 tenons 0,40 N (dessus de crâne). Ce sont de petits éléments de 1 à 2 g aux extrémités minces (mains, pieds, museau) : pas de cellule voisine cachée ni de même couleur, ou la retuilisation couperait un lien (toutes les variantes de pavage et de longueur de pont ont été essayées). Trois de ces cinq groupes existent déjà en V11 (museau, deux bas de torse) ; deux sont nouveaux (rouge/jaune et dessus de crâne) et un groupe V11 du museau a disparu : bilan +1 cas.

## Compromis Paco (objectifs incompatibles, deux options présentées)
| | option A (palette V12) | option B (palette V11 + réparation de couleur) |
|---|---|---|
| Cas faibles (objectif V11 : 7) | 8 (+1) | **6** |
| FS gravité min | 9,82 (V11 : 11,15) | **11,15** |
| ΔE moyen | **15,5** | 16,4 |
| Cellules sans correspondance | **182** | 467 (pas d'Orange / Dark_Tan) |
| Cellules parasites | 114 | **101** |
| Pièces / étapes | 3 193 / 371 | 3 102 / 289 |
Le choix dépend de ce que l'on privilégie (fidélité des tons orangés ou marge mécanique) : il n'a pas été tranché artificiellement. La configuration par défaut du dépôt reste l'option A (`subjects/paco.json`), l'option B est `subjects/paco_option_B.json`.
