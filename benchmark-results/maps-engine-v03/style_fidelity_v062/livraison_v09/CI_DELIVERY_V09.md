# CI et chaîne de livraison V0.9
Branche `research/lego-maps-v09-prototype-hyrule` ; code et résultats au commit `2a8391b` (les rapports sont dans le commit suivant). Run CI de référence : https://github.com/Yuyuops/Apr-s/actions/runs/42094250651 (succès, 21 min).

## Ce que la CI exécute (`.github/workflows/lego-maps-v09-deliverables.yml`)
Un seul job reconstruit **de zéro** (checkout, installation épinglée du moteur 1, navigateur de rendu) les **quatre cartes finales** (Italie, Écosse, Japon, Royaume-Uni) et les **deux prototypes réduits** via `regen_deliverables.sh --render --pdf` : génération, validation indépendante du moteur 1, vérification BOM (catalogue), analyse de fragilité, plan de montage, rendus réels face / trois-quarts / zoom, notice PDF (tableau) et notice illustrée (prototypes), puis `check_delivery.py` :
- validateur : 0 collision, 0 déconnectée, 0 îlot, 0 non supportée ; 0 substitution de couleur ; 0 couple pièce/couleur non catalogué ;
- lignes LDraw = `parts.json` = `parts_list.csv` (par pièce/couleur) ; identifiants du plan de montage = identifiants du modèle.
Le job échoue si un contrôle échoue. Déclencheurs : push sur la branche (fichiers de code, styles, compositions) et lancement manuel. Un push de documentation seule ne relance pas la CI.

## Résultat du run de référence : **succès**
| Modèle | Pièces | Réf. | Concordance (`all_ok`) | LDraw identique à l'exécution locale |
|---|---:|---:|:---:|:---:|
| Italie | 13 633 | 111 | oui | oui |
| Écosse | 13 676 | 103 | oui | oui |
| Japon | 11 477 | 110 | oui | oui |
| Royaume-Uni | 13 228 | 105 | oui | oui |
| Prototype A | 3 489 | 85 | oui | oui |
| Prototype B | 2 658 | 101 | oui | oui |
**Reproductibilité inter-environnements démontrée** : les 6 fichiers LDraw produits sur le runner ont le même SHA-256 que ceux de mon exécution locale (`deliverables_manifest.json`). Cette comparaison est en rapport seul (elle n'échoue pas), mais le résultat est 0 écart sur 6.

## Artefacts de livraison
- `lego-maps-v09-light` (≈ 29 Mo, 30 jours) : manifeste, métriques, nomenclatures, validations, fragilité, `delivery_check.json`, LDraw et rendus.
- `lego-maps-v09-notices-pdf` (≈ 101 Mo, 30 jours) : notices tableau des 4 cartes et notices illustrées des 2 prototypes.

## Stockage des gros PDF : décision
- **Retenu** : les PDF ne sont **plus versionnés** (`*.pdf` ignoré ; les 4 PDF V0.8 retirés de l'arbre de la branche). Ils sont **publiés comme artefacts CI** et **régénérables** par une commande : `style_fidelity_v062/regen_deliverables.sh OUT --render --pdf` (avec `LEGO_ENGINE_HOME` : voir `env.sh`). Rien de nécessaire à la reconstruction n'est supprimé (scripts, styles, compositions, données Natural Earth épinglées, manifeste de hachages).
- **Raisons** : PDF volumineux (17–25 Mo), sans valeur de diff, et entièrement déterministes à partir du code.
- **Limites honnêtes** : (1) les artefacts expirent après 30 jours : il faudra relancer la CI ou la commande ; (2) **les 4 PDF V0.8 (≈ 76 Mo) restent dans l'historique Git** de la branche V0.8, car la consigne interdit de réécrire l'historique : le dépôt les porte toujours ; (3) je n'ai pas mis en place Git LFS (non configuré).

## Ce que la CI ne couvre pas
Essais physiques, stock, prix ; notation artistique (jugement humain) ; lisibilité réelle des PDF ; régression visuelle pixel à pixel ; module figurines (isolé) ; Hyrule (pas de source).
