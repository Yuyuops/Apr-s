# Capacités génériques du module lignes et cavités (V8.1)

## Ce qui est automatique et générique

| Capacité | Entrée | Sortie | Réglage |
|---|---|---|---|
| Orientation d'une tache | normale du GLB | haut / bas / latéral, inclinaison | seuils à 0,5 de la composante verticale |
| **Pièce de surface inclinée** | tache vers le haut | pièce + quart de tour + cellules, d'après l'inclinaison de la face supérieure **mesurée sur le maillage** de chaque pièce | coût : inclinaison / 30° + direction / 90° + (1 − IoU) + 0,2 × saillie |
| Revêtement de surface vers le bas | tache vers le bas | plaques recolorées sous l'empreinte (épaisseur 2 plaques) | `LINING_LAYERS` = 2 |
| **Détection d'une cavité ouverte** | grille de corps + taches | colonnes plafond / plancher, composante liée à une tache | `CEIL_MAX` = 5, `FLOOR_MAX` = 6 (plaques) |
| Ouverture minimale | cavité | creusement du plafond | `MIN_OPEN` = 3 plaques (9,6 mm) |
| Ligne de lèvre | bord ouvert d'une cavité | plafond du bord recoloré | dominante des taches du plafond |
| Langue / plancher | taches vers le haut | plancher recoloré (2 plaques) | marge de 4 mm |
| Parois intérieures | cavité | cellules voisines recolorées | couleur de l'intérieur |
| **Contrôles de construction** | pièces posées | pas de collision, tenons réels (`validate_v3`), tuiles dessous → plaques, cellules des oreilles et des yeux réservées | — |

## Pièces étudiées

| Famille | Statut |
|---|---|
| Tuiles 1×1 à 1×4 (3070b, 3069b, 63864, 2431), tuile à bout arrondi (24246) | candidates de T1 |
| Pentes fromage 31° (54200, 85984), pentes 45° (3040b, 3039), pente 33° (4286) | candidates de T1 ; **54200 retenue** |
| Plaques 1×N | utilisées pour les revêtements (corps) |
| Briques SNOT 87087, 11211 | utilisées pour les yeux (V8) ; non utilisées ici |
| Tuile quart de rond (25269), pente courbe (11477), tuile à clip (4081b) | **étudiées, non implémentées** : aucune courbe de bouche (lèvre courbe, commissure) n'a été produite faute de temps ; le module ne sait pas encore suivre une polyligne courbe |
| Barres, clips, charnières | **non implémentés** |
| Pièce orientée sous le museau (tenons vers le haut) | non nécessaire : le plafond est fait de plaques du corps, qui se posent par le dessus ; aucune pièce n'est accrochée par le dessous |

## Ce qui n'est PAS automatique

- **Lignes courbes fines** (commissure de la bouche, sourcils, plis de la joue) : le module les traite par recoloration de cellules, sans pièce courbe.
- **Détection de lignes minces comme telles** : les 11 taches « marque » de V8 (traits, sourcils) ne sont pas traitées.
- **Cavité fermée sur un côté** (cas du profil gauche) : non résolu.
- **Surfaces latérales inclinées** : T1 et T2 ne les traitent pas.

## Réglages à confirmer sur un autre personnage (test de généralisation)

Les **trois règles de V8**, réglées sur Paco, **ne sont pas corrigées** :

1. remplissage du disque dans l'appariement des yeux ;
2. regroupement des taches de la truffe (0,35 × longueur du museau) ;
3. largeur d'une tache qui enveloppe un bout.

S'y ajoutent les paramètres de V8.1, **réglés en voyant Paco** et à confirmer :

- `MIN_OPEN` = 3 : passé de 4 à 3 plaques parce que la cavité en avait déjà 3 dans la grille ;
- `LINING_LAYERS` = 2 : choisi pour que la tranche soit visible de côté ;
- `CEIL_MAX` = 5 et `FLOOR_MAX` = 6 ;
- la marge de 4 mm.
