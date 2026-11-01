# LEGO V7 : première sculpture complète automatique (Paco cartoon, 400 mm)

Point de départ : commit `0d601b4` (V6.1). Le GLB de référence n'a pas été modifié. Aucun achat, aucun appel payant, aucune modification de `main`, aucune fusion, aucun travail sur le moteur 2.

## Verdict : **INTÉGRATION PARTIELLE**

**Ce qui marche.** La chaîne produit automatiquement un Paco complet, **reconnaissable** et **constructible numériquement** :

- 2 773 pièces ;
- 0 collision, 0 pièce déconnectée, 0 îlot, 0 pièce posée dans le vide ;
- notice de 331 étapes ;
- 68 couples pièce × couleur, tous vérifiés ;
- centre de gravité à l'intérieur de l'appui des pieds.

Aucune pièce n'est placée à la main.

**Ce qui manque :**

- les petits détails du visage (yeux, truffe, bouche) ;
- les mains ;
- une notice détaillée à l'intérieur des sous-ensembles d'oreilles ;
- un seuil de la segmentation, réglé au vu de ce cas (§ 6).

L'architecture n'est pas en cause : les composants se sont assemblés par adaptateurs, sans réécriture.

## 1. Phase 1 : audit d'intégration

| Composant | Statut | Interface et adaptateur |
|---|---|---|
| Voxellisation et couleurs brickify (`headgrid.py`, fonctions originales) | Utilisable tel quel | **Adaptateur `fullgrid.py`** : même code, sans découpe au cou. Vérifié : son découpage au cou redonne **exactement** la grille de tête des itérations 05 à 12 (grilles grossière et fine identiques). Les oreilles conçues depuis V4.1 étaient donc déjà à l'échelle du personnage entier. |
| Volume `brickify_plus` (réglages du prototype C) | Utilisable tel quel | Appelé une seule fois sur la grille complète, après creusement par les deux oreilles |
| Générateur V6.1 (`autogen.py` + choix `autogen61.py`) | Utilisable avec 3 adaptations | (1) grille et repère passés en paramètres ; (2) masque de protection fourni avec la grille ; (3) **fixation à plusieurs niveaux** (v = 48 + 40 n), une capacité qui manquait pour une oreille pendante. Les valeurs par défaut gardent le comportement de V6/V6.1. Différences : `code/autogen_diff_V7.patch`. |
| Recherche de fixation 3-4-5 | Étendue | Recherche **conjointe** des deux plaques : chaque plaque principale valide est essayée avec sa meilleure seconde plaque. Classement : deux chemins, puis seconde plaque cachée, puis nombre de tenons. |
| Contrôle de connexité, `reorder_notice`, `validate_v3`, `ldr_expand`, `render_ldr` | Utilisables tels quels | 2 sous-ensembles « oreille » dans le même fichier |
| Catalogue (Rebrickable) | Utilisable tel quel | — |
| Générateur de notice PDF par couche (`make_instructions.py`) | Non utilisé | Pas de PDF volumineux. La notice est le `.ldr` ordonné (lisible par Studio ou LeoCAD), avec un tableau des étapes et 4 rendus d'avancement. |
| Placement du GLB pour les rendus | Adaptateur `ref_glb_fullframe.py` | Même transformation que la grille, personnage entier |

## 2. Phase 2 : segmentation automatique (`code/segment.py`, `segmentation.json`)

Règles générales : couleurs, découpe au cou (couche la plus étroite), composantes connexes, coupes par couche, ACP.

**Règle de décision :**

- une zone **mince** (3e axe < 0,30 × 1er et < 0,45 × 2e, épaisseur < 35 mm, au moins 60 cellules) va au générateur V6.1 ;
- une tache de couleur de moins de 2 tenons de large est rendue par la couleur de la grille, et c'est une capacité manquante ;
- tout le reste va au volume `brickify_plus`.

| Zone | Cellules | Épaisseur (mm) | Décision | Confiance |
|---|---|---|---|---|
| oreille_haute | 196 | 24.8 | generateur V6.1 (contour, panneau a deux faces, fixation 3-4-5) | haute |
| oreille_basse | 203 | 30.3 | generateur V6.1 (contour, panneau a deux faces, fixation 3-4-5) | moyenne |
| yeux | 14 | 16.7 | couleur de la grille seulement (detail trop petit pour une piece de forme) - capacite manquante : module de details ronds | faible |
| truffe | 7 | 8.0 | couleur de la grille seulement (detail trop petit pour une piece de forme) - capacite manquante : module de details ronds | faible |
| bouche | 2 | None | couleur de la grille seulement (detail trop petit pour une piece de forme) - capacite manquante : module de details ronds | faible |
| museau | 1418 | 42.6 | volume brickify_plus (reglages du prototype C) | moyenne |
| crane | 2982 | 48.0 | volume brickify_plus (reglages du prototype C) | haute |
| pieds | 1171 | 47.4 | volume brickify_plus (reglages du prototype C) | haute |
| jambes | 3836 | 64.7 | volume brickify_plus (reglages du prototype C) | haute |
| bras_mains | 33 | 17.8 | volume brickify_plus (reglages du prototype C) | moyenne |
| torse | 1793 | 52.4 | volume brickify_plus (reglages du prototype C) | haute |

**Limites de la segmentation :**

- **Bras.** Ils ne sont isolés que là où ils se détachent du torse : 33 cellules sur la longueur réelle. Le reste est compté dans le torse. Sans effet ici, puisque les deux zones vont au même traitement (volume).
- **Oreille basse.** Elle est classée mince avec 30,3 mm d'épaisseur voxel. Le seuil a été porté de 30 à 35 mm **après** avoir vu ce cas (justification : sandwich de 20,8 mm + une cellule de gonflement de la voxellisation + marge). Ce seuil reste à confirmer sur d'autres personnages.

## 3. Phase 3 : construction

- **Volume.** Grille complète (35 × 126 × 35 cellules) sans les deux oreilles : cellules d'oreille, peau noire voisine et cœur isolé (règle de V4.1). 1 197 cellules creusées, dont **0** dans les yeux, la bouche ou la truffe. Reconstruction par `brickify_plus` : 2 414 pièces, dont 63 morceaux flottants retirés en les comptant.
- **Oreille haute.** V6.1, avec les mêmes pièces de forme que V6.1, aux mêmes positions relatives.
- **Oreille basse.** V6.1, dans le **même plan** que l'oreille haute (normales 0,80 / −0,60 et 0,78 / −0,62). Le repère est abaissé de 264 LDU (un nombre entier de plaques), tiré de son point le plus bas.
- **Fixations** (recherche automatique conjointe) :

| Oreille | Chemin 1 | Chemin 2 | Visible ? |
|---|---|---|---|
| Haute | Plaque 2×8 à v 40…48, **4 appuis** | Plaque 4×4 à v 80…88, **2 appuis** | **Non**. Seconde plaque de rang 1, 0 case visible. La plaque visible de V6/V6.1 est corrigée, sans pièce fragile et avec les deux chemins. |
| Basse | Plaque 4×8 à v 200…208, **7 appuis** | Plaque 4×8 à v 240…248, **5 appuis** (3 coïncidences prévues par le générateur) | Presque pas : rang 1, 1 case exposée côté crâne |

- **Autres détails.** Yeux, truffe, bouche, logo et doigts restent rendus par la couleur et le volume de la grille. **Aucune solution de remplacement fragile n'a été créée.** Voir § 6.

## 4. Phase 4 : constructibilité globale (`validation/`)

| Contrôle | Résultat |
|---|---|
| Collisions (géométrie réelle, `validate_v3`) | **0** |
| Pièces déconnectées / îlots / tenons bouchés | **0 / 0 / 0** |
| Ordre de montage | **331 étapes**, 0 pièce posée dans le vide, 0 pièce retirée. L'oreille haute est montée en 2 morceaux (176 + 5 pièces). |
| Interfaces entre modules | 18 appuis 1×1 sous les 4 plaques tournées, tous posés. 12 tuiles du corps changées en plaques sous les appuis. 268 liaisons latérales. |
| Pièces / références × couleurs | **2 773 pièces**, 68 couples, **tous vérifiés** (Rebrickable, au moins 20 sets). Jaune 1 506, rouge 671, noir 517, blanc 79. |
| Masse indicative | **≈ 1 127 g** |
| Centre de gravité | À 189 mm de haut, **à l'intérieur de l'appui des pieds**, avec 74 mm de marge (appui de 100 cm²) |
| Porte-à-faux : oreilles | Pire découpage : oreille basse, 59 g, 6 tenons, coefficient 7,7 sous son poids, **0,67 N** au bout. Oreille haute plus forte. |
| Points faibles | Main droite (rouge) : un groupe de 10 pièces tenu par 1 tenon, 0,07 N. Deux petits groupes de bord d'oreille (7 et 11 pièces, 1 tenon). En tout, 46 sous-ensembles se décrochent sous moins de 0,5 N, surtout les mains, les doigts et les bords. |
| Statue soulevée par la tête | Les semelles ne tiennent au reste que par 5 tenons. C'est sans effet posé sur une table, mais il ne faut pas soulever la statue par la tête. |

Les calculs mécaniques sont indicatifs (1 N par tenon supposé, pièces rigides). **Le modèle n'est pas validé physiquement.** Bancs d'essai : `bancs_essai/` et `PROTOCOLE_ESSAI_FIXATIONS.md`.

## 5. Phase 5 : évaluation visuelle (`comparaison_GLB_LEGO_V7.png`, `gros_plans_GLB_LEGO_V7.png`)

Vraies pièces LDraw, mêmes vues et même lumière que le GLB : face, dos, profils gauche et droit, trois quarts, dessus, et gros plans de la tête, des oreilles, des mains et des pieds.

| Critère | Constat |
|---|---|
| Reconnaissance du personnage | **Oui.** Chien jaune au long museau, deux grandes oreilles noires d'un même côté, salopette rouge, bras et pieds jaunes. Reconnaissable sous toutes les vues. |
| Silhouette et proportions | Bonnes : hauteur, tête, longueur du museau, place des oreilles. L'oreille basse descend un peu moins bas que dans le GLB. |
| Oreilles | Les plus réussies : palettes épaisses, bords arrondis et biseautés, faces lisses (V6.1). |
| Couleurs | Justes par zones. Le museau garde des traînées noires et rouges en escalier, héritées de la colorisation de la grille. |
| Détails | **Insuffisants.** Yeux, truffe et bouche réduits à quelques cellules ; logo de salopette illisible ; mains en escalier, doigts perdus. |
| Raccords | Les oreilles entrent dans le crâne sans pied ni plaque visible. Quelques taches noires de la grille restent autour des racines. |

**Bilan visuel.** Le personnage est reconnaissable, mais le visage n'atteint pas la qualité des oreilles. C'est le principal écart visuel.

## 6. Phase 6 : maturité du moteur 1, échecs, causes et corrections minimales

| Problème | Cause | Correction minimale proposée |
|---|---|---|
| Yeux, truffe, bouche trop schématiques | Ces détails font 1 à 3 tenons. Le volume en cellules de 8 mm ne peut pas les rendre, et V6.1 ne traite que des contours plats. **Capacité manquante.** | Module de **détails ronds de surface** : œil = tuile ronde 2×2 blanche + 1×1 noire, truffe = demi-sphère ou tuile ronde, posés en SNOT sur la surface du crâne d'après la position et la couleur de la zone segmentée. Même famille de règles que les appuis. |
| Mains et doigts fragiles, en escalier | Volume fin (moins de 2 tenons) ; groupes tenus par 1 tenon | Règle de renfort des membres fins (plaques traversantes), ou module de main générique |
| Notice : chaque oreille en une seule étape | `reorder_notice` garde un sous-ensemble en un bloc | Sous-notice par sous-ensemble : ordre des groupes du générateur (âme, faces, tuiles), déjà connu |
| Seuil de minceur réglé au vu de ce cas (30 → 35 mm) | L'oreille basse est épaissie par la voxellisation | Mesurer l'épaisseur sur le maillage plutôt que sur les voxels, puis valider le seuil sur un 2e personnage |
| Traînées de couleur sur le museau | Colorisation de la grille (brickify) | Lissage des couleurs de surface par zone segmentée |
| Statue soulevée par la tête : 5 tenons sous les semelles | Couche de semelle peu liée par le volume | Plaque de semelle traversante (règle de base) |

**Pourquoi ce n'est pas « intégration validée ».** Le rendu des détails du visage n'est pas convaincant, la notice n'est pas détaillée dans les sous-ensembles, et un seuil a été réglé sur ce cas.

**Pourquoi ce n'est pas « architecture à corriger ».** L'intégration n'a demandé que des adaptateurs génériques (grille complète, repère par oreille, fixation à plusieurs niveaux, recherche conjointe), sans aucun traitement propre à Paco.

**Aucune optimisation n'est commencée.** Le passage au vrai Paco gris et blanc attend la validation de ce personnage.
