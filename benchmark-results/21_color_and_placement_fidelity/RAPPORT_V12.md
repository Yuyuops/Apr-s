# Rapport V12

## 1. Ce qui a été corrigé (génériquement)
| Cause trouvée par l'audit V11 | Correction | Où |
|---|---|---|
| Couleurs de Paco câblées (jaune 14, rouge 4, blanc 15, noir 0) dans les détails, la bouche, l'assemblage, la segmentation | Les classes de détail sont déduites de la géométrie, de la position et des couleurs **observées** dans le GLB ; la palette est une donnée du sujet (`palette_util.py`). Plus aucun code de couleur littéral dans `detect/microdetails/lcm82/assemble_v82/segment/integrate`. Avec la palette V11 figée, Paco reste **identique octet pour octet à V9.1** (sha256 f878c3b7…) | `palette_util.py` + modules |
| Palette figée à la main par sujet | Sélection automatique : couleurs LDraw opaques dont les pièces de base existent dans ≥ 20 sets Rebrickable (≥ 60 pour être « non rare »), ajout glouton d'une couleur seulement si ΔE moyen −0,8, ≥ 3 % de la surface, ≤ 8 couleurs ; couleurs de contraste (noir, blanc) ajoutées et signalées. Aucune disponibilité ni prix inventés | `palette_select.py` → `modeles/*_palette.json` |
| Pièces dont la couleur ne correspond pas à la surface du GLB (plaques de fixation noires, erreurs de quantification) | Réparation **couleur seule** : une pièce exposée prend la couleur de la palette (pièce×couleur existante, ≥ 20 sets) qui minimise ΔE vs la surface GLB, si le gain est ≥ 30 % et ≥ 8 ΔE/cellule. Pièces hors treillis (fixations, oreilles) : toujours évaluées ; pièces du volume : seulement s'il y a une cellule parasite (excès ≥ 40). Aucune pièce déplacée, ajoutée, retirée | `colour_repair.py` → `*_colour_repair.json` |
| Règle de « peau noire » de l'oreille câblée sur le code 0 | Couleurs neutres sombres de la palette du sujet (`dark_neutral`). Sans cela, la palette automatique laissait 4 plaques du volume en collision avec l'oreille basse (7 paires) — détecté par le validateur, corrigé avant la mesure finale | `integrate.py` |

## 2. Avant / après (audit de fidélité, mêmes cellules exposées : 6212 Paco, 11846 Beagle)
| | Paco V11 | Paco V12 | Beagle V11 | Beagle V12 |
|---|---|---|---|---|
| ΔE moyen / médian | 20,4 / 12,9 | **15,5 / 12,5** | 17,1 / 15,6 | **14,7 / 13,3** |
| Cellules parasites (excès ≥ 40) | 369 | **114** | 195 | **31** |
| dont noires sur jaune/rouge/blanc | 237 | **25** | — | — |
| Cellules sans correspondance catalogue (≥ 30) | 467 | **182** | 0 | 31 |
| Parasites du module d'oreille (fixations) | 106 | **20** | — | — |
| Couleurs de Paco (jaune, rouge) dans le Beagle | — | — | 106 plaques | **0** |
| Cellules de pièces structurelles visibles (audit) | 5 (87087) | 5 (87087 : nez, volontairement exposé) | | |
| IoU d'occupation (silhouette) | 0,867 | 0,867 | 0,998 | 0,998 |
| Pièces / étapes | 3098 / 202 (notice V9.1) | 3193 / 371 | 11111 / 593 | 10498 / 602 |
| Collisions / pièces déconnectées / sans appui | 0/0/0 | **0/0/0** | 0/0/0 | **0/0/0** |
| Facteur de sécurité gravité minimal (indicatif) | 11,2 | 9,8 | 38,2 | 15,8 |
| Sous-ensembles à force en bout < 0,5 N | 7 | 8 | 10 | **32** |
Palette Paco V12 : Orange, Noir, Jaune, Rouge, Dark_Tan, Blanc (554 cellules de grille changent de couleur, occupation identique). Palette Beagle V12 : Dark_Tan, Dark_Orange, Blanc, Reddish_Brown, Noir (Medium_Nougat et Dark_Brown ne sont plus choisis ; aucun jaune/rouge).
Le sommaire des parasites restants de Paco est dans `audit_apres/audit_paco_v12.json` (types : 3023 ×24, 43898 ×19 [pièce de détail, hors réparation], 3623, 3069b, 3031, 3034…). 182 cellules de Paco n'ont toujours aucune couleur LEGO acceptable (ΔE ≥ 30 : tons orangés/translucides du GLB) : elles sont **rapportées, non masquées**.

## 3. Fixations d'oreilles visibles (Phase 3)
Moyen générique : couleur de surface sur les plaques exposées (plaques 3035/3034/3031/3008/3007, tuiles 3069b/3070b, 52107, 3666 de la racine), dans une couleur où la pièce existe (≥ 20 sets). Aucune pièce n'est retirée ni déplacée : le graphe de tenons est identique avant/après réparation (même géométrie pour les 3193 pièces, 123 changements de couleur seulement ; vérifié ligne à ligne). Les vérifications V9.1 (`checks_v91.py`) sur le modèle V12 : 89 couples pièce×couleur « vérifiés » dans le catalogue, 8 (oreille basse) et 7 (oreille haute) pièces de contact avec la tête, 1 chemin disjoint depuis le bout libre — **valeurs identiques à V11** (l'indépendance n'est donc ni améliorée ni dégradée ; elle reste celle héritée de V7). Séquence d'assemblage et renforts de bord d'oreille V9.1 inchangés dans la réparation. Résultat : cellules d'oreille parasites 106 → 20. Restent exposées (couleur sans meilleure alternative disponible ou trop peu de gain) : 3031 ×8, 3034 ×8 notamment ; elles ne sont pas masquées plus avant. **Limite visible** : quelques cellules orange/jaune apparaissent à la jonction oreille-crâne (rendu `rendus/paco_5_trois_quarts.png`) : l'orange est justifié par le GLB (ombre jaune-orangé) mais se voit.

## 4. Placement des deux oreilles (Phase 4, `placement_oreilles/`)
Écart de centroïde au GLB (mm), trois nuages LEGO sur une même définition GLB : tout le sous-ensemble / cellules de l'oreille / cellules exposées.
| | tout | zone | visible |
|---|---|---|---|
| Oreille basse V11 | 17,6 | 6,2 | 2,1 |
| Oreille haute V11 | 11,1 | 15,5 | 25,2 |
| Oreille haute V12 | 9,5 | 13,5 | 21,8 |
Dénivelé entre les oreilles : GLB 87,7–89,3 mm contre LEGO 98,0 (tout), 105–106 (zone), 111–113 (visible).
Conclusion : (a) **l'oreille basse est bien placée** (2–6 mm sur la surface visible) ; son écart de 17,6 mm vient du **volume de racine** (bloc de fixation enterré dans la tête), pas du placement. (b) L'oreille haute montre 14–25 mm d'écart sur ses surfaces zone/visible : la silhouette LEGO est un empilement par plaques de 8 mm / 20 mm, plus épais que la fine oreille du GLB, et la définition GLB (sommets sombres) est partielle ; je n'ai **pas de preuve d'une erreur géométrique** du placement lui-même et aucune validation de fixation pour le déplacer. **Aucune oreille n'a été déplacée ni symétrisée** (source asymétrique). Le surplus de dénivelé reste donc non expliqué à 10–20 mm près : limite ouverte.

## 5. Non-régression
- Paco avec la palette V11 figée : brut identique octet pour octet à V9.1 (hash vérifié après toutes les modifications V12).
- Tests : 15/15 (`tests/resultats_tests.json`). Nouveaux : T8 (baseline V12, `refs/audit_baseline_v12.json`), T9 (V12 meilleur que V11 sur chaque sujet sans modifier la baseline historique), T10 (Beagle sans couleurs de Paco), T10b (0 collision / déconnexion). Les baselines et références V9.1/V10/V11 ne sont pas touchées (T2 : 38 empreintes intactes).
- Reproductibilité : relancer `lego_run.py` avec la base Rebrickable de référence ; une base plus récente peut changer la palette automatique (disponibilités) — c'est consigné dans `*_palette.json`.

## 6. Limites honnêtes
1. **Beagle : points faibles accrus** (32 vs 10 sous-ensembles à force en bout < 0,5 N ; SF gravité min 15,8 vs 38,2 — toujours ≫ 2). Cause : la nouvelle palette (Dark_Tan à la place de Medium_Nougat/Dark_Brown) fragmente autrement les plaques ; la réparation de couleur n'y change rien (mesuré avant/après). Modèle indicatif non physique.
2. Paco : +95 pièces (3098 → 3193) et 8 sous-ensembles < 0,5 N (7 en V11) à cause du regroupement par couleurs de la palette automatique.
3. Oreille haute : écart de placement visible non expliqué (§4). 20 cellules de fixation encore parasites. 182 cellules Paco sans couleur LEGO proche.
4. Aucun essai physique ; aucune disponibilité commerciale ou prix revendiqué (seuil ≥ 20 sets Rebrickable seulement).
