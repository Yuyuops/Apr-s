# Sprint V16 — Non-régression (preuves d'exécution)

| Contrôle | Commande / source | Résultat |
|---|---|---|
| 8 baselines LEGO Maps (après gel final du code) | `baseline_maps_build.sh` → `regression/maps_post_final.log` | **8/8 IDENTICAL** (italia 17d9bdc6…, ecosse 84c47d38…, japon ac3134cd…, royaume_uni 3abcc72e…, protoA 6545a26d…, protoB 35d8ae4e…, hyrule 721b8573…, hyrule_biomes 5afb9ac8…) « no regression » |
| Tests moteur V16 (options OFF par défaut, sans collision, déterministe) | `python -m unittest tests.test_engine_v16` | 2/2 OK (rejoué après les correctifs de repli) |
| Builder unifié : geo Italie | `regression/builder_post.log` | LDraw identique à la référence : **True** |
| Builder unifié : `run paco.glb` | idem | LDraw identique à Paco V12.1 accepté : **True** |
| Tests unitaires / sculpture / GLB / Paco / Beagle V12.1 | exécutés avant le gel final (voir `FINAL_VERDICT.md`) ; IDENTICAL | non rejoués après les 3 derniers correctifs de repli (limités à des chemins `wild`, désactivés par défaut) |
| Photos → 3D → LEGO | `lego_builder run --photos …` | **BLOCKED** : `ModuleNotFoundError: gradio_client` dans le venv moteur (et service HF Space externe requis). Non exécuté, aucun PASS déclaré. |
| Aucune référence CI gelée/modifiée ; aucune fusion dans `main` ; aucun achat | `git diff ci/reference_hashes.json` vide | OK |
