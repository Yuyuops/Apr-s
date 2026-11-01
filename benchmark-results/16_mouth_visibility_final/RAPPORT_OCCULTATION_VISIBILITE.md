# LEGO V8.2 : diagnostic de visibilité de la bouche

Point de départ : commit `8a7e549` (V8.1). Aucune itération esthétique : un diagnostic, puis **une seule correction générique**.

Le GLB source n'est pas modifié. Les dossiers `14_facial_microdetails/` et `15_mouth_and_cavities/` ne sont **pas modifiés** (références immuables). Les corrections apparaissent ici. Je n'ai rien acheté ni déployé, rien fusionné dans `main`, et je n'ai pas touché au moteur 2.

## Verdict : **VALIDER AVEC LIMITATION**

Le raisonnement est détaillé plus bas.

- **Géométrie.** L'ouverture de la bouche est reproduite : 92 à 98 % de la surface de cavité visible du GLB vue de côté, silhouette IoU 0,96 à 0,99. **Il n'y a pas d'occultation géométrique propre au profil gauche.**
- **Couleur.** Dans le GLB, l'intérieur visible de la cavité est jaune à 97-100 %. Sa lisibilité vient de la forme et de l'ombrage, pas de la couleur.
- **Défaut de V8.1 révélé par ce diagnostic.** La sélection de la cavité mélangeait des hauteurs différentes. **130 des 223 cellules recolorées par V8.1 se trouvaient loin de la bouche** (pieds, jambes et bassin), et la ligne de lèvre sombre n'existe pas dans le GLB. La correction (V8.2) supprime ces deux défauts.
- **Limitation qui subsiste.** Dans la zone de la bouche, 79 % des pixels sombres vus de profil gauche ne sont pas de la bouche : ce sont des pièces du **module d'oreille basse** (plaques et brique de sa fixation). Ce module n'est pas modifié (consigne). Ce n'est pas un défaut de revêtement.

**Ce que ce verdict n'affirme pas.** À taille normale, la bouche de V8.2 se lit moins nettement que celle de V8.1 sur le profil droit : elle perd la ligne sombre que V8.1 y ajoutait. Cette ligne n'existe pas dans le GLB, et V8.1 l'avait étalée sur le corps.

## 1. Correction de mes propres résultats précédents

Le diagnostic a trouvé deux erreurs.

**Erreur de V8.1 (`lcm.py`, variante B).** La cavité était sélectionnée par colonne (x, z) avec **toutes ses hauteurs**. Une colonne de la bouche portait donc aussi les poches situées plus bas dans le corps (entre les jambes, sous les bras). Conséquences :

- V8.1 a recoloré 223 cellules ; **93 seulement sont dans la zone de la bouche, 130 sont ailleurs** (couches 8 à 60 : pieds, jambes et bassin). Ce sont les points sombres sur les pieds et les jambes visibles sur les rendus V8.1 « personnage entier », que je n'avais pas signalés.
- Mon rapport V8.1 attribuait à la ligne de lèvre une lisibilité qu'elle ne fournissait en partie que par ces cellules et par les pièces d'oreille.

**Erreur de ma première mesure de ce diagnostic.** La cavité y était construite par colonnes aussi : la fenêtre couvrait tout le corps et mesurait aussi les jambes. Ces résultats sont conservés dans `analyse/*CONTAMINEE*` pour trace, et **ne sont pas utilisés**. Tous les chiffres ci-dessous viennent de la mesure corrigée (`analyse/visibilite_par_camera_corrigee.json`).

## 2. Méthode

**Projection et tampon de profondeur** (`generateur/visibility3d.py`) : projection orthographique, 5 pixels par mm, sur les vraies pièces LDraw (le `g.glb` de chaque modèle) et sur le maillage GLB. Cavité = composante 3D (cellules à 6 voisins) des poches ouvertes sur l'extérieur, avec plafond à moins de 5 plaques et plancher à moins de 6, qui touche une tache de bouche : **303 cellules, couches 80 à 89**.

Pour chaque caméra et chaque modèle :

- **visible** : surface de cavité dont le premier point vu borde la cavité (aire en mm²) ;
- **masqué** : surface de cavité projetée mais cachée par une joue, le museau ou la mâchoire ;
- **couleurs exposées** : classe de couleur du premier point vu ;
- **silhouette** : IoU des masques de touche, et écart médian de profondeur avec le GLB.

Neuf caméras : profils gauche et droit (à 5° et à l'horizontale), face, trois quarts, dessous, deux trois quarts par le bas.

**Visibilité des cellules recolorées** (`generateur/cellvis*.py`) : une cellule recolorée compte comme visible si au moins un échantillon de ses faces exposées n'est pas caché par le tampon de profondeur.

**Origine des pixels sombres** (`generateur/darkcells.py`) : pour la caméra gauche et V8.2, chaque pixel sombre est rattaché à sa cellule, puis à la pièce qui l'occupe.

## 3. Occultation et silhouette (V8.1 et V8.2 ont la même géométrie)

| Caméra | GLB visible / masqué (mm²) | LEGO visible / masqué (mm²) | IoU silhouette | Écart de profondeur médian |
|---|---|---|---|---|
| Profil gauche (5°) | 1 485 / 613 | **1 459 / 640** | 0,964 | 3,0 mm |
| Profil droit (5°) | 1 924 / 269 | **1 778 / 415** | 0,973 | 3,4 mm |
| Face | 1 514 / 631 | **1 338 / 808** | 0,981 | 4,2 mm |
| Trois quarts | 2 168 / 1 453 | **2 059 / 1 561** | 0,964 | 2,6 mm |
| Dessous | 973 / 4 090 | **704 / 4 358** | 0,74 | 2,1 mm |
| 3/4 gauche, par le bas | 2 121 / 2 160 | **2 208 / 2 073** | 0,961 | 2,2 mm |
| 3/4 droit, par le bas | 1 411 / 1 574 | **1 366 / 1 618** | 0,989 | 3,7 mm |

**Lecture :**

- **Profil gauche** : le LEGO montre 98 % de la cavité visible du GLB et en masque 31 %, contre 29 % pour le GLB. **Ce côté n'est pas plus occulté que dans le GLB** ; la joue cache autant dans les deux modèles.
- **Face** : le GLB cache déjà 29 % de la cavité (lèvre et museau). Le LEGO en cache 38 %. La différence de 12 points est réelle mais modérée ; elle vient de la voxellisation (marche de 8 mm, écart de profondeur de 4 mm).
- **Dessous** : seule vue où la cavité visible du LEGO est nettement plus petite (−28 %, IoU 0,74). C'est une vraie différence de géométrie, due à la hauteur d'une plaque (3,2 mm) par rapport à l'ouverture.
- L'écart de profondeur médian (2 à 4 mm) est du même ordre qu'une demi-cellule : c'est la résolution du moteur, pas une erreur de sélection.

## 4. Couleurs réellement exposées

Parts des pixels de cavité visibles, par classe (GLB / V8 / V8.1 / V8.2) :

| Caméra | Sombre | Rouge | Peau |
|---|---|---|---|
| Profil gauche | 0 / 30 / **46** / 30 % | 0 / 0 / 0 / 0 % | 100 / 70 / 54 / 70 % |
| Profil droit | 0 / 37 / **43** / 34 % | 2 / 1 / 8 / 1 % | 98 / 62 / 49 / 66 % |
| Face | 0 / 1 / **21** / 0 % | 3 / 2 / 13 / 0 % | 97 / 97 / 66 / 100 % |
| Trois quarts | 0 / 17 / **34** / 16 % | 2 / 0 / 6 / 0 % | 98 / 83 / 60 / 84 % |
| Dessous | 12 / 13 / 23 / 7 % | 3 / 0 / 0 / 0 % | 85 / 87 / 77 / 93 % |

- **Le GLB est jaune dans sa cavité à 97-100 %** (rouge 0 à 3 %, sombre 0 à 3 % hors vue de dessous). La bouche du GLB se lit par sa forme et son ombrage.
- **V8.1 est le plus sombre** de tous : la ligne de lèvre et les parois sombres de V8.1 n'ont pas de référence dans le GLB.
- **V8.2 retrouve le niveau de V8** (le sombre restant n'est pas du revêtement, voir § 5).
- Le **rouge** (langue) ne représente que 0 à 3 % de la surface de cavité vue dans le GLB : moins d'une cellule de large. Le moteur ne peut pas en faire un élément lisible à 8 mm par cellule, hors la pente rouge posée (T1).

## 5. D'où vient le sombre qui reste ? (caméra gauche, V8.2)

Sur les pixels sombres de la zone vue depuis la caméra gauche :

| Origine | Part des pixels sombres |
|---|---|
| Cellules occupées par des **pièces d'oreille ou d'œil** (cellules creusées de la grille) | **79 %** |
| Cellules noires du corps | 2 % |
| Autres cellules du corps (ombrage sombre de la pièce) | 19 % |

Ces pièces d'oreille et d'œil forment **22 % de tous les pixels de la zone** vus de cette caméra. Les cellules les plus sombres de la zone contiennent des pièces de **`V7_oreille_basse`** (plaques d'angle 52107, brique 3008, plaque 3035, toutes noires) et la plaque 3035 noire de sa deuxième fixation. Elles se trouvent au coin arrière de la bouche, dans la tête.

**Je n'ai fait cette analyse d'origine que pour la caméra gauche.** Pour les autres caméras, la même cause est probable mais non mesurée.

## 6. Les cellules recolorées sont-elles visibles ? (`analyse/cellules_visibles*`)

| Modèle | Cellules recolorées | dans la zone de la bouche | visibles du profil gauche | du profil droit | de face |
|---|---|---|---|---|---|
| V8.1 | 223 | **93** | 27 (dont rouges : 3 sur 25) | 36 (rouges : 11) | 35 |
| V8.2 | 23 | 23 | 3 | 7 | 5 |

Sur V8.1, 71 des 223 cellules sont visibles du profil gauche, mais seules **27** sont dans la bouche. Le rouge, dont dépend la lecture de la langue, n'est visible du profil gauche que sur 3 cellules.

## 7. Cause établie

| Hypothèse | Verdict |
|---|---|
| Occultation géométrique (joue, museau) propre au côté gauche | **Non** : le LEGO cache à peu près autant que le GLB (31 % contre 29 %). |
| Revêtement incomplet du côté gauche | **Non** : le GLB n'a presque pas de couleur à y mettre (jaune à 100 %). Ce que V8.1 ajoutait venait d'une sélection erronée et d'un trait inventé. |
| Couleur exposée différente du GLB | **Oui**, par excès de sombre : 30 % côté gauche pour 0 % dans le GLB, dont 79 % viennent de **pièces de la fixation de l'oreille basse**. |
| Quelques détails du GLB trop petits pour le moteur | **Oui** : le liseré rouge de la langue (moins d'une cellule). |

## 8. Correction générique unique (V8.2, `generateur/lcm82.py`, variante C)

La mission autorisait de corriger la sélection des parois exposées. Rien d'autre n'est modifié.

1. **Sélection** : la cavité est une **composante 3D** de cellules (6 voisins) qui touche une tache de bouche (303 cellules au lieu de colonnes de toute la hauteur). Le revêtement n'atteint plus que la bouche : **23 cellules** recolorées, toutes dans la zone, contre 223 en V8.1.
2. **Couleur transférée du GLB** : pour chaque cellule exposée de la cavité, couleur majoritaire du GLB sous 3 × 3 échantillons de ses faces (sombre, rouge, peau, clair). La ligne de lèvre sombre inventée est supprimée. Une cellule exposée jaune dans le GLB redevient jaune.

Les traitements T1 (pente rouge) et T2 (taches de plafond) et l'ouverture minimale sont ceux de V8.1. **Aucune coordonnée, aucune pièce propre à Paco.**

**Ce que la correction ne fait pas :**

- **Contour de la lèvre** : non représenté. Aucune pièce de lèvre n'est implémentée dans le moteur.
- **Percement de la joue** et **sourire** : non faits, conformément à la consigne.

## 9. Contrôles (`validation/`)

| Contrôle | V8 | V8.1 | V8.2 |
|---|---|---|---|
| Pièces / types | 2 758 / 41 | 2 796 / 42 | **2 756 / 42** |
| Collisions | 0 | 0 | **0** |
| Déconnectées / îlots / non soutenues / tenons bouchés | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | **0 / 0 / 0 / 0** |
| Étapes | 331 | 335 | **326**, aucune pièce non ordonnée |
| Couples pièce × couleur | 72 | 74 | **73, tous vérifiés** |
| Sous-ensembles sous 0,5 N | 49 | 43 | **50** |
| Sous 2 N | 128 | 121 | **131** |
| Force minimale | 0,07 N | 0,07 N | **0,07 N** |

- **Oreilles** : mêmes pièces, mêmes positions, mêmes matrices que V8 et V8.1.
- **Yeux et truffe** : mêmes 8 pièces, mêmes positions. La pente rouge de la bouche est identique à V8.1.
- **Non-régression V6 et V6.1** : les générateurs `autogen.py` et `autogen61.py` ne sont pas modifiés depuis le rejeu de V8.1 (aucune différence avec les références archivées).
- **Groupes fragiles : 50 contre 43 pour V8.1.** V8.1 en avait moins (43) ; la cause n'est pas isolée (le moteur reconstruit tout le corps à chaque changement de cellule, et V8.1 avait recoloré 130 cellules hors de la bouche). V8.2 retrouve le niveau de V8 (49) plus 1.
  - **Zone de la bouche** : aucun groupe faible parmi les 10 plus faibles.
  - **Nouveau dans les 10 plus faibles** : un groupe de 7 pièces (4 rouges, 2 jaunes) sur 2 tenons, 0,26 N, aux couches 65 à 70 (haut du torse, épaule). Il est **loin de la bouche** (15 couches plus bas) et vient du nouveau découpage des plaques du corps, pas du traitement de la bouche. **Justification** : le moteur reconstruit tout le corps à chaque changement de cellule ; un petit groupe de plus ou de moins est le bruit de ce découpage. Il n'est pas corrigé ici (hors mission).
  - Les autres plus faibles (mains, bords d'oreille, groupes derrière l'œil gauche) sont ceux de V8 et V7, **non traités**.

## 10. Comparaisons (`comparaisons/`)

Vraies pièces LDraw, mêmes vues et même lumière, GLB / V8.1 / V8.2 :

- `personnage_taille_normale_GLB_V81_V82.png` : V8.2 n'a plus les points sombres sur les pieds et les jambes que V8.1 y avait.
- `tete_taille_normale_GLB_V81_V82.png` : profils et trois quarts.
- `bouche_gros_plans_GLB_V81_V82.png` : gauche, droit, dessous, deux trois quarts.

**Évaluation visuelle de la bouche, à taille normale :**

- **Profil droit** : encoche sous le museau et mâchoire visibles, sans ligne de lèvre sombre ni langue marquée. C'est ce que le GLB montre en géométrie. La lecture est moins nette qu'en V8.1.
- **Profil gauche** : l'ouverture est géométriquement présente mais ne se lit pas, car le coin de la bouche est occupé par les pièces noires de l'oreille basse.
- **Face** : non lisible, comme dans le GLB où la lèvre et le museau cachent déjà la cavité.
- **Dessous** : la cavité est lisible mais plus petite que dans le GLB (−28 %).

## 11. Conclusion sur le moteur

Voir `CONCLUSION_MOTEUR.md`.
