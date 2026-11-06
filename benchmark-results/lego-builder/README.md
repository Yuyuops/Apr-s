# LEGO Builder : de l'image au modèle LEGO vérifié
```
export LEGO_ENGINE_HOME=<install du moteur 1 : venv, .deps, node_modules>   # voir benchmark-results/20_portable_engine/README.md
export PYTHONPATH=benchmark-results/lego-builder:benchmark-results/maps-engine-v03/style_fidelity_v062
PY=$LEGO_ENGINE_HOME/.venv/bin/python

$PY -m lego_builder analyze  ma_carte.jpg                                  # quel type de construction ?
$PY -m lego_builder run      ma_carte.jpg  --out projets/ma_carte --size-mm 400 --title MONPAYS
$PY -m lego_builder run      mon_chien.glb --out projets/chien   --size-mm 400
$PY -m lego_builder geo --composition COMP.json --style STYLE.json --out projets/italie   # carte géographique réelle
$PY -m lego_builder check    projets/ma_carte                                # manifeste strict
```
Résultat dans `projets/<nom>/` : `source/` (original intact), `derived/` (classes, composition, style, aperçu), `analysis.json`, `manifest.json`, `model/` (`diorama.ldr`, `parts_list.csv`, validations, rendus, plan de montage). `--pdf` ajoute la notice PDF des cartes.
Documentation : `ARCHITECTURE_AUDIT.md`, `LEGO_CORE_DESIGN.md`, `IMAGE_INGESTION.md`, `GENERATOR_INTERFACES.md`, `END_TO_END_TESTS.md`, `FINAL_VERDICT.md`. Les images sources de tiers ne sont pas redistribuées.
