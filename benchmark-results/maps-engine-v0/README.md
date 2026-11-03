# LEGO Maps — Moteur 2 / V0

**État : prototype V0 exécuté et évalué — verdict `results/VERDICT.md` : V0 AVEC LIMITATIONS.** Branche `research/lego-maps-v0-20261103`, issue du moteur 1 V12.1 (`dca6993`) ; ne pas fusionner dans `main`. Moteur 1 en lecture seule.

* Visualiser : `results/viewer.html` (rotation / zoom), `results/renders/` (face, profil, trois-quarts, rotations, zooms), `results/notice.pdf`.
* Lire : `results/RAPPORT_V0.md`, `results/VERDICT.md`. Essai 1 aveugle : `results/essai1/`.
* Relancer : `cd engine && LEGO_DEPS=<deps avec ldraw + rb.db> LEGO_NODE_MODULES=<node_modules three+playwright> python -m maps_engine.run_map full --input ../fixtures/ile_temoin.svg --out ../results [--mode 2d]` (dépend de `../20_portable_engine/engine` en lecture seule ; `python -m maps_engine.run_map generate` produit seulement LDraw + nomenclature).
* Prix / stock : Briquestore uniquement, **non vérifiés** (colonnes vides).
