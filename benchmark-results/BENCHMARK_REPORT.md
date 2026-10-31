# Benchmark des moteurs de construction LEGO : rapport final

**Date : 2026-10-31. Sujets : Paco (bipède jaune et rouge) et le Beagle (quadrupède marron et blanc). Hauteur cible : 250 mm, avec un essai à 400 mm.**

Toutes les images LEGO de ce dossier sont calculées à partir des fichiers `.dat` officiels de la bibliothèque LDraw,
référencés par le `.ldr` produit par le moteur. Aucune retouche et aucune IA générative n'interviennent dans les rendus LEGO.
**La fidélité visuelle reste à valider par vous** : les commentaires ci-dessous sont des constats, pas une validation.

Planches principales :
- `03_lego_brickify/paco_reference_vs_lego.png`
- `03_lego_brickify/beagle_reference_vs_lego.png`
- GLB avant conversion : `02_glb_gratuit_hunyuan2mv/paco_reference_vs_glb.png`, `02_glb_gratuit_hunyuan2mv/beagle_reference_vs_glb.png`

---

## 1. Décision

| Question | Réponse |
|---|---|
| Le maillage 3D est-il le blocage ? | **Non.** La forme produite gratuitement par Hunyuan3D-2mv à partir des 4 vues est fidèle pour les deux chiens. Pour Paco : tête de profil, deux grandes oreilles en plaques, salopette, mains, pieds. Pour le Beagle : oreilles tombantes, langue, queue relevée, quatre pattes. Les couleurs du GLB ont été projetées depuis vos images, sans IA (voir §3). |
| brickify produit-il un résultat reconnaissable ? | **Oui pour la silhouette, sous les 4 angles.** Le rendu est « cubique », c'est structurel (voir §5). À 250 mm, les yeux et le badge « P » de Paco disparaissent ou se réduisent à 1 ou 2 tenons. À 400 mm, ils réapparaissent. |
| Est-il constructible tel quel ? | **Non, pas sans corrections.** Défauts mécaniques (oreilles ou bras retenus par 1 seul tenon), notice fausse sur 83 à 486 pièces, combinaisons pièce × couleur jamais produites sur le Beagle, image miroir. Détails en §4. |
| AutoTile fait-il mieux ? | **Non.** Sur les mêmes GLB, sa sortie LDraw contient des collisions et des centaines de pièces déconnectées (§6). |
| Faut-il payer fal.ai (Hunyuan3D v3.1 Pro) ? | **Pas pour la forme.** Ce serait éventuellement utile pour de meilleures couleurs sur Paco (0,525 $), à décider par vous (§7). |

**Verdict brickify : AMÉLIORER.** Ni GARDER tel quel, ni ABANDONNER.
Classement des causes d'échec selon votre README : **limite du catalogue rectangulaire de brickify** (rendu cubique, petits détails perdus),
**défaut mécanique** (appendices retenus par 1 tenon) et **notice insuffisante** (ordre de pose). Ce n'est **pas** un « blocage au maillage IA ».

## 2. Chaîne exécutée

| Étape | Outil | Coût |
|---|---|---|
| Images → forme 3D | Hunyuan3D-2mv (démo Hugging Face officielle `tencent/Hunyuan3D-2mv`, commit `98b7866`, modèle `hunyuan3d-dit-v2-mv-turbo`), 4 vues face / dos / gauche / droite sur fond blanc, 30 étapes, octree 256, graine 1234 | gratuit (quota ZeroGPU anonyme) |
| Couleurs | `tools/colorize_from_views.py` : projection des 4 images de référence sur le maillage, sans IA | gratuit |
| GLB → LEGO | brickify **original non modifié** (`1564bb3`), puis rendus, validation indépendante et notice | gratuit |
| Comparaison | AutoTile `bf16473`, chemin `--mesh` (sans GPT, SAM ni Replicate) | gratuit |

**Aucun appel payant n'a été fait.**

Incidents rencontrés et corrigés, tous documentés :
1. **Première génération ratée (une boîte).** Les images détourées sur fond transparent sont mal lues par la démo. Les entrées sur fond blanc (`*_blanc.png`) donnent la bonne forme. Le quota gratuit étant épuisé, la version avec texture de Hunyuan n'a pas pu être lancée, d'où la projection des couleurs.
2. **brickify n'accepte que des GLB texturés** (`visual.to_color()`). `tools/vcol_to_texture.py` place les couleurs dans une texture, à raison d'un texel par sommet. La relecture des couleurs est vérifiée **à l'identique**.
3. **Bug de mon validateur, corrigé.** « Grey » (LDraw) et « Gray » (Rebrickable) ne correspondaient pas. Les gris étaient donc faussement déclarés « jamais produits ». Le constat n°2 du rapport intermédiaire (Bright Light Orange) n'est pas concerné.

## 3. Modèles 3D (avant conversion)

| | Paco | Beagle |
|---|---|---|
| Faces conservées (plus grand composant) | 231 740 sur 374 524. Le reste n'est que des triangles isolés parasites. | 380 110 sur 692 728 (idem) |
| Composants réels | 1 (oreilles, bras et queue rattachés au corps), donc `--components 1` suffit | 1 |
| Recalage des couleurs (IoU de silhouette) | face 0,81 · dos 0,73 · profil gauche 0,69 · profil droit 0,80 | face 0,92 · dos 0,84 · profils 0,85 / 0,86 |
| Défauts visibles | Traînées jaunes sur les flancs de la salopette, une main rouge, un trait noir sur le museau. Cause : la tête de la vue de face est tournée de trois quarts, la pose diffère entre les vues, et les références sont des rendus en perspective. | Très fidèle. Zones blanches légèrement ombrées. |

## 4. Résultats brickify (validation indépendante, `*_validation.json`)

Passage **brut** = commande de votre README (`--colour-mode palette --palette-passes 2 --interior dominant`).
Passage **réglé** :
- entrée pré-inversée en X (`tools/mirror_x.py`) pour annuler le miroir de brickify ;
- `--exclude` pour ne garder que les couleurs des références : Paco jaune, rouge, noir, blanc ; Beagle blanc, Dark Orange, Medium Nougat, Reddish Brown, Dark Brown, noir, rose ;
- `--palette-passes 4`.

| | Paco brut 250 | Paco réglé 250 | Paco réglé 400 | Beagle brut 250 | Beagle réglé 250 | Beagle réglé 400 |
|---|---|---|---|---|---|---|
| Pièces | 1 400 | 1 105 | 2 920 | 3 539 | 3 189 | 8 329 |
| Taille (l × p × h, mm) | 176×176×253 | 176×176×253 | 280×280×403 | 152×296×253 | 152×296×253 | 240×464×403 |
| Collisions | 0 | 0 | 0 | 0 | 0 | 0 |
| Pièces non reliées au sol (brickify et mon contrôle) | 0 | 0 | 0 | 0 | 0 | 0 |
| Îlots posés au sol mais non fixés au corps (pièces) | 1 (8) | 5 (20) | 1 (5) | 12 (76) | 12 (60) | 9 (63) |
| Pièces posées dans le vide selon la notice | 85 | 83 | 213 | 198 | 177 | 486 |
| Liaisons à 1 seul tenon | 1 254 / 1 710 | 999 / 1 375 | 2 524 / 3 792 | 3 409 / 4 522 | 3 075 / 4 259 | 7 531 / 11 876 |
| **Point de rupture le plus grave** | **bras : 92 pièces / 1 tenon** | **oreille noire entière : 299 pièces / 1 tenon** | museau : 173 pièces / 12 tenons | oreille : 36 pièces / 1 tenon | appendice avant-haut (tête ou oreille) : 71 pièces / 3 tenons ; aucun point à 1 tenon | une oreille : 42 pièces / 1 tenon |
| Angle de basculement | 12,8° | 12,7° | 13,7° | 27,6° | 27,5° | 26,9° |
| Pièce × couleur jamais produite | 0 | 0 | 0 | 9× plaque 6×8 Dark Orange | 6×8 (9) et 4×4 (1) Dark Orange | 6×8 (21) et 4×4 (2) Dark Orange |
| Pièce × couleur rare (< 5 sets) | 1 | 0 | 0 | 8 | 6 | 8 |
| Étapes / pages de notice | 220 / 80 | 189 / 78 | 438 / 127 | 492 / 80 | 443 / 80 | 1 118 / 127 |

Lecture :
- **Le miroir est confirmé et imputable à brickify.** Mon rendu applique une vraie rotation (Y et Z inversés). brickify n'inverse que Y. Sur le passage brut, la tête de Paco regarde à droite au lieu de gauche. La pré-inversion de l'entrée corrige le problème sans toucher au moteur.
- **Les réglages de couleur aident Paco** : les gris, oranges et rouge foncé parasites disparaissent. Ils **dégradent un peu le Beagle** : le poitrail blanc se mouchette de Medium Nougat, au lieu du gris clair du passage brut. Aucun réglage n'est parfait, car l'ombrage des références est lu comme une couleur.
- **La mécanique dépend de la taille et du hasard du pavage.** À 250 mm, un appendice entier de Paco (bras ou oreille) tient par 1 tenon. À 400 mm, le pire point de Paco tient par 12 tenons, mais une oreille du Beagle tient encore par 1 tenon. Paco, bipède, a peu de marge au basculement (≈ 13°).
- **Les « îlots »** sont de petits groupes de pièces au pied des pattes. Ils touchent le sol, donc brickify les compte comme non flottants, mais ils ne sont pas fixés au modèle.
- Ces contrôles sont **géométriques, pas un essai physique**. L'inspection humaine reste obligatoire (README, critère 2).

## 5. Limites structurelles (non réglables)

1. Le catalogue ne contient que des briques et plaques rectangulaires (28 types utilisés au plus) : pas de pentes, tuiles, pièces rondes ni SNOT.
   Les grandes oreilles en plaques fines et arrondies de Paco deviennent des escaliers de 1×1 et 1×2. Ses yeux et son badge « P » ne sont lisibles qu'à 400 mm.
2. Le pas horizontal de 8 mm (1 tenon) fixe la finesse du rendu. À 250 mm, le bras de Paco fait environ 2 tenons de large.
3. Le pavage ne tient pas compte des couleurs. Résultat : des pièces Dark Orange de grande taille jamais produites, ou très rares.
4. L'ordre de la notice suit les couches. Les pièces qui ne tiennent que par le dessus apparaissent « posées dans le vide ».

## 6. Comparaison AutoTile (mêmes GLB, sans réglage)

| | Paco (résolution 32) | Beagle (résolution 37) |
|---|---|---|
| Éléments | 681 (dont 70 tuiles, 14 pentes) | 3 296 (220 tuiles, 40 pentes) |
| Taille (mm) | 184×192×326 | 168×320×336 |
| Collisions | **215 paires** | **1 013 paires** |
| Pièces non reliées au sol | **626** | **1 159** |
| Pièces jamais produites dans cette couleur | oui (références de pente renommées, etc.) | oui (brique 4×10 et 1×12 Dark Orange, etc.) |

Il propose des pentes et des tuiles, mais sa sortie LDraw n'est pas constructible. Je ne l'ai pas débogué : une partie des défauts peut venir de son exportateur LDraw.
En l'état, **AutoTile n'est pas une alternative à brickify** pour ces sujets. Les rendus sont dans `04_autotile/`.

## 7. Suite proposée (à décider par vous)

1. **Valider visuellement** les planches `*_reference_vs_lego.png`. C'est le premier critère d'acceptation.
2. **Améliorations ciblées de brickify, si vous le souhaitez.** Rien n'a été modifié dans le moteur :
   - corriger le miroir à la sortie ;
   - interdire les liaisons à 1 tenon sur les appendices ;
   - choisir les pièces en fonction des couleurs réellement produites (Rebrickable) ;
   - supprimer ou rattacher les îlots ;
   - remettre en ordre les étapes de la notice.
3. **Option payante facultative** : Hunyuan3D v3.1 Pro pour Paco seul (0,525 $), pour obtenir une texture cohérente à la place de la projection.
   Le prix officiel a été relu le 2026-10-31 : 0,375 $ + 0,15 $ pour le multivue, soit 35 unités à 0,015 $. **Non exécuté.**
4. Coût des pièces et durée de montage : **non vérifiés** (aucune donnée BrickLink collectée). BrickLink Studio n'a pas été utilisé : il n'existe pas en version Linux.

## 8. Fichiers

- `02_glb_gratuit_hunyuan2mv/` : GLB colorés (`paco.glb`, `beagle.glb`), réponses de la démo, rapports de projection, planches 5 vues.
- `03_lego_brickify/<chien>_<brut250|regle250|regle400>/` : contenu de chaque dossier :
  - modèle et commande : `.ldr`, `*_command.txt`, `*_brickify.log` ;
  - listes de pièces : `*_parts_list.csv`, `*_inventory.csv`, `*_bricklink_wanted.xml` (à importer **sans acheter**) ;
  - contrôles : `*_report.json` (brickify), `*_validation.json` (contrôle indépendant) ;
  - notice et rendus : `*_instructions.pdf`, `renders/`.
- `04_autotile/` : sorties AutoTile, rendus et validation.
- `00_proxy_dress_rehearsal_fox/` : répétition sur le proxy (inchangée).
- Les GLB fournis par vous (« volumes géométriques », `chiens_glb_regeneres_2026_10_31.zip`) n'ont servi que de contrôle technique. **Ils ne sont utilisés dans aucun résultat.**
