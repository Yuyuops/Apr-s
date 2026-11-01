# Verdict V8.1 : **CORRIGER SOUS CONDITION**

**Ce qui marche.** Un module générique de lignes et de cavités rend la bouche de Paco lisible **de profil droit, de dessous et de trois quarts**, à taille normale :

- une ligne de lèvre sombre ;
- une ouverture creusée à 3 plaques au moins (9,6 mm) ;
- une mâchoire visible ;
- une langue rouge ;
- un intérieur sombre.

Tout part du GLB et de la géométrie LDraw mesurée. Rien n'a été saisi pour Paco : ni coordonnée, ni référence de pièce.

**Le défaut précis qui subsiste :** la bouche ne se lit pas de profil gauche ni de face. La cause n'est pas établie avec certitude (le GLB n'est pas transparent à cet endroit ; son liseré rouge fait moins d'une cellule). Correction minimale : mesurer ce que voit la caméra gauche dans le GLB et la grille, puis revêtir les parois visibles de ce côté (`PROBLEMES_NON_RESOLUS.md`, n° 1).

**Les contrôles passent :**

- `validate_v3` : 0 collision, 0 pièce déconnectée, 335 étapes ;
- 74 couples pièce × couleur vérifiés ;
- oreilles, yeux et truffe inchangés ;
- non-régression V6 / V6.1 sans aucune différence ;
- sous-ensembles sous 0,5 N : 43 (49 en V8), aucun nouveau point faible dans le top 10.

**Réserves.** Cette itération n'a pas de lèvre courbe ni de commissure : les pièces courbes ont été étudiées, non implémentées. Plusieurs paramètres ont été réglés en voyant Paco et restent à confirmer sur un autre personnage, avec les trois règles de V8.

**Pourquoi pas « CHANGER DE MÉTHODE »** : le module construit déjà une cavité lisible sans conception manuelle. **Pourquoi pas « VALIDER V8.1 »** : un côté de la bouche reste illisible.
