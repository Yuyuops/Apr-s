# Plan de génération — Italia 128 × 128 tenons (1 024 × 1 024 mm hors cadre, 1 056 mm avec cadre de 2 tenons ; 102,4 cm hors cadre)

Statut : **plan et prévisualisation de composition uniquement. Aucune fabrication, aucun modèle Italie complet généré.** Rejeu : `python compose.py && python sector_plan.py` (Python du moteur 1, données dans `fixtures/`).

## 1. Deux échelles indépendantes (`artistic_scale_config.json`)
- **Géographique** (fixe) : contour Natural Earth (Italie, Sicile, Sardaigne) projeté sur 128 × 128 (1 tenon ≈ 8 km, 2 290 cellules de terre), relief réel Terrain Tiles (z 6) converti en niveaux de brique (`niveau = 2,4·(altitude/1000 m)^0,9`, plafonné à 11, exagération verticale déclarée ≈ 25×), villes en position vraie.
- **Décorative** (réglable) : monuments (Colisée, Tour de Pise, Vésuve), titre, rose des vents, arbres. Empreintes en tenons `[lignes, colonnes]` dans le fichier de configuration, avec liste de tailles décroissantes et variante simplifiée ; priorités, marges, décalage maximal, suppression autorisée ou non. Aucune dimension n'est codée dans le code : `compose.py` lit le JSON (changer de pays = changer le fichier et les fixtures).
- **Politique de conflit** (automatique, journalisée dans `placements.json`) : garder l'ancre et la plus grande taille → décaler vers la terre → taille inférieure → variante simplifiée → suppression si permise sinon ÉCHEC signalé. Jamais de chevauchement avec zones réservées, bord de cadre, autres monuments (marge `clearance`).

## 2. Résultat de la composition (`output/composition_preview.png`, `sector_overlay.png`)
Titre ITALIA (35 × 7 tenons) en mer bas-gauche, rose des vents (15 tenons) en mer bas-droite, **Colisée 18 × 22 (décalé de 8 tenons vers le nord pour rester à terre, ancre vraie tracée en rouge)**, Tour de Pise 6 × 6 (décalée de 3,2), Vésuve 9 × 9 (1,0). **Risque de composition** : le Colisée plein cache environ 40 % de la largeur de la péninsule centrale et son plateau recouvre le relief des Apennins ; la variante simplifiée 15 × 18 est prévue dans la configuration. Décision à prendre sur rendu 3D, pas sur cette vue.

## 3. Sous-modèles et modules
| Module | État |
|---|---|
| Colisée | existant, paramétrique. Testé à 18 × 15 (293 pièces) et 14 × 11 (170 pièces) : valides (0/0/0/0), mais **sous ~18 × 22 il perd son ovale et devient une boîte à arcades** → prévoir une variante « icône » dédiée avant de descendre sous cette taille. |
| Montagne | existant (V0.5.3), appliqué sur le champ de niveaux réels ; à adapter : crêtes déduites du MNT au lieu de pics paramétriques |
| Tour de Pise, Vésuve | **à créer** (modules `pisa_tower`, `volcano_cone`) ; densités de pièces provisoires |
| Titre ITALIA, rose des vents | **preuve faite** : `decor_patch.py` génère les lettres (police 5 × 7 tenons) et la rose en vraies tuiles 1×1/1×2/1×4/2×2 : 229 pièces, validation moteur 1 propre (`output/decor_patch/`) |
| Végétation | uniquement conifères solides (rond 2×2 + cône 2×2, 4 + 4 tenons) sur terrasses 2×2, densité par niveau et ligne des arbres 300–1 900 m |
| Cadre décoratif | anneau de 2 tenons (briques + tuiles de couverture, système V0.2) ; non généré ici |
| Palette | verts/roches/neige de V0.5.3 + sable ; couples pièce/couleur contrôlés contre le catalogue Rebrickable par `verify_bom.py` |

## 4. Génération par secteurs (`output/sector_plan.json`)
16 secteurs de 32 × 32 tenons, découpés sur la grille des plaques de base 8 × 8, halo de 4 tenons ; champ de hauteurs global unique (les halos sont identiques, le secteur d'indice inférieur émet les pièces). Ordre : socle (16 × 16 plaques 8×8, 2ᵉ couche chevauchant les joints inter-secteurs) → mer → secteurs en lecture (briques, pentes, plages, terrasses, conifères) → sous-modèles de monuments (sous-fichiers LDraw placés comme un bloc) → titre et rose → cadre → validation moteur 1 du modèle fusionné + par secteur. Pièces estimées par secteur dans le JSON.

## 5. Estimation (ingénierie, non vérifiée)
**≈ 6 900 pièces (fourchette 5 200 – 9 400)**, mesurée sur les densités du diorama V0.5.3 : mer et socle 0,11 pièce/cellule, terre 0,54 + 0,20 par niveau moyen, Colisée 941. L'enveloppe de 10 000–25 000 pièces reste **non atteinte** à 128 tenons car 86 % de la grille est de la mer ; une fidélité supérieure viendrait des monuments et de la densité de relief, pas du nombre de pièces. Aucun budget imposé.

## 6. Prochaines étapes (hors mission)
1. Modules Pise et Vésuve ; 2. relief MNT → hauteurs par secteur avec la génération de montagne validée ; 3. un secteur pilote (S11 Toscane/Rome, le plus dense, ~1 500 pièces) généré, validé et rendu ; 4. décision de taille du Colisée sur rendu ; 5. assemblage des 16 secteurs.
