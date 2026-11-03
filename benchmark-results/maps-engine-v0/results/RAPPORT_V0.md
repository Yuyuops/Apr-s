# Rapport V0 — moteur 2, cartes et tableaux en relief

Entrée : `fixtures/ile_temoin.svg` (carte fictive originale) puis `fixtures/test_3_zones.svg`. Plateau **32 × 32 tenons = 256 × 256 mm** (pas 8 mm), plaques de 3,2 mm. Moteur 1 (`../20_portable_engine`) **utilisé en lecture seule** : `conn.py` / `partlib.py` (géométrie LDraw), `validate_v4.py` (collisions, liaisons, pièces isolées, stabilité indicative), `ldr_expand.py` (expansion LDraw), `palette_util.py` / `_paths.py` (couleurs LDConfig, chemins) ; le rendu three.js d'`render_ldr.js` est copié dans `engine/render_map.js` avec un éclairage recalibré (l'original éclaircit les couleurs). Aucun fichier du moteur 1, des GLB ou des archives n'a été modifié.

## 1. Flux (dossier `engine/maps_engine/`)
`image SVG/PNG/JPG → classes (classify.py) → grille 32×32 → hauteurs par style déclaré (build.py + styles/relief_classic.json) → couleurs LEGO (palette.py) → pavage par couche (tiling.py) → dos rigide (build.backing) → LDraw / nomenclature (build.py, export.py) → validations (validate.py) → rendus, viewer, notice (render.py, viewer.py, notice.py) → évaluation (evaluate.py, après coup)`.
* **Reconnaissance** : clusters de couleurs plates (graines ≥ 100 px, fusion ΔE < 8), puis chaque cluster est coupé en « corps » et « mince » (ouverture d'une cellule : rivières et routes plus étroites qu'un tenon) ; nom par **famille de teinte** (bleu / vert / rouge / chaud) et par **forme** (contact avec le bord = mer ; mince = rivière ou route ; enclavé dans la colline et plus clair = sommet ; petit rouge = village). Aucune valeur hexadécimale d'une carte dans le code.
* **Cellules** : vote majoritaire, sauf classes minces / ponctuelles retenues dès 20 % de la cellule (la plus couverte gagne : une rivière qui croise une route) ; les pièces minces d'un même objet sont reconnectées.
* **Relief artistique déclaré** : niveaux de plaques par classe (mer 0, lac 0, rivière 0, terre 1, route 1, forêt 2, colline 3, sommet 4, village 2), **jamais des altitudes**. Mode `2d` = tout à plat.
* **Couleurs** : couleurs LDraw opaques dont les plaques de base existent en ≥ 20 sets Rebrickable (34 couleurs candidates) ; affectation **injective** pondérée par la surface (deux classes ne partagent jamais une couleur).
* **Pavage** : plaques réellement existantes (24 formats de 1×1 à 8×8, 12×4, 10×6…, références vérifiées dans la géométrie LDraw) ; glouton par aire décroissante, avec (i) joints **décalés** par rapport à la couche du dessous, (ii) **pénalité d'orphelins** (une cellule qui n'aurait plus de voisine compatible), (iii) 8 essais avec jitter. Les cellules cachées (entourées de colonnes au moins aussi hautes) sont « joker » et prennent la couleur qui permet de grandes plaques.
* **Dos rigide** : deux couches de plaques DBG, 16 plaques 8×8 puis 25 plaques décalées de 4 tenons (9 × 8×8, 12 × 4×8, 4 × 4×4) : 0 % de joints alignés entre les deux couches.

## 2. Essai 1 aveugle (archivé, `essai1/`, commit 7fd35eb) et corrections ensuite
L'oracle et `make_fixture.py` n'ont été ouverts qu'après. Résultat brut : 148 pièces, **16 × 1×1 (10,8 %)**, 273 liaisons, 0 collision, 0 pièce déconnectée ; la rivière coupée en 2 morceaux (la route gagnait au croisement) ; sommet, forêt, lac, mer corrects. Corrections faites **après** l'évaluation et appliquées aux sorties finales :
1. *priorité des classes minces par couverture* (rivière continue : 2 → 1 composante, comme l'oracle) ;
2. *pavage avec pénalité d'orphelins* : 1×1 16 → 9, plaques tenues par un seul tenon 16 → 9 ;
3. convention d'axes du LDraw (x = colonne, z = −ligne : la carte vue de dessus n'est ni miroir ni tournée) et marqueurs `0 STEP` par étape de notice ; éclairage du rendu recalibré ; vues, viewer et notice. La géométrie (pièces) de l'essai 1 n'est pas reproductible par le code actuel : `git checkout 7fd35eb`.
Effet mesuré sur la fidélité (oracle) : IoU de cellules moyen 0,939 → **0,905** (le village passe de 2 à 1 cellule, la route 0,78 → 0,82) ; pièces 148 → 153. Les corrections ont donc un coût de fidélité faible mais mesuré.

## 3. Résultats (île témoin, 2.5D) — `results/` ; 2D — `comparaison_2d_2_5d/ile_temoin_2d/`
| | 2.5D (7 couches, 22,4 mm) | 2D (3 couches, 9,6 mm) |
|---|---|---|
| Pièces / références | **153 / 53** | 171 / 52 |
| 1×1 | **9 (5,9 %)** | 11 (6,4 %) |
| Liaisons / tenons engagés | 285 / 2 627 | 238 / 2 048 |
| Collisions / pièces déconnectées / composantes | **0 / 0 / 1** | 0 / 0 / 1 |
| Plaques tenues par 1 tenon / points d'articulation | 9 / 25 | 11 / 16 |
| Coupe minimale du noyau (dos + niveau mer) | 2 tenons | 1 tenon |
| Force en bout minimale (modèle indicatif du moteur 1, 1 N / tenon supposé) | 2,18 N | 4,29 N |
| Étapes de notice / pièces max par étape | 15 / 43 | 11 / 56 |
| IoU de cellules moyen (oracle) / IoU pixels moyen | 0,905 / 0,671 | 0,905 / 0,671 |
| Hauteurs identiques à l'oracle | 98,7 % | 53,0 % (plat volontaire) |
Le relief **ne coûte pas de pièces** (153 contre 171 : les cellules cachées des couches basses forment de grandes plaques) mais ajoute 18 étapes de hauteur et un noyau moins épais.

**Fidélité par classe (IoU pixels / cellules)** : mer 0,96 / 1,0 ; terre 0,88 / 0,99 ; forêt 0,85 / 0,97 ; colline 0,74 / 0,96 ; lac 0,78 / 0,90 ; sommet 0,70 / 1,0 ; rivière 0,41 / 1,0 ; route 0,46 / 0,82 ; village 0,25 / 0,5. Fidélité des frontières (F1, tolérance 1 cellule) : 1,00. Les classes minces ont un IoU pixel bas par construction : 8 mm par tenon contre 4,5 px de large pour la rivière (≈ 0,56 tenon).
**Couleurs réelles des pièces** (ΔE CIE76 contre la source de l'oracle, valeurs LDraw) : moyenne pondérée **12,95** ; mer 8,7 ; lac 5,4 ; rivière 9,3 ; route 3,9 ; colline 13,1 ; village 18,2 ; **terre 18,5** (Tan) ; **forêt 21,2** ; **sommet 28,7** (gris clair : l'affectation injective l'éloigne du sable). Limites de la palette LEGO retenue, mesurées, non corrigées.
**Hauteurs** : 98,7 % des cellules identiques ; l'écart est le village (niveau 2 dans mon style, pas de marche dans l'oracle) : choix de style, pas une erreur de reconnaissance.

## 4. Généralisation : `test_3_zones.svg` (aucun oracle ; référence = remplissages exacts du SVG)
Classes trouvées par le moteur : mer, terre, forêt (aucune classe fantôme). IoU de cellules 1,0 / 1,0 / 1,0, IoU pixels 0,97 / 0,92 / 0,91, ΔE 13,3. 119 pièces (2 × 1×1 = 1,7 %), 36 références, 8 étapes, 0 collision, 0 déconnexion, force en bout min 2,73 N ; version 2D : 127 pièces.

## 5. Rigidité, connexions, complexité
Les contrôles (moteur 1 + moteur 2) : couverture de couche exacte, aucune plaque sans appui, 1 composante connexe, dimensions 256 × 256 mm × 22,4 mm, 0 collision. Le dos (2 couches décalées) donne une coupe minimale de 2 tenons dans le noyau seulement à cause d'**une plaque feuille** (1 à 2 tenons) ; la structure d'ensemble est tenue par ≥ 2 600 tenons. **Points faibles mesurés** : 9 plaques de relief attachées par 1 tenon (dont 9 des 1×1), 25 points d'articulation (feuilles), alignement des joints entre couches de relief 0,14–0,75 (la couche 3→4 de 0,75 est très alignée mais ne porte que 7 pièces). Rigidité = **calcul indicatif** (1 N par tenon supposé), **aucun essai physique** ; aucune fixation murale n'est déclarée sûre.
Complexité de construction : 15 étapes, ≤ 43 pièces par étape, 153 pièces dont 41 de dos ; 7 couches.

## 6. Notice, rendus, viewer
`notice.pdf` (18 pages A4) : synthèse et avertissements, régions et couleurs, nomenclature, puis **une étape par région et par couche** (vue de dessus, pièces déjà posées en pâle, tableau des références, liste « #id (colonne, ligne) » traçable). Contrôle de cohérence (`validation/coherence_sorties.json`) : 153 pièces identiques dans `map.ldr`, `parts.json`, `parts_list.csv` et le plan d'étapes (sans doublon, couverture complète). **La notice est une séquence numérique, pas la preuve d'un montage physique.** Rendus (géométrie LDraw réelle) : face, profil, trois-quarts, 3 rotations, zooms sur village / sommet / lac (+ vues en relief). `viewer.html` : fichier autonome, rotation / zoom / survol des pièces / curseur de couches (géométrie simplifiée boîte + tenons aux cotes LDraw) ; vérifié sans erreur de console.

## 7. Prix et stocks
Briquestore seul (https://store.bricklink.com/briquestore.fr). Une requête unique le 2026-11-03 : statut HTTP 202 (page non exploitable par machine) ; **aucun contournement**. Prix, stock et date de vérification restent **vides / `null`** dans `parts_list.csv` ; la colonne `rebrickable_sets_count` n'est qu'un indicateur d'existence technique de la pièce dans la couleur, **pas un stock**. Aucune commande réalisable n'est prétendue.

## 8. Limites
Un seul oracle ; test de généralisation très simple (3 zones) ; la reconnaissance repose sur des règles de famille de teinte (pas testée sur des photos, des dégradés, du texte ou des cartes à plus de 9 classes) ; relief purement artistique ; ΔE élevés sur terre, forêt, sommet ; classes minces imprécises au pixel ; 1×1 résiduels (9) ; pas de tuiles de finition ni de cadre ; aucun essai physique ; rendu three.js légèrement plus sombre que les valeurs LDraw (≈ 5 %).
