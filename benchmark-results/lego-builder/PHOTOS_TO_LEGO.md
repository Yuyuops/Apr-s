# Photos → GLB → sculpture LEGO (une commande)
Branche `research/lego-builder-photos-to-lego` (depuis `research/lego-builder-unified`). Aucun moteur réécrit ; aucun modèle validé modifié.

## La commande
```
export LEGO_ENGINE_HOME=…  PYTHONPATH=benchmark-results/lego-builder:benchmark-results/maps-engine-v03/style_fidelity_v062  LEGO_GRADIO_PATH=<dossier de gradio_client>
python -m lego_builder run --photos face.png dos.png profil_gauche.png profil_droit.png --out projets/paco --size-mm 400 [--subject paco|beagle|config.json]
```
Dépendance : `pip install gradio_client` (`requirements-reconstruct.txt`) ; accès Internet à huggingface.co ; photos détourées (RGBA) ou fond uniforme. Les vues sont reconnues par leurs noms (face/front, dos/back, profil_gauche/left, profil_droit/right).

## Ce que la commande enchaîne (scripts existants, branchés)
1. Détourage : conservé si l'image est RGBA ; sinon **détourage automatique seulement si le fond est uniforme**, sinon refus explicite.
2. Fond blanc, puis `tools/hf_gen.py` : forme par Hunyuan3D-2mv (Space public Hugging Face, point d'entrée `/shape_generation`, graine fixe 1234, 30 pas, octree 256), jusqu'à 3 essais.
3. `tools/colorize_from_views.py` : couleurs projetées des 4 vues sur le maillage (lancer de rayons, sans IA). Seule modification d'un outil : le dossier des vues est paramétrable (`INPUTS_DIR`), défaut inchangé.
4. **Contrôle du GLB** (`check_glb`) : couleurs présentes, IoU de silhouette de chaque vue ≥ 0,60, part de sommets vus dans aucune vue ≤ 20 %, fragments ; génération refusée si un seuil échoue.
5. Moteur 1 (`lego_run.py`) → LDraw → catalogue → rendus comparés au GLB → plan de montage (notice rapide, voir plus bas).
Tout est consigné dans `manifest.json` (incertitudes, contrôles, statut).

## Photos de Paco : disponibles
Les quatre photos sont dans le dépôt : `benchmark-results/01_inputs_prepared/paco_{face,dos,profil_gauche,profil_droit}_rgba.png` (versions détourées) et `originaux/`. Aucun fichier manquant. (Beagle : mêmes fichiers `beagle_*`.)

## Résultat réel pour Paco (400 mm)
- Reconstruction : **32 s** au total (Space Hugging Face : 18 s). **Le GLB reconstruit est identique, sommet par sommet, face par face et couleur par couleur, au `paco.glb` historique** (115 868 sommets, 231 740 faces ; rapport de projection identique : IoU de silhouette 0,805 / 0,732 / 0,690 / 0,795 ; 9,1 % de sommets sans vue). La graine fixe rend la reconstruction déterministe ; seuls les octets du conteneur glTF diffèrent (SHA-256 du fichier différent).
- Contrôle du GLB : couleurs par sommets, étanche, vues recalées, couverture correcte → `ready_for_generation`. Incertitude consignée : dos et volumes cachés **estimés** par le modèle (4 vues).
- Génération avec la configuration validée de Paco (`--subject paco`) : **LDraw identique octet à octet** (SHA-256 `9d07c041…`) au modèle accepté V12.1 : 3 193 pièces, 89 références, 0 collision, 8 cas faibles (idem).
- Génération **sans déclarer le sujet** (GLB reconnu comme inconnu, configuration générique dérivée du Beagle, sans oreilles modelées) : **3 846 pièces, 65 références**, validé (0 collision, 0 tenon bloqué, catalogue complet, 8 cas faibles).

## Comparaison avec Paco V12.1 (mêmes caméras, rendu LEGO contre rendu du GLB)
| | V12.1 (config Paco) | Générique (sujet inconnu) |
|---|---:|---:|
| Pièces / références | 3 193 / 89 | 3 846 / 65 |
| IoU de silhouette (moyenne de 4 vues) | 0,895 | **0,914** |
| IoU de la tête (38 % du haut) | 0,889 | **0,930** |
| Écart de couleur ΔE76 moyen (zone commune) | 28,9 | 28,8 |
| ΔE76 de la tête | 25,0 | 24,9 |
| Palette (pièces) | Yellow 1 691, Red 701, Black 429, Orange 202, Dark_Tan 127, White 43 | Yellow 1 942, Black 819, Red 690, Orange 199, Dark_Tan 152, White 44 |
| Jonctions à un seul tenon | 2 995 | 3 831 (+28 %) |
| Cas faibles (groupes) | 8 | 8 |
Planche : `e2e_results/photos/paco_3way.png` (GLB | V12.1 | générique), mesures : `paco_compare_metrics.json`.
**Lecture honnête** : la silhouette générique est un peu plus fidèle (oreilles voxelisées, sans modules conçus) ; les couleurs globales sont équivalentes (ΔE76 élevé des deux côtés : écart de rendu et de palette LEGO, non un défaut propre à l'une). Le **détail du visage est moins net** en générique : l'œil de V12.1 (noir et blanc) est reconnaissable, celui du générique est une tache sombre. **Solidité** : même nombre de cas faibles, mais +28 % de jonctions à un tenon et +20 % de pièces ; **aucun essai physique**, ce sont des indicateurs. La V12.1 reste le meilleur résultat de Paco ; elle n'a pas été remplacée.

## Sujet « inconnu »
- **Test réalisé : photos du Beagle sans déclarer le sujet.** Reconstruction identique à `beagle.glb` (mêmes sommets et couleurs), configuration générique, 10 567 pièces, 64 références, 0 collision, 0 cas faible, catalogue complet ; **LDraw identique octet à octet** au Beagle V12.1. **Ce n'est pas un sujet réellement inconnu** : la configuration générique dérive du Beagle, donc l'égalité est attendue.
- Seul vrai test de généralisation de la configuration générique : **Paco passé par la configuration du Beagle** (ci-dessus) : validé, silhouette fidèle, détails du visage dégradés.
- **Sujet jamais vu : non testé.** Le dépôt ne contient les photos d'aucun autre sujet et je ne peux pas en inventer. **Il me faut quatre photos (face, dos, deux profils) d'un nouveau sujet**, détourées ou sur fond uniforme.

## Notice : plus de blocage de 20 minutes
- Cause : l'étape `notice` appelle `run_ears_v91.py --all`, qui cherche une séquence pour **tout le modèle** comme s'il s'agissait d'une oreille. Plus de 20 minutes de calcul sur 3 processus sans fin constatée.
- Isolation : tout appel du builder passe par `core.run(timeout=…)` qui tue **tout le groupe de processus** à l'échéance ; le builder note `status: timeout` et garde le fichier d'étapes ordonnées (`final/*_notice.ldr`).
- Mode **rapide** (défaut) : séquences d'oreille seulement pour les sous-ensembles d'oreille étiquetés (`--notice-ears sub`, option ajoutée à `lego_run.py`, défaut historique `all` inchangé) : **525 s (8 min 45 s)** pour Paco, 207 étapes, **0 étape avec contrôle en défaut** ; modèles sans oreilles : quelques secondes. Mode `full` : historique, sous délai maximal (`--notice-timeout`, 900 s par défaut). Mode `off`.
- Mesures : plan Paco rapide 525 s ; plan complet : non terminé après plus de 20 minutes.

## CI : tests de non-régression bloquants
- `ci/reference_hashes.json` : SHA-256 des 8 LDraw de cartes, du Paco V12.1, du Beagle V12.1 et des deux GLB d'entrée.
- `tests/check_regression.py` : code de sortie 1 si un hachage diffère, si un modèle manque ou si un GLB d'entrée est un pointeur LFS.
- `lego-maps-v09-deliverables.yml` : l'ancienne étape « rapport seulement » est **remplacée par une étape bloquante** (cartes).
- `lego-builder-regression.yml` : tests unitaires ; GLB d'entrée ; Paco et Beagle reconstruits et comparés à V12.1 (bloquant) ; **photos → GLB → LEGO** avec comparaison bloquante du GLB (`tests/compare_glb.py`) et du LDraw.
- Dépend d'un service externe (Hugging Face) pour le job photos : un échec du Space fait échouer ce job ; **il est séparé** des jobs de non-régression pour que l'un ne masque pas l'autre.
