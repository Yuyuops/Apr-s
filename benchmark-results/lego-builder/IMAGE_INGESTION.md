# Import universel : analyse, conversion, manifeste
Commandes : `python -m lego_builder analyze|prepare|build|run|geo|check` (voir `README.md`). Aucune étape manuelle : pas de masque TIFF, pas de JSON à écrire.

## 3.1 Analyse automatique (`analyze.py`)
Pour un fichier, le système détermine : nature (image, GLB, SVG), type probable, taille et canal alpha, uniformité du fond, contraste sujet/fond, couleurs dominantes (cartes de couleurs : eau, végétation, neige, sable), présence d'un cadre sombre autour d'une planche, incertitudes. Il propose **map_relief_25d**, **sculpture_3d**, **mosaic_2d** ou **undetermined** (avec la correction manuelle `--type`).
- GLB : lecture du maillage (faces, étendues, étanchéité, source de couleur) ; avertissement si non étanche ou sans couleurs.
- Une seule photo d'objet : **aucune géométrie 3D n'est prétendue** ; le manifeste passe en `needs_input` (reconstruction nécessaire, dos et volumes cachés estimés).
- Les scores sont heuristiques et listés avec leurs preuves. **Défaut trouvé pendant les tests** : mon premier critère « eau » ne voyait pas l'eau bleu pâle d'un rendu clair et classait ce rendu « indéterminé » ; corrigé (saturation 0,12 au lieu de 0,22).

## 3.2 Conversion pour les cartes (`map_ingest.py`)
1. **Détection de la planche** : fond sombre (cadre autour d'une planche claire) ou fond clair uniforme ; les 4 coins sont les 4 points de l'enveloppe convexe qui maximisent l'aire. Image sans cadre : carte plate, coins = coins de l'image.
2. **Perspective** : homographie vers un rectangle. Les proportions réelles ne sont pas observables : une estimation par la géométrie de la vue a été essayée et **échoue** sur nos deux images (contrainte d'orthogonalité non satisfaite), donc **plateau supposé carré** et signalé ; `--aspect` permet de corriger.
3. **Classes de terrain** : règles de couleur (teinte, saturation, luminosité) en **données** (`data/biome_rules_default.json`, remplaçable par `--rules`), appartenance floue lissée puis arg max, régions minimales, règle contextuelle (neige ou pierre cernée d'eau = eau).
4. **Hauteurs** : **estimées** par une heuristique de forme (niveau de base par biome, gain vers l'intérieur) ; **aucune altitude réelle** n'est lue. Le manifeste porte `relief_is_estimated`. Une vraie carte de hauteur (SRTM par exemple) n'est pas branchée dans cette version.
5. **Grille** : `--size-mm` (défaut 400) → tenons de côté (8 mm) moins le cadre.
6. **Fichiers** (dans `derived/`) : `terrain_classes.tif` (format interne), `palette.json`, `composition.json`, `style.json`, `preview.png` (image redressée + classes colorées).
La source originale reste dans `source/` ; seules les données dérivées sont écrites ailleurs.

## 3.3 Conversion pour les sculptures
- **GLB** : lu, analysé, puis passé tel quel au moteur 1. Un GLB **connu** (empreinte SHA-256 dans `data/known_subjects.json` : Paco, Beagle) reprend sa configuration validée ; tout autre GLB reçoit une configuration **générique** (sans oreilles, palette automatique) avec la mention que les règles de segmentation (bipède/quadrupède) ne sont pas validées pour lui.
- **Plusieurs photos / une photo** : le dépôt contient un script de reconstruction (`tools/hf_gen.py`, Hunyuan3D-2mv via un Space Hugging Face, 4 vues). Le service est joignable (HTTP 200) mais **cette session ne l'a pas exécuté** : l'orchestrateur ne lance pas la reconstruction et le manifeste reste `needs_input` avec l'explication. La reconstruction visuelle et la génération LEGO restent deux traitements distincts.

## 3.4 Manifeste de projet (`manifest.py`, `schema/project_manifest.schema.json`)
Champs : version de schéma, identifiant, source (type, fichiers, SHA-256, mention de droits), type de construction, générateur, source géométrique (classes, composition géodonnées ou GLB ; **pas de GLB imposé aux cartes**), cible (taille), palette (catalogue LEGO), analyse, paramètres, stratégie de validation, **incertitudes**, statut (`analysed`, `needs_input`, `ready_for_generation`, `generated`, `validated`, `failed`), résultats, livrables.
Validation stricte avant génération : types, énumérations, clés obligatoires, fichiers référencés présents, **SHA-256 des sources vérifiés** (une source modifiée est refusée).

## Limites
Fond clair texturé ou planche non convexe : détection de coins non garantie (retour à l'image entière). Cadre épais : bande de cadre classée comme terrain (symptôme visible sur l'image de test). Neige blanche et écume blanche indistinguables. Classes limitées à sept biomes (eau, herbe, forêt, désert, pierre, roche, neige). Les règles ont été **écrites sur une seule image (Hyrule)** : leur généralisation est mesurée dans `END_TO_END_TESTS.md`.
