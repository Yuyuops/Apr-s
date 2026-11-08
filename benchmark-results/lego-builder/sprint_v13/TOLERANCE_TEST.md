# Sprint V13 — B4 : coupon de tolérance (à imprimer et mesurer par un humain)

**Ce coupon n'a PAS été imprimé. Rien ne prouve que les tolérances LEGO fonctionnent en FDM** ; il sert à trouver, sur *votre* imprimante et *votre* filament, quelles valeurs donnent un emboîtement correct. Fichiers : `tolerance_coupon/tolerance_coupon_plate.3mf` (une plaque, 140 × 112 mm, 22 pièces), STL individuels, `coupon.json` (paramètres). Générateur : `python -m lego_builder.print3d.coupon OUT`. Tranchage indépendant PrusaSlicer : 2 h 29, 20,5 g (≠ Bambu Studio).

## Contenu
| Bloc | Pièces | Ce qu'il teste |
|---|---|---|
| A — plots / tube | 3 bases 2×2 à plots Ø 4,7 / 4,8 / 4,9 ; 5 capuchons 2×2 (tuile creuse à tube central) tube Ø ext. 6,3 / 6,4 / 6,5 / 6,6 / 6,7, **imprimés retournés** | 15 combinaisons à essayer à la main (le nominal LEGO 4,8 / 6,51 donne un jeu quasi nul : en FDM il faut trouver la valeur qui tient sans forcer ni jouer) |
| B — liaison de modules | 4 paires de blocs 20×20×10 avec douille r = 2,5 + 0,10 / 0,20 / 0,30 / 0,40 ; 4 tenons Ø 5,0 × 12 | jeu de la liaison module-à-module |
| C — détails courbes | pente 31° 1×1, pente 45° 1×2, tuile ronde 1×1, quart de rond 1×1 (enveloppe LDraw réelle) | netteté des arêtes et rayons vs nominal |
| D — jauge | marches de peau 0,8 / 1,0 / 1,2 / 1,6 / 2,0 mm ; boîte creuse parois 1,2 | ce que l'imprimante reproduit réellement |

## Protocole de mesure (à remplir)
Matériel : pied à coulisse 0,01 mm ; même filament et même profil que le futur tirage ; 0,2 mm, ≥ 3 périmètres ; refroidir, ébavurer sans lime.
1. Mesurer chaque plot (Ø, 2 axes), chaque tube (Ø ext.), chaque douille, chaque tenon ; noter l'écart au nominal.
2. Essayer les 15 couples base×capuchon : *impossible / dur (outil) / ferme (main, tient à l'envers) / lâche*. Retenir le couple « ferme » avec 3 démontages/remontages sans perte.
3. Liaison de modules : tenon dans chaque douille ; noter jeu et rigidité.
4. Détails courbes : comparer au nominal (pente 31°, rayon du quart de rond) ; noter déformations/escalier.
5. Jauge : plus fine peau fermée et paroi sans trous.

| Mesure | Nominal | Mesuré | Résultat |
|---|---|---|---|
| plot 4,7 / 4,8 / 4,9 | | | |
| tube 6,3 … 6,7 | | | |
| couple retenu (plot, tube) | | | |
| douille retenue (jeu) | 0,10 … 0,40 | | |
| peau mini fermée | 1,0 | | |

**Critère de passage** : au moins un couple plot/tube « ferme et répétable » ET une douille retenue ET détails courbes reconnaissables. Sinon : NO-GO fabrication complète (ajuster `stud_d`, `tube_od`, `socket_clear` dans `common.PARAMS` et recommencer). **Statut : BLOCKED — attend l'impression (intervention humaine).**
