# Clôture V16 — Écart artistique : référence LEGO / V15 B / V16

**Aucune note artistique n'est donnée** (validation humaine requise). Ce document est descriptif et mesuré. Planches : `renders/gap_*.jpg` (gauche : référence LEGO tierce ; droite : V16, même zone), `sprint_v16/renders/full/compare_reference_V15B_V16_face.jpg` et `compare_V15B_vs_V16_trois_quarts.jpg`.

## Mesures (reproductibles)
| Mesure | Référence | V15 B | V16 |
|---|---|---|---|
| Composantes de classes (96×78 ; référence : 1128×916 puis rééchantillonnée au plus proche à 96×78) | 939 (967 à 96×78) | 281 | 351 |
| Part de cellules visibles en pièces ≥ 8 tenons (moyenne des 9 secteurs) | n.m. | 34,1 % | 23,8 % |
| Part de cellules visibles en pièces 1×1 | n.m. | 11,1 % | 27,9 % |
| Couleurs distinctes par secteur (min–max) | n.m. | 8–12 | 8–15 |
| Densité d'arêtes du rendu de face (rendus non comparables à l'identique) | 0,459 | — | 0,328 |
Lecture : V16 a réduit les grandes plaques lisses (−10 pts) et multiplié les petits éléments, mais le raster 96×78 ne porte que **351 composantes contre ≈ 950** : c'est le facteur limitant. Les parts de classes (eau, herbe, forêt, désert, neige…) sont déjà proches de la référence (`sprint_v15/data/reference_measures.json`) : l'écart n'est **pas** la composition, mais la structure spatiale fine.

## Détails absents (comparaison visuelle zone par zone)
1. **Réseau hydrographique fin** : la référence dessine des rivières d'1 à 2 plots qui entourent des îlots de plaine et relient les lacs ; V16 n'a que de grands plans d'eau (raster à contours inchangés). C'est la différence de lecture géographique la plus nette au centre.
2. **Points d'intérêt construits** : château d'Hyrule et tours, villes (Gerudo), ponts bruns, ruines, stations, arbres-repères. V16 : seulement des pastilles rouge/jaune/blanche (repères) sans forme.
3. **Chemins et ponts** : aucun trait linéaire clair (routes, ponts) ; la référence les marque en tan/brun.
4. **Mont du Destin** : la référence a un cratère entouré de roches rouges/oranges et braises ; V16 a un cône brun étagé avec trou noir, sans rouge ni orange.
5. **Archipel et côtes** : îlots détachés, plages claires, écume ; V16 : côte nette, eau uniforme (dégradé de 2 tons seulement).
6. **Désert** : la référence combine tans clairs/foncés, nombreuses plaques rondes 1×1, ruines, reliefs en dunes ; V16 : grandes plaques tan (4×8) très lisses, 3 motifs circulaires répétés.
7. **Neige** : la référence utilise briques rondes/arrondies blanches en volumes ; V16 : plateaux blancs étagés correctement mais sans arrondis.
8. **Végétation** : la référence mêle 3 verts, fleurs orange/roses/jaunes en grappes, arbres de tailles variées ; V16 : un vert d'arbre sombre et peu de fleurs isolées.

## Régions trop uniformes (V16)
Plaine centrale (secteur 3×3 centre : seulement 12 % de cellules en pièces ≥ 8 tenons mais très peu de contraste local), bande désertique sud-ouest, océan est (plaques bleues unies), massif de pierre/neige nord-ouest (grandes surfaces grises).

## Éléments caractéristiques de Hyrule manquants
Château d'Hyrule (au centre), plateau des Pionniers, villes (Gerudo, Kakariko), Domaine Zora, ranches/stations, tours (Sheikah), ponts, route centrale, volcan rouge, lac Hylia détaillé, archipel.

## Limites de représentation à 96 × 78
- 1 plot ≈ 1,04 % de la largeur : **les rivières de la référence, vues sur les planches, font environ 1 plot de large ou moins** ; un bâtiment lisible demande ≥ 3×3 plots, soit ≈ 4 % de la largeur.
- 351 composantes de classes contre ≈ 950 : on ne peut pas porter toutes les petites formes ; il faut **choisir** (rivières principales, 8–12 repères).
- Au-delà de 96×78 (C3 128×104) le gain visuel est réel mais coûte +87 % de pièces (V15 : 23 420) : non retenu ; le nombre de pièces n'est pas un objectif.

## Améliorations réalisables sans forte hausse du nombre de pièces
- **Rivières principales en canaux de 1 plot** (remplacent du terrain : ≈ +1 à 3 % de pièces).
- **Quelques repères (8–12) de ≤ 25 pièces** posés sur des fondations 2×2 : ≈ +2 à 3 % de pièces.
- **Variation tonale et chemins** (2–3 verts, sable, chemin tan, braises rouges au Mont du Destin) : changement de couleur, pas de pièces supplémentaires ; ≈ 0 à +2 %.
- Fleurs en grappes **plutôt que** pastilles isolées (échange, pas ajout), tuiles affleurantes (C2) plutôt que saillantes pour ne pas aggraver le risque d'arrachage (C3).
