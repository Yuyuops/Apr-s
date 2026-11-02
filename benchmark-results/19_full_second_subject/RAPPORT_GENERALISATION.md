# Beagle complet : génération, fidélité et constructibilité (phases 2 à 4)

Chaîne : `generateur/run_beagle.sh` (moteur V9.1 + évolutions E1 à E3 de `RAPPORT_NON_REGRESSION_PACO.md`). Modèle : `modeles/beagle_V10_notice.ldr` (11 111 pièces, 24 références, 77 couples pièce × couleur). Déterministe : deux exécutions donnent le même fichier. Tous les rendus sont ceux de **l'assemblage LDraw réel** (`rendus/`, pièces officielles LDraw), jamais d'une grille.

## 1. Ce que le moteur a fait automatiquement

| Étape demandée | Fait ? | Observations |
|---|---|---|
| 1. Lecture, orientation, échelle du GLB | Oui | 30 × 126 × 58 cellules, 400 mm de haut, 464 mm de long. La posture quadrupède est conservée parce que le moteur n'impose pas d'axe, mais **il ne la détecte pas** : il ne « sait » pas que c'est un quadrupède |
| 2. Segmentation | **Non pertinente** | Règles de Paco (cou à 70 % de la hauteur, deux jambes, bras) ; aucune oreille ni œil trouvé, « yeux » = le blanc des pattes. Le moteur n'a **pas déterminé la posture ni les appuis** |
| 3. Corps et quatre pattes | Oui | Volume `brickify_plus` : quatre pattes présentes, 18 pièces touchent le plan le plus bas |
| 4. Oreilles | **Non** | Aucun module d'oreille : les oreilles pendantes sont des plaques du volume (sans fixation dédiée, ni face lisse, ni module). Le module de V6.1 est lié au repère de Paco |
| 5. Yeux, truffe, bouche, détails | **Partiel et faux en partie** | Truffe construite (brique 87087 à tenon latéral, plaque 6141, dôme 3960, noire) ; **pas d'yeux** ; 20 « taches de bouche » et 32 « marques » détectées d'après la palette de Paco (noir, jaune, rouge, blanc) ont donné 12 pentes 54200 (9 noires, 3 rouges) et la recoloration de 379 cellules du volume : **63 plaques jaunes et 43 rouges parsemées sur la tête et les oreilles**, couleurs qui n'existent pas sur le chien (voir § 2) |
| 6. Fixations | Non applicable | Pas de module d'oreille donc pas de fixation 3-4-5 |
| 7. Renforcement | Oui | 46 groupes fragiles et 152 cas sous 0,5 N → 11 groupes / 23 cas après la passe 1 → **7 groupes / 10 cas** après la passe 2 ; scope : 0 violation (241 cellules intérieures recolorées, aucune cellule visible) |
| 8. Accessibilité, notice | Oui | 581 étapes, 0 défaut d'insertion |

## 2. Fidélité visuelle (mesurée, non retouchée)

`comparaisons/`, `rendus/`, `validation/fidelite_silhouette.json`. Silhouette : intersection sur union des masques (fond blanc et ombre retirés) entre le rendu du GLB et celui du LDraw, mêmes vues.

| Vue | Silhouette (IoU) | Rapport des aires LEGO / GLB |
|---|---:|---:|
| Profil gauche | **0,81** | 1,04 |
| Profil droit | **0,79** | 1,03 |
| Trois quarts | **0,74** | 1,08 |
| Dessus | 0,70 | 1,29 |
| Face | 0,69 | 0,92 |
| Dos | non évaluable : le rendu du GLB de référence montre la face à la place du dos (surfaces à face simple vues par l'intérieur) | |

* **Proportions et posture** : bonnes : quatre pattes, queue relevée, tête avancée, museau, longueur de 464 mm. Le chien est **reconnaissable comme un chien de ce type** dans les profils et les trois quarts. Le LEGO est plus massif en dessus (aire × 1,29) : le volume en plaques épaissit les oreilles et le cou.
* **Couleurs : mauvaises**. Couleur moyenne du GLB (175, 146, 114), du LEGO (108, 76, 53), écart moyen d'environ 100 sur 255. Le moteur associe le beige du GLB à **Dark Orange**, plus foncé et plus rouge, et aux Reddish Brown / Dark Brown pour les oreilles. Cette association vient de la palette autorisée et de la règle de distance du moteur ; aucun réglage n'a été fait pour la corriger.
* **Détails** : truffe reconnaissable ; museau et bouche rendus par des tuiles ; **yeux absents** ; taches jaunes et rouges parasites (palette de Paco appliquée à un autre sujet) sur la tête ; pattes lisibles mais bords de plaques apparents. Les oreilles sont brunes et pendantes comme sur le GLB, mais sans la surface lisse ni le contour propre de celles de Paco.
* **Reconnaissance** (jugement visuel, indépendant des scores) : on reconnaît un chien brun et blanc à oreilles tombantes, queue relevée, museau blanc ; on ne reconnaît ni le regard, ni le tricolore doré du modèle (couleur dominante trop sombre). Reconnaissable **avec réserve**.

## 3. Constructibilité numérique

| Contrôle | Résultat |
|---|---|
| Collisions non autorisées | **0** |
| Pièces déconnectées / îlots / tenons bloqués | **0 / 0 / 0** |
| Liaisons de tenons | 21 091 liaisons, 51 020 tenons engagés |
| Pièces posées sans liaison à la pose (ordre du fichier) | 0 |
| Séquence de montage | **581 étapes**, au plus 20 pièces par étape, **0 étape en défaut** (contrôle d'emboîtement, de dégagement, de collision de la notice de V9) |
| Pièces à emboîter par le dessous | 1 333 (pieds 202, jambes 186, torse 586, tête 188, museau 98, bras-mains 48, yeux 23, truffe 2) ; marge minimale du centre de gravité 71 mm ; **2 pièces à tenir** (coefficient de basculement 0,9) |
| Stabilité sur le plan de contact | Voir ci-dessous |
| Résistance indicative | 2 285 cas ; sous 0,5 N : **10** ; sous 2 N : 65 ; force minimale **0,10 N** ; coefficient de gravité minimal 38 |
| Groupes fragiles restants | **7**, tous de 1,0 à 1,9 g (4 à 12 pièces) : museau/truffe 0,10 N ; patte 0,15 N ; avant du corps 0,19 N et 0,22 N ; bout de queue 0,22 N ; flanc 0,31 N ; patte 0,47 N. Aucun n'est une fixation d'oreille (il n'y en a pas) |
| Pièces et couleurs | **77 couples sur 77 « vérifiés »** (≥ 5 sets) ; mais 919 plaques 4×6 (3032) en Dark Orange, une référence présente dans 21 sets seulement, rendent l'approvisionnement difficile |
| Nomenclature | `nomenclature_complete.csv` : 11 111 pièces ; Dark Orange 6 179, Medium Nougat 1 859, blanc 1 740, Reddish Brown 556, Dark Brown 496, noir 175, jaune 63, rouge 43 |
| Masse | 5 253 g **du modèle** (volume × 0,10 g par case, calibré sur des briques) : **ce n'est pas une pesée** ; masse réelle inconnue, probablement supérieure |

### Stabilité réelle (`validation/stabilite.json`) : **défaut non corrigé**
* Enveloppe convexe des 18 pièces au plan le plus bas : 487 cm², marge du centre de gravité **78,8 mm** (calcul).
* Mais ces 18 pièces forment **10 plaques de contact de 0,6 à 3,2 cm², 17 cm² au total** : le dessous des pattes n'est pas plan (les pattes ne touchent la table qu'en quelques plaques). C'est le défaut du plan d'appui de V9 (4 plaques isolées pour Paco) : le contrôle R1 ne regarde que l'enveloppe, pas la surface réellement touchée. **Risque de balancement et de pression localisée**, non traité en V10.

## 4. Notice (PDF, voir `notice/`)

581 étapes, modules : corps (555 étapes) et détails du visage (13 sous-assemblages de 2 pièces chacun, les pentes et le nez). Pas de bras, pas d'oreille : **pas de sous-assemblages structurels** ; les pattes sont construites couche par couche avec le corps. Chaque page : pièces à ajouter, direction d'emboîtement, vue (pâle = posé, couleur = à poser). Trois PDF (`notice/`, 582 pages, 17,5 Mo, pages réduites à 60 % pour rester légères) : corps étapes 1 à 277, 278 à 581, détails du visage. **Pas de page de précautions** pour le Beagle (elle n'a pas été générée) : les 7 points fragiles et les 2 poses à tenir ne sont signalés que dans les rapports.

## 5. Valeurs calculées et propriétés non vérifiées physiquement
Calculées : collisions, connexions, séquence rigide, force indicative (1 N par tenon, traction et moment seulement), masse du modèle, marge de basculement, disponibilité Rebrickable. **Non vérifiées** : toute résistance réelle, la facilité du montage, la masse, la stabilité réelle, l'état de surface réel, la disponibilité effective des quantités.
