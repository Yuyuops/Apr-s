# Phase 3 : peut-on automatiser cette méthode ?

## État réel du programme V5.1 (sans exagération)

`scripts/design_v51.py` **n'est pas un moteur automatique.** Une partie est choisie à la main et inscrite telle quelle, une autre est produite par des règles.

| Élément | Comment il est produit |
|---|---|
| Contour : choix et place des 17 pièces de la face extérieure (demi-disque, ailes, plaques) | **À la main** (liste `OUTER`, reprise de V5 et décalée d'une rangée) |
| Racine : pièces R1-R2, zone de racine de l'âme, bloc de racine | **À la main** |
| Position de la plaque tournée | Recherche exhaustive sur la grille de la tête (coïncidences 3-4-5, plaque recouverte par la tête, distance aux yeux et à la bouche). Le résultat a été choisi et inscrit à la main. |
| Face intérieure | **Règle** : miroir de chaque pièce de la face extérieure, choix main gauche/droite et rotation par recouvrement d'empreinte |
| Tuiles | **Règle** : tuile de même taille, ou tuile sur la rangée de tenons des ailes. Exception : le bout arrondi, tuilé à la main. |
| Âme | **Règle** : assises remplies le long du contour (briques à tenons latéraux, plaques à joints décalés, âme ajourée, tuiles de fermeture) |
| Assise sous la plaque tournée, creusement de la tête, reconstruction de la tête | **Règle** (calcul des coïncidences, `brickify_plus`) |
| Contrôles (collisions, connexions, notice, catalogue, tenue, rendus) | **Automatiques** (`validate_v2.py`, `reorder_notice.py`, `render_ldr.js`) |

## 1. Modules standard réutilisables

1. **Fixation par coïncidence 3-4-5.** Plaque tournée noyée, 1×1 aux positions coïncidentes, rien ailleurs. Elle sert pour tout détail orienté à 53,13° (ou 36,87°) par rapport à la grille. Elle est générique et déjà calculée par programme.
2. **Panneau sandwich à deux faces finies.** Face en plaques et tuiles, âme d'un tenon à tenons latéraux tous les 40 LDU, face miroir. Il sert pour les oreilles, nageoires, ailes, crêtes, queues plates. Épaisseur fixe de 52 LDU (20,8 mm) ; une version mince sur une seule face (V5, 24 LDU) est aussi disponible.
3. **Racine noyée.** Âme prolongée dans le volume de la tête, bloc sur la plaque tournée, tête reconstruite autour.
4. **Finitions.** Tuiles de même taille, tuiles quart de rond 1×1 sur les courbes, rangée de tuiles sur les ailes.

## 2. Ce qui peut être paramétré automatiquement

| Paramètre | Automatisable ? | Limite |
|---|---|---|
| Taille | Oui, par changement d'échelle du contour puis nouvelle sélection des pièces | Les pièces de forme ont des tailles fixes : sous environ 6 tenons de long, il en reste trop peu pour dessiner une courbe |
| Contour | Oui (voir §4), à partir de la silhouette du GLB dans le plan du détail | Qualité dépendante du catalogue de pièces de forme |
| Orientation | Partiellement : seuls des angles « pythagoriciens » donnent des emboîtements exacts, 0°, 36,87° et 53,13° (3-4-5), 22,6° et 67,4° (5-12-13), 28,1° (8-15-17). | Entre ces angles : charnières, avec moins de tenue |
| Épaisseur | Partiellement : 24 LDU (une face), 52 LDU (sandwich), 92 LDU (âme de 2 assises de briques, à essayer). Variation locale par retrait des tuiles et de l'âme | Pas de valeur continue |
| Fixation | Oui : recherche des positions de plaque avec coïncidences soutenues, recouvertes par la tête et loin des zones protégées (déjà programmée) | Nombre de coïncidences limité (1 sur 5) : il faut de grandes plaques ou plusieurs niveaux |

## 3. Ce qui exige encore une conception manuelle

- **La décomposition fine du contour** en pièces de forme quand plusieurs familles se recoupent : quelle aile pour quelle pente, où couper, quelle pièce sur quel rang pour accrocher l'âme. En V5.1, deux ailes ont exigé de laisser dépasser l'âme.
- **Le raccord** : où le détail entre dans le corps, la taille du bloc de racine, et la vérification visuelle des affleurements. Deux itérations ont été nécessaires ici, la tête n'étant pas du côté attendu.
- **Les cas sans pièce adaptée** : tenons de la dernière assise au bord supérieur, miroir imparfait des ailes asymétriques.
- **Le jugement visuel final.** Les métriques ne le remplacent pas (règle de la mission).

## 4. Comment un futur algorithme pourrait choisir et agencer les pièces depuis le GLB

1. **Plan du détail.** Isoler le détail dans le GLB (couleur ou segmentation), ajuster son plan moyen, arrondir l'orientation à l'angle pythagoricien le plus proche. L'écart est un critère.
2. **Contour.** Silhouette projetée, convertie en polyligne dans la grille des tenons (pas de 20 LDU, rangées alignées sur l'âme).
3. **Segmentation du contour** par courbure : arcs (rayon 1, 2 ou 4 tenons), pentes (0,25 / 0,33 / 0,5 tenon par tenon), droites.
4. **Choix des pièces de forme par programmation dynamique le long du contour.** Chaque pièce du catalogue est un gabarit avec empreinte, pente et rayon. Le coût combine l'écart au contour en LDU, le nombre de pièces, une pénalité si la pièce ne couvre aucune rangée d'accroche et une pénalité de disponibilité. C'est l'étape qui remplace le choix manuel. **Ce n'est pas l'ancien remplissage voxel :** on suit un bord, on ne remplit pas des cellules.
5. **Intérieur** : rectangles maximaux, joints décalés par rapport à l'âme. **Âme, miroir, tuiles et racine** : règles de V5.1.
6. **Fixation** : la recherche de coïncidences de V5.1. Si la tenue est insuffisante, ajouter un 2e niveau de plaque tournée.
7. **Boucle de validation** : collisions, connexions, notice, catalogue, tenue, rendus. En cas d'échec, l'étape 4 recommence avec des pénalités modifiées.
8. **Contrôle humain sur rendu** avant toute validation (critère inchangé).

**Prochaine étape possible (non engagée) :** programmer l'étape 4 seule et la tester sur cette oreille. Le critère serait de retrouver, sans liste manuelle, un contour au moins aussi proche que la liste `OUTER` de V5 (IoU de contour 0,86). Rien n'est encore automatisé à ce niveau.
