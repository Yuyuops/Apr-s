# Notice : tête C reconstruite + oreille V5.1

Fichier de référence : `tete_C_avec_oreille_V51.ldr`, 85 étapes, réordonné par `tools/reorder_notice.py`. Le contrôle `validate_v2.py` ne trouve aucune pièce posée sans liaison.
Module seul : `module_oreille.ldr` (repère de la tête), en 6 étapes : plaque tournée, âme, face extérieure, tuiles extérieures, face intérieure, tuiles intérieures.
**Ordre vérifié par calcul, pas par un montage réel.**

1. **Tête, couche par couche,** jusqu'à la couche 29 incluse. Aux 5 positions marquées, la couche 30 reçoit 5 plaques 1×1 noires : ce sont les seuls points d'appui de l'oreille.
2. **Plaque 4×6 noire tournée à 53,13°,** posée sur ces 5 tenons. Les autres cases sous elle restent vides. Le triangle 3-4-5 garantit l'alignement.
3. **Sous-ensemble « oreille »,** construit à part, puis posé sur la plaque :
   1. **Bloc de racine.** Briques 2×6 et 1×6, plaque 4×6.
   2. **Âme.** Assises alternées :
      - briques à tenons sur 2 faces (52107, 47905) ;
      - 2 plaques 1×N, joints décalés ;
      - tuiles 1×1 au sommet des colonnes.
   3. **Face extérieure.**
      - Le demi-disque 4×8 au bout libre.
      - Les ailes du bord supérieur, de gauche à droite.
      - L'aile du bord inférieur gauche.
      - Les plaques intérieures et la racine.
      - Toutes ces pièces s'enfoncent sur les tenons latéraux de l'âme.
   4. **Tuiles extérieures.** Sur le bout arrondi, 4 tuiles 1×1 quart de rond, 1 tuile 1×2 à bouts arrondis, 1 tuile 2×6 et 1 tuile 1×4.
   5. **Face intérieure** (miroir) **et ses tuiles.**
4. **Fin du crâne.** Les couches de tête au-dessus de la plaque se referment autour de la racine de l'oreille.

**Points d'attention pour un montage réel :**

- L'oreille (87 g) ne tient au crâne que par la plaque tournée : un seul chemin, 5 tenons. C'est la première chose à tester.
- La racine traverse la surface de la tête : en montage réel, la tête doit être montée autour de l'oreille, pas avant.
