# Reproductibilité du moteur 1 depuis les fichiers archivés

**Conclusion : le moteur n'est PAS autonome.** Il fonctionne dans l'environnement de travail `~/bench` ; il n'est pas reproductible à partir du seul dépôt. Ce rapport identifie ce qui manque, sans prétendre le contraire.

## 1. Ce qui est reproductible

* **Déterminisme** : la chaîne complète du Beagle (`generateur/run_beagle.sh`), lancée deux fois dans deux dossiers, donne des grilles identiques (`grid`, `fine`) et un LDraw final **identique octet à octet** (même somme md5).
* **GLB source** : `02_glb_gratuit_hunyuan2mv/beagle.glb` est un vrai fichier (Git LFS résolu), 9 884 728 octets, sommets et couleurs identiques à la copie de travail.
* **Commande documentée** (depuis `~/bench`) : `bash proto/v10/run_beagle.sh <dossier de sortie>` (copie dans `generateur/run_beagle.sh`, sources dans `generateur/outils_v10/`).
* **Versions des paquets** de l'environnement : numpy 2.5.4, scipy 1.18.1, trimesh 5.2.0, networkx 3.7, scikit-learn 1.9.1, pillow 13.0.0, rtree 1.4.1, embreex 4.4.0.post1, Python 3.13 (relevées par `pip freeze` ; aucun `requirements.txt` n'était archivé).

## 2. Ce qui manque ou dépend silencieusement de `~/bench`

| Dépendance | État | Conséquence |
|---|---|---|
| **Moteur d'origine `brickify`** (`~/bench/brickify/pipeline/brickify.py`, importé par `fullgrid.py`) | Dépôt externe `hamnaanaa/brickify`, commit `1564bb3`, **non archivé** ici | Impossible de rejouer la voxélisation depuis le dépôt seul |
| **Bibliothèque LDraw complète** (≈ 711 Mo) | Externe, non archivée | Géométries des pièces, validation, rendus |
| **Base Rebrickable** `data/rb.db` (≈ 200 Mo) | Externe, non archivée ; sert à la disponibilité des pièces par couleur | Catalogue vérifié, choix des pièces |
| **Racine `~/bench` codée en dur** | Dans presque tous les scripts | Aucun script ne s'exécute hors de ce dossier |
| **Fichiers intermédiaires de Paco** : `proto/v7/paco_full400.npz`, `segmentation.npz`, `ref_full_frame.glb`, `run/ears.pkl`, `proto/ear08/run/module_report.json`, silhouettes d'oreille copiées sous des noms de travail | **Aucun n'est dans le dépôt** (vérifié : 0 fichier suivi) | Le rejeu de **Paco** V7 → V9.1 depuis le dépôt est impossible ; seuls les LDraw produits sont archivés. Une partie est régénérable (grille depuis le GLB), le repère d'oreille et `ears.pkl` ne le sont pas sans les anciens dossiers |
| **GLB texturé** `runs/beagle_hf2mv_shape_blanc/beagle_couleur_tex_miroirX.glb` | Dans `~/bench` seulement ; le GLB du dépôt est à couleurs par sommets | Étape d'encodage non scriptée dans le dépôt |
| **Modules d'oreille** (`ear11`, `ear12`, `design_v51.py`…) | Copies dispersées dans les dossiers d'itération, versions différentes | Aucune version unique de référence |
| **Rendus** : Node 22, three.js 0.160, Playwright/Chromium | Versions notées dans `BENCHMARK_REPORT.md`, non verrouillées | Rendus et PDF |
| **Noms codés pour Paco** (fichiers de sortie `paco_V82.ldr`, en-têtes « Paco 400 mm ») | Dans `assemble_v8*.py` | Cosmétique : le Beagle sort sous le nom `paco_V82.ldr`, renommé à la livraison |

## 3. Recommandation (non réalisée dans cette mission)

Archiver dans le dépôt : un `requirements.txt` verrouillé, l'empreinte du commit de `brickify`, un script d'installation de `rb.db` et de LDraw avec empreintes, les intermédiaires de Paco (ou leur régénération scriptée), une racine configurable, une seule copie versionnée de chaque module.
