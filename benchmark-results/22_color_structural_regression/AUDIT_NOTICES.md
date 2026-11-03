# Audit des notices (étapes) — pourquoi 202 → 371 (Paco) et 593 → 602 (Beagle)

Il y a **trois comptages différents** qui ont été confondus :
| Comptage | Paco | Beagle |
|---|---|---|
| (1) Notice hiérarchique V9.1/V10 (`notice_plan.py` + plans d'oreilles ; livrée en PDF) | **201** étapes (202 lignes CSV avec l'en-tête), 9 blocs de sous-assemblage | **581** étapes |
| (2) Notice plate du moteur portable (`reorder_notice.py`, compteur `0 STEP` du LDraw, utilisé par l'étape *final* de `lego_run.py`) | V11 : 288 (+1) ; V12 : 370 (+1) ; V12.1 A : 370 ; V12.1 B : 288 | V10 : 592 (+1) ; V12 : 601 ; **V12.1 : 543 (+1)** |
| (3) Nombre de blocs de sous-assemblage dans le LDraw | V9.1 : 9 ; moteur portable : 3 (oreilles seulement) | 0 |

Les « 202 → 371 » comparent donc (1) à (2) : **changement de planificateur et de format**, pas une perte de pièces. La géométrie V9.1 elle-même, rejouée par le moteur portable, donne 288 étapes plates (V11, octet pour octet identique à V9.1) : l'écart 201 → 288 vient du planificateur plat (« toutes les pièces posables du niveau le plus bas à chaque étape », sans regroupement des bras ni des détails ; seuls 3 blocs d'oreille sont conservés sur les 9 de V9.1 : la **hiérarchie bras / détails est perdue dans le LDraw plat**, pas dans le modèle : le plan hiérarchique recalculé sur V11 retrouve les 201 étapes et les 9 blocs). Écart 288 → 370 entre V11 et V12 : **nouveau découpage des plaques** par la palette automatique (+95 pièces, davantage de régions de couleur donc de niveaux et de poses « par-dessous »), confirmé par l'option B (palette V11, 288). Beagle 592 → 601 est le même mécanisme (plat contre plat) ; V12.1 descend à 543 : le renfort étendu re-tuile des couches avec des plaques plus longues (cause non isolée plus précisément ; le nombre de pièces, lui, remonte à 10 567).

Notice hiérarchique (comparaison de même nature, `notice_plan.py` sur la notice plate de chaque modèle) :
| Beagle | V11 (méthode courante) | V12.1 |
|---|---|---|
| Étapes du plan | 581 (valeur archivée retrouvée) | **554** |
| Pièces absentes du plan | 0 | 0 |
| Étapes dont un contrôle de mouvement échoue | 0 | 0 |
| Modules | corps 555 + 13 détails de visage | corps 528 + 13 détails de visage |

| Paco (même planificateur hiérarchique, ouvrages d'oreilles planifiés par `run_ears_v91.py`) | V11 (rejeu V9.1) | V12.1 option A |
|---|---|---|
| Étapes du plan | **201** (valeur archivée retrouvée) | **207** (+6 ; pièces 3 098 → 3 193) |
| Corps / bras G / bras D | 124 / 8 / 7 | 128 / 9 / 8 |
| Oreille basse (+2 unités) / oreille haute (+ attache) | 25 (+2+2) / 23 (+2) | 25 (+2+2) / 23 (+2) |
| Détails du visage | 4 blocs de 2 étapes | 4 blocs de 2 étapes |
| Pièces absentes du plan | 0 | 0 |
| Étapes dont un contrôle de mouvement échoue / problèmes d'insertion | 0 / 0 | 0 / 0 |
**Conclusion :** la notice hiérarchique de Paco est conservée (mêmes modules, mêmes sous-assemblages d'oreille, mêmes séquences d'oreille) ; l'augmentation **comparable** est de 201 à 207 étapes (+3 %, pour +3 % de pièces), et le chiffre 371 est celui de la notice plate. Pour éviter de reproduire la confusion, `lego_run.py` dispose désormais d'une étape optionnelle `notice` (`--stop-after notice`) qui produit le plan hiérarchique, le CSV des étapes, l'arbre et la nomenclature ; la notice plate de l'étape *final* est étiquetée comme telle. Le PDF illustré n'a pas été régénéré (rendu de ≈ 200 pages) : seuls le plan, le CSV et l'arbre le sont.
Les étapes sont des **séquences numériques** vérifiées par translations rigides et graphe de tenons ; elles ne prouvent aucun montage physique (aucun essai à la main n'a été réalisé).
