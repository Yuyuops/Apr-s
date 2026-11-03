### Tableau comparatif demandé — île témoin (32 × 32 tenons de champ)

| Indicateur | V0 | V0.1 A (LEGO apparent) | V0.1 B (premium) |
|---|---|---|---|
| Fidélité des contours : déplacement moyen de la côte réelle (mm) / IoU terre | 1.64 / 0.961 | 1.49 / 0.966 | 1.64 / 0.961 |
| Classes : IoU de cellules moyen / IoU pixels moyen | 0.905 / 0.671 | 0.905 / 0.671 | 0.905 / 0.671 |
| ΔE2000 moyen (valeurs réelles, pondéré surface) | 4.21 | 3.49 | 3.54 |
| ΔE76 moyen (comparable aux chiffres de V0) | 16.16 | 15.25 | 15.13 |
| Lisibilité du relief (paires de zones adjacentes distinguables) | 13 / 13 paires | 13 / 13 paires | 13 / 13 paires |
| Nombre de pièces (dos + relief + cadre) | 153 | 221 | 365 |
| Références (pièce × couleur) | 53 | 66 | 70 |
| Pièces 1×1 (part) | 9 (5.9 %) | 15 (6.8 %) | 23 (6.3 %) |
| Pièces sur un seul tenon (dont feuilles décoratives) | 9 (8) | 15 (12) | 23 (16) |
| Points d'articulation du graphe / porteuses tenues par < 4 tenons | 25 / 10 | 28 / 13 | 51 / 42 |
| Collisions / pièces déconnectées / composantes | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 0 / 1 |
| Épaisseur totale (mm) / tableau complet (mm) | 22.4 / 256 | 22.4 / 272 | 22.4 / 288 |
| Masse estimée (g, hypothèses explicites) | 785 | 954.00 | 1194.00 |
| Nombre d'étapes de notice / pièces max par étape | 15 / 43 | 23 / 20 | 32 / 20 |
| Qualité esthétique | à juger sur les rendus côte à côte | à juger sur les rendus côte à côte | à juger sur les rendus côte à côte |

### Même tableau — carte à trois zones

| Indicateur | V0 | V0.1 A | V0.1 B |
|---|---|---|---|
| IoU de cellules / IoU pixels | 1.000 / 0.931 | 1.000 / 0.931 | 1.000 / 0.931 |
| ΔE2000 / ΔE76 moyens | 5.29 / 18.41 | 3.80 / 16.50 | 3.80 / 16.50 |
| Pièces / références / 1×1 | 119 / 36 / 2 | 167 / 42 / 1 | 258 / 50 / 7 |
| Pièces sur un seul tenon / points d'articulation | 2 / 13 | 1 / 18 | 7 / 26 |
| Collisions / déconnectées | 0 / 0 | 0 / 0 | 0 / 0 |
| Épaisseur (mm) / masse (g) / étapes | 16.0 / 781 / 8 | 16.0 / 921.0 / 13 | 16.0 / 1073.0 / 18 |

### Écarts de couleur par classe — avant (V0, valeurs réelles) et après (V0.1 A) ; île témoin

| classe | V0 : couleur | ΔE2000 | ΔE76 | V0.1 : couleur | ΔE2000 | ΔE76 |
|---|---|---|---|---|---|---|
| colline | Dark_Tan | 9.7 | 16.0 | Medium_Nougat | 5.4 | 6.7 |
| foret | Sand_Green | 22.7 | 32.2 | Green | 8.0 | 13.4 |
| lac | Dark_Azure | 7.6 | 14.7 | Medium_Blue | 6.0 | 18.3 |
| mer | Blue | 4.7 | 26.3 | Blue | 4.7 | 26.3 |
| riviere | Medium_Blue | 6.0 | 18.3 | Medium_Blue | 6.0 | 18.3 |
| route | Medium_Nougat | 2.2 | 3.9 | Medium_Nougat | 2.2 | 3.9 |
| sommet | Light_Bluish_Grey | 20.4 | 30.1 | Tan | 8.2 | 11.4 |
| terre | Tan | 1.1 | 1.5 | Tan | 1.1 | 1.5 |
| village | Dark_Orange | 15.0 | 26.0 | Red | 8.9 | 34.9 |

### Résolution : 32 × 32 contre 48 × 48 (finition A, mêmes algorithmes)

| Indicateur | 32 × 32 (A) | 48 × 48 (A) |
|---|---|---|
| Taille du champ (mm) | 256 | 384 |
| Pièces / 1×1 | 221 / 15 | 393 / 33 |
| IoU de cellules / pixels | 0.905 / 0.671 | 0.952 / 0.767 |
| Contours de toutes les classes : déplacement moyen (mm) sur la grille de classes | 1.89 | 1.21 |
| IoU de la terre (empreinte réelle des plaques, côte seule) | 0.966 | 0.970 |
| Surface de la rivière / de la route (rapport au source) | 2.26 / 1.74 | 1.72 / 1.64 |
| Masse (g) / étapes | 954.0 / 23 | 2019.0 / 31 |

### Coins coupés (plaque biseautée 2×2, géométrie existante 26601) — île témoin, finition A

|  | sans coins coupés | avec coins coupés (A) |
|---|---|---|
| Plaques biseautées | 0 | 18 |
| Pièces / 1×1 | 202 / 11 | 221 / 15 |
| Côte : déplacement moyen (mm) / max (mm) / IoU terre | 1.64 / 5.32 / 0.961 | 1.49 / 4.95 / 0.966 |

