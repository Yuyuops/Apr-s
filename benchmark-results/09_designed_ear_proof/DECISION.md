# Décision : preuve de faisabilité par conception directe (V5)

## Verdict : **VALIDER LA MÉTHODE**

La conception directe donne ce que l'approche automatique par voxels n'a jamais donné : une oreille **visiblement meilleure que C**, sans zoomer, sur la face extérieure, le profil, les trois quarts et la face intérieure. Le contour est net (demi-disque, ailes biseautées), la surface lisse, et aucun tenon n'est visible. Le module est réalisable : 0 collision, 0 îlot, 0 pièce posée dans le vide, 79 pièces dont tous les couples pièce × couleur existent (au moins 27 sets).

| Critère | Résultat V5 |
|---|---|
| Mieux que C, visuellement | **Oui sur 4 vues sur 6** (face extérieure, profil, trois quarts, face intérieure). **Non** de face (oreille trop fine) ni au raccord (pied visible). |
| Surface extérieure propre | Oui : 0 tenon visible, tuiles et chanfreins de bord |
| Épaisseur raisonnable | 9,6 mm (3 plaques). C'est raisonnable pour la construction, mais 2 fois plus fin que la référence (≈ 20 mm). |
| Raccord discret | **Partiellement.** Plus de talon rectangulaire, mais un pied de 4 tenons reste visible sous le lobe, et un jour sépare le bout du lobe et le crâne. |
| Connexions, collisions, catalogue, montage | Valides (`validation_technique.json`, `NOTICE.md`) |
| Tenue indicative | Point faible inchangé depuis V4.1 : 2 plateaux tournants, 4 contacts, 0,16 N au bout pour 37 g. Ce n'est pas une mesure physique. |
| Silhouette globale (grille de 8 mm) | 0,923 de face et 0,939 de profil, contre 0,955 et 0,958 pour C. Comme demandé, la métrique ne décide pas. Ici, elle pénalise surtout la finesse de l'oreille et le vide sous le lobe. |

## Réserves à lever avant toute généralisation (non engagées)

1. **Épaisseur.** Une oreille à 2 faces finies, d'environ 20 mm, demanderait une âme à tenons sur 2 faces (briques 47905 ou 52107) entre 2 panneaux tuilés. Il faut l'essayer sur ce même module.
2. **Raccord.** Habiller le pied (pente ou panneau courbe noir), ou faire descendre la racine du lobe le long de la paroi du crâne, là où la référence se fond dans la tête.
3. **Tenue.** Une 2e liaison entre le bout du lobe et le crâne, ou 2 plateaux 4×4, avant tout montage réel.

Conformément à la mission, **aucune nouvelle itération n'est commencée sans nouvelle décision.** Rien n'est transposé à une autre taille, à l'autre oreille, au museau ni au vrai chien. Il n'y a ni bibliothèque de modules ni choix automatique de module.
