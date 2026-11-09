# Clôture V16 — Non-régression finale (commit `f962b6a`)

Exécutée sur la tête de branche `f962b6a` (arbre propre, voir `regression/commit.txt`) par `regression/closure_reg.sh` ; un journal par étape dans `regression/` (commande en tête, code de sortie et durée en pied). Moteur : `20_portable_engine` (venv épinglé). Aucune référence CI modifiée.

| # | Contrôle | Commande (résumé) | Résultat | Preuve |
|---|---|---|---|---|
| 1 | GLB d'entrée = références | `tests/check_regression.py glb` | **PASS** (exit 0) | `01_glb_inputs.log` |
| 2 | Tests unitaires du moteur | `tests/test_unit.py` | **PASS** 9/9 avec le python du venv moteur (scipy présent) ; **1re tentative en échec** avec le `python3` système (`ModuleNotFoundError: scipy`, le CI installe numpy/pillow/scipy avant) | `02_unit.log`, `02_unit_attempt1_system_python_no_scipy.log` |
| 3 | Tests moteur V16 | `tests/test_engine_v16.py` | **PASS** 2/2 | `03_engine_v16.log` |
| 4 | LEGO Maps, 8 baselines | `sprint_v16/baseline_maps_build.sh` → `check_regression.py maps` | **PASS** 8/8 IDENTICAL : italia 17d9bdc6…, ecosse 84c47d38…, japon ac3134cd…, royaume_uni 3abcc72e…, protoA 6545a26d…, protoB 35d8ae4e…, hyrule 721b8573…, hyrule_biomes 5afb9ac8… | `04_maps_8_baselines.log` |
| 5 | Builder unifié, carte (geo Italie) | `python -m lego_builder geo …italia…` | **PASS** : 13 633 pièces, validé ; SHA identique à la baseline `italia` (17d9bdc6…) | `05_builder_geo_italy.log`, `artefact_sha256.txt` |
| 6–7 | Sculpture Paco (GLB → LEGO) | `lego_builder run paco.glb` + `check_regression.py sculpture paco` | **PASS** : 3 193 pièces, **IDENTICAL 9d07c041a496** (V12.1) | `06`, `07` |
| 8–9 | Sculpture Beagle | `lego_builder run beagle.glb` + `check_regression.py sculpture beagle` | **PASS** : 10 567 pièces, **IDENTICAL 551bde0f77f2** (V12.1) | `08`, `09` |
| 10–12 | **Photos → 3D → LEGO** | 4 photos de Paco → service Hugging Face Space (Hunyuan3D-2mv) → GLB → LEGO | **PASS** (service accessible ; `gradio_client` installé dans `/tmp/gradio_site`, hors dépôt) : GLB reconstruit **identique** au GLB de référence (115 868 sommets, 231 740 faces, couleurs identiques : True) ; LDraw **IDENTICAL 9d07c041a496** | `10`, `11`, `12` |

SHA-256 complets des artefacts reconstruits (`regression/artefact_sha256.txt`) :
`17d9bdc60637614404494517c1736906ec238b1310257f2f9563d7c750cd776f` (Italie), `9d07c041a4968245228c016c651fef0710fd26fee68f67eac771df261c28089a` (Paco, GLB et photos), `551bde0f77f20c227b4c4fde7f9c286c32139c4c6ac2b458edc0b8cedf31808f` (Beagle).

## Blocages et limites
- **Le blocage « Photos→3D » de la clôture V16 est levé** : il venait d'un module Python absent (`gradio_client`) du venv, pas du service. Le service externe était accessible au moment du test ; ce résultat dépend de sa disponibilité (reconstruction à graine fixe, résultat identique ici).
- Le test d'impression 3D (STL/3MF, tranchage) n'est pas dans le périmètre demandé et n'a pas été rejoué.
- Le CI GitHub n'a pas été relancé dans cette clôture (exécutions locales uniquement) ; aucun PASS CI n'est déclaré.
- Les tests ci-dessus portent sur `f962b6a` ; les nouveaux outils d'analyse de la clôture (`tools/*_v16.py`) ne modifient ni le moteur ni les références.
