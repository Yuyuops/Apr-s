# Verdict V9.1

## VALIDER AVEC RÉSERVE PHYSIQUE

Les contrôles numériques et la notice passent ; **la résistance réelle, le montage réel et la stabilité réelle restent à confirmer par des essais**. Aucun essai physique n'a été réalisé, aucun achat n'a été fait, rien n'est fusionné dans `main`.

## Pourquoi pas « VALIDER V9.1 »

La définition de « VALIDER V9.1 » demande que les validations numériques passent *et* que les groupes critiques soient renforcés. Les deux sont vrais dans les limites du modèle. Mais :

1. le renfort des bords d'oreille repose sur des **tuiles dont les tenons travaillent en cisaillement**, que le modèle de résistance ne sait pas traiter (il ne compte que la traction et le moment, 1 N par tenon) ;
2. **quatre groupes restent fragiles** (mains, museau, 0,19 à 0,26 N), dont la main droite, manipulable (2,1 g) ;
3. **55 poses de bras et 57 poses de l'oreille basse** exigent de tenir l'assemblage ;
4. aucune étape de la notice n'a été exécutée par une personne.

## Pourquoi pas « BLOCAGE »

* **Aucune impossibilité structurelle** : les 31 pièces d'oreille de V9 ne sont pas emprisonnées (erreur du planificateur de V9). Toutes les pièces d'oreille ont une séquence, vérifiée par deux modèles de collision (0 défaut au rejeu, quatre géométries d'oreille).
* **Aucune modification sensible du dessin** : la silhouette, les couleurs et la géométrie V6.1 sont inchangées ; 16 tuiles remplacées par 48, mêmes cases, mêmes couleurs.

## Critères

| Critère de la mission | Résultat |
|---|---|
| Toutes les pièces d'oreille ont une séquence de montage crédible | **Oui** : 181 + 188 pièces (V9.1) et 337 (V9), 170 (Paco A), 276 (Beagle) ; 0 défaut au rejeu indépendant. Crédible = possible au sens du modèle rigide, non vérifiée à la main |
| Générateur d'oreilles : tester sur Paco (2 oreilles) et le Beagle | **Fait**. Aucune correction géométrique nécessaire ; renfort après génération appliqué aux deux |
| Quatre groupes fragiles réévalués | **Oui** : plus aucun cas d'oreille sous 0,5 N (10 → 0), minimum 0,54 N (0,08 N en V9) |
| Éléments structurels exposés : fixation plus robuste ; détails décoratifs justifiés et signalés | **Oui pour les oreilles** ; 4 détails (mains, museau) justifiés, signalés dans la notice (page 2) ; main droite = réserve |
| Collisions, connexions | **0 / 0 / 0** (collisions, pièces déconnectées, îlots) |
| Accessibilité, ordre | Oreilles : séquence par pièce ; corps : 283 poses par le dessous stables ; bras : 55 à tenir |
| Deux chemins de fixation par oreille | Pièces de fixation **identiques** à V9 ; indépendance héritée de V7 |
| Stabilité sur le plan de contact | **41,1 mm**, identique à V9 (calcul) |
| Pièces et couleurs disponibles | **73 couples sur 73 « vérifiée »** (Rebrickable) |
| Fidélité visuelle | 0,05 à 0,12 % des pixels ; silhouette et couleurs inchangées |
| Aucune modification hors zone | **0 violation** ; 16 tests réussis sur 16 |
| Aucune nouvelle dégradation du visage ni de la bouche | **Oui** : bouche, yeux, truffe, pente identiques à V8.2 |
| Masse recalculée, anomalie V9 | **1 117,7 g** (modèle) ; l'anomalie est un arrondi, la masse du modèle ne dépend que du volume |
| 338 pièces par le bas, documentées séparément | **Oui** (`RAPPORT_NOTICE.md` § 3) |
| Notice : chaque pièce dans une séquence plausible, pas de bloc de dizaines de pièces sans construction préalable, vues éclatées, orientation, PDF et LDraw | **Oui** (5 PDF, 203 pages, LDraw ordonné) |
| Étapes non confirmables signalées séparément | **Oui** (`RAPPORT_NOTICE.md` § 5, page 2 de la notice) |
| Non-régression V6, V6.1, V8.2 | **AUCUNE DIFFERENCE** (V6, V6.1) ; V8.2 identique pour le visage et la bouche |
| Test de portée des changements non autorisés | **Détecte** (T11, T12, T14) |

## Ce qui reste non démontré physiquement

La tenue des bords d'oreille renforcés (cisaillement), des mains et du museau ; la facilité réelle du montage ; la masse réelle ; la stabilité debout ; l'indépendance des deux chemins de fixation. Voir `RISQUES_RESIDUELS.md` et `PROTOCOLE_ESSAI_PHYSIQUE.md`.

**V10 n'est pas commencé.**
