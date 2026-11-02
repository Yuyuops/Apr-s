# Reproduction depuis un clone propre, et non-régression

## 1. Conditions du test

* **Nouveau clone** de la branche poussée (`git clone --branch research/lego-brickify-benchmark`), dans un dossier vide ; GLB récupérés par Git LFS (`git lfs pull`) : `beagle.glb` 9 884 728 octets, `paco.glb` 6 026 992 octets, vrais fichiers.
* **L'ancien dossier de travail `~/bench` a été rendu introuvable** pendant tout le test (renommé), pour que rien ne puisse s'y référer silencieusement ; il n'a été restauré qu'après. Aucun fichier temporaire, aucun chemin de développeur : le test T1 le vérifie dans les sources.
* Installation : `bash scripts/install.sh --no-node` (venv Python 3.13.18 neuf, `locks/requirements.lock.txt`, `brickify` au commit `1564bb3b…`, bibliothèque LDraw au commit `1f24cac1…`, base Rebrickable) : **1 min 21 s**. Node : `npm ci --ignore-scripts` (three 0.160.0, playwright 1.63.0 d'après `package-lock.json`), Chromium système.
* Commandes : `lego_run.py --glb <GLB du dépôt> --subject subjects/<sujet>.json --out runs/<sujet>`, GLB lu **directement** (couleurs par sommets), sans copie texturée.

## 2. Résultats

| Sujet | Durée | Grille, segmentation, détails | Modèle brut (sha256) | Pièces |
|---|---:|---|---|---|
| **Paco** | 204 s | identiques à l'archive | **identique** à `paco_V91_brut.ldr` | 3 098 / 3 098 |
| **Beagle**, base Rebrickable à jour | 341 s | identiques (grille, segmentation, détails, V8.2 avant renforts) | **différent** : 11 074 pièces contre 11 111 (86 en plus, 123 en moins) | voir § 3 |
| **Beagle**, base Rebrickable de référence | 359 s | identiques | **identique** à `beagle_V10_brut.ldr` | 11 111 / 11 111 |

Le plan de notice du Beagle (`notice_plan.py`) est **identique** à `plan_notice.json` de V10 avec la base de référence (581 étapes) ; avec la base à jour il en compte 579, conséquence du modèle différent. Les rendus de la chaîne Node du clone propre sont **identiques au pixel** à ceux de V10 (0 pixel différent sur trois vues).
Journaux, manifestes sha256 et comparaisons : `reproduction/`.

## 3. L'écart du Beagle : dérive de la base Rebrickable, expliquée et mesurée

La base Rebrickable (release `latest-v8` de `ojuuji/rb.db`) est **glissante** : elle n'est pas figée par version. Celle téléchargée pour le test a un horodatage de `1793543538`, celle de référence `1793454908` (environ un jour d'écart) : 104 541 lignes de disponibilité au lieu de 104 469, **1 760 couples pièce × couleur modifiés, dont 11 franchissent le seuil de 20 sets** du moteur (`MIN_SETS`) ; parmi eux, cinq pour les couleurs du Beagle, dont **la plaque 1×3 (3623) en Dark Brown : 19 → 20 sets**. Cette pièce devient « disponible » et le moteur l'utilise : les différences du modèle sont des 3623 (+38), 3023 (+28), 3024 (+17) en plus et des 3024 (−61), 3023 (−53) en moins, **presque toutes en Dark Brown (308 : +55, −95)**. La preuve est expérimentale : avec la base de référence, **le même code redonne le modèle de V10 à l'octet**. Aucun écart ne vient du code, des dépendances Python, de LDraw ou de brickify.
Mesure complète : `refs/rb_db_drift.json`, `reproduction/beagle/compare_references.json`.

**Conséquence** : la reproductibilité exacte du Beagle dépend d'une version précise de la base Rebrickable, que le dépôt amont ne permet **pas de figer** (la release « latest » change) et que je ne redistribue pas dans Git (200 Mo, données tierces). Pour rejouer exactement : `LEGO_DEPS=<dossier contenant la base de référence>`. Paco, qui n'utilise pas de pièce voisine du seuil, est insensible à cette dérive.

## 4. Ce qui n'a pas été rejoué dans le clone propre (par honnêteté)

* La **séquence et les plans d'oreilles** de Paco (`run_ears_v91.py`, 25 à 40 minutes de calcul) et la **notice** de Paco, ainsi que les **PDF** de notices (`make_notice_pdf.py`) : leurs entrées (V9.1) sont reproduites à l'identique, mais ces étapes longues n'ont pas été relancées depuis le clone. Le moteur de rendu, lui, l'a été.
* Les étapes optionnelles `suspended_analysis`, `check_ear_seq`, `strength_cmp`, `mass_report`, `export_notice` sont consolidées et passent le test de syntaxe, sans nouvelle exécution.
* L'installation a été faite avec `--no-node` puis `npm ci` séparément.

## 5. Non-régression des anciens résultats

Les références historiques (modèles Paco V8.2, V9, V9.1, Beagle V10, oreilles V6 et V6.1 de Paco et du Beagle, validations, nomenclatures, GLB) **restent où elles sont**, non copiées, non modifiées ; leurs empreintes sont dans `refs/references.json` (38 fichiers, test T2). Comparaison d'un modèle régénéré : `tests/compare_references.py <paco|beagle> <run> <sortie>`.

## 6. Dépendances et licences

| Dépendance | Version fixée | Licence / remarque |
|---|---|---|
| brickify (hamnaanaa) | commit `1564bb3b2704c522e084fdb1b2a3ce9d3f11d300` | MIT ; cloné, non copié dans Git |
| Bibliothèque LDraw | `gkjohnson/ldraw-parts-library` commit `1f24cac1821b9a86a5a84cd3a40291aad24679b3` (LDraw du 30 janvier 2023) | CC BY 4.0 ; non copiée dans Git |
| Base Rebrickable | release glissante `latest-v8` ; empreintes de référence dans `locks/deps.lock.json` | données Rebrickable, non redistribuées ; **non figeable** |
| Python | 3.13 ; `locks/requirements.lock.txt` (numpy 2.5.4, scipy 1.18.1, trimesh 5.2.0, networkx 3.7, scikit-learn 1.9.1, pillow 13.0.0, rtree 1.4.1, embreex 4.4.0.post1) | |
| Node | 22 ; `package-lock.json` (three 0.160.0, playwright 1.63.0) | |
