# Décision : démonstrateur d'oreille articulée (Brickify V4)

## Verdict : **CORRIGER LE MODULE**

| Critère | Exigence | Résultat |
|---|---|---|
| Silhouette | Amélioration visible par rapport à C | **Non atteint.** Oreille plate et inclinée comme la référence, mais posée sur des cales visibles, détachée de la tête, contour trop épais. Silhouette de face 0,888 contre 0,955 pour C. |
| Orientation | Conforme au GLB, de face et de profil | **Atteint** : 53,13° contre 52,5° mesurés (triangle 3-4-5 vérifié). Plan décalé de 1,2 tenon vers l'extérieur. |
| Pièces | Références et couleurs vérifiées | **Atteint** : 48 lignes, toutes produites. Le dessus de plateau tournant n'existe qu'en gris clair (caché). |
| Connexions | Aucun îlot déconnecté | **Atteint** (0 îlot, 0 pièce déconnectée) |
| Collisions | Aucune collision non autorisée | **Atteint** : 0 collision, contrôlée sur la géométrie réelle des pièces tournées et des équerres ; seul chevauchement autorisé, le pivot du plateau tournant. |
| Montage | Séquence réalisable, rien posé dans le vide | **Atteint sur le papier** : notice réordonnée, panneau monté à part puis clipsé. |
| Fixation | Plusieurs chemins de connexion | **Atteint** : 2 plateaux tournants (4 tenons chacun dans la tête), 4 équerres, 8 tenons latéraux. Force de décrochage indicative au bout de l'oreille : 0,57 N, avec un pivot compté comme un seul contact. |
| Coût | Aucun prix inventé | Aucun prix donné : coût non vérifié. |

**Le potentiel est démontré** pour le mécanisme : un module orientable à l'angle mesuré, avec des pièces réelles, sans collision, raccordé par plusieurs chemins et monté dans un ordre réaliste, le tout vérifié par un validateur indépendant.
**Le critère visuel, qui est prioritaire, n'est pas atteint.** Il ne s'agit pas d'une impossibilité géométrique : trois problèmes précis restent à résoudre.

## Problèmes à corriger, par ordre d'importance

1. **Raccord avec la tête.** Les plateaux tournants sont posés sur le dessus arrondi du crâne, mis à niveau par 37 plaques 1×1. Les cales se voient, et l'oreille flotte au-dessus de la tête.
   **Correction :** creuser dans la tête une poche plane qui reçoit les plateaux en dessous de la surface. On retire des cellules de la tête, comme la fente de E, mais cachées sous le panneau. La base du panneau peut alors entrer dans la tête et la toucher.
2. **Silhouette du panneau.** Cellules de 8 mm, 7 pièces de contour seulement, bord carré du côté de la tête, petite excroissance à la base.
   **Correction :** ajustement du contour avec plus de pièces arrondies posées sur le panneau, du côté visible (tuiles quart de rond, coins arrondis 2×2, pentes courbes sur la tranche), et trois rangées de cellules partielles au lieu du seuil de 60 %.
3. **Dessous visible.** La face intérieure montre les tubes des plaques.
   **Correction :** ajouter une troisième couche de tuiles sur la face intérieure, hors des points d'accroche, ou monter le panneau tenons vers la tête et le couvrir de tuiles côté extérieur. Il faut d'abord vérifier sur la référence quelle face doit montrer des tenons.

## Ce qui n'est pas engagé

Conformément à la mission, je ne lance pas de nouvelle série d'essais, je ne touche pas aux autres détails (museau, yeux, queue, pattes) et je ne transpose rien au vrai chien.
La prochaine étape proposée est une seule correction de ce module, sur les trois points ci-dessus. Elle sera validée à nouveau sur les mêmes vues et contre les mêmes critères.
