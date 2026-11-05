# Vérification des pièces courbes (V0.6.1)
Méthode : boîte du corps lue par le moteur 1 (`probe_parts.py`), maillage LDraw étendu (`ldr_expand`), comptage de sommets dans les quatre coins du plan, couples pièce/couleur Rebrickable (`pair_sets.json`), validation indépendante du modèle assemblé. La boîte englobante n'est **pas** utilisée comme géométrie réelle : l'orientation du coin arrondi a été lue sur le maillage.
| Pièce | Dimensions (tenons × plaques) | Géométrie / orientation | Couleurs utilisées (sets Rebrickable) | Statut V0.6.1 |
|---|---|---|---|---|
| **25269** tuile 1×1 coin arrondi | 1×1×1 | sous-face sans sommets dans le coin **+x,-z** à rot 0 = coin SE ; rotation convertie par `rot_xz` en coin voulu | terre 84 (75), crème 19 (188), Sand Green 378 (14), Light Aqua 323 (86), Aqua 118 (non catalogué : couple absent → pas d'arrondi), blanc 15 (463) | **intégrée** : 312 coins arrondis sur le prototype ; 0 collision, 0 déconnexion |
| 26601 plaque 2×2 sans coin | 2×2×1, 3 tenons | même coin manquant | Sand Green 378 (45), blanc (229) | mesurée, **non intégrée** (plaque à tenons ; pas de gain mesuré face à 25269) |
| 30357 plaque 3×3 à coin rond 2×2 | 3×3×1, 8 tenons | non orientée | Light Aqua 323 (3), blanc (153) | mesurée, **non intégrée** (3 sets en Light Aqua ; tenons visibles) |
| 11477 / 15068 / 93273 pentes courbes | 1×2×2, 2×2×2, 1×4×2 | origine décalée en y (boîte négative) | non testées en couleurs de strate | mesurées, **non intégrées** : les strates sont des empilements de plaques verticales, une pente courbe demande de refaire le profil des flancs (travail restant) |
Limite : seuls les coins **convexes** de la surface supérieure sont arrondis (1 tenon de rayon) ; les coins concaves et les flancs restent en marches.
