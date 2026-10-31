# Essai comparatif intégral — brickify / Studio — deux chiens, hauteur 250 mm

## Objet
Tester le moteur ORIGINAL brickify à partir d'images, puis son rendu, ses exports et ses diagnostics. Ne pas substituer le convertisseur maison. Les images sont dérivées des planches fournies par l'utilisateur (rendus de référence, non des photos d'assemblage vérifiées).

## Préparation
- Python 3.11+, Git, quelques Go d'espace, Internet. Windows/macOS/Linux ou environnement Codex.
- Cloner https://github.com/hamnaanaa/brickify
- Installer `python -m pip install -r requirements.txt`.
- Télécharger la bibliothèque officielle LDraw (`https://library.ldraw.org/library/updates/complete.zip`) et la décompresser. Localiser `LDConfig.ldr` ainsi que les sous-dossiers `parts` et `p`.
- Obtenir une clé fal.ai séparément si génération depuis image, et la stocker en variable `FAL_KEY` (ou secret GitHub Actions). Ne jamais la committer.

## Exécution image → GLB — moteur exact du dépôt
```bash
export FAL_KEY='VOTRE_CLE'  # Linux/macOS uniquement, NE PAS écrire la clé dans le dépôt
python pipeline/image_to_3d.py --image inputs/paco_face.png --out out/paco --model hunyuan3d-v3
python pipeline/image_to_3d.py --image inputs/beagle_face.png --out out/beagle --model hunyuan3d-v3
```
L'outil actuel du dépôt est SINGLE-VIEW, pas multi-vue : pour exploiter pleinement les vues face/dos/profils, utiliser l'interface v3.1 Pro multi-vue de fal.ai puis télécharger le GLB obtenu, ou adapter l'appel API séparément. Les images de profil sont incluses à cet effet.

## Exécution GLB → LEGO — moteur original, couleurs automatiques, 25 cm
```bash
python pipeline/brickify.py --glb out/paco/paco_face.glb --height-mm 250 --out out/paco --name paco --colour-mode palette --palette-passes 2 --interior dominant --ldconfig /CHEMIN/ldraw/LDConfig.ldr
python pipeline/brickify.py --glb out/beagle/beagle_face.glb --height-mm 250 --out out/beagle --name beagle --colour-mode palette --palette-passes 2 --interior dominant --ldconfig /CHEMIN/ldraw/LDConfig.ldr
```
**Important :** la valeur par défaut du dépôt `--colour-mode muse` contient des règles de couleur adaptées à son personnage démo. Toujours utiliser `--colour-mode palette` pour les chiens. Paramètre `--components` à revoir selon les composantes du GLB (la valeur 1 par défaut ne garde que la composante majeure ; oreilles, queue ou museau séparés risquent d'être perdus).

## Rendu des vraies pièces
```bash
python pipeline/make_viewer.py --model out/paco/paco_model.json --ldraw /CHEMIN/ldraw --out out/paco/paco_viewer.html
python pipeline/make_viewer.py --model out/beagle/beagle_model.json --ldraw /CHEMIN/ldraw --out out/beagle/beagle_viewer.html
```
Ouvrir les HTML dans un navigateur avec accès Internet (Three.js via CDN). Tourner à la souris et conserver captures face, dos, profil, 3/4. En cas de restrictions `file://`, servir localement avec `python -m http.server`.

## Vérifications avant tout développement
1. Prévisualiser séparément les GLB issus de Hunyuan : si la forme 3D est fausse, le problème est AVANT brickify.
2. Vérifier dans `*_report.json` : `floating_after_repair == 0`, `stud_connections`, `parts`, `steps`, taille.
3. Ouvrir `*.ldr` dans BrickLink Studio. Vérifier couleurs/références, collisions, ordre d'assemblage, possibilité de monter les oreilles, la queue, les pattes.
4. Contrôler le nombre de pièces et la liste `*_parts_list.csv`, importer `*_bricklink_wanted.xml` dans BrickLink **sans acheter**.
5. Comparer le MÊME mesh OBJ/STL dans Studio > File > Import > Import 3D Model (outil Sculpture) : choix des briques, parois, épaisseur du socle, couleurs, étapes par couche.
6. Pour un test de limites : comparer le rendu 25 cm et 40 cm. Plus grande taille = plus de détails mais davantage de pièces.
7. Confronter aux références : proportion des yeux, oreilles, museau, pattes, queue, formes, silhouette en face et profil.

## Critères d'acceptation
- Reconnaissable et proche des références sous 4 angles (évaluation par l'utilisateur) ; les modèles générés ne sont pas automatiquement fidèles.
- Aucune pièce flottante et aucune collision. Une connexion par studs NE garantit pas la résistance d'un bras, d'une patte ou d'une queue : inspection humaine obligatoire.
- Liste de pièces LEGO existantes avec couleurs confirmées et notice comprenant suffisamment d'étapes.
- Coût et durée non inventés : indiquer 'non vérifié' si prix BrickLink non collectés ou rythme non mesuré.
- Si échec : classer 'bloqué au maillage IA', 'limite du catalogue rectangulaire de brickify', 'défaut mécanique', ou 'notice insuffisante'.

## Limite structurelle majeure
Le moteur brickify utilise des briques et des plates rectangulaires dans un petit catalogue. Il ne sait pas automatiquement reconcevoir toutes les pièces arrondies, articulées et techniques SNOT visibles dans les références du client. Un résultat très cubique malgré la pleine exécution est donc une vraie limite de conception, non un réglage caché.
