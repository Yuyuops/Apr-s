# Essai 1 — premier essai aveugle (archivé avant tout ajustement)

* Entrée : `results/input/ile_temoin.png` (rastérisation Chromium de `fixtures/ile_temoin.svg`) — **l'image seule**.
* L'oracle `fixtures/ile_temoin_oracle.json` et `scripts/make_fixture.py` (qui écrit une heightmap de contrôle) **n'ont pas été ouverts ni exécutés** avant la génération ; l'oracle n'est lu qu'après, pour l'évaluation.
* Commande : `python -m maps_engine.run_map generate --input ../results/input/ile_temoin.png --out ../results/essai1 --mode 2.5d` (moteur 2 tel que commité dans le même commit ; empreinte des sources du moteur : `d9416560b6d2dd03`).
* Contenu : `map.ldr`, `parts_list.csv`, `parts.json`, `classes_hauteurs.json` (classes inférées, hauteurs, couleurs LEGO choisies), `generation.json`.
* Ce dossier n'est **pas modifié** par la suite : les corrections éventuelles du moteur sont évaluées dans `results/` (sorties finales).
