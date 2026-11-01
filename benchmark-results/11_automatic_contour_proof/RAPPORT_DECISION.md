# LEGO V6 : du prototype manuel au moteur automatique

Point de départ : commit `3dac38a` (V5.1). Le GLB source n'a pas été modifié. Aucun achat, aucun service payant, aucune modification de `main`, aucune fusion, aucune application web, aucun travail sur le moteur de tableaux 3D.

## Verdict : **CORRIGER L'ALGORITHME**

**L'automatisation fonctionne :**

- les deux contours sont produits par le même programme, sans liste de positions de pièces ;
- tous les contrôles techniques passent ;
- la fixation a deux chemins indépendants et une tenue indicative 6,6 fois supérieure à V5.1.

**Mais le rendu bute sur un défaut précis et reproductible :** les **grands bouts arrondis** (rayon de 3 à 4 tenons) ne sont pas reproduits.

- Le bout libre de l'oreille de Paco finit en pointe, au lieu du demi-disque de V5 et V5.1.
- Le bas de l'oreille du Beagle est plat au lieu d'être ovale.

La cause est identifiée (§ 4). Elle relève de l'algorithme de choix des pièces, pas de l'architecture. On ne redessine rien à la main.

| Critère | Résultat |
|---|---|
| Deux contours produits automatiquement | **Oui** (A Paco, B Beagle), aucune retouche après génération |
| Rendu convaincant | **Partiellement.** Silhouette générale, biseaux, faces propres et épaisseur sont convaincants. Les bouts arrondis ne le sont pas, et sur Paco une plaque de fixation affleure sur le crâne. |
| Fixation techniquement crédible | **Oui, au calcul.** 2 chemins indépendants (5 + 2 vrais tenons), 2,1 N au bout. Le banc d'essai réel est prêt, l'essai n'est pas fait. |
| Exige de redessiner chaque forme ? | **Non** : la même chaîne a traité les deux oreilles |

## 1. Étape 1 : fixation

La fixation est trouvée par le générateur lui-même (`find_fixation`) à partir de la grille de la tête. Il y a 2 plaques tournées de 53,13° (triangle 3-4-5), chacune emboîtée sur des tenons de la tête qui coïncident avec son propre réseau de tenons :

| | Plaque | Niveau | Tenons coïncidents posés | Remarque |
|---|---|---|---|---|
| Chemin 1 | 4×6 (3032) | v 40…48, sous un bloc de racine | **5** | Cachée dans le crâne |
| Chemin 2 | 4×4 (3031) | v 80…88, sur le bloc | **2** | Repli de rang 2 : sur ce crâne, aucune position cachée n'a 2 appuis à au moins 30 LDU de l'âme. La plaque affleure sur 6 cases sur 16. |

Le générateur protège automatiquement les zones sensibles :

- il refuse toute position dont le volume creusé toucherait un œil ou la bouche (vérifié : 0 cellule touchée) ;
- il interdit au panneau le volume des plaques et de leurs appuis.

| Oreille de Paco | V5 | V5.1 | **V6 (automatique)** |
|---|---|---|---|
| Liaison au crâne | 2 plateaux tournants | 1 plaque, 5 tenons | **2 plaques, 5 + 2 tenons** |
| Masse (pire découpage) | 37 g | 86,8 g | **75 à 83 g** |
| Force de décrochage au bout | 0,16 N | 0,32 N | **2,13 N** |
| Coefficient sous le poids propre | 3,47 | 2,17 | **> 49** (tous les découpages de l'oreille) |
| Collisions / pièces déconnectées / posées dans le vide | 0 | 0 | **0 / 0 / 0** (1 313 pièces, 78 étapes) |
| Silhouette face / profil | 0,923 / 0,939 | 0,943 / 0,942 | **0,932 / 0,941** |

**Hypothèses du calcul** (`validate_v2.py`, inchangé) :

- 1,0 N de tenue par tenon (valeur supposée), pièces rigides, 0,10 g par tenon × tenon × plaque ;
- poids propre, puis force au bout de chaque sous-ensemble ;
- seule la direction d'emboîtement dominante est comptée.

La variante `validate_v2_bigcases.py` (nouvelle copie, l'original n'est pas modifié) ajoute seulement la liste de tous les découpages de plus de 40 pièces, pour retrouver celui de l'oreille. **Rien n'est validé physiquement :** le banc d'essai et son protocole sont dans `banc_essai/` et `PROTOCOLE_ESSAI_FIXATION.md`.

## 2. Étape 2 : contour automatique (`generateur/`)

Ce qui suit est **réellement automatique** : aucune position de pièce n'est inscrite dans le programme.

1. **Extraction** (`contour.py`). Faces de l'oreille dans le GLB, plan moyen, projection, image au pas de 4 LDU, ouverture de 20 LDU, plus grande composante. Le même traitement sert pour A et B.
2. **Analyse du contour.** Pente locale (ACP sur 40 LDU) et rayon de courbure (cercle ajusté sur 60 LDU), puis classement en bords d'axe, pentes ou arcs.
   - A : pentes de 0,21 à 0,54, arcs de 35 à 69 LDU.
   - B : pentes de 0,85 à 5,8, arcs de 54 à 86 LDU.
3. **Catalogue** de pièces de forme réelles disponibles en noir. Chacune a son empreinte mesurée sur la géométrie LDraw et son bord biseauté ou courbe.
   - Ailes : 2×2, 2×3, 2×4, 2×6, 3×6, 3×8.
   - Formes arrondies ou coupées : demi-disque 4×8, quart de rond 4×4, 3×3 à coin rond, 3×3 à coin coupé, 6×6 à coin rond.
4. **Candidats.** Chaque pièce, rotation et position est retenue si son bord biseauté ou courbe suit le contour cible (transformée de distance). Elle reçoit un gain par rapport à des cases pleines (accord − 2 × dépassement − 2 × vide laissé dans sa boîte). Contrainte : une case pleine sur une rangée d'accroche de l'âme.
5. **Combinaison.** Choix glouton sans case partagée. 12 réglages sont essayés et la combinaison la plus fidèle est gardée. Tous les résultats sont dans le rapport JSON.
6. **Intérieur.** Grands rectangles d'abord, chacun sur une rangée d'accroche. 4 ordres de balayage sont essayés et celui qui laisse le moins de cases vides est gardé.
7. **Règles de V5.1**, généralisées : tuiles (quart de rond si un coin de case sort de la pièce), face intérieure en miroir, âme (hauteur tirée du contour, ajourée sauf derrière les pièces étroites), tuiles de fermeture.
8. **Fixation, creusement et reconstruction de la tête**, puis contrôle de connexité. Ce contrôle retire les pièces non reliées et les compte : 0 sur A et sur B.
9. **Validateurs existants** (`validate_v2`, `reorder_notice`) et rendus LDraw.

## 3. Étape 3 : généralisation

| | A : oreille de Paco | B : oreille du Beagle |
|---|---|---|
| Contour | Palette allongée, biseau en haut, bout arrondi | Ovale tombant, côtés raides, haut et bas arrondis |
| Pièces de forme choisies | 3×3 à coin coupé, 4 ailes 2×2 / 2×3 | 2 ailes 2×6, 2 ailes 2×2 / 2×3, 1 quart de rond 4×4 |
| Plaques intérieures | 7 | 15 |
| **Recouvrement du contour (IoU)** | **0,911** avec le lobe de référence de V5, hors crâne. Même mesure : V5 manuelle 0,839, V5.1 manuelle 0,871. **Objectif ≥ 0,86 atteint.** | **0,958** avec sa propre silhouette |
| Collisions / pièces déconnectées / îlots | 0 / 0 / 0 (tête complète) | 0 / 0 / 0 (module seul, 247 pièces) |
| Pièces et couleurs | 23 références, au moins 107 sets | 30 références, au moins 27 sets |
| Retouche manuelle | Aucune | Aucune |

**À propos de l'IoU de 0,86 de V5.** Elle était mesurée au pas de 5 LDU, dans le repère de V5. Recalculée ici avec exactement la même définition que V6 (pas de 4 LDU, hors crâne, lobe à v ≥ 46), V5 donne 0,839.

**Limite de l'essai B.** L'oreille du Beagle est générée et validée **seule**, sans tête ni fixation. Elle est mise à l'échelle de 20 tenons pour être comparable à celle de Paco ; il n'existe pas de grille de tête du Beagle à cette échelle. Son module pèse 132 g.

## 4. Le défaut précis à corriger

1. **Grands arcs non reproduits.** Le choix glouton évalue chaque pièce seule, contre des cases pleines. Une grande pièce arrondie (demi-disque 4×8, quart de rond 4×4) réserve toute sa boîte, ce qu'impose le validateur, qui traite toute pièce à angles droits comme une boîte. Son gain individuel est alors battu par des ailes et des coins coupés plus petits, choisis d'abord. Résultat : une pointe ou un méplat là où il faut un arrondi.

   **Correction proposée :**
   - choix **conjoint** le long du contour (programmation dynamique ou programme en nombres entiers sur les segments d'arc et de pente), au lieu du glouton ;
   - un candidat d'arc par segment d'arc mesuré à l'étape 2 (le rayon est déjà connu) ;
   - un contrôle de collision sur la vraie géométrie des pièces arrondies, pour ne plus réserver leur boîte entière.

2. **Seconde plaque de fixation visible sur Paco.** La forme du crâne laisse peu de volume caché près de la racine.

   **Correction proposée :** 3e niveau de recherche, appuis sur les côtés du crâne, ou ancrage dans un « bouchon » de crâne conçu pour la racine.

3. **Masse.** Une oreille épaisse de 20 tenons pèse 75 à 130 g. La règle d'âme ajourée pourrait évider davantage.

Aucune nouvelle itération n'est engagée sans décision. Les autres parties de la sculpture ne sont pas abordées.
