# Les 31 pièces d'oreille « sans séquence » de V9 : diagnostic individuel (phase 1)

Données : `rapport_31_pieces/diag31.csv` et `.json` (une ligne par pièce), séquences : `seq_a2.json`, `seq_pacoA.json`, `seq_beagle.json`, rejeu : `validation/replay_*.json`.

## 1. Conclusion

**Aucune des 31 pièces n'est emprisonnée.** Les quatre causes envisagées se répartissent ainsi :

| Cause | Pièces | Preuve |
|---|---|---|
| 1. Impossibilité géométrique | **0** | Les 31 pièces sont séquencées une par une, dans l'oreille complète, par une translation rigide chacune, vérifiée par un second modèle de collision |
| 2. Ordre de montage incorrect | 0 comme cause isolée | L'ordre de V9 n'est pas la cause : c'est sa méthode (cause 3) |
| 3. Limitation du planificateur | **31** | Voir § 2 |
| 4. Flexion ou déformation | **0** | Aucune pièce de la séquence n'a besoin de se déformer : chaque pièce se pose par un seul mouvement le long de l'axe de ses tenons |

Le blocage de V9 (« 31 pièces sans séquence ») était donc **une erreur d'outil, pas un défaut du dessin des oreilles**. Le rapport V9 le présentait comme « non démontré impossible » ; il est maintenant démontré possible, à la précision des modèles décrits en § 4.

## 2. Pourquoi le premier planificateur échouait

Le planificateur de V9 (`plan_units`) démontait l'oreille en **unités rigides** : une unité était la composante connexe des contacts perpendiculaires à la direction de retrait, avec la condition que tous ses contacts de frontière soient dans le même sens. Il construisait ensuite chaque unité **à part**, isolée, puis l'attachait. Une oreille est un sandwich : face externe (plaques dont les tenons sortent vers l'extérieur) + tuiles, noyau d'un tenon d'épaisseur, face interne en miroir. Les briques du noyau portent des tenons des deux côtés (axes +T et −T, T étant la normale de l'oreille) et sont empilées le long de Y. Dans ce montage :

* retirer une unité par l'axe Y entraîne par les tenons latéraux T tout le tranche de sandwich (faces, tuiles, briques à tenons latéraux) : l'unité devient énorme et ses contacts de frontière portent les deux signes de T ;
* retirer par T un élément pris entre deux voisines qui portent les deux signes de T est refusé, alors qu'il suffit de retirer d'abord la tuile (un seul signe) puis la plaque.

Le critère « une seule direction commune pour toutes les liaisons de l'unité » est correct, mais appliqué à des unités **construites à part** il refuse des ordres valides **une pièce à la fois dans la structure**. 11 des 31 pièces sont prises en sandwich entre deux sens de T ; 21 des 31 sont posées **avant** certaines de leurs voisines dans le nouvel ordre (le premier planificateur exigeait l'inverse).

## 3. Le nouveau séquenceur (généralisé, sans coordonnées de Paco)

`generateur/seq.py`, démontage inverse par pièce ou par groupe rigide :

* **règle des tenons** : un groupe C peut sortir par un mouvement e si chaque contact de tenon entre C et le reste est libéré exactement par e (le porteur du tenon sort par −axe, le receveur par +axe) ;
* **règle du chemin** : le volume balayé par C le long de e (jusqu'à sortir du modèle) ne rencontre aucune pièce hors de C ; les pièces qui gênent doivent sortir **avant** C (précédence, pas appartenance au groupe) ;
* un groupe de plusieurs pièces n'est admis que s'il est lié par la règle des tenons seule, ou, en dernier recours, s'il forme un seul assemblage connexe ;
* mouvements essayés : les translations le long des axes des tenons de l'oreille (Y, +T, −T) et des axes globaux ; puis **dégagement de 5 ldu le long de l'axe des tenons suivi d'un glissement** dans une autre direction (translation et rotation rigides combinées : seule la composante de rotation n'est pas explorée, voir § 5) ;
* préférence : un reste toujours connexe, une pièce seule, les pièces les plus hautes sortent en premier (donc montage de bas en haut).

## 4. Contrôle indépendant

`generateur/verify_seq.py` rejoue chaque séquence avec une **autre géométrie** : boîtes exactes des pièces pleines et maillage rempli du dessin LDraw pour les autres (1,5 ldu de pas, au moins 1 ldu à l'intérieur des faces), un pas de 1 ldu le long du chemin complet, et la règle des tenons. Les 2 premiers ldu du chemin sont ignorés : le modèle comporte des contacts serrés de moins de 1 ldu entre pièces voisines que le premier mouvement lève.

| Oreille | Pièces | Étapes | Défauts au rejeu |
|---|---:|---:|---:|
| Paco, haute (V9) | 176 + 5 | 181 | **0** |
| Paco, basse (V9) | 156 | 154 (2 unités de 2 pièces) | **0** |
| Paco A, oreille V6.1 isolée | 170 | 170 | **0** |
| Beagle (archivée) | 276 | 276 | **0** |
| Paco, haute (V9.1) | 176 + 5 | 181 | **0** |
| Paco, basse (V9.1) | 188 | 186 | **0** |

**Incident de contrôle, par transparence.** Une première version du rejeu signalait 2 à 3 étapes par oreille en collision (briques de racine 47905 et 3008). Ce n'était pas une collision : la géométrie de contrôle d'une petite brique creuse retombait, faute de point assez à l'intérieur, sur des points posés sur sa face, qui frôlaient la brique voisine à 0,7 ldu. Les deux briques se touchent exactement par leurs boîtes (recouvrement nul). Le défaut est dans l'outil de contrôle, corrigé dans `verify_seq.py` (boîtes exactes pour les pièces pleines) ; les chiffres ci-dessus sont ceux d'après la correction.

## 5. Ce que ce diagnostic ne montre pas

* Le séquenceur ne traite que des **translations rigides** (avec dégagement puis glissement) : aucune rotation d'une pièce pendant la pose, aucun doigt, aucun outil, aucune souplesse. Ces séquences sont des **preuves de possibilité au sens du modèle**, pas des preuves de facilité de montage.
* Les tenons et les creux ne sont pas dans le modèle de collision : le dégagement de 5 ldu (2 mm) le long de l'axe garantit seulement que les tenons se libèrent avant tout glissement.
* Le planificateur n'est pas complet : un échec ne prouverait rien, un succès (le cas ici) prouve la possibilité du modèle.

## 6. Le tableau des 31 pièces

Voir `rapport_31_pieces/diag31.csv` (colonnes : pièce, oreille, référence, couleur, ensemble bloqué de V9, niveau, nombre de voisines, prise en sandwich T, rang V9.1, mouvement d'insertion, voisines déjà posées, voisines posées après, cause).

Répartition : oreille basse 19, haute 11, attache 2 de la haute 1 ; références 3460 (5), 52107 (5), 47905 (4), 3070b/3069b/3023 (3 chacune), 3666 (2), 3024 (2), 24299, 3623, 63864, 6636 (1 chacune). Mouvement d'insertion : 19 poussées vers le bas (axe Y), 9 de côté (axe T), 3 pièces posées en premières.
