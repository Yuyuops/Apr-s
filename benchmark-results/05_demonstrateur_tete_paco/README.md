# Étude de faisabilité : brickify avec pièces de forme et connexions renforcées

**Démonstrateur limité à la tête et aux oreilles de Paco, 400 mm. Date : 2026-10-31.**
Rendus calculés avec les vraies pièces LDraw officielles, sans retouche. Le contrôle de stabilité est numérique : ce n'est pas un essai physique.
L'application finale n'a pas été développée, et l'étude n'a pas été étendue au chien entier.

Planches :
- `paco_tete_brickify_vs_prototype.png` : référence, brickify actuel, prototype C et prototype B, sous 5 angles ;
- `paco_tete_gros_plan.png` : gros plan, brickify actuel et prototype B.

## 1. Protocole

- **Même point de départ pour tous.** Le GLB gratuit validé (Hunyuan3D-2mv), corrigé du miroir, est découpé à 400 mm.
  La voxellisation et les couleurs viennent des fonctions **originales** de brickify, importées sans modification (`tools/proto/headgrid.py`).
  La grille complète est identique à celle de brickify : 35 × 126 × 35 cellules, soit 15 501 cellules.
- **Découpe.** La tête commence à la couche la plus étroite du cou (couche 70). Elle fait 27 × 56 × 35 cellules, soit 6 557 cellules.
  Le plan de coupe sert d'appui, comme si la tête reposait sur le corps.
- **Référence = brickify actuel.** Son empilement est appelé sur cette même grille, sans modification (`baseline_head.py`).
- **Prototype** (`tools/proto/brickify_plus.py`), en quatre étapes :
  0. *Occupation.* Une cellule n'est gardée que si le modèle 3D en remplit au moins 50 %. brickify garde toute cellule que la surface touche, ce qui gonfle le volume de 37 %.
     Les morceaux coupés sont recollés, et les cellules qui deviennent visibles prennent la couleur de surface la plus proche.
  1. *Pièces de forme.* Pentes 45°, 31° et courbes, pentes inversées, tuiles. Leur forme réelle est mesurée sur la géométrie LDraw (`partlib.py` : profil, tenons, points d'appui).
     Chaque pose est retenue si elle réduit l'écart avec le modèle 3D sur une grille 4 fois plus fine, et si les règles de support sont respectées : un appui sur une cellule occupée, rien posé sur une face sans tenon, aucune cellule intérieure.
  2. *Empilement renforcé.* Plaques seulement, croisées d'une couche à l'autre, en privilégiant les plaques qui recouvrent les joints de la couche du dessous.
     Seules les pièces produites dans la couleur voulue (au moins 20 sets selon Rebrickable) sont utilisées.
  3. *Réparation des pièces flottantes.* Réempilement local, puis pont par une petite plaque (au plus 8 cellules) dans la couche, au-dessus ou en dessous.
     Le pont choisit la couleur qui modifie le moins de cellules visibles.
- **Variantes :**
  - A : étapes 1 à 3, avec l'occupation de brickify ;
  - B : étapes 0 à 3 ;
  - C : étapes 0, 2 et 3, sans pièces de forme.

## 2. Validation indépendante étendue (`tools/validate_ldr.py`)

- **Tenons réels.** Ils sont lus dans la géométrie : une tuile n'en a pas, une pente 45° n'en a qu'une rangée, et une pente inversée ne reçoit des tenons que sous sa partie droite.
  L'encombrement des pièces dont l'origine n'est pas sur le dessus est corrigé.
  Les 6 modèles complets du benchmark ont été revalidés : chiffres identiques.
- **Stabilité numérique, hypothèses.** Maintien de 1 N par tenon (valeur prudente ; mesures courantes de 1 à 4 N), et 0,10 g par cellule d'un tenon × une plaque.
- **Cas étudiés.** Pour chaque sous-ensemble qui ne tient que par des tenons à un même niveau :
  (a) le coefficient de sécurité sous son propre poids ;
  (b) la **force horizontale au bout du sous-ensemble qui le décroche** en faisant pivoter ses tenons.
  Ce second critère traduit la manipulation, par exemple un doigt qui touche une oreille.

## 3. Résultats

| | brickify actuel | Prototype A (forme) | **Prototype B (occupation + forme)** | Prototype C (occupation seule) |
|---|---|---|---|---|
| Pièces | 1 446 | 2 038 | 1 760 | 1 735 |
| dont pièces de forme / tuiles | 0 / 0 | 178 / 7 | 66 / 27 | 0 / 35 |
| Volume LEGO / volume réel (cellules) | 6 557 / 4 792 | 6 362 / 4 792 | 4 787 / 4 792 | 4 799 / 4 792 |
| **IoU de volume avec le modèle 3D** | 0,728 | 0,748 | **0,857** | 0,853 |
| IoU des silhouettes face / profil / dessus | 0,921 / 0,934 / 0,811 | 0,928 / 0,942 / 0,811 | **0,958 / 0,961 / 0,893** | 0,955 / 0,958 / 0,893 |
| Collisions | 0 | 0 | 0 | 0 |
| Pièces non reliées / îlots | 0 / 3 | 0 / 0 | 0 / 0 | 0 / 0 |
| Pièces posées dans le vide selon la notice | 96 | 69 | 50 | 55 |
| Points de rupture uniques | 443 | 519 | 352 | **271** |
| **Sous-ensembles ≥ 1 g décrochés par moins de 0,5 N au bout** | **156** | 92 | 31 | **25** |
| Même chose, moins de 2 N | 194 | 111 | 41 | 34 |
| Force minimale de décrochage | 0,04 N | 0,04 N | 0,04 N | 0,04 N |
| Coefficient minimal sous le poids propre | 18,0 | 51,0 | 10,1 | 38,2 |
| Cellules visibles dont la couleur a changé | 39 | 39 | 12 | 0 |
| Pièce × couleur jamais produite / rare | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

## 4. Lecture

1. **Le gain principal vient de l'occupation, pas des pièces de forme.**
   - Avec le seuil de 50 %, la tête a le bon volume, les oreilles et le museau s'affinent, et les silhouettes passent de 0,92-0,93 à 0,96.
   - Les pièces de forme n'ajoutent que +0,004 d'IoU sur le volume et +0,003 sur les silhouettes.
   - Une fois la forme juste, le prototype ne pose plus que des pentes 31° : 52 pentes 1×1 (54200) et 14 pentes 1×2 (85984).
   - Les pentes 45° et les courbes testées n'améliorent pas assez la forme à cette échelle.
2. **Les connexions sont nettement meilleures, sans être bonnes partout.**
   - Les îlots disparaissent.
   - Les sous-ensembles fragiles (moins de 0,5 N) passent de 156 à 25-31, et les points de rupture uniques de 443 à 271-352.
   - Le pire cas ne change pas (0,04 N) : c'est le **bout des oreilles**, une colonne noire de 1 à 2 tenons de section posée sur 1 ou 2 tenons.
   - Avec des plaques empilées, la tenue d'une jonction verticale est limitée par la surface de contact entre deux couches, quelle que soit la façon d'empiler. Une oreille fine montée à plat reste fragile au bout.
3. **Le prix à payer :**
   - 20 % de pièces en plus (1 735-1 760 contre 1 446) ;
   - beaucoup de petites pièces : 824 plaques 1×1 sur 1 760 dans B ;
   - des liaisons à un seul tenon toujours majoritaires, environ 70 % comme dans brickify.
4. **Visuellement**, les oreilles sont plus fines et plus ovales, et le museau moins massif. Le rendu reste en escalier et très en dessous des références.
   Les oreilles des références sont de grandes plaques arrondies, montées de côté. Une grille horizontale de 8 mm ne peut pas les reproduire.

## 5. Faisabilité et suite proposée (non engagée)

| Piste | Faisabilité | Gain attendu |
|---|---|---|
| Occupation à 50 % avec recollage | **Faite, validée** | Forte sur la fidélité et sur les connexions |
| Pentes 31° et 45°, pentes inversées, tuiles | Faite | Faible une fois l'occupation corrigée |
| Plaques croisées par couleur réellement produite | Faite | Moyenne sur la tenue ; plus de pièces |
| **Oreilles montées de côté (SNOT : équerres, briques à tenons latéraux)** | Étude nécessaire : détecter les « plaques » fines du modèle 3D, les construire dans leur propre plan, les attacher par équerres ; le validateur doit gérer les tenons horizontaux | **Forte** sur les oreilles, à la fois pour la forme et la tenue |
| Grandes pièces arrondies (plaques rondes, plaques en coin) pour les contours d'oreilles | Possible après SNOT | Forte visuellement |
| Épaississement caché des attaches fines | Facile | Moyen ; modifie légèrement la forme |

Recommandation : ne pas étendre au chien entier en l'état. Le critère « qualité visuelle et connexions améliorées » n'est atteint qu'en partie :
la fidélité et la majorité des connexions progressent, mais le bout des oreilles reste fragile et le rendu reste cubique.
L'étape suivante utile est un essai **SNOT limité à une oreille**.

## 6. Fichiers

- `brickify_actuel/`, `prototype_A_forme/`, `prototype_B_seuil_pentes/`, `prototype_C_seuil/` : contenu de chaque dossier :
  - `.ldr` et `*_report.json` ;
  - `*_validation.json` (stabilité dans `clutch_stability`) et `*_fidelity.json` ;
  - inventaire et liste BrickLink (à importer **sans acheter**) ;
  - `renders/` (6 vues).
- `paco_head400.npz/.json` : grille de la tête (couleurs brickify) et grille fine du modèle 3D.
- Code : `tools/proto/` et `tools/{validate_ldr,partlib,studrefs}.py`.
- Les GLB de géométrie LEGO (26 Mo chacun) ne sont pas versionnés : ils se régénèrent à partir des `.ldr` (`tools/proto/evaluate.sh`).
