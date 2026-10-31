# Contrôle des 8 vues de référence (768×768 px, rendus de LEGO, pas des photos)

Le détourage a été fait avec rembg (isnet-general-use). Seul le sujet principal est gardé, aucun pixel du sujet n'est modifié.
Les fichiers `*_rgba.png` sont détourés, sur fond transparent et au format carré. Ce sont les entrées prévues pour la reconstruction 3D.

## Beagle (marron/blanc, quadrupède)
| Vue | Constat |
|---|---|
| face | Cohérente : oreilles tombantes marron foncé, liste blanche, langue rose. Le bord gauche de l'oreille est légèrement rogné dans le panneau source. |
| dos | **Rognée dans la source** : le flanc et l'oreille droite sont coupés net (bord vertical de 228 px). La largeur réelle n'est pas mesurable sur cette vue. |
| profil droit | Complet. Queue relevée blanche et marron, quatre pattes visibles. |
| profil gauche | **Queue rognée** au bord droit (bord vertical de 110 px). 8 fragments d'une figure voisine ont été retirés. |
| cohérence | Les deux profils sont symétriques, avec des taches compatibles. Hauteur/longueur ≈ 0,87 sur les deux profils. Vues cohérentes, mais deux sont incomplètes. |

## Paco (jaune, oreilles noires, salopette rouge, **bipède**)
| Vue | Constat |
|---|---|
| face | **La tête est tournée de trois quarts** (museau vers la gauche) alors que le corps est de face. Une seule oreille est visible. Ce n'est donc pas une vraie vue de face pour la tête. |
| dos | Deux oreilles **asymétriques** : l'une relevée, l'autre tombante. |
| profil droit | **Oreille rognée** au bord gauche (bord vertical de 94 px). La pointe du museau touche presque le bord droit. |
| profil gauche | Complet. |
| cohérence | La pose des oreilles et de la tête diffère d'une vue à l'autre. Un reconstructeur multivue recevra des indices contradictoires. Les oreilles sont de grandes plaques fines et les bras sont fins, ce sont les éléments les plus exposés à la perte lors de la voxellisation à 8 mm. |

## Conséquences attendues
- Le README fourni précise que `image_to_3d.py` est **mono-vue** (face seule). Pour Paco, la vue de face a la tête tournée : une reconstruction à partir d'elle seule risque de déformer la tête.
- Les références sont elles-mêmes des rendus de briques à tenons. Hunyuan reproduira probablement ce relief bosselé dans le maillage ; brickify le revoxellisera à 8 mm, ce qui ne pose pas de problème.
- Comme les oreilles de Paco sont asymétriques, l'inversion miroir probable de brickify (voir le rapport) sera visible sur ce modèle.
