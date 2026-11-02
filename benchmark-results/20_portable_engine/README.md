# 20 : moteur 1 portable et reproductible (LEGO V11)

Installation et exécution depuis un clone propre (aucun fichier de `~/bench`) :

```
git clone --branch research/lego-brickify-benchmark https://github.com/Yuyuops/Apr-s.git && cd Apr-s && git lfs pull --include="benchmark-results/02_glb_gratuit_hunyuan2mv/*.glb"
cd benchmark-results/20_portable_engine
bash scripts/install.sh                       # venv Python verrouille, modules Node, brickify / LDraw / Rebrickable aux versions fixees
.venv/bin/python engine/lego_run.py --glb ../02_glb_gratuit_hunyuan2mv/beagle.glb --subject subjects/beagle.json --out runs/beagle
.venv/bin/python engine/lego_run.py --glb ../02_glb_gratuit_hunyuan2mv/paco.glb   --subject subjects/paco.json   --out runs/paco
.venv/bin/python tests/compare_references.py beagle runs/beagle runs/beagle_compare.json
```

Commande standard : `lego_run.py --glb <chemin> --out <dossier> [--subject <config>] [--height-mm 400] [--palette-exclude 4,1,...] [--stop-after <etape>]`. La palette (couleurs LDraw exclues) est une **entrée** du sujet, comme pour brickify.

Voir `VERDICT.md`, `ARCHITECTURE.md`, `REPRODUCTION.md`, `AUDIT_FIDELITE_COULEURS_PLACEMENT.md`.
