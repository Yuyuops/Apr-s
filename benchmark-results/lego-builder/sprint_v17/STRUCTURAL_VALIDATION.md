# Sprint V17 — Validation technique de la zone du château

Commandes : `build_style.py styles/hyrule_v17_objects.json compositions/hyrule_v17_zone_D.json … --flank vertical --no-title`, puis `check_render.py`, `verify_bom.py`, `fragility.py`, `validate_v4 --dump` + `tools/structural_classify_v16.py` + `tools/weaklink_v16.py` (mêmes définitions que la clôture V16). Génération : **≈ 45 s** (zone, objets inclus).

| Contrôle | V16 zone D | V17 zone D |
|---|---|---|
| Pièces / références | 1 750 / 104 | 1 950 / 136 |
| Collisions / pièces déconnectées / îlots / non supportées | 0 / 0 / 0 / 0 | **0 / 0 / 0 / 0** (`all_pass` True) |
| BOM | valide | **valide** : toutes les pièces/couleurs cataloguées, 0 paire hors catalogue |
| Génération reproductible | — | **oui** : 2 constructions → SHA-256 identique `0364fdd1e2eb…` (diorama.ldr de `D_v17b`) |

## Fragilité porteuse séparée de la fragilité décorative
| Catégorie (1 tenon) | V16 | V17 | Lecture |
|---|---|---|---|
| **C1 porteuses** (le retrait coupe ≥ 1 pièce) | 12 (coupure max 2) | 81 (coupure max 3) | surtout **troncs d'arbres** 3062b (24) et plaques 1×1 (56) : la couronne repose sur 1 tenon ; chaîne ≤ 3 pièces, ≤ 0,5 g |
| C2 décoratives captées | 146 | 157 | stable |
| C3 décoratives exposées | 232 | 271 | arbres/rochers/tours en saillie |
| Total 1 tenon | 390 (22,3 %) | 509 (26,1 %) | hausse due aux assemblages (arbres) |
| Liens faibles (≤ 2 tenons, coupant ≥ 4 pièces) | 0 | **2** (piliers 1×2 de 5 pièces, ≈ 0,4–1,8 g, type déjà vu en V16, hors objets) | |
| Liens moyens / forts | 0 / 43 | 12 / 52 | |
| Pire défaillance isolée (graphe) | 9 pièces | 12 pièces | plaque 3031 (4×4) retenue par ≥ 6 tenons, ce n'est pas un lien faible |
**Objets autonomes** (`OBJECT_LIBRARY.md`) : château 31 pièces, 8 pièces porteuses à 1 tenon (cônes de tourelles, coupure ≤ 2) ; tour 2×2 sans pièce à 1 tenon ; pont = 1 plaque sur 2 plots de berge ; **le pilier « monument » est fragile par conception** (non utilisé dans la zone).
Conclusion technique : aucun défaut de **structure** (0 collision/déconnexion/îlot, BOM valide) ; le risque ajouté est **décoratif ou local** (arbres, tourelles). Les chiffres sont numériques ; aucune mesure physique.
