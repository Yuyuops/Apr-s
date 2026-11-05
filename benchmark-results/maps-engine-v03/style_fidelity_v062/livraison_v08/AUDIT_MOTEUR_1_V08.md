# Moteur 1 — audit et amélioration (V0.8)
Branche `research/lego-maps-premium-feasible-v08` (base : `research/lego-maps-v07-engine2-final`, commit de préparation `bda7aec` ; le commit de livraison est le dernier de la branche). Workflow CI `lego-maps-premium-feasible.yml` : run n°1 réussi (artefact récupéré, 2 styles initiaux validés 0/0/0/0). Génération locale reproductible : `build_style.py STYLE COMPOSITION OUT --flank vertical` (7 à 8 s par carte), puis `check_render.py --no-render`, `verify_bom.py`, `render_views.py`, `fragility.py`, `notice_steps.py`, `make_step_pdf.py`. Données : Natural Earth admin-0 10 m (domaine public, commit épinglé).
Branche de correction distincte : `research/lego-maps-engine1-fragility-v08`.

## Références (modèles finaux)
| Carte | Pièces | 1 tenon | dont porteuses | Points d'articulation | Pire défaillance |
|---|---:|---:|---:|---:|---|
| Italie | 13 633 | 1 092 | 408 | 976 | 28 pièces, 5,7 g |
| Écosse | 13 676 | 1 108 | 402 | 975 | 4 pièces, 6,4 g (cadre) |
| Japon | 11 477 | 1 216 | 476 | 1 066 | 11 pièces, 2,7 g |
| Royaume-Uni | 13 228 | 1 157 | 411 | 1 003 | 8 pièces, 2,4 g |
(V0.7 Italie : 13 816 pièces, 1 053, 390, 928. Le nouveau style a plus d'îlots à un tenon et de petites pièces ; valeurs indicatives, non physiques.)

## Amélioration démontrée : vitesse de l'analyse de fragilité
Cause : `subtree_mass` copiait le graphe entier (13 k nœuds, 80 k liens) pour chacun des ~1 000 points d'articulation. Correction : parcours en largeur qui saute le nœud testé, sans copie, et même ordre de sommation.
| | Avant | Après |
|---|---:|---:|
| Italie (13 633 pièces) | 107 s | **23 s** (×4,6) |
| Japon (11 477 pièces) | 85 s | **21 s** (×4,0) |
Sorties **identiques octet à octet** (`fragility.json` et `joints_per_part.json`, Italie et Japon). Aucun effet sur le modèle ni sur l'esthétique. Fichier : `fragility_fast.py` (remplace `fragility.py` sur la branche moteur 1).

## Non fait (documenté, pas implémenté)
- Réduction des porteuses à un tenon et des points d'articulation, supports de décors, optimisation du nombre de pièces, notices avec images 3D : aucune solution testée avec gain mesuré ; rien n'a été modifié dans le pavage, pour ne pas dégrader l'esthétique ni invalider les modèles.
- Le moteur 1 reste donc inchangé pour la constructibilité ; seule l'analyse est accélérée.
