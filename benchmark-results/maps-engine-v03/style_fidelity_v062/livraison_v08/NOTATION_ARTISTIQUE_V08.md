# Notation artistique — grille Premium LEGO (V0.8)
Branche `research/lego-maps-premium-feasible-v08` (base : `research/lego-maps-v07-engine2-final`, commit de préparation `bda7aec` ; le commit de livraison est le dernier de la branche). Workflow CI `lego-maps-premium-feasible.yml` : run n°1 réussi (artefact récupéré, 2 styles initiaux validés 0/0/0/0). Génération locale reproductible : `build_style.py STYLE COMPOSITION OUT --flank vertical` (7 à 8 s par carte), puis `check_render.py --no-render`, `verify_bom.py`, `render_views.py`, `fragility.py`, `notice_steps.py`, `make_step_pdf.py`. Données : Natural Earth admin-0 10 m (domaine public, commit épinglé).

**Grille déclarée avant notation** (5 critères /5, total /25, objectif ≥ 20 sans critère < 3). Distincte de la note historique de fidélité à l'image d'origine : **15/25, inchangée**. Notes attribuées par moi après inspection des rendus (mêmes caméras pour toutes les cartes), sans relecture humaine indépendante : à confirmer visuellement.
Planches : `v08_face.png`, `v08_trois_quarts.png`, `v08_cycle1_face.png`, `v08_cycle2_*.png`, `v08_cartes2_{face,trois_quarts,zoom}.png`.

## Comparaison des variantes sur l'Italie
| Variante | Lisib. géo | Relief/hiérarchie | Harmonie couleurs | Cadre/typo | Esthétique | **Total** |
|---|---:|---:|---:|---:|---:|---:|
| V0.7 (référence, cadre blanc/or, mer Light Aqua/Aqua/Sand Green) | 4 | 3 | 3 | 4 | 3 | **17** |
| Ivoire/Or/Sauge (CI) | 4 | 3 | 3 | 3 | 3 | **16** |
| Noyer/Or/Lagon (CI) | 3 | 2 | 3 | 3 | 3 | **14** |
| Ivoire cycle 1 | 4 | 3 | 3 | 4 | 3 | **17** |
| Noyer cycle 1 (titre en haut, sans compas) | 4 | 3 | 4 | 4 | 3 | **18** |
| **Noyer cycle 2 + îlots (retenu)** | **4** | **3** | **4** | **4** | **4** | **19** |

Justifications du retenu : lisibilité 4 (péninsule, Sicile, Sardaigne et 4 îlots lisibles ; côte en escalier irréductible) ; relief 3 (strates de 3 plaques lisibles en oblique, mais en vue de face seule la teinte distingue les niveaux) ; harmonie 4 (noyer, or, sable, brun et lagon cohérents ; le Pale Blue reste un aplat) ; cadre/typo 4 (filets et médaillons or sur noyer, titre blanc propre depuis la suppression des tenons parasites) ; esthétique 4 (rendu sobre, sans élément artificiel). 
**Écart : 19/25 < 20. Le critère de sortie n'est pas atteint.** Deux cycles de correction ont été utilisés.

## Cycles (2 maximum)
1. **Cycle 1.** Hypothèses : (a) le titre du Noyer, placé en bas en crème, chevauchait terre et mer ; (b) les tenons visibles dans les contre-formes des lettres et le compas flou dégradaient la finition. Modifications : tenons de pose limités aux cellules des lettres (générique), titre en haut en blanc, plaque dorée à la place du compas. Résultat : Noyer 14 → 18, Ivoire 16 → 17. Accepté.
2. **Cycle 2.** Hypothèse : des strates de 3 plaques (avec contours organiques de l'Ivoire) rendent le relief plus lisible ; la plaque dorée sans inscription est retirée. Résultat : relief plus net en oblique, mais note de relief inchangée en vue de face ; esthétique 3 → 4. Accepté.
Correction générique ajoutée ensuite (hors cycles de style) : conservation des îlots (voir VALIDATION).

## Notes par géographie (style Noyer/Lagon, même moteur)
| Carte | Lisib. | Relief | Harmonie | Cadre/typo | Esthétique | **Total** | Défauts constatés |
|---|---:|---:|---:|---:|---:|---:|---|
| Italie 64×96 | 4 | 3 | 4 | 4 | 4 | **19** | escalier côtier ; relief de face faible |
| Écosse | 4 | 3 | 3 | 4 | 3 | **17** | Angleterre (GBR) en brun au sud ; mer bleue dominante ; Orcades/Shetland partielles |
| Japon | 4 | 3 | 4 | 3 | 4 | **18** | Ryukyu hors cadre ; glyphe J anguleux |
| Royaume-Uni | 4 | 3 | 3 | 4 | 3 | **17** | Shetland hors cadre ; titre « UK » petit ; mer monotone |
Aucune carte n'atteint 20/25. Aucune n'a de critère < 3.
