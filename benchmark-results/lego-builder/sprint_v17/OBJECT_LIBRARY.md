# Sprint V17 — Bibliothèque d'objets (`maps-engine-v03/style_fidelity_v062/objects.py`)

Générique : aucune donnée de Hyrule dans le code ; un **manifeste JSON** (`sprint_v17/castle_zone_objects.json`) décrit des objets avec leur type, position (coordonnées de carte, `origin_rc` de la composition soustrait), paramètres, **statut (observé/estimé)** et source. Activation : clé `objects` du style ou `--objects FILE` ; **désactivée par défaut** (baselines inchangées, voir `REGRESSION_REPORT.md`).

| Assemblage | Emprise | Hauteur | Pièces réelles (catalogue du moteur) | Contrôles propres |
|---|---|---|---|---|
| `tree` (rond / conifère / grand / petit) | 2×2 / 1×1 | 6–11 plaques | 3062b, 3941, 4589 | pas de collision ; chaque pièce repose sur une pièce à tenons ; couleurs cataloguées |
| `rock` | 2×2 | 5 | 3022, 3039, 3024 | idem |
| `tower` (n briques, anneau, toit cône) | 2×2 | 3n(+6) | 3941, 3942c | idem |
| `monument` (colonne) | 2×2 | 4+3n | 3022, 3062b, 6141, 4589 | idem (fragile par conception : pilier de 1×1) |
| `castle` | 6×6 | 18 | 3010, 3004, 3941, 3942c, 3062b, 4589 (31 pièces) | idem |
| `bridge` (portée n) | 1×(n+2) | 1 | plaques 1×L (3623, 3710, 3666, 3460…) | pose sur 2 plots de berge ; portée limitée aux longueurs de plaque existantes |
Termes de terrain : `river` (cellules d'eau, largeur, niveau), `land` (chaussée), `path` (recoloration), `scatter` (semis déterministe d'un assemblage sur des classes).
Substitution de couleur : **journalisée, jamais silencieuse** (ex. cône 4589 en vert 288 absent du catalogue → vert 2 ; 3941 en 308 → 70).

## Nomenclature, géométrie, connexions
Par assemblage : `data/assemblies_structure.json` (BOM, hauteur, pièces à 1 tenon, coupure maximale) ; géométrie validée par `tests/test_objects_v17.py` : **12 variantes** posées sur une surface à tenons de 8×8, **validation indépendante du moteur : 0 collision, 0 pièce déconnectée, 0 îlot, 0 pièce non supportée** ; zone D reconstruite deux fois : **SHA-256 identique** (`0364fdd1e2eb…`).

## Fragilité par assemblage (autonome)
| | Pièces | Pièces porteuses à 1 tenon (coupure max) | Décoratives exposées |
|---|---|---|---|
| tree rond / conifère / grand | 2 / 3 / 4 | 1 (1) / 2 (2) / 3 (3) : le tronc porte la couronne | 1 |
| rock, tower, tower basse | 3 / 4 / 1 | 0 | 1 / 0 / 0 (tours 2×2 : 4 tenons) |
| castle | 31 | 8 (2) : cônes de tourelles d'angle | 4 |
| monument | 7 | 5 (5) : colonne 1×1 empilée, **fragile par conception** | 1 |

## Réutilisation (autre diorama)
Le moteur Maps lit un raster de classes ; la bibliothèque ne dépend que de classes nommées (`forest`, `grass`, `water`…), de niveaux et d'une liste de pièces. Un autre diorama fournit son manifeste. **Non implémenté (V18 possible)** : un type `sculpture` qui poserait un sous-modèle LDraw produit par le générateur de sculptures (GLB → LEGO) pour des objets plus complexes que les assemblages paramétriques.
