# Mode « biomes + relief » (V1.0) — Hyrule
Branche `research/lego-maps-v10-biomes-relief` (depuis la V0.9). Démonstrateur visuel : **pas une validation géographique du moteur**. Source : l'image que vous avez fournie (SHA-256 `4b9c7b22e3b461c0…`, droits inconnus, non versionnée) ; seuls la grille de classes (TIFF) et les règles sont versionnées.

## Résultat
| | Hyrule V0.9 (terre/mer/désert) | **Hyrule biomes + relief** |
|---|---:|---:|
| Pièces / références | 16 721 / 99 | **10 682 / 134** |
| Dimensions | 704 × 704 mm, 76,8 mm | 704 × 704 mm, 67,2 mm |
| Validation moteur 1 | 0 collision, 0 déconnectée, 0 îlot, 0 non supportée | **idem** |
| Catalogue | complet, 0 substitution | **complet, 0 substitution, 0 couleur de repli** |
| Reconnaissable ? | non (aplat brun) | **oui** : plaine verte centrale, désert au sud-ouest, volcan au nord-est, neiges au nord-ouest, lacs, mer à l'est et au sud |
Planche : `hyrule_biomes_3vues.png` / `biomes_compare.png` (envoyées dans la conversation), rendus `hyrule_biomes/renders/`.
Ce n'est **pas** la finesse du modèle d'origine (tours, arbres, château, relief détaillé) : à 80 × 80 tenons, la carte est faite de grandes régions colorées en terrasses.

## Comment ça marche (4 étapes, tout est en données)
1. **Mesurer** les 4 coins du plateau sur l'image (pixels) et écrire des **règles de couleur** par biome (teinte, saturation, luminosité) : `hyrule_biome_rules.json` ; gabarit : `biome_rules_template.json`.
2. **Classer** : `biomes_from_render.py SRC.jpg RULES.json OUT.tif PREVIEW.jpg --grid 80 80` : rectification de perspective, classification par couleur, lissage, régions minimales ; sort un TIFF dont la valeur de pixel est le code de classe (**TIFF et non PNG** : les PNG du dépôt sont des objets LFS que la CI ne lit pas).
3. **Décrire** dans la composition (`compositions/hyrule_biomes_80x80.json`) le fichier TIFF et les noms des classes ; dans le **style** (`styles/premium_biomes_hyrule.json`, section `biomes`) pour chaque biome : couleur du dessus, couleur des parois, niveau de base, gain de relief éventuel.
4. **Générer** : `build_style.py styles/premium_biomes_hyrule.json compositions/hyrule_biomes_80x80.json OUT --flank vertical`, puis les contrôles habituels (`check_render.py`, `verify_bom.py`, `fragility.py`, `notice_steps.py`, `check_delivery.py`) ; tout est dans `regen_deliverables.sh`.
Reproduire sur une autre carte : fournir une image, 4 coins, des règles, un style ; **aucun code à modifier**.

## Règles de hauteur (génériques, documentées)
- Niveau de base par biome (Hyrule : eau 1, désert 2, herbe et forêt 3, pierre 4, roche 5, neige 6), 2 plaques par niveau.
- **Gain intérieur** : pour les biomes qui en ont un, la hauteur monte d'un niveau tous les *step* tenons de distance au bord du biome, jusqu'à *max* niveaux (pierre : 5 tenons, +1 ; roche : 4, +2 ; neige : 3, +2). **C'est une heuristique de forme, pas l'altitude réelle de Hyrule** (aucune carte de hauteur n'a été extraite).
- Couleurs (toutes catalogues, aucune pièce inventée) : eau Bright Light Blue 212, herbe Bright Green 10, forêt Green 2, désert Tan 19, pierre Light Bluish Gray 71, roche Medium Nougat 84, neige White 15. Parois : couleurs voisines (Dark Green 288, Dark Tan 28, Dark Bluish Gray 72, Dark Brown 70, Light Bluish Gray 71). **Reddish Brown 88 et Dark Orange 68 n'existent pas dans le catalogue de paires du projet** : le brun-orangé du volcan est donc approché par Medium Nougat 84 (écart visible).
- Titre « HYRULE » sur terre (`allow_subject_land`) avec socle gris foncé (`backdrop_colour`) pour la lisibilité.

## Problème rencontré et correction mesurée (moteur 1 / pavage)
La première version colorait les parois par biome sur toute la hauteur : **15 002 pièces, 182 références**, et une structure très fragmentée.
Correction : les plans de paroi **cachés** par les voisins (aucun côté visible) prennent une couleur neutre (`hidden_wall` = Dark Bluish Gray 72) : plaques plus grandes, meilleur recouvrement. L'aspect extérieur est identique (vérifié en rendu côte à côte).
| | sans `hidden_wall` | **avec** |
|---|---:|---:|
| Pièces | 15 002 | **10 682 (−29 %)** |
| Références | 182 | **134** |
| Pièces à un seul tenon | 2 709 | **1 898** |
| dont porteuses | 1 857 | **1 050** |
| Points d'articulation | 2 301 | **1 532** |
| Pire défaillance simple | 18 pièces, 8,0 g | 24 pièces, **4,4 g** |
Indicateurs numériques, **pas des essais physiques**. À noter : la structure reste **bien plus fragile que les cartes à deux classes** (Hyrule V0.9 : 431 pièces à un tenon, 437 points d'articulation) ; le mode biomes multiplie les petites zones de couleur. À tester à la main avant toute construction.

## Non-régression
Italie, Japon et Hyrule V0.9 reconstruits avec le nouveau code : LDraw **identiques octet à octet** (le mode ne s'active qu'avec `biome_map`). La CI le revérifie pour les 8 modèles.

## Limites
Droits de l'image source inconnus ; proportions supposées carrées ; coins mesurés à l'œil (≈ 1 tenon) ; seuils de couleur réglés à la main sur cette seule image (la neige ombrée du nord-ouest est en partie classée « pierre ») ; pas de carte de hauteur ; pas d'îlots conservés en mode biomes (l'audit d'îlots n'est pas calculé) ; pas de notation artistique ; aucun essai physique, prix ni stock.
