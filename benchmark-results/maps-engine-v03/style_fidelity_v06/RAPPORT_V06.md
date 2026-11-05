# LEGO Maps V0.6 — Style Fidelity : premier cycle, style A (Italia Prestige)
Branche `research/lego-maps-v06-style-fidelity`. Aucun achat, moteur 1 inchangé, pas de fusion dans `main`, aucun essai physique. Monuments désactivés (non utilisés). Rendus = géométrie LDraw réelle.

## Ce qui a été construit (nouvelle architecture)
`géographie (geodata.py) → composition (compositions/*.json) → strates (strata.py) → style (styles/*.json) → pavage → validations`.
- **Styles paramétrables** `styles/italia_prestige.json` et `styles/atlas_natural.json` (palette, relief, strates, finition, cadre, titre, décor) ; aucune règle propre à l'Italie dans le code ; composition en portrait indépendante du style (`compositions/italia_portrait_64x96.json`, échelle identique en latitude et longitude : aucune déformation des côtes).
- **Générateur de strates côtières** : distance à la terre (sujet + voisins) sur trame fine 8 sous-tenons, lissage gaussien, bruit basse fréquence (boucles/baies), nettoyage morphologique, niveaux emboîtés, suppression des marches isolées.
- **Surfaces** : plaques/tuiles à pavage conscient des appuis, tuiles 2×N favorisées, orientation cohérente ; **pas de substitution silencieuse de couleur** (erreur si un couple pièce/couleur n'est pas catalogué).
- **Cadre blanc épais**, coins ornés (plaques rondes/plaques or 297), **titre ITALIA en lettres surélevées** (tuiles), drapeau en tuiles. Style B : fichier de style prêt, **non généré** (voir verdict).

## Cycles (même caméra, même échelle : `comparatifs/`, `results/A_prestige_64x96/`)
| Cycle | Observé | Changement | Effet réel |
|---|---|---|---|
| 1 | strates plates (2 plaques), grands aplats gris-vert, titre absent | — | référence de départ |
| 2 | strates 3 plaques / 4 largeurs plus serrées, tuiles groupées | relief visible en trois-quarts, profondeur lisible ; **titre toujours absent** (aucune bande de mer libre de 37×9) | gain de relief, 12 651 pièces |
| 3 | titre autorisé sur la terre voisine plate (haut du tableau) | **ITALIA lisible**, cadre/ornements/drapeau en place | 12 881 pièces, 112 références |

## Évaluation (0-5) — observations vérifiables sur `comparatifs/A_reference_vs_cycle3.png`
| Critère | Note | Observation |
|---|---|---|
| Composition | 3 | portrait, terre grande, titre en haut, marges équilibrées ; mais pas d'étagère décorative, trop de mer vide au sud-est |
| Silhouette | 2 | **contours en escalier de 1 tenon** (maille 64×96), loin des courbes lisses de la référence ; Corse/Sardaigne grossières |
| Relief | 3 | 4 strates emboîtées qui épousent la côte avec baies et lobes ; mais flancs verticaux en briques de plaques, **pas de pentes courbes** : l'effet « terrasses » domine sur la douceur de la référence |
| Couleurs | 2 | terre et crème proches ; **le « turquoise » est un vert-gris terne** (Sand Green, ΔE ≈ 16 de la référence) : aucune couleur LEGO bien cataloguée n'est plus proche → écart de teinte visible |
| Finition | 3 | cadre blanc propre, ornements et titre présents ; ornements dorés minuscules, pas de scrolls, pas de coins épais comme la référence |
**Total 13/25, un critère à 2 : la porte (20/25, aucun < 3) n'est PAS franchie.**

## Validation numérique du cycle 3
12 881 pièces, 112 références : **0 collision, 0 déconnectée, 0 îlot, 0 pose sans appui, 0 tenon bloqué** ; LDraw = JSON = nomenclature ; 112/112 couples catalogués. Fragilité mesurée sur le cycle 2 (12 651 pièces) : 644 pièces à un tenon (390 porteuses), 818 points d'articulation, masse cumulée des cascades 279 g, pire défaillance 6,4 g (4 pièces). Cycle 3 non re-mesuré (ajout titre/ornements seulement). Aucun essai physique ; accrochage non évalué.

## Causes et alternative proposée (après deux cycles sans gain sur silhouette/couleur)
1. **Résolution de la maille** : à 64×96 tenons les côtes sont forcément en marches de 8 mm ; la référence cache ses marches avec des strates plus épaisses et des pièces de pente/arrondies. Alternative : traiter l'arrondi des **niveaux supérieurs** (terre et bande côtière) avec des pièces d'angle et de bord arrondi vérifiées (plaque 2×2 coin arrondi 26601, tuile coin arrondi 25269, plaque 3×3 à coin arrondi 30357, pentes courbes 11477/15068/93273), en pavant sur un contour sous-tenon plutôt que sur la grille entière.
2. **Teinte** : tester la couleur de sol à fort pourcentage de blanc (White 15) et Light Aqua 323 en alternance, ou accepter Sand Green et le déclarer ; une commande de couleur spéciale n'est pas possible sans vérification de stock.
3. **Pas d'extension de résolution** pour masquer ces défauts (consigne respectée).

## Décision
Verdict V0.6 intermédiaire : **GO AVEC LIMITATIONS refusé ; état = NO-GO partiel du style A à 64×96, à corriger avant d'augmenter la taille.** L'Italie complète 128×192, le style B (pipeline présent mais non rendu) et le Royaume-Uni n'ont **pas** été lancés : la porte artistique n'est pas franchie, et la consigne interdit de les produire dans ce cas. Notice détaillée et rendus haute résolution : non produits.
