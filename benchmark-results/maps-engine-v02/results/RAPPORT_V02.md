# Rapport MAPS V0.2
Voir `VERDICT.md` pour la décision et les tableaux. Détails de méthode :

## Données
- `results/ile_temoin/{A_corrigee,H_mat1}`, `results/test_3_zones/{A_corrigee,H_mat1}`, `results/ecosse/{A_32,H_32,A_32_inscription,A_48}` : chacun contient map.ldr, parts_list.csv (BOM), notice.pdf, viewer.html, renders/, validation/, parts.json, etapes.json, generation.json.
- Références V0.1 inchangées : `../maps-engine-v01/results/…/A`.
- Comparatifs : `results/comparatifs/` (cote_a_cote_3_*.png = 1 A actuelle / 2 hybride / 3 nouvelle carte ; ile_A_vs_corrigee_vs_hybride_*.png ; zones_face.png ; ecosse_32_vs_48_face.png).
- Métriques de fragilité : `engine/frag.py` (porteuses < 4 tenons, critiques, 1 tenon, points d'articulation).

## Contrôles effectués (8 sorties)
LDraw = parts.json = BOM (nombre de pièces égal pour les 8) ; chaque pièce apparaît une fois dans les étapes ; ≤ 20 pièces par étape ; 0 collision, 0 déconnectée (validate) ; prix/stock Briquestore tous vides.
Non refaits en V0.2 : étude de charge murale et test de clic du viewer (scripts V0.1 non adaptés) ; viewers générés par le même code que V0.1.

## Hybride : ce qui a été essayé
Tuiles lisses sur mer/lac/rivière (`--smooth`), chape de cadre, bandes littorales, passe-partout (`--mat 1`). Les tuiles lisses de mer créent de petites plaques cachées au rivage (33 porteuses faibles sans passe-partout) ; avec mat 1 : 11. Tuiles lisses sur terre : écartées (laides, moins solides).

## Source de la 3ᵉ carte
Natural Earth (domaine public), script `fixtures/make_ecosse_map.py`, licence `fixtures/LICENCE_NATURAL_EARTH.md` (attribution donnée par courtoisie). Polygone des Grampians = région descriptive, non altitude.

## Correctif après gel du moteur
Un seul : l'hybride plantait quand une classe de tuiles lisses (ex. « lac ») était absente de la carte (`ValueError`) ; le filtre sur les classes présentes a été ajouté et H_32 relancé. Les premiers résultats A_32 / A_48 / A_32_inscription n'ont pas été modifiés.

## Limites
Masse ±30 % (estimation) ; aucune mesure physique ; disponibilité des couleurs = proxy Rebrickable (≥ 20 sets), pas un stock ; scripts annexes copiés de V0.1 (compare_all, verify_outputs, wall_load…) pointent encore vers les chemins V0.1.
