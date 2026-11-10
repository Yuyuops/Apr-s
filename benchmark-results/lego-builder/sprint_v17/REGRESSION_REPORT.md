# Sprint V17 — Non-régression (commit `bac6138`, code fonctionnel de V17)

Exécutée par `regression/v17_reg.sh` ; un journal par étape dans `regression/` (commande, code de sortie, durée). Arbre propre hors documents. Références CI **non modifiées** (`ci/reference_hashes.json` intact).

| Contrôle | Commande (résumé) | Résultat |
|---|---|---|
| GLB d'entrée | `tests/check_regression.py glb` | **PASS** |
| Tests unitaires | `tests/test_unit.py` (python du moteur) | **PASS** 9/9 |
| Tests moteur V16 | `tests/test_engine_v16.py` | **PASS** 2/2 |
| **Tests objets V17** | `tests/test_objects_v17.py` | **PASS** : 12 assemblages validés par le validateur indépendant ; construction de la zone D reproductible (SHA-256 `0364fdd1e2eb…` ×2) |
| **LEGO Maps, 8 baselines** (objets désactivés par défaut) | `sprint_v16/baseline_maps_build.sh` | **PASS 8/8 IDENTICAL** (italia 17d9bdc6…, ecosse 84c47d38…, japon ac3134cd…, royaume_uni 3abcc72e…, protoA 6545a26d…, protoB 35d8ae4e…, hyrule 721b8573…, hyrule_biomes 5afb9ac8…) |
| Builder unifié, Italie (geo) | `python -m lego_builder geo …` | **PASS** : SHA identique à la baseline `italia` (17d9bdc6…) |
| Sculpture Paco (GLB) | `lego_builder run paco.glb` + `check_regression.py sculpture` | **PASS** IDENTICAL 9d07c041a496 |
| Sculpture Beagle | idem | **PASS** IDENTICAL 551bde0f77f2 |
| **Photos → 3D → LEGO** | `lego_builder run --photos …` (service Hugging Face Space) | **BLOCKED** : `AppError: You have exceeded your ZeroGPU quota (60s requested vs. 56s left). Try again in 7:28:02` (quota gratuit du service externe épuisé par les exécutions de la veille). **Non exécuté, aucun PASS déclaré.** Dernier PASS vérifié : clôture V16 sur `f962b6a` (GLB reconstruit identique, Paco IDENTICAL). V17 ne modifie pas ce chemin de code (seul `build_style.py` des cartes change, sous options désactivées par défaut). |
| CI GitHub | non relancé | aucun PASS CI déclaré |
SHA-256 des artefacts : `regression/artefact_sha256.txt` ; SHA-256 des livrables V17 : `SHA256SUMS.txt`.
