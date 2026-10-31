# Itération Brickify V3 : finition des surfaces et assemblages SNOT, tête de Paco à 400 mm

Périmètre : museau, yeux et contour du visage, oreilles et leurs fixations. Le personnage entier n'est pas reconstruit.
Le GLB de référence n'a pas été modifié. Aucun service payant, aucune commande, aucun déploiement.

Documents :
- `VISUAL_COMPARISON.md` : comparaison visuelle ;
- `ASSEMBLY_VALIDATION.md` : validation technique ;
- `DECISION.md` : verdict et architecture proposée.

## 1. Audit préalable

| Point | Constat |
|---|---|
| Sources du prototype C | `tools/proto/brickify_plus.py --occupancy 0.5 --no-shapes`, grille `05_demonstrateur_tete_paco/paco_head400.npz` (voxellisation et couleurs de brickify d'origine, `tools/proto/headgrid.py`). **Reproduit à l'identique** : SHA-1 du `.ldr` `2a1a3b8a…`, contrôlé avant et après les modifications de cette itération. |
| Modules de conversion | `headgrid.py` (grille de brickify), `brickify_plus.py` (occupation 50 %, empilement de plaques croisées, réparation), `partlib.py` (formes mesurées dans LDraw). |
| Modules de contrôle | v1 : `validate_ldr.py` (tenons verticaux seulement). v2 (nouveau) : `validate_v2.py` + `conn.py`, indépendants de l'orientation (voir `ASSEMBLY_VALIDATION.md`). |
| Catalogue de C | 17 plaques rectangulaires et 6 tuiles, filtrées par couleur réellement produite (au moins 20 sets dans Rebrickable). Aucune pente, courbe ni pièce SNOT. |
| Pourquoi les pentes et courbes servaient peu (prototype B) | Elles étaient choisies une par une, chacune pour son gain local de forme, sans cohérence d'orientation, avec un seuil de gain élevé. Une fois l'occupation corrigée, presque rien ne passait ce seuil, et ce qui passait faisait des taches. |
| Pourquoi aucun montage non vertical | La grille de brickify est à tenons vers le haut seulement. Le validateur v1 ne savait lire que des tenons verticaux. Aucun module ne savait placer ni vérifier une pièce tournée de côté. |
| Résultats antérieurs | Conservés tels quels dans `03_…` et `05_…`. Le prototype C sert de référence reproductible. |

## 2. Ce qui a été ajouté

- **`tools/conn.py`.** Pour toute pièce LDraw, les positions et directions de chaque tenon (dessus, côté, équerre) et de chaque point d'appui, lus dans la géométrie officielle.
- **`tools/validate_v2.py`.** Validateur indépendant de l'orientation :
  - liaisons tenon/point d'appui en 3D ;
  - collisions sur une grille de 4 LDU, et tenons qui butent sur une autre pièce ;
  - ordre de notice avec sous-ensembles ;
  - catalogue ;
  - stabilité, pour chaque direction de tenons ;
  - fidélité.

  Sur C, il retrouve les valeurs de la v1 : même fidélité, mêmes collisions, mêmes pièces déconnectées, même ordre de pose, même coefficient minimal (38,23).
- **`tools/reorder_notice.py`.** Réordonne la notice pour qu'aucune pièce ne soit posée sans liaison avec une pièce déjà posée. Appliqué de la même façon à C, D et E.
- **`brickify_plus.py --finish`** (variante D). Finition des dessus visibles à partir de la normale du modèle 3D lissé :
  - surface à moins de 20° : tuile ;
  - de 20° à 60° : pente 1×1 30° (54200) tournée vers le bas de la pente ;
  - au-delà : paroi conservée.

  Les tenons noirs des oreilles sont gardés, comme sur la référence.
- **`snot_ears.py`** (variante E). Oreilles reconstruites en deux couches de plaques noires à tenons horizontaux, accrochées à des briques à tenon latéral (87087) intégrées à la tête. Les briques d'accroche sont espacées de 5 plaques en hauteur, pour tomber sur la grille de 20 LDU de l'oreille.

## 3. Protocole commun aux trois versions

- Même GLB (`02_glb_gratuit_hunyuan2mv/paco.glb`, corrigé du miroir), même échelle (400 mm pour le personnage complet), même grille de tête (27 × 56 × 35 cellules).
- Rendus avec `tools/proto/render_set.sh`, à partir des pièces LDraw réelles et sans retouche, avec des **boîtes de cadrage fixes en mm**. Le centre, la distance, la lumière et la taille d'image sont donc identiques d'une version à l'autre.
  - Vue complète : `[[0,0,-280],[216,179.2,0]]`.
  - Museau : `[[56,51.2,-280],[208,115.2,-150]]`.
  - Oreilles : `[[0,0,-150],[120,179.2,0]]`, angle 40°.

## 4. Reproduire (depuis `~/bench`, outils de `benchmark-results/tools`)

```bash
H=benchmark-results/05_demonstrateur_tete_paco/paco_head400.npz
# C (référence)
python tools/proto/brickify_plus.py $H out/C paco_tete_C_seuil --occupancy 0.5 --no-shapes
# D
python tools/proto/brickify_plus.py $H out/D paco_tete_D --occupancy 0.5 --no-shapes --finish --tiles-all --studded 0
# E
EARS_PANELS=2 EAR_DISP_W=3 EAR_MIN_ANCHORS=3 python tools/proto/snot_ears.py $H out/E paco_tete_E \
    --occupancy 0.5 --no-shapes --finish --tiles-all --studded 0 --drop-floating
# notice, validation, rendus (pour chaque version)
python tools/reorder_notice.py out/D/paco_tete_D.ldr out/D/paco_tete_D_notice.ldr
python tools/validate_v2.py --ldr out/D/paco_tete_D_notice.ldr --ldraw <ldraw> --rbdb data/rb.db --out out/D --name paco_tete_D_notice --npz $H
tools/proto/render_set.sh out/D/paco_tete_D.ldr out/D/r6
```

**Versions :** identiques à `VERSIONS.md`. brickify `1564bb3` (fonctions importées sans modification), LDraw `1f24cac`, rb.db latest-v8, Python 3.13.18, trimesh 5.2.0, numpy 2.5.4, networkx 3.7, embreex 4.4.0.post1, scikit-learn 1.9.1, three.js 0.160.0.

## 5. Fichiers

- `variante_{C,D,E}/` : contenu de chaque dossier :
  - `*.ldr` : notice réordonnée, modèle de référence ;
  - `*_brut.ldr` : sortie directe du générateur ;
  - `*_nomenclature.csv` : nomenclature avec le statut catalogue ;
  - `*_validation_v2.json` et `rendus/`.
- E contient aussi `anchors.json` (briques d'accroche) et `paco_tete_E_generation.json` (plans d'oreilles, retraits comptés).
- Planches : `comparaison_C_D_E.png`, `detail_museau.png`, `detail_oreilles.png`.
- `PARTS_CATALOG_VALIDATION.csv` : chaque couple pièce × couleur des trois versions, avec son statut Rebrickable.
- Aucun PDF. Les GLB de géométrie LEGO se régénèrent avec `tools/ldr_expand.py`.
