# Sprint V14 — Benchmark de tranchage sur les exports V13 réels

**Ce que c'est** : les vrais exports V13 (Paco : `tests/data/paco_sample.ldr`, 3 193 pièces ; Hyrule : `livraison_v10/hyrule_biomes/diorama.ldr`, 10 682 pièces, SHA = référence CI) tranchés par **PrusaSlicer 2.7.2** (seul slicer installable ici) avec des **profils proxy** par machine. **Ce n'est PAS un résultat de Bambu Studio, Creality Print ou Snapmaker Orca** : aucun profil constructeur n'était disponible (binaires et dépôts de profils inaccessibles). Les temps sont donc des estimations sous profil proxy ; seule la masse de filament de tranchage et les géométries sont directement issues des fichiers.

## Profils proxy (identiques sauf accélération)
Buse 0,4 ; couches 0,2 ; 3 périmètres ; remplissage 15 % ; PLA 1,24 g/cm³ ; débit max 21 mm³/s (**hypothèse commune ; seul le U1 annonce 32 mm³/s**) ; vitesses périmètre 200 / ext. 120 / remplissage 250 mm/s ; accélération A1 **10 000**, Hi **12 000**, U1 **20 000** mm/s² (valeurs constructeur vérifiées) ; plateau utile commun 250 mm (conservateur pour Hi 260 et U1 270).

## Couverture et échantillonnage (déclarés)
- Modules multicolores (17) : tranchés **intégralement**, avec et sans supports (supports auto 45°) sous profil A1 ; sans supports aussi sous Hi et U1.
- Plaques monochromes (procédé 3 : 7 Paco + 43 Hyrule) : toutes tranchées sous A1 (sans/avec supports) ; Hi/U1 sur un échantillon (1 plaque sur 4) puis ratio de temps.
- Briques individuelles : **1 plaque sur 4** tranchée sous A1 (Paco 6/21, Hyrule 33/131), 1 sur 8 pour Hi/U1 ; totaux = moyenne × nombre de plaques.
- **1 plaque Paco monochrome (`mono_005`, 101 pièces noires) fait planter PrusaSlicer (segfault reproductible)** : estimée par ratio volume (voir `cost.json`, `crashed_plates_estimated`).

## Paco

| Procédé | Plateaux | Temps tranché A1 | Hi | U1 | Filament tranché (g) | Remarques |
|---|---|---|---|---|---|---|
| 1. Briques individuelles | 21 | 147 h | 147 h | 147 h | 1948 | 3077/3193 pièces imprimables ; 100 % des plots à plat ; ponts sous tuiles |
| 2. Modules multicolores (8) | 8 | voir ci-dessous (+supports) | — | — | 1764 dont supports 680 | 7990 colour-changes ; 4 module(s) dépassent 4 couleurs par couche |
| 3. Pièces monochromes assemblées | 7 | 128 h | — | — | 2286 | 421 pièces à assembler ; supports +845 g |

### Modules (procédé 2) — mesures par module
| Module | Couleurs | Max couleurs / couche | Changements de couleur (couches 0,2 mm) | Pièces connexes | Temps A1 sans supports | **fusionné** sans / avec supports (h) | **fusionné** g sans / avec | Avert. |
|---|---|---|---|---|---|---|---|---|
| module_0_0_0.3mf | 5 | 4 | 2120 | 77 | 16.7 h (objets séparés) | 7.6 / 15.2 | 216 / 350 | Floating bridge anchors, Low bed adhesion, Loose extrusions; |
| module_0_0_1.3mf | 5 | 5 | 429 | 20 | 2.2 h (objets séparés) | 1.5 / 3.0 | 32 / 58 | Floating bridge anchors, Loose extrusions; Floating bridge a |
| module_0_1_0.3mf | 6 | 5 | 1315 | 101 | 18.1 h (objets séparés) | 15.7 / 27.8 | 343 / 536 | Floating bridge anchors; Floating object part; Long bridging |
| module_0_1_1.3mf | 6 | 4 | 365 | 15 | 3.0 h (objets séparés) | 2.3 / 4.4 | 36 / 73 | Floating bridge anchors, Low bed adhesion, Loose extrusions; |
| module_1_0_0.3mf | 5 | 5 | 1919 | 78 | 16.0 h (objets séparés) | 7.5 / 15.3 | 206 / 342 | Floating bridge anchors; Floating object part; Long bridging |
| module_1_0_1.3mf | 5 | 4 | 433 | 19 | 2.6 h (objets séparés) | 1.4 / 2.5 | 28 / 48 | Floating bridge anchors, Low bed adhesion, Loose extrusions; |
| module_1_1_0.3mf | 6 | 5 | 574 | 28 | 4.9 h (objets séparés) | 3.3 / 4.3 | 75 / 92 | Floating bridge anchors; Floating object part; Long bridging |
| module_1_1_1.3mf | 6 | 4 | 835 | 83 | 10.0 h (objets séparés) | 7.4 / 14.3 | 148 / 266 | Floating bridge anchors; Floating object part; Long bridging |

## Hyrule

| Procédé | Plateaux | Temps tranché A1 | Hi | U1 | Filament tranché (g) | Remarques |
|---|---|---|---|---|---|---|
| 1. Briques individuelles | 131 | 1098 h | 1098 h | 1098 h | 13929 | 10167/10682 pièces imprimables ; 100 % des plots à plat ; ponts sous tuiles |
| 2. Modules multicolores (9) | 9 | voir ci-dessous (+supports) | — | — | 5519 dont supports 69 | 4031 colour-changes ; 8 module(s) dépassent 4 couleurs par couche |
| 3. Pièces monochromes assemblées | 43 | 208 h | — | — | 7028 | 594 pièces à assembler ; supports +124 g |

### Modules (procédé 2) — mesures par module
| Module | Couleurs | Max couleurs / couche | Changements de couleur (couches 0,2 mm) | Pièces connexes | Temps A1 sans supports | **fusionné** sans / avec supports (h) | **fusionné** g sans / avec | Avert. |
|---|---|---|---|---|---|---|---|---|
| module_0_0_0.3mf | 5 | 3 | 211 | 29 | 17.8 h (objets séparés) | 12.3 / 12.9 | 557 / 566 | Floating bridge anchors, Long bridging extrusions; [2026-11- |
| module_0_0_1.3mf | 10 | 5 | 489 | 106 | 28.0 h (objets séparés) | 14.5 / 15.3 | 660 / 667 | Floating bridge anchors; Floating object part; Long bridging |
| module_0_0_2.3mf | 8 | 5 | 420 | 58 | 24.3 h (objets séparés) | 15.1 / 15.9 | 681 / 691 | Floating bridge anchors, Long bridging extrusions; Floating  |
| module_1_0_0.3mf | 12 | 7 | 568 | 58 | 20.2 h (objets séparés) | 12.4 / 12.9 | 537 / 543 | Floating bridge anchors, Long bridging extrusions; Floating  |
| module_1_0_1.3mf | 11 | 5 | 394 | 71 | 18.4 h (objets séparés) | 11.1 / 11.6 | 502 / 506 | Floating bridge anchors, Loose extrusions; Floating object p |
| module_1_0_2.3mf | 10 | 6 | 600 | 83 | 23.5 h (objets séparés) | 15.1 / 15.7 | 669 / 675 | Floating bridge anchors; Floating object part; Long bridging |
| module_2_0_0.3mf | 10 | 5 | 342 | 49 | 21.1 h (objets séparés) | 14.2 / 14.9 | 594 / 603 | Floating bridge anchors; Floating object part, Floating brid |
| module_2_0_1.3mf | 10 | 6 | 551 | 67 | 23.7 h (objets séparés) | 14.3 / 15.0 | 595 / 602 | Floating bridge anchors, Loose extrusions, Long bridging ext |
| module_2_0_2.3mf | 10 | 5 | 456 | 73 | 23.5 h (objets séparés) | 14.6 / 15.3 | 655 / 664 | Floating object part, Floating bridge anchors, Long bridging |

## Constats mesurés
- **Aucun module ne se tranche sans avertissement de ponts/pièces flottantes.** Supports (45°) mesurés sur modules **fusionnés en un solide** (le tranchage en objets séparés surestime les supports : conflits de chemins entre corps) : Paco +63 % de masse (1 084 → 1 764 g), Hyrule +1 % (5 450 → 5 519 g).
- **Paco : 5 à 6 couleurs par module, jusqu'à 5 simultanées dans une même couche ; Hyrule : 5 à 12 couleurs, jusqu'à 7 simultanées.** Une machine à 4 emplacements ne peut donc pas imprimer ces modules en une passe.
- Les temps de tranchage sous profil proxy sont **≈ 3× supérieurs** aux estimations par formule de `BAMBU_EXPORT.md` (Paco briques : formule 53 h, tranché ≈ 160 h ; Hyrule : 395 h → ≈ 1 200 h).
- Aucune différence de temps significative entre machines n'apparaît sur les plaques monochromes : sous profil proxy commun, la différence vient presque uniquement de l'accélération, et la vitesse réelle de chaque firmware **n'a pas été mesurée**.
