# Sprint V14 — Rendu actuel de Hyrule (modèle réel du moteur, aucune image conceptuelle)

## Provenance
| Élément | Valeur |
|---|---|
| Modèle rendu | `benchmark-results/maps-engine-v03/style_fidelity_v062/livraison_v10/hyrule_biomes/diorama.ldr` (dernière version validée, celle exportée en V13) |
| SHA-256 | `5afb9ac8fe80f0089542e33ba639950251ce372d392512dbc29f777877a9ab8b` = entrée `hyrule_biomes` de `ci/reference_hashes.json` (**référence CI bloquante inchangée**) |
| Moteur | LEGO Maps V1.0 « biomes + relief » (style `premium_biomes_hyrule`, mode biomes, `frame_studs` 4, 467 coins arrondis), fichier généré au commit `5621e97` (2026-11-06) ; Builder unifié `f4c367e` ; dépôt au moment du rendu : `ae2f5d5806a49eab6b64766858b708a9df604377` |
| Pièces / références | **10 682 pièces, 134 références**, grille 80 × 80 plots, hauteur 21 plaques (67,2 mm) |
| Validation indépendante | all_pass = true, 0 collision, 0 pièce déconnectée, 0 îlot, 0 non supporté |
| Régénération | **non nécessaire** : le fichier est identique octet pour octet à la référence CI ; aucun fichier de référence n'a été modifié |
| Rendu | three.js sur les maillages LDraw réels et couleurs Rebrickable réelles (`render_views.py`), tailles 2000–2200 px ; vues dans `hyrule_render/views_main.json` et `views_extra.json` |
| Note | la variante `e2e_results/B_hyrule_*` (Hyrule produit depuis l'image par le Builder unifié) est un autre fichier (autre SHA) ; elle n'a pas été rendue ici |

## Images (`benchmark-results/lego-builder/sprint_v14/hyrule_render/`)
| Vue | Fichier | Taille |
|---|---|---|
| Face complète | `hyrule_face.jpg` | 2000 × 2000 |
| Trois-quarts | `hyrule_trois_quarts.jpg` | 2200 × 1500 |
| Latérale (relief) | `hyrule_lateral_relief.jpg` | 2200 × 1100 |
| Gros plan littoral (rives nord-ouest, eau/roche/herbe) | `hyrule_littoral.jpg` | 2000 × 1500 |
| Gros plan littoral sud-est | `hyrule_littoral_sud_est.jpg` | 2000 × 1500 |
| LEGO vs modules imprimables (9 modules 3MF V13 « shape-aware », ombrage plat) | `hyrule_lego_vs_modules.jpg` | 2200 × 2000 |

## Lecture critique de l'esthétique (honnête)
- Les couleurs et la composition sont celles du moteur ; le relief est **faible** (3 niveaux de roche, 21 plaques max) : la vue latérale montre surtout le cadre, le relief est peu lisible de profil.
- Défauts visibles : plages de vert uniformes très étendues, rochers gris épars, littoral réduit à quelques cases d'eau bleu clair (plus d'eau « intérieure » que de vrai rivage) ; le bleu des océans est clair/plat.
- Points forts : arrondis (quarts de rond) bien visibles en gros plan, cadre doré/brun propre, lettrage lisible.
- Modules imprimables : mêmes couleurs, mêmes courbes (arrondis conservés), mais **pas de joints de briques ni de plots visibles de dessus** à ce niveau de rendu ; les 9 modules sont séparés par des joints de 6 mm ajoutés pour la visualisation.
