# LEGO Core : services communs
Le cœur est une **façade** (`lego_builder/core.py`) qui pilote les scripts existants ; il ne réimplémente rien et ne déplace aucun code (non-régression démontrée, voir `END_TO_END_TESTS.md`).

## Services
| Service | Fonction | Implémentation réutilisée |
|---|---|---|
| Catalogue | vérifier chaque couple pièce/couleur (`.dat` existe, couleur valide, paire cataloguée par Rebrickable) | `verify_bom.py` (LDraw épinglée + `rb.db`) |
| Validation structurelle | 0 collision, connectivité, supports, tenue | validateur du moteur 1 (`validate_v4.py`), déjà partagé par les cartes |
| Rendus | vues réelles sur les pièces LDraw | `ldr_expand.py` + three.js (`render_views.py` pour les cartes, `render_compare.py` pour les sculptures) |
| Nomenclature | `parts_list.csv` (part_num, color_id, quantity) + import Rebrickable | `core.parts_csv_from_catalogue` |
| Fragilité | indicatifs numériques par famille | cartes : `fragility.py` ; sculptures : groupes faibles du moteur 1 |
| Notice | cartes : plan par couches ; sculptures : plan hiérarchique | `notice_steps.py`, `notice_plan.py` |
| Contrat de livraison | manifeste + `diorama.ldr` + `parts_list.csv` + validations | `manifest.py` + schéma JSON |

## Stratégies de validation par famille (`core.strategies()`)
Un validateur unique ne prétend pas tout couvrir :
- **Tableau 2,5D (cartes)** : plateau fixé dans un cadre, socle ajusté sur les joints. Contrôles : graphe de liaisons (0 collision, 0 pièce déconnectée, 0 îlot, 0 non supporté), catalogue, fragilité indicative, concordance plan et nomenclature. Non revendiqué : résistance physique, comportement porté ou suspendu, stock, prix.
- **Sculpture autoportante** : surface de contact au sol et centre de gravité comptent. Contrôles : validateur du moteur 1 (collisions, connectivité, tenue par sous-ensemble), groupes faibles et passes de renfort, contrôle de portée, catalogue. Non revendiqué : stabilité de la pose debout (aucun essai réel), stock, prix.
- **Mosaïque plane** : **non implémentée** (voir `GENERATOR_INTERFACES.md`).

## Trois niveaux, jamais confondus
1. Existence catalogue : vérifiée par le cœur. 2. Disponibilité commerciale : **non vérifiée** (aucune source de prix ou de stock accessible). 3. Constructibilité physique : **non validée** (aucun essai). Aucun niveau n'est déclaré sur la base du précédent.

## Ce qui n'est pas mutualisé, volontairement
Pavage, appuis, notices : liés à la géométrie. Les déplacer n'apporterait rien et risquerait la reproductibilité.
