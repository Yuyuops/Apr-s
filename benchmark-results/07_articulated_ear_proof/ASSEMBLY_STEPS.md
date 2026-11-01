# Séquence de montage : tête C + module d'oreille

Notice de référence : `tete_C_avec_module.ldr`, 89 étapes, réordonnée par `tools/reorder_notice.py`. Aucune pièce n'y est posée sans liaison avec une pièce déjà posée (contrôle `validate_v2.py`).
Le module seul est dans `module_oreille.ldr` (31 étapes, même contrôle).
**Séquence vérifiée par calcul, pas par un montage réel.**

1. **Tête C** (étapes 1 à 85 environ), couche par couche depuis le plan du cou. Quelques pièces en surplomb s'emboîtent par en dessous d'une pièce déjà posée, quand l'espace sous elles est libre.
2. **Cales.** Sur le dessus du crâne, à la base de l'oreille, poser les 37 plaques 1×1 noires en colonnes jusqu'au niveau commun (couche 32). Vérifier que les deux zones 2×2 sont planes.
3. **Bases des plateaux tournants** (3680, noires), alignées sur la grille. Leurs coins sont distants de 3 tenons sur un axe et de 4 sur l'autre.
4. **Sous-ensemble « oreille », construit à part** (bloc `BRICKIFY SUBASSEMBLY oreille`) :
   1. poser les deux dessus de plateau (3679, gris clair) à 5 tenons l'un de l'autre sous la plaque 2×10 (3832) ;
   2. poser l'équerre 99781 (Down) et les plaques 1×2 de rehausse, puis les trois équerres 99780 (Up), sur la rangée de la plaque du côté du panneau ;
   3. clipser la couche intérieure du panneau sur les 8 tenons latéraux des équerres. Ses plaques ne sont reliées entre elles que par la couche extérieure : la notice les pose donc en alternance intérieure/extérieure, de proche en proche ;
   4. terminer la couche extérieure : contour en plaques biseautées et à coin arrondi, tenons vers l'extérieur.
5. **Fixation.** Présenter le sous-ensemble au-dessus des bases. Tourner les dessus de plateau jusqu'à ce que leurs ergots tombent dans les bases (53,13°, imposé par la plaque), puis enfoncer verticalement.

**Points d'attention pour un montage réel :**
- les 8 tenons latéraux doivent être engagés ensemble au moment où l'on clipse le panneau ;
- les colonnes de cales 1×1 sont la partie la plus fragile du chemin d'effort ;
- l'oreille ne tient à la tête que par les deux plateaux tournants. Un plateau tournant 2×2 se déclipse sous une traction verticale modérée, ce qui n'est pas quantifié ici.
