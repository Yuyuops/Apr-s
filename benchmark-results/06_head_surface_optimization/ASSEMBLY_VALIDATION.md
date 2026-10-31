# Validation technique : C, D, E (tête de Paco, 400 mm)

Les mesures viennent de `tools/validate_v2.py`, appliqué aux notices réordonnées (`variante_*/*.ldr`).
Les valeurs « avant réordonnancement » se rapportent aux sorties brutes (`*_brut.ldr`).
**Rien ici n'est validé physiquement : seul un montage réel le peut.**

| | Prototype C | Variante D (finition) | Variante E (finition + oreilles SNOT) |
|---|---|---|---|
| Pièces | 1 735 | 1 764 (+29, +1,7 %) | 1 131 (−604) |
| Références différentes | 20 | 21 | 22 |
| Lignes pièce × couleur | 33 | 34 | 44 |
| Pièces déconnectées | 0 | 0 | 0 |
| Îlots | 0 | 0 | 0 |
| Collisions (boîtes, grille de 4 LDU) | 0 | 0 | 0 |
| Tenons qui butent sur une autre pièce | 0 | 0 | 0 |
| Liaisons latérales (SNOT) | 0 | 0 | 61 |
| Liaisons à un seul tenon / total | 1 812 / 2 587 | 1 856 / 2 609 | 1 074 / 1 766 |
| Sous-ensembles ≥ 1 g décrochés par moins de 0,5 N au bout (indicatif) | 26 sur 107 | 27 sur 130 | 12 sur 77 |
| Même chose, moins de 2 N | 35 | 39 | 18 |
| Force minimale de décrochage (indicatif) | 0,04 N | 0,04 N | 0,08 N |
| Coefficient minimal sous le poids propre (indicatif) | 38,2 | 38,2 | 7,3 |
| Pièces posées sans liaison pendant le montage : avant → après réordonnancement | 55 → **0** | 51 → **0** | 54 → **0** |
| Sous-ensembles impossibles à rattacher | — | — | 0 (3 sous-ensembles d'oreille) |
| Étapes de notice (réordonnée) | 149 | 143 | 86 |
| Couples pièce × couleur non vérifiés, jamais produits ou rares | 0 | 0 | 0 |
| IoU de volume avec le modèle 3D | 0,853 | 0,851 | **0,674** |
| IoU des silhouettes face / profil / dessus | 0,955 / 0,958 / 0,893 | 0,955 / 0,956 / 0,893 | **0,715** / 0,919 / 0,791 |
| Retraits faits par le générateur | — | — | 13 pièces flottantes de la tête (13 cellules) ; 67 cellules d'oreille sans accroche |

## Points critiques

- **D.** Mêmes fixations que C : seuls les dessus changent. Les pentes 54200 (42) et les tuiles n'ont pas de tenon : rien n'est posé dessus, et le validateur le confirme (0 tenon bloqué).
  Le bout des oreilles reste le point faible : 0,04 N, colonne de 1 à 2 tenons, comme dans C.
- **E.** Chaque oreille ne tient que par **4 tenons latéraux**. Les briques d'accroche n'ont pu être placées que là où la tête offre 3 plaques pleines sur l'axe imposé.
  - La force minimale de décrochage double (0,08 contre 0,04 N), mais le coefficient minimal sous le poids propre tombe de 38 à 7,3. Une oreille en porte-à-faux sur 4 tenons latéraux est moins sûre qu'un empilement vertical.
  - Pour obtenir zéro pièce flottante, le générateur a dû **retirer** 13 pièces de la tête et 67 cellules d'oreille non accrochables. Il ne les a pas reliées. C'est compté ci-dessus.
- **Montage.** Les trois notices réordonnées ne demandent de poser aucune pièce dans le vide.
  - Pour C et D, certaines pièces s'emboîtent par en dessous d'une pièce déjà posée. C'est faisable quand l'espace sous la pièce est libre.
  - Pour E, chaque oreille se monte à part (ordre de proche en proche), puis s'accroche aux tenons latéraux. La manœuvre est possible sur le papier, mais délicate à la main : une grande plaque doit s'enfoncer de côté sur 4 tenons alignés.

## Modèle du contrôle de stabilité (à lire avant d'utiliser les newtons)

- Pièces supposées rigides.
- Une liaison par tenon résiste à l'arrachement avec **1,0 N par tenon**. C'est une hypothèse prudente : les mesures publiées sur des briques neuves vont d'environ 1 à 4 N, et la valeur baisse avec l'usure, le lot de couleur et la température. La compression est supposée sans limite.
- Pour chaque direction de tenons et chaque plan entre deux couches, on considère chaque sous-ensemble qui ne tient que par des tenons à ce niveau. On calcule :
  1. le coefficient sous son propre poids ;
  2. la force horizontale à son extrémité qui le fait pivoter autour d'un bord du polygone formé par ses tenons, chaque tenon résistant avec un bras égal à sa distance au bord plus le rayon d'un tenon.
- Masse : 0,10 g par volume tenon × tenon × plaque de matière.
- Non modélisés : frottement entre pièces voisines, serrage latéral, jeu, fatigue, chocs.
- **Ces valeurs servent à comparer des variantes entre elles. Ce ne sont pas des résistances réelles garanties.**
