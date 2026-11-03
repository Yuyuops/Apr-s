# Phase 1 — Audit visuel de V0 (avant toute modification)

Comparaison de `maps-engine-v0/results/` (commit 2456d1a, **non modifié**) avec l'image source `ile_temoin.svg` : figure `V0_source_vs_rendu.png`, mesures `couleurs_v0_reelles.json` et `ecarts_contours_v0.json`.

## Défaut n° 0 (le plus important, découvert pendant l'audit) : mauvaises valeurs de couleur
V0 a choisi et mesuré ses couleurs avec les valeurs de `LDConfig.ldr` de la bibliothèque LDraw installée, **qui ne sont pas les couleurs réelles des briques** (ex. LDraw « Tan » = #B0A06F, Rebrickable / LEGO « Tan » = #E4CD9E ; « Sand Green » #708E7C contre #A0BCAC ; « Blue » #1E5AA8 contre #0055BF ; « Dark Azure » #469BC3 contre #078BC9). Les ΔE rapportés par V0 (12,95) étaient donc faux pour de vraies briques et les rendus V0 sont plus sombres que la réalité. Avec les valeurs Rebrickable (table `colors` du catalogue technique) :
| classe | ΔE annoncé V0 (LDraw) | **ΔE réel** | commentaire |
|---|---|---|---|
| terre (Tan) | 18,4 | **1,5** | en réalité excellente |
| mer (Blue) | 8,8 | **26,4** | trop vive / trop claire |
| forêt (Sand Green) | 21,1 | **32,0** | gris-vert pâle, très peu contrasté |
| sommet (Light Bluish Gray) | 28,7 | **30,1** | gris clair, hors palette de la carte |
| colline (Dark Tan) | 13,1 | 15,8 | |
| lac / rivière | 5,4 / 10,4 | 15,3 / 20,5 | deux couleurs différentes pour un même bleu source (ΔE source 1,9) |
| village (Dark Orange) | 17,2 | 25,8 | |
| **moyenne pondérée surface** | 12,98 | **16,25** | |

## Défauts mesurés
1. **Contours grossiers** : déplacement moyen de la frontière 0,7 mm (côte) à 2,3 mm (rivière) et maximal 5,3–7,4 mm, c'est-à-dire < 1 tenon (8 mm) : escaliers visibles sur la côte, la colline et le lac. Limite de la résolution 32×32.
2. **Couleurs éloignées** : ΔE réel 16,25 (cf. tableau) ; l'**affectation injective** force un gris pour le sommet et un bleu distinct pour la rivière.
3. **Relief peu lisible** : 4 marches de 3,2 mm, sans variation de teinte ni de finition ; vu de dessus, forêt (ΔE LEGO 27 contre 43 dans la source) et terre se confondent plus que dans l'image.
4. **Zones qui se confondent / variations artificielles** : lac et rivière ΔE 12 dans V0 alors que la source les donne identiques (1,9) ; colline / sommet 19 (source 18, correct).
5. **Rivière et route pixelisées et trop épaisses** : 14 et 17 cellules ; surface 2,3 × et 1,7 × celle de la source (1 tenon = 8 mm contre ≈ 4,5 – 5 mm réels) ; la route est coupée par la rivière et par le village.
6. **Surface et bordures** : aucun cadre ; côtés = empilement visible de plaques de dos gris et de plaques bleues ; épaisseur 22,4 mm.
7. **Tenons visibles partout** (100 % de la surface), y compris sur les grandes zones plates de mer et de terre.
8. **Mécanique** : 9 plaques de relief tenues par 1 tenon, 25 points d'articulation, coupe minimale du noyau 2 tenons (une plaque feuille), alignement des joints entre couches 0,14 – 0,24 pour les trois premières couches de relief.
9. **Notice** : 15 étapes de 5 à 43 pièces (trop grosses), pas de séparation dos / relief / cadre.

## Conséquences pour V0.1
Couleurs : valeurs Rebrickable partout (mesure, choix, rendu, viewer) ; choix non injectif sous contrainte de lisibilité. Finitions : A (tenons apparents) et B (tuiles lisses sur les grands aplats, côtés finis) avec cadre. Rivière / route : mesurer la limite à 32×32 et comparer 48×48. Structure : joints décalés renforcés, pas de 1×1 évitable, cadre et bordures solidaires du dos. Notice : étapes ≤ 24 pièces, sections dos / relief / cadre.
