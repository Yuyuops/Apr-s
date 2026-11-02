# Évolutions génériques acceptées en V10 et non-régression de Paco

Règle appliquée : une évolution n'est acceptée que si (1) elle est **nécessaire pour que le moteur s'exécute** sur un second sujet, (2) elle ne contient aucune coordonnée ni choix propre au Beagle, (3) elle laisse **Paco strictement identique**. Aucune évolution n'a été choisie d'après la qualité du résultat. Preuves : `paco_non_regression/preuves.txt`.

| # | Défaut rencontré (échec) | Évolution | Justification | Effet sur Paco |
|---|---|---|---|---|
| E1 | `brickify_plus.py` plante quand une case isolée n'a aucune pièce disponible dans sa couleur (pas de tuile 1×1 en Dark Brown) | Repli : plaque 1×1 de la couleur (tenon visible), comptée (`FALLBACK_COUNT`) | Le moteur ne doit pas planter quand le catalogue d'une couleur est incomplet ; la plaque 1×1 existe dans toutes les couleurs essayées | **Aucun** : le repli ne se déclenche pas pour les quatre couleurs de Paco. Corps de Paco (2 414 pièces) **identique octet à octet** ; `assemble_v82.py` complet rejoué : `paco_V82.ldr` **identique octet à octet** à l'archive |
| E2 | Les outils de V9 (`scope.py`, donc `reinforce.py`, `final_scope.py`, `notice_plan.py`) fixent la grille à 40 × 130 × 40 ; le Beagle fait 30 × 126 × 58 : les cellules au-delà de 40 en profondeur étaient **ignorées sans erreur** | Grille lue dans `LEGO_SHAPE` (défaut 40,130,40) | Un contrôle de portée qui ignore silencieusement 30 % du modèle est faux | **Aucun** : défaut inchangé ; 16 tests de portée sur 16 ; `reinforce.py` identique (diff vide) |
| E3 | `notice_plan.py` s'arrête (`SystemExit`) si les « bras » d'un bipède ne sont pas détectés | Si aucun bras n'est détecté : tout le corps sur la ligne principale (de bas en haut, 20 pièces par étape), message dans le plan | Le quadrupède n'a pas de bras ; construire les pattes couche par couche est la règle du corps | **Aucun** : plan de la notice de Paco V9.1 **identique** (201 étapes, mêmes modules, mêmes contrôles) |

## Adaptations de données (pas de code du moteur modifié)

* **GLB** : encodage par texture du GLB source (mêmes sommets et couleurs), puis miroir X, comme pour Paco.
* **« Run V7 » sans oreille** : les étapes de V8 lisent `ears.pkl` et la grille « sans oreilles ». Le moteur n'ayant trouvé aucune oreille, un `ears.pkl` **vide** et la grille complète leur sont fournis (script `generateur/run_beagle.sh`). Le masque de protection est calculé par **la règle de `integrate.py`** (zones yeux, bouche, truffe de la segmentation).
* **Module de bouche** : mêmes réglages que V8.2 (`MD_SKIP_MOUTH`, variante C).

## Ce qui n'a PAS été rejoué sur Paco, par honnêteté

* Le générateur d'oreilles, la fixation 3-4-5 et le renfort des bords d'oreille de V9.1 n'ont pas été touchés ni relancés : leurs fichiers d'entrée intermédiaires ne sont pas dans le dépôt (voir `RAPPORT_REPRODUCTIBILITE.md`). Leur non-régression repose sur le fait qu'aucune de leurs sources n'a changé.

## Bilan par axe pour Paco

| Axe | Effet |
|---|---|
| Géométrie | Aucun (modèles identiques octet à octet là où rejoués) |
| Couleurs | Aucun |
| Stabilité | Aucun |
| Fragilité | Aucun |
| Notice | Aucun (plan identique) |
| Fidélité visuelle | Aucun (mêmes LDraw) |
