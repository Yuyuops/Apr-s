# Protocole d'essai réel : fixation à deux plaques tournées (V6)

Le banc reproduit **exactement** les coïncidences 3-4-5 calculées pour la tête de Paco : mêmes positions, mêmes pièces.

- Fichier : `banc_essai/banc_essai_fixation.ldr` (23 pièces, 10 étapes).
- Rendus : `rendus/banc_essai/`.
- Contrôle numérique : 0 collision, 0 pièce déconnectée, 7 tenons d'essai (`banc_essai/validation.json`).

## Nomenclature (`banc_essai/nomenclature.csv`)

| Pièce | Couleur | Qté | Rôle |
|---|---|---|---|
| Plaque 6×10 (3033) | gris foncé | 1 | Représente le crâne |
| Brique 1×1 (3005) + plaque 1×1 (3024) | gris foncé | 2 + 4 | Colonnes sous les 2 appuis de la plaque haute |
| **Plaque 1×1 (3024)** | **rouge** | **7** | **Les tenons d'essai** (5 sous la plaque basse, 2 sous la plaque haute) |
| Plaque 4×6 (3032) | noir | 2 | Plaque tournée basse ; plaque du bloc |
| Brique 2×6 (2456), brique 1×6 (3009), briques à tenons latéraux 52107 ×2 et 47905 ×1 | noir | 5 | Bloc de racine (début de l'âme) |
| Plaque 4×4 (3031) | noir | 1 | Plaque tournée haute |
| Plaque 2×16 (4282) | jaune | 1 | Bras de levier dirigé vers le bout de l'oreille |

Toutes les pièces existent dans cette couleur, dans au moins 20 sets. On peut les remplacer par n'importe quelle couleur : la couleur ne change rien à l'essai.

## Montage

1. Poser la plaque 6×10 à plat, sur une table.
2. Monter les 2 colonnes (brique 1×1 + plaque 1×1), puis poser les 7 plaques 1×1 rouges aux positions du fichier. Ouvrir le `.ldr` dans BrickLink Studio ou LeoCAD : les positions s'y lisent directement.
3. Poser la plaque 4×6 basse **tournée de 53,13°** sur les 5 tenons rouges du bas. Si les 5 tenons entrent ensemble, l'angle est juste : c'est le premier contrôle.
4. Monter le bloc sur elle, puis la plaque 4×4 haute sur le bloc et sur les 2 tenons rouges hauts.
5. Fixer le bras 2×16 sur la plaque haute.

## Mesures (à répéter 5 fois, en démontant et remontant entre deux essais)

1. **Emboîtement.** Nombre de tenons rouges réellement enfoncés, sur 7. Contrôle à l'œil et au toucher (jeu, basculement).
2. **Tenue en porte-à-faux.** Suspendre au bout du bras (à 124 mm du bord de la plaque haute) un petit sac, et y ajouter des masses par pas de 5 g (pièces de monnaie pesées). Noter :
   - la masse au premier décollement visible ;
   - la masse au décrochage.
   La force vaut masse × 9,81.
3. **Chemins indépendants.** Refaire l'essai 2 :
   - en retirant les 2 tenons rouges hauts (chemin 1 seul) ;
   - puis en retirant les 5 tenons bas (chemin 2 seul).
4. **Comparaison avec le calcul.** Sur le banc, le modèle annonce 3,3 N au bout du bras. Pour l'oreille, il annonce 2,1 N au bout ; elle pèse 75 à 83 g, soit une force d'environ 0,8 N à reprendre.

## Critères de lecture

| Résultat | Interprétation |
|---|---|
| 7 tenons sur 7 enfoncés, décrochage > 2 N | Fixation crédible pour l'oreille de 80 g |
| Décrochage entre 0,8 et 2 N | Tient l'oreille au repos, fragile à la manipulation : renforcer |
| Tenons qui ne s'enfoncent pas ensemble, ou décrochage < 0,8 N | Revoir la fixation (tolérances des coïncidences 3-4-5 à vérifier) |

Photographier chaque essai et noter les valeurs dans un tableau : n° d'essai, tenons enfoncés, masse au décollement, masse au décrochage, configuration.
