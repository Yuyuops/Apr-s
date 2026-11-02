# Résistance des groupes de bord d'oreille : avant / après (phase 3)

Modèle de résistance **inchangé** (`validate_v3`, copie `validate_v4` avec `--dump`) : pièces rigides, **1 N par tenon**, traction et moment autour de l'arête de la zone de contact, force indicative au bout de chaque sous-ensemble. Ni le coefficient, ni le critère de 0,5 N, ni l'algorithme n'ont été modifiés. Données : `validation/strength_cmp.json`, `weak_final.json`, `class_final.json`, figures `rapport_avant_apres/`.

## 1. Pourquoi les quatre groupes étaient fragiles

Une oreille est un sandwich (face externe, noyau d'un tenon d'épaisseur, face interne). Les quatre groupes sont des **calottes de bord** de l'oreille basse : plaques de face (ailes 78443/78444, coins 43722/43723, plaques 54383/54384) et tuiles, appuyées sur le noyau par **un ou deux tenons verticaux alignés** (le noyau n'a qu'un tenon d'épaisseur). Les plaques de face voisines, côte à côte dans le même plan, ne sont liées par rien : **un joint de plaques n'est pas une liaison mécanique**. Un bras de levier de plusieurs studs sur un point d'appui sans largeur donne 0,08 à 0,41 N.

## 2. La règle ajoutée : tuiles à cheval sur les joints (R3, `generateur/stitch.py`)

Les tuiles reposent sur les tenons des plaques de face. Une tuile qui couvre un tenon de chaque côté d'un joint de plaques **les lie par de vraies liaisons de tenons**, décalées par rapport au joint. Pour chaque groupe fragile d'une oreille :

1. chercher les couples de cases voisines dans la même face, l'une sur une plaque du groupe, l'autre sur une plaque **différente** (vérifié par plaque, pas par tuile) ;
2. en choisir un ensemble écarté (distance au moins 2 cases entre couples, au plus 3 par face et par groupe) ;
3. remplacer les deux tuiles concernées par une tuile 1×2 couvrant exactement le couple, et recouvrir le reste des deux tuiles par des tuiles 1×k (k = 1, 2, 3, 4, 6) ;
4. refuser si les cases couvertes ne sont pas strictement les mêmes avant et après.

Les références sont celles du générateur (3070b, 3069b, 63864, 2431, 6636), **déjà présentes dans le modèle**. Aucune nouvelle référence ; aucune pièce de structure touchée. Les groupes sont traités ensemble (un groupe peut réutiliser les tuiles produites pour un autre).

Résultat sur Paco : **16 tuiles retirées, 48 ajoutées** (12 × 6636, 2 × 3069b, 2 × 63864 retirées ; 26 × 3069b, 18 × 3070b, 4 × 63864 ajoutées), 18 tuiles à cheval (couples de cases), sur les deux faces. Les cases couvertes, les couleurs et la surface sont identiques (`scope` : occupation 0, couleur exposée 0, finition 0).

## 3. Résultats

| Mesure | V9 | V9.1 |
|---|---:|---:|
| Cas de résistance de tout le modèle sous 0,5 N | 17 | **7** |
| Cas sous 2 N | 77 | **48** |
| Groupes fragiles | 8 | **4** |
| Force minimale du modèle | 0,08 N | **0,19 N** |
| Coefficient de sécurité de gravité minimal | 2,68 | **11,15** |
| Cas d'oreille (≥ 1 g) sous 0,5 N | 10 | **0** |
| Cas d'oreille sous 2 N | 38 | **9** |
| Force minimale d'un cas d'oreille | 0,08 N | **0,54 N** |
| Liaisons de tenons du modèle | 4 849 | 4 899 |

Les quatre groupes de V9, un par un (plus aucun cas de l'oreille ne contient le groupe en dessous de 0,5 N) :

| Groupe V9 | Pièces, masse | Tenons / force avant | Après : plus petit cas qui contient le groupe |
|---|---|---|---|
| 6 (calotte du bord haut) | 15 pièces, 5,1 g | 1 tenon, **0,08 N** | 119 pièces, 47,6 g, 23 tenons, 71,5 N |
| 8 (calotte voisine) | 18 pièces, 8,1 g | 3 tenons, 0,41 N | 119 pièces, 47,6 g, 23 tenons, 71,5 N |
| 5 (bord bas) | 7 pièces, 3,5 g | 1 tenon, **0,21 N** | 155 pièces, 66,5 g, 8 tenons, 5,8 N |
| 1 (coin gauche) | 5 pièces, 1,3 g | 1 tenon, 0,27 N | 155 pièces, 66,5 g, 8 tenons, 5,8 N |

Les neuf cas d'oreille restant sous 2 N : 0,54 N (1,9 g, 2 tenons), 0,54 N (1,8 g), 0,62 N (5,3 g, 13 pièces), 0,81 N (3,0 g), 0,83 N (5,7 g), 1,34 N (3,3 g), puis trois cas de l'oreille entière (155 pièces, 78,5 g, 9 tenons, 1,4 N). **La marge sur le seuil de 0,5 N est faible (0,54 N) pour deux petits cas.**

Non-régression de la méthode : même opération sur l'oreille du Beagle (V6.1, archivée) : 5 groupes avant, **1 après**, et le seul qui reste est l'oreille entière sur ses 4 tenons de racine, **sans signification** puisque la tête n'existe pas dans ce modèle isolé (`validation/beagle_*`). Les 4 groupes de moins de 100 pièces sont résolus.

## 4. Ce que le renfort change réellement, et ses limites

* **Mécaniquement** : la calotte est maintenant liée au reste de la face par des tuiles dont les tenons s'engagent dans les plaques des deux côtés du joint. Un détachement doit désormais vaincre ces liaisons en plus du tenon vertical.
* **Dans le modèle de calcul** : les tuiles font joindre la calotte à un sous-ensemble beaucoup plus grand (cas de 119 et 155 pièces). Le groupe fragile n'existe plus comme cas isolé ; sa force est celle du cas qui le contient.
* **Limite principale** : ces tenons sont chargés **en cisaillement** (le poids de la calotte agit selon Y, les tenons de tuile sont orientés selon T), alors que le modèle ne traite que la traction et le moment : il ne sait **ni compter ni refuser le cisaillement**. Le gain réel vient du frottement de maintien des tenons et de la raideur des tuiles, **non démontrés**.
* Autres limites du modèle (inchangées) : 1 N par tenon supposé ; aucun frottement entre pièces voisines ; aucun jeu ; ni torsion, ni fatigue, ni usure ; pièces rigides.
* **Visible** : 18 tuiles à cheval changent le tracé des joints de tuiles sur les faces de l'oreille basse (même couleur noire, même surface). Écart de rendu mesuré : 0,05 à 0,12 % des pixels (`comparaisons/`).

## 5. Les quatre groupes restants (hors oreilles) et leur justification

| Groupe | Pièces | Masse | Tenons | Force | Catégorie |
|---|---:|---:|---:|---:|---|
| Bout du museau / truffe | 7 | 1,3 g | 2 | 0,19 N | décoration légère |
| Museau | 9 | 1,4 g | 3 | 0,26 N | décoration légère |
| Main gauche (doigts) | 5 | 1,0 g | 2 | 0,26 N | décoration légère |
| Main droite (doigts) | 12 | 2,1 g | 3 | 0,26 N | **intermédiaire** |

Ces groupes n'ont **pas** été renforcés dans cette itération (hors du périmètre levé : oreilles). Ils sont explicitement justifiés comme détails de faible masse (≤ 2,1 g) sans fonction de structure, **sauf la main droite (2,1 g), qui est manipulable** : elle reste une réserve. Ils sont signalés dans la page de précautions de la notice (page 2 du premier PDF).
