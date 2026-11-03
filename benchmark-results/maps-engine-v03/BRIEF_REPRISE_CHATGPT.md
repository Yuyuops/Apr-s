# LEGO Maps V0.3 — reprise technique ChatGPT

Statut : **diagnostic initial uniquement**, aucune modification du moteur de génération et aucun test de régression exécuté dans ce commit.

Base source : `research/lego-maps-v0-20261103`, commit `f672fc2a391296e75505eb2dab862d5179f6d456`.
Branche isolée de travail : `research/lego-maps-v03-chatgpt-20261103`.
Finition retenue : **A corrigée V0.2**. Ne pas modifier le moteur 1, les archives V0/V0.1/V0.2 ni les GLB.

## Données inspectées et reproduites

En recalculant le graphe de supports depuis les `parts.json` du modèle Écosse, avec la même règle que `maps-engine-v02/engine/frag.py` :
- 32×32 : 301 pièces, 44 porteuses faibles, **17 critiques**.
- 48×48 : 487 pièces, 44 porteuses faibles, **19 critiques**.
- En 32×32, concentration des critiques : forêt 8, village 4, colline 4, rivière 1.
- Les pièces typiques sont des plaques 1×1, 1×2, 1×3 attachées par 1 à 3 tenons et servant de **seul support** à au moins une pièce enfant.

Fichier de détail : `references/baseline_scotland.json` — liste des IDs, régions, niveaux, positions et pièces uniquement supportées par une porteuse critique.

Ce contrôle valide les **comptages**, pas la tenue en cisaillement ni la résistance physique. `frag.py` est une heuristique de graphe; il faut garder la validation indépendante du moteur 1.

## Hypothèse testable

Le pavage actuel `engine/maps_engine/tiling.py` maximise essentiellement surface couverte, faible fragmentation et joints décalés. Il ne pénalise **pas suffisamment la création d'un support exclusif** sur la couche supérieure. Des détails fins deviennent ainsi structurellement dépendants d'une seule plaque.

## Ordre d'implémentation V0.3

1. **Baseline gelée** : comparer cinq sorties avec la même version de la base technique et du validateur. Zéro patch sur les données de référence. Vérifier les scripts `run_all.sh`, `frag.py`, `verify_outputs.py` et leurs chemins.
2. **Graphe de dépendances** : créer un contrôle de support juste après chaque couche et avant d'accepter le pavage suivant. Calculer les supports directs/exclusifs, liaisons, tenons et connexion au noyau; conserver la distinction feuille / porteuse.
3. **Optimisation locale** : explorer pavages alternatifs de la couche porteuse ET de la couche portée (fenêtre limitée), en conservant occupation, couleurs visibles et relief; inclure une pénalisation très forte des nouvelles porteuses critiques, avant le nombre total de pièces. Préférer un support multiple réel, pas une astuce de décompte.
4. **Renfort invisible** : si le pavage seul ne résout pas un point, tester un pont caché existant et montable. Chaque changement doit repasser collisions, connexions, appui, notice, disponibilité pièce×couleur.
5. **Cas impossibles** : si la géométrie impose un support unique et qu'aucune solution LEGO réelle n'existe, produire un certificat de blocage local avec coordonnées et coût potentiel d'un ajustement esthétique. **Ne jamais déclarer zéro critique par changement de seuil.**
6. **Rejouer cinq cas** : île 32×32, carte trois zones, Écosse 32×32, Écosse 48×48 et nouvelle carte indépendante avec licence. Comparer IoU, contours, ΔE2000, collisions, porteuses critiques, points d'articulation, pièces, masse, étapes et temps de génération.
7. **Étude murale / viewer** : mettre à jour les scripts hérités V0.1 qui pointent encore vers les anciens dossiers. Ne déclarer aucune sécurité physique sans essai réel.

## Conditions de décision

- Cible : **0 porteuse critique** sur les tests lorsque constructible sans dégrader l'image, ou démonstration détaillée des cas irréductibles.
- **0 collision, 0 déconnexion**, aucune disparition d'île ou d'autre zone essentielle.
- Effort pièces : **≤ +15 %** sur chaque référence V0.2, sinon documenter l'arbitrage.
- Verdict technique et résultat réel reproductible avant toute nouvelle finition.
- Aucun achat, aucune fusion dans main, aucun travail moteur 1, aucun prix/stock inventé.

## Environnement d'exécution

Le connecteur GitHub permet de lire/écrire les fichiers et d'auditer les sorties, mais l'environnement de terminal de cette conversation ne peut pas cloner directement GitHub (DNS inaccessible). **Exécuter les tests du projet dans ChatGPT Work**, environnement muni d'un ordinateur/navigateur connecté et de l'accès GitHub, ou sur un runner autorisé; aucun test du moteur V0.3 n'a encore été réalisé.
