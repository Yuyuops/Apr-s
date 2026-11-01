# Conclusion : capacité du moteur à générer les détails de visage

## Ce que le moteur fait automatiquement, avec de vraies pièces

| Détail | Résultat |
|---|---|
| **Yeux et pupilles** | Deux yeux appariés par symétrie, un faux œil du GLB écarté. Pièces choisies par leur géométrie et leur disponibilité. Fidèles à la référence (V8). |
| **Truffe** | Coupole noire choisie par diamètre et bombé (V8). |
| **Ouverture de la bouche** | Encoche d'au moins 3 plaques reproduite : 92 à 98 % de la surface de cavité visible du GLB vue de côté, silhouette IoU 0,96 à 0,99 (V8.1, inchangé en V8.2). |
| **Petite surface inclinée** | Pente fromage rouge choisie par la pente mesurée sur son maillage (V8.1). |
| **Couleur de la cavité** | Transférée du GLB sur les cellules exposées, restreinte à la bouche (V8.2). |

## Ce que le moteur ne sait pas faire, et pourquoi

- **Détails de moins d'une cellule** (8 × 8 × 3,2 mm) : le liseré rouge de la langue (0 à 3 % de la cavité visible) n'a aucune pièce qui le rende.
- **Contour de lèvre et lignes fines** : aucun module de pièces courbes (quart de rond, pente courbe, clip). Étudiés, non implémentés.
- **Lecture par l'ombrage** : le GLB montre la bouche surtout par ombrage. Un volume à plaques de 3,2 mm n'a pas d'ombrage équivalent.
- **Cohabitation avec la fixation d'oreille** : la fixation de l'oreille basse occupe le coin arrière de la bouche et y expose des pièces noires. C'est une propriété du module d'oreille (V6.1 et V7), non modifié ici.

## Ce que le diagnostic a changé dans l'état des résultats

- V8.1 contenait un **défaut de sélection** (130 cellules sur 223 recolorées hors de la bouche) et une **ligne de lèvre sombre sans référence dans le GLB**. La lisibilité de V8.1 était en partie artificielle. Ces défauts sont corrigés en V8.2.
- La première mesure de ce diagnostic avait le même défaut de sélection : elle est écartée.

## Ce qui reste hors de portée sans nouvelle décision

1. Le coin de la bouche gauche est occupé par des pièces d'oreille : il faudrait changer la position ou la fixation de l'oreille basse (module gelé).
2. La langue et la lèvre demanderaient des pièces courbes et un suivi de contour : nouvelle méthode, non engagée.

**Règle d'arrêt : les itérations esthétiques sur cette bouche s'arrêtent ici.**
