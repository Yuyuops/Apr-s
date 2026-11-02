# Verdict V10

## GÉNÉRALISATION PARTIELLE

Le moteur 1 produit un Beagle complet, déterministe et constructible selon les contrôles numériques, **sans conception manuelle ni coordonnée du Beagle**. Mais :

* **tel qu'il était gelé en V9.1, il n'a produit aucune sculpture** (premier essai : `RAPPORT_ESSAI1_SANS_MODIFICATION.md`) ; trois évolutions génériques, acceptées sans changer Paco, ont été nécessaires pour qu'il s'exécute ;
* les parties qui définissent le personnage (**segmentation, oreilles, yeux, détails**) restent propres à Paco : le Beagle n'a ni module d'oreille, ni yeux, et des taches jaunes et rouges parasites ; les couleurs sont trop sombres ;
* la chaîne n'est **pas reproductible depuis le dépôt seul**.

## Pourquoi pas « MOTEUR 1 : MVP NUMÉRIQUE VALIDÉ »

Il exige « Paco et Beagle générés sans conception manuelle spécifique, des rendus convaincants, des notices exploitables ». Les rendus du Beagle ne sont convaincants que pour la forme (silhouette de profil IoU 0,79 à 0,81) : pas pour le visage ni les couleurs. La notice est exploitable mais linéaire. Les modules qui rendent un personnage reconnaissable ne se généralisent pas encore.

## Pourquoi pas « ARCHITECTURE À CORRIGER »

Aucune pièce du Beagle n'a été choisie ni redessinée à la main, aucune coordonnée du Beagle n'est dans le code, et le noyau (voxélisation, volume, renfort 157 → 10 cas fragiles, contrôle de portée, validation, séquence de la notice) s'applique tel quel à une autre géométrie. Les parties spécifiques à Paco sont localisées dans des modules identifiables (segmentation, oreilles, détails, constantes) et peuvent devenir génériques sans repenser l'ensemble. **Ce verdict est à la limite** : il basculerait en « ARCHITECTURE À CORRIGER » si ces modules s'avéraient non généralisables ou si la reproductibilité depuis le dépôt restait impossible.

## Modules génériques manquants pour passer au MVP (non développés ici)

1. **Segmentation par la géométrie** : posture, appuis, extrémités, sans cou à 70 % ni bipédie.
2. **Module d'oreille générique** : repère et fixation déduits de la géométrie.
3. **Détecteur de détails indépendant de la palette de Paco** (yeux, marques), et module d'yeux.
4. **Plan d'appui réel** : surface de contact des pattes (17 cm² pour 5,2 kg de modèle).
5. **Archivage** : `brickify`, LDraw, Rebrickable, intermédiaires, racine configurable.
6. Notice hiérarchique pour un quadrupède (pattes, queue, tête en sous-assemblages).

## Réserve physique

Reste explicitement ouverte pour Paco et Beagle : aucune résistance, aucun montage, aucune masse ni stabilité mesurés. Pas de masse issue du volume présentée comme une pesée.

## Contrôles

Beagle : 11 111 pièces ; 0 collision ; 0 pièce déconnectée ; 581 étapes sans défaut ; 77 couples pièce × couleur vérifiés ; 10 cas sous 0,5 N ; 7 groupes fragiles ; scope 0 violation. Paco rejoué : identique octet à octet (corps, V8.2) et plan de notice identique ; 16 tests de portée sur 16.
