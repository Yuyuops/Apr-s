# Architecture du moteur 1 (après V11)

## 1. Schéma

```
GLB ──► analyse ──► segmentation ──► géométrie LEGO ──► détails ──► renforts ──► validation ──► notice
        glb_io      segment.py       fullgrid.py        detect.py    reinforce.py  validate_v4   notice_plan.py
        (couleurs   (zones par       brickify_plus.py   microdetails stitch.py     weak_groups   make_notice_pdf.py
        sommets /   règles)          integrate.py       assemble_v82 (oreilles)    scope.py      render_*.js
        texture,                     (oreilles)         lcm82.py                   seq / ear_plan
        miroir)                                                                    audit_fidelity
```
Chaque flèche est un fichier (grille `.npz`, `segmentation.json/.npz`, `details.json`, `.ldr`, plans `.json`) ; `engine/lego_run.py` enchaîne les étapes `input, grid, segment, frame, ears, details, assemble, validate, reinforce, stitch, final` et écrit `ctx.json` et `manifest.json` (empreintes sha256).

## 2. Organisation du dépôt (`benchmark-results/20_portable_engine/`)

| Dossier | Contenu |
|---|---|
| `engine/` | Version de référence de chaque module, à plat ; `_paths.py` (aucun chemin absolu : `LEGO_ENGINE_HOME`, `LEGO_DEPS`, `LEGO_CTX`, `LEGO_TARGETS`, `LEGO_EAR_FRAME`, `LEGO_SHAPE`) ; `data/paco_ear_frame.json` et `targets/` (données propres à Paco) |
| `subjects/` | Configuration par sujet (palette, hauteur, passes de renfort, oreilles) : `paco.json`, `beagle.json` |
| `locks/`, `package*.json` | Dépendances Python et Node verrouillées, commits de `brickify` et LDraw, empreintes de Rebrickable |
| `scripts/` | `install.sh`, `fetch_deps.sh`, `check_rb_db.py`, `make_references.py`, `consolidate.py` (provenance) |
| `refs/` | Empreintes des résultats historiques (jamais copiés, jamais modifiés), intermédiaires archivés, dérive de Rebrickable, baseline de l'audit |
| `tests/` | `run_tests.py` (9 tests), `compare_references.py`, `make_audit_baseline.py` |
| `reproduction/`, `audit/` | Journaux, manifestes et comparaisons du test depuis un clone propre ; rapports et cartes de l'audit |

## 3. Classement des modules

**Génériques et validés** (reproduits à l'identique sur Paco et Beagle depuis un clone propre) : `glb_io`, `fullgrid` (voxélisation et couleurs), `brickify_plus` (volume, avec le repli de V10), `reinforce` + `weak_groups` + `validate_v3/v4` (renforts R1 et R2, 157 → 10 cas fragiles sur le Beagle), `scope` (contrôle de portée, 16 tests), `reorder_notice`, `ldr_expand`, `partlib`, `conn`, `notice_plan` (jusqu'au plan : identique pour le Beagle), `render_ldr.js` et `render_steps.js` (rendus identiques au pixel à ceux de V10).

**Génériques mais insuffisamment testés** : `seq`, `ear_plan`, `verify_seq`, `fix_steps` (séquences d'oreilles : 4 géométries d'oreille, 1 seul sujet de tête) ; `stitch` (renfort des bords d'oreille : Paco et oreille isolée du Beagle) ; `suspended_analysis` ; `make_notice_pdf` (testé sur Paco et Beagle en V9.1 et V10, pas rejoué dans le clone propre) ; `audit_fidelity` (nouveau, 2 sujets) ; `detect.py` et `microdetails.py` (génériques dans leurs règles, mais voir ci-dessous).

**Encore spécifiques à Paco** :
* `segment.py` : cou à 70 % de la hauteur, deux colonnes de jambes, bras par composantes ; faux sur un quadrupède (V10) ;
* `integrate.py`, `autogen.py`, `autogen61.py`, `design_v51.py` : le repère de l'oreille (rotation 3-4-5, origine : `engine/data/paco_ear_frame.json`), les silhouettes (`engine/targets/`) et la recherche de fixation sont ceux de la tête de Paco ;
* `detect.py`, `microdetails.py`, `lcm82.py`, `assemble_v82.py` : classes de couleurs (noir, jaune, rouge, blanc), noms de sortie `paco_V82.ldr` ;
* `notice_plan.py` : la détection des bras suppose un bipède (repli ajouté en V10).

**Manquants** : segmentation par la géométrie (posture, appuis, extrémités) ; module d'oreille générique ; module d'yeux et détecteur indépendant de la palette ; sélection de palette par minimisation d'écart ; plan d'appui réel (surface de contact des pattes) ; notice hiérarchique pour un quadrupède ; version figée de la base Rebrickable.

## 4. Ce que V11 a changé (et pas changé)

Les algorithmes n'ont pas été réécrits. Changements : chemins absolus remplacés par `_paths.py` ; lecture directe du GLB (couleurs par sommets ou texture) et miroir interne ; `scope.py` unique (version du contrôle de portée avec attribution des pièces hors réseau, grille paramétrable) ; moteurs de rendu qui trouvent `three` dans `node_modules` à la racine ; commande unique `lego_run.py`. Les résultats de Paco (V9.1) et du Beagle (V10) sont reproduits : `REPRODUCTION.md`.

## 5. Interfaces à fournir pour généraliser (préparées, non développées)

| Capacité | Interface (entrée → sortie) |
|---|---|
| **Segmentation** | `grid.npz` + GLB → `segmentation.json` : `zones[] = {id, nom, role ∈ {corps, tête, patte, appendice, oreille, queue, museau, œil}, cellules, racine (cellules de contact avec le parent), axe, épaisseur}` ; **la posture** (axe vertical, sens avant, appuis au sol) fait partie de la sortie ; aucune hypothèse de bipédie |
| **Oreilles / appendices minces** | `appendice = {zone_id, racine, repère {R (3×3), O}, silhouette (raster 4 ldu), épaisseur}` → module d'oreille : même contrat que `integrate.py`, le repère étant **calculé** (plan principal de la zone) au lieu de lu dans `ear_frame.json` ; sortie : sous-assemblage LDraw + fixations + rapport |
| **Yeux et détails** | `details.json` (classe, centre, normale, taille, couleur observée en RVB) + `classes_vers_palette` dans la configuration du sujet → pièces ; la couleur d'une classe est **observée sur le GLB**, pas un nom fixe |
| **Couleurs** | `palette = {codes_autorises, codes_references_du_sujet, critere : minimiser ΔE Lab, seuil}` → quantificateur ; sortie `grid.npz` + `rapport_palette.json` (plancher, confusions) ; test : `audit_fidelity` |
| **Stabilité** | `contact = [{pièces, aire_cm2, hauteur}]` du plan le plus bas + centre de gravité → condition de stabilité sur la surface touchée (et non sur l'enveloppe) et correction R1 qui rend les pattes coplanaires |
