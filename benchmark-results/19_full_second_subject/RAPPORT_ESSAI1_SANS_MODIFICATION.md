# Premier essai du Beagle, moteur gelé (V9.1), aucune modification

Archivé tel quel, **même s'il est mauvais**. Journal : `essai1/ESSAI1_journal.txt`. Les paramètres et algorithmes de V9.1 sont gelés (copie `generateur/brickify_plus_v91_gele.py`). Entrée : le GLB source du dépôt (`02_glb_gratuit_hunyuan2mv/beagle.glb`, 9,9 Mo, récupéré en vrai fichier, non modifié). Palette de couleurs : la commande de référence du Beagle (`03_lego_brickify/beagle_regle400`, `--exclude …`), une **entrée** choisie par l'utilisateur, la même démarche que pour Paco (jaune, rouge, noir, blanc).

## Résultat du premier essai : **aucune sculpture**

| Étape du moteur | Résultat |
|---|---|
| 0. Lecture du GLB source tel quel (couleurs par sommets) | **Échec** : `fullgrid.py` attend un GLB à texture (`mesh.visual.to_color()`) ; le GLB du dépôt est à couleurs par sommets. Contournement sans modification de code : le GLB texturé archivé dans `~/bench/runs` (sommets et couleurs **identiques**, écart maximal 0), puis miroir X (`tools/mirror_x.py`) |
| 1. Grille 400 mm | Réussie : 30 × 126 × 58 cellules, 59 778 occupées, hauteur 400 mm. Le moteur fait 58 cellules de long (464 mm) : il traite bien un quadrupède |
| 2. Segmentation | **Exécutée mais fausse pour un quadrupède** : cou « automatique » à la couche 88 (70 % de la hauteur : le haut du dos), **aucune oreille**, zone « yeux » de 456 mm d'étendue (le blanc des pattes et du poitrail), « bras et mains » = 542 cellules, « torse » = 33 353 cellules qui contiennent les pattes arrière et l'arrière-train, « crâne » de 376 mm de long |
| 3. Oreilles, fixation (`integrate.py`) | **Non exécutable sur un autre sujet** : le script lit en dur `paco_full400.npz` (ligne 27), le repère de l'oreille de Paco `ear08/run/module_report.json` (ligne 29) et copie la silhouette `A_paco` pour l'oreille haute (ligne 136). Le lancer sans modification **régénérerait les oreilles de Paco** : il n'a pas été lancé |
| 4. Volume du corps (`brickify_plus.py --no-shapes`) | **Plantage** : `TypeError: cannot unpack non-iterable NoneType` dans `pack_region`. Cause : en Dark Brown (couleur 308) il n'existe pas de tuile 1×1 (3070b, moins de 20 sets) ; une case isolée de cette couleur sur une couche de tuiles n'a aucune pièce possible, et le repli à la plaque 1×1 n'est prévu que si **toute** la table est vide |
| 5. Détails, renforts, notice | Non atteints |

Le plantage de l'étape 4 est un défaut **générique** (le moteur suppose qu'une tuile 1×1 existe dans toutes les couleurs, vrai pour les quatre couleurs de Paco). Les étapes 2 et 3 sont des défauts de **spécialisation à Paco**.

## Ce qui a été ensuite possible, et sous quelle règle

Rien n'a été réglé sur le résultat visuel. Seules ont été acceptées les évolutions **nécessaires pour que le moteur s'exécute**, listées dans `RAPPORT_NON_REGRESSION_PACO.md` avec leur justification et leur effet sur Paco. Aucun seuil n'a été modifié, aucune coordonnée du Beagle n'a été codée, aucune pièce n'a été choisie.

L'état du corps seul après la seule évolution E1 (repli de tuile), avant les renforts : `essai1/comparaison_essai1_corps_seul.png` : 10 606 pièces, 0 collision, 0 pièce déconnectée, **157 cas de résistance sous 0,5 N, 44 groupes fragiles**, minimum 0,05 N. Pas d'oreille dédiée, pas d'yeux, pas de détails.
