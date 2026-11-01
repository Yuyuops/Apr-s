# Problèmes non résolus : V8.2

| # | Problème | Gravité | Cause démontrée | Correction possible (non engagée) |
|---|---|---|---|---|
| 1 | Pièces noires de l'oreille basse visibles au coin de la bouche (profil gauche) | Limitation locale | 79 % des pixels sombres de la zone vus de la caméra gauche sont des pièces de `V7_oreille_basse` (plaques 52107, brique 3008, plaque 3035) dans les cellules creusées de la tête | Changer le niveau ou la position de la fixation de l'oreille basse (module gelé : décision nécessaire) |
| 2 | Liseré rouge de la langue non lisible | Limitation | Moins d'une cellule de large dans le GLB (0 à 3 % de la cavité visible) | Aucune pièce plus fine que 8 mm dans le moteur ; module de lignes (non engagé) |
| 3 | Contour de lèvre non représenté | Limitation | Pièces courbes étudiées, non implémentées | Suivi de contour en SNOT avec tuiles et quarts de rond (non engagé) |
| 4 | Cavité vue de dessous 28 % plus petite que dans le GLB (IoU 0,74) | Faible | Hauteur d'une plaque (3,2 mm) | — |
| 5 | Cavité vue de face plus cachée (38 % contre 29 %) | Faible | Voxellisation (marche de 8 mm, écart de profondeur de 4 mm) | — |
| 6 | +1 groupe faible parmi les 10 plus faibles (7 pièces, 2 tenons, 0,26 N, haut du torse, épaule) | Faible | Nouveau découpage des plaques du corps, à 15 couches de la bouche | Contrôle « au moins 3 tenons » après reconstruction |
| 7 | Réglages de V8.1 et trois règles de V8 réglés sur Paco | Méthode | Réglés en voyant Paco | Test de généralisation sur un autre personnage (non fait) |
| 8 | Mains, bords d'oreille, semelles, notice des oreilles | — | Inchangés, hors mission | Voir les dossiers 13 à 15 |
| 9 | Aucune validation physique | — | Aucun achat autorisé | — |
