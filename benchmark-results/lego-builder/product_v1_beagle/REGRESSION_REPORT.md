# Product V1 Beagle — Non-régression

Exécutée par `tools/product_regression_v1.sh` sur le commit `7d8d4e7` (moteurs **non modifiés** ; seuls des outils `tools/*_v1.py` et des documents ont été ajoutés) ; un journal par étape dans `regression/` (commande, code de sortie, durée). Références CI non modifiées.

| Contrôle | Résultat | Preuve |
|---|---|---|
| GLB d'entrée = références | **PASS** (exit 0) | `01_glb_inputs.log` |
| Tests unitaires du moteur | **PASS** 9/9 | `02_unit.log` |
| Tests moteur V16 et objets V17 | **PASS** 2/2 ; 12 assemblages validés + zone reproductible | `03_*`, `03b_*` |
| **LEGO Maps, 8 baselines** | **PASS 8/8 IDENTICAL** (italia 17d9bdc6…, ecosse, japon, royaume_uni, protoA, protoB, hyrule 721b8573…, hyrule_biomes 5afb9ac8…) | `04_maps_8_baselines.log` |
| **Builder unifié** (carte Italie) | **PASS** SHA identique à la baseline `italia` | `05`, `artefact_sha256.txt` |
| **Paco** (GLB → LEGO) | **PASS IDENTICAL 9d07c041a496** (V12.1) | `06`, `07` |
| **Beagle** (GLB → LEGO) | **PASS IDENTICAL 551bde0f77f2** (V12.1) ; 10 567 pièces, 64 références | `08`, `09` |
| **Photos → 3D → LEGO** (Hugging Face Space) | **PASS** : service accessible ; GLB reconstruit identique au GLB de référence (115 868 sommets, 231 740 faces) ; Paco IDENTICAL 9d07c041a496 | `10`, `11`, `12` |
| Reproductibilité du Beagle depuis le ZIP livré | **PASS** : reconstruction depuis `beagle.glb` → SHA-256 identique | `validation/package_validation.json` (contrôle 8) |
Le CI GitHub n'a pas été relancé : aucun PASS CI déclaré. Photos → 3D dépend de la disponibilité du service externe (quota ZeroGPU) au moment du test.
