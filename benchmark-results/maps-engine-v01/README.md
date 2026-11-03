# LEGO Maps — V0.1 : du prototype au tableau décoratif

Base : V0 (`../maps-engine-v0/`, commit 2456d1a, intact). Moteur 1 en lecture seule. **Verdict : `results/VERDICT.md` (V0.1 AVEC LIMITATIONS).**
* Voir : `results/comparatifs/` (A / B côte à côte), `results/ile_temoin/{A,B}/viewer.html` (rotation, zoom, clic = référence), `results/ile_temoin/{A,B}/notice.pdf`, `results/ile_temoin/{A,B}/renders/`.
* Lire : `results/RAPPORT_V01.md`, `results/tableaux_mesures.md`, `audit_v0/AUDIT_VISUEL_V0.md`, `results/controles/`.
* Dossiers de sortie : `results/ile_temoin/{A, B, A_sans_coins_coupes, A_48x48}`, `results/test_3_zones/{A, B}` ; chacun contient `map.ldr`, `parts_list.csv`, `parts.json`, `notice.pdf`, `viewer.html`, `renders/`, `validation/`, `etapes.json`.
* Relancer : `LEGO_DEPS=<ldraw + rb.db> LEGO_NODE_MODULES=<three + playwright> PY=<python> ./run_all.sh` puis `python engine/compare_all.py`, `engine/verify_outputs.py`, `engine/fragile_structure.py`, `engine/wall_load.py`, `engine/make_report.py`.
* Prix / stock : Briquestore uniquement, **non vérifiés** (colonnes vides).
