# LEGO Maps V0.3 — correction des supports faibles

Branche isolée : research/lego-maps-v03-chatgpt-20261103.
Etat : sources implementees et tests unitaires prepares ; aucun resultat de generation V0.3 complet n'a encore ete verifie dans cette conversation.

Le moteur V0.2 a ete copie sous engine/ via les memes blobs Git, sans modifier ses archives. Les modules nouveaux sont engine/maps_engine/support_opt.py et engine/run_v03.py. Les tests sont dans tests/test_support_opt.py.

L'optimiseur reconstruit le graphe des pieces en appui, detecte les porteuses de moins de 4 tenons, puis explore le repavage local (2 ou 3 pieces) sur les couches affectees. Les nouveaux arrangements doivent utiliser des plaques du catalogue dans la vraie couleur, conserver exactement l'occupation, le relief, les couleurs, les formes speciales et la mise en page. Le resultat est accompagne d'un rapport avant/apres et d'une liste de blocages locaux. Un blocage local ne vaut pas preuve d'impossibilite physique.

## Tests

Depuis benchmark-results/maps-engine-v03, avec le Python de l'environnement V11 :

    ../20_portable_engine/.venv/bin/python tests/test_support_opt.py

Generer l'Ecosse en 32x32 sans traitement lourd :

    ../20_portable_engine/.venv/bin/python engine/run_v03.py generate --input ../maps-engine-v02/fixtures/ecosse_carte.png --out results/ecosse/A_32 --finish A --n 32

Lancer la suite de cinq cartes :

    bash run_all.sh --generate

Pour LDraw, BOM, rendus, viewer, notice, validation du moteur 1 :

    bash run_all.sh --full

Le runner utilise les dependances LDraw/Rebrickable installees pour V11. Les blobs Git LFS doivent etre telecharges. Le code ne touche pas aux autres moteurs ni aux references V0, V0.1, V0.2.

## References V0.2

- Ecosse 32x32 : 301 pieces, 44 porteuses faibles, 17 critiques.
- Ecosse 48x48 : 487 pieces, 44 porteuses faibles, 19 critiques.
- Ile temoin : 224 pieces, 12 porteuses faibles, zero critique.
- Trois zones : 166 pieces, 6 porteuses faibles, zero critique.
- Cinquieme carte : nouvel archipel fictif original, jamais utilise pour les corrections.

La mise en production ou l'accrochage mural sont interdits sans essai physique. Aucun prix ni stock n'est invente. La verite commerciale reste exclusivement Briquestore, non verifiee ici.

Le prochain verdict doit etre base sur les cinq rejeux, avec zero collision et deconnexion, control des portes critiques, difference de surface, nomenclature, notice et un budget pieces de +15 % maximum.

## V0.3 essais d'extension (sans compromis esthétique)

Le premier rejeu reel avec 3 passes a corrige l'Ecosse 32x32 (17 vers 13 critiques) et 48x48 (19 vers 13). Un essai conservateur local sur les memes `parts.json` a montre une amelioration additionnelle en autorisant 12 passes. Le CLI passe a 12 passes **sans changer les seuils**, avec la meme condition stricte d'amelioration lexicographique. Les nombres definitifs seront ceux de la CI avec catalogue valide et controle LDraw.
