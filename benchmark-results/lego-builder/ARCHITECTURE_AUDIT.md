# Audit de l'existant (LEGO Builder)
Branche `research/lego-builder-unified` (depuis `research/lego-maps-v10-biomes-relief`). Audit fait en lisant le code et en exécutant les pipelines ; rien n'a été déplacé.

## Ce qui existe
- **Cartes (moteur 2)** : `benchmark-results/maps-engine-v03/style_fidelity_v062/` : `build_style.py` (géographie ou classes de biomes → niveaux → pavage → LDraw), `tiler.py`, `scene.py` (placement, collisions au placement, appuis), `basefit.py`, `strata.py`, `geodata.py`, `check_render.py`, `verify_bom.py`, `fragility.py`, `notice_steps.py`, `make_step_pdf.py`, `make_visual_notice.py`, `check_delivery.py`, `regen_deliverables.sh`, CI `lego-maps-v09-deliverables.yml`.
- **Sculptures (moteur 1)** : `benchmark-results/20_portable_engine/` : `lego_run.py` (GLB → palette → grille voxel → segmentation → oreilles → détails → assemblage → validation → renforts → couture → notice), `glb_io.py`, `fullgrid.py`, `brickify_plus.py`, `validate_v4.py`, `reinforce.py`, `notice_plan.py`, `render_ldr.js`, `render_compare.py`, `subjects/*.json`, `tests/run_tests.py` (9 tests), `tests/compare_references.py`. Reconstruction photos → GLB : `benchmark-results/tools/hf_gen.py` (Hunyuan3D-2mv via Hugging Face Space, 4 vues).
- **Dépendances communes** : bibliothèque LDraw épinglée et base Rebrickable (`.deps/`), `_paths.py`, Python (numpy, scipy, networkx, PIL, trimesh, scikit-learn), Node + three.js + Playwright (rendus sur les vraies pièces LDraw).

## Tableau fonction par fonction
| Fonction | Cartes | Sculptures | Mutualisable | Décision |
|---|---|---|---|---|
| Catalogue pièces/couleurs | `part_catalog.json`, `pair_sets.json` (paires Rebrickable), `avail()` | `partlib.py`, `palette_select.py` sur `rb.db` | **Oui, la source** : les deux lisent LDraw + `rb.db` via `_paths.py` | Façade `core.verify_catalogue` (vérification `.dat` + couleur + paire catalogue) pour les deux ; les tables par famille restent |
| Géométrie des pièces et connexions | `scene.py` (empreintes, tenons) | `partlib.py`, `conn.py`, `validate_v4.py` | **Déjà partagé** : les cartes appellent le validateur du moteur 1 via `maps_engine.validate` | Rien à déplacer |
| Placement / pavage | `tiler.py` (couches 2,5D, plaques et tuiles par régions) | `fullgrid.py` + brickify (volume 3D, briques) | **Non** : géométries différentes (champ de hauteur contre volume) | Garder séparés |
| Collisions | `Scene.add` (au placement) + validateur indépendant | `validate_v4.py` | **Oui** : validateur commun | Facade unique ; vérification indépendante pour les deux |
| Supports / appuis | `stud_cells`, `basefit.py`, plateaux fixés au cadre | renforts R1/R2, `scope.py`, plan d'appui des pattes | **Non** : stratégies mécaniques différentes (tableau fixé ou sculpture autoportante) | Stratégies explicites par famille (`core.strategies`) |
| Fragilité | `fragility.py` (graphe de liaisons ; lit `parts.json`) | `weak_groups.py`, `classify_weak.py`, `suspended_analysis.py`, tenue au tenon (`clutch_stability`) | **Partiel** : même graphe du validateur, indicateurs différents | Chaque famille garde son rapport ; `fragility.py` accéléré (V0.8) réservé aux cartes. Adaptateur LDraw seul : **non fait** |
| Couleurs | palettes de style, `palette_C*`, règles de biomes | `palette_select.py` (minimise ΔE Lab, automatique) | **Possible** (la sélection par ΔE pourrait servir aux biomes) | Non fait : à tester, risque visuel |
| Génération LDraw | `Scene.write` | `assemble_v82.py` | **Oui au niveau du contrat** : un `.ldr` | Contrat commun = `diorama.ldr` + `parts_list.csv` |
| GLB | aucun | `glb_io.py` (couleurs par sommets ou texture, miroir) | Non (spécifique 3D) | Générateur sculpture seulement |
| Rendus 3D | `render_views.py` + `render_map.js` | `render_ldr.js`, `render_compare.py`, `render_steps.js` | **Oui** : `ldr_expand.py` + three.js sur les `.dat` LDraw | Façade `core.render_ldr` ; vues par famille |
| Nomenclature | `parts_list.csv` + `verify_bom.py` | `*_catalogue.csv` | **Oui** | `core.parts_csv_from_catalogue` pour la sculpture |
| Notices | pas à pas par couches (tableau + illustrée pilote) | notice hiérarchique par modules (`notice_plan.py`) | **Non** (ordre de montage différent) | Gardées ; contrat de livraison commun |
| Disponibilité et coût | colonnes `stock_verified` et `unit_price` vides | idem | Oui, mais **bloqué** : aucune source de prix ou de stock accessible | Non faisable ici ; à signaler partout |
| Tests existants | CI V0.9 (8 modèles), `check_delivery.py`, empreintes de LDraw | `run_tests.py` (9), `compare_references.py` | Non croisés | Tests de bout en bout ajoutés (`END_TO_END_TESTS.md`) |
| Entrée utilisateur (image) | masque/TIFF et règles JSON **à la main** (V0.9–V1.0) | GLB fourni ; photos → GLB par script séparé | **Manquant** | Orchestrateur : `analyze`, `prepare`, `build` |

## Incompatibilités constatées
1. Les cartes lisent un dossier avec `parts.json` (régions, plans) ; les sculptures n'en produisent pas : les outils de fragilité et de notice des cartes ne s'appliquent pas tels quels aux sculptures.
2. Les chemins d'installation : le moteur 1 utilise `LEGO_ENGINE_HOME` ; les cartes importent un paquet `maps_engine` (dossier voisin) et `_paths.py` du moteur 1.
3. Les PNG du dépôt sont des objets Git LFS (la CI extrait sans LFS) : les entrées de la chaîne ne doivent pas être des PNG versionnés.
4. Réglages spécifiques : `subjects/paco.json` contient des données propres à Paco (repère d'oreille), `segment.py` suppose un bipède (voir `20_portable_engine/ARCHITECTURE.md`).

## Capacités manquantes pour l'image utilisateur (avant cette mission)
Reconnaissance du type d'entrée ; détection de la planche et correction de perspective ; classification de terrain sans règles écrites à la main ; génération automatique de la composition, du style et de la palette ; manifeste de projet ; commande unique.
