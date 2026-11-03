# LEGO Maps V0.3 — résultats vérifiés sur cinq cartes

Date des essais : 2026-11-03.

## Traçabilité

- Branche : `research/lego-maps-v03-chatgpt-20261103`
- Exécution GitHub Actions complète : https://github.com/Yuyuops/Apr-s/actions/runs/41716299430
- Artefact : https://github.com/Yuyuops/Apr-s/actions/runs/41716299430/artifacts/13270701067
- Code V0.2 copié sous `engine/`, archives V0.2 non modifiées.
- Python, brickify, LDraw et Rebrickable installés depuis les scripts du moteur 1.
- Rebrickable : release glissante, empreinte `pcs_mat` `7a989a23b4fbfd9f5de301a9a55c0fd534b98d4bac681dae5a37766329ef3d23`, différente de la référence V11.

## Résultats V0.3 (12 passes maximum)

| Carte | Pièces avant | Pièces après | Faibles avant → après | Critiques avant → après | Modifications |
| --- | ---: | ---: | ---: | ---: | ---: |
| Écosse 32×32 | 301 | **304** | 44 → 45 | **17 → 10** | 7 |
| Écosse 48×48 | 487 | **487** | 44 → 34 | **19 → 7** | 9 |
| Île témoin 32×32 | 224 | **224** | 12 → 12 | **0 → 0** | 0 |
| Trois zones 32×32 | 166 | **166** | 6 → 6 | **0 → 0** | 0 |
| Archipel original 32×32 | 196 | **196** | 12 → 7 | **8 → 5** | 4 |

**Important :** le nombre de porteuses critiques diminue sur les trois modèles fragiles, mais ne tombe pas à zéro. L'Écosse 32 a aussi une porteuse faible supplémentaire : l'optimiseur priorise les porteuses **critiques**, pas le nombre total de porteuses faibles.

## Contrôles

- Tests du module et références historiques : PASS (GitHub Actions).
- Pour chaque modèle, comparateur `tests/compare_v03.py` : PASS.
- LDraw, liste de pièces et fichier de pièces : quantités cohérentes.
- Au sein de chaque modèle, inventaire exact des cellules occupées, couleurs, type et niveau avant/après : inchangé.
- Croissance de pièces : inférieure à 15 % pour chaque carte (Écosse 32 : +3 pièces seulement).
- Validation indépendante par le moteur 1 sur les cinq fichiers LDraw : **0 collision, 0 déconnexion, 0 îlot, 0 pièce sans support à la pose**.
- Rigidité réelle, cisaillement, stabilité murale, résistance au vieillissement : **non vérifiés physiquement**.

## Résidus et décision

Les 10, 7 et 5 porteuses critiques restantes ne doivent pas être cachées ni déclarées irréductibles. Plusieurs sont des plaques de 1×1 ou 1×2 portant seules un détail, entourées de zones de couleurs différentes. Une réorganisation **strictement dans la même couleur et le même niveau** ne peut pas tout corriger. Pour les résoudre, la prochaine étude doit comparer les compromis de relief, liaisons cachées ou modification locale des détails, chaque fois avec validation mécanique indépendante et preuve de fidélité.

**Verdict : V0.3 numérique avec limitations**, pas apte à être déclaré sûr pour accrochage au mur. Le prochain chantier de structure doit prouver l'amélioration des cas résiduels sans modifier les seuils, puis procéder à des essais physiques.

## Sorties

Les cinq modèles LDraw, nomenclatures, rapports d'optimisation et validations sont téléchargeables via l'artefact GitHub ci-dessus. Les notices PDF et rendus ne faisaient pas partie de ce test de génération; leur test séparé ne doit pas être confondu avec cette validation.

Aucun achat, aucune fusion main, aucun prix ou stock inventé, aucun changement au moteur 1.
