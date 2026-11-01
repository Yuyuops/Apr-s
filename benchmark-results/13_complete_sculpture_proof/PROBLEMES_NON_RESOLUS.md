# Problèmes non résolus : V7

| # | Problème | Gravité | Cause | Correction minimale |
|---|---|---|---|---|
| 1 | Yeux, truffe et bouche réduits à quelques cellules de couleur | Forte (visuelle) | **Capacité manquante** : aucun module ne sait traiter un détail de 1 à 3 tenons. Le volume en cellules de 8 mm et V6.1 (contours plats) ne le peuvent pas. | Module générique de détails ronds en SNOT (tuiles rondes, demi-sphères), placé d'après la zone segmentée |
| 2 | Mains en escalier, doigts perdus. Une main ne tient que par 1 tenon (0,07 N). | Moyenne | Membres de moins de 2 tenons de section, rendus en volume | Règle de renfort des membres fins (plaques traversantes), ou module de main |
| 3 | 46 sous-ensembles se décrochent sous moins de 0,5 N (mains, bords d'oreilles : groupes de 7 et 11 pièces sur 1 tenon) | Moyenne | Pièces de bord du générateur V6.1 et du volume reliées par un seul tenon | Contrôle « au moins 2 tenons par groupe » dans les deux générateurs |
| 4 | Notice : chaque oreille est montée en une seule étape (176 et 156 pièces) | Moyenne | `reorder_notice` garde un sous-ensemble en un seul bloc | Sous-notice suivant l'ordre âme → faces → tuiles du générateur |
| 5 | Seuil de minceur de la segmentation porté de 30 à 35 mm au vu de l'oreille basse (30,3 mm) | Moyenne (méthode) | L'épaisseur est mesurée sur les voxels, qui gonflent | Mesurer sur le maillage, puis valider sur un 2e personnage |
| 6 | Bras mal segmentés : 33 cellules seulement | Faible | Ils ne sont séparés du torse que par couche | Croissance 3D depuis les mains. Sans effet ici : même traitement (volume). |
| 7 | Traînées noires et rouges sur le museau ; taches noires autour des racines d'oreilles | Faible à moyenne | Colorisation de la grille brickify | Lissage des couleurs de surface par zone |
| 8 | Oreille basse un peu courte et un peu haute par rapport au GLB | Faible | Repère abaissé d'un nombre entier de plaques ; contour coupé au point le plus bas | Repère au demi-pas, avec le contour complet |
| 9 | Statue soulevée par la tête : semelles tenues par 5 tenons | Faible (posée) | Couche de semelle peu liée | Plaque de semelle traversante |
| 10 | Aucune validation physique | — | Pas d'achat autorisé | `PROTOCOLE_ESSAI_FIXATIONS.md` |

`autogen.py` (V6) a été modifié pour V7 : paramètres de repère, masque de protection, niveaux de fixation, contrôle de bornes. Différences : `code/autogen_diff_V7.patch`. Les valeurs par défaut gardent le comportement de V6/V6.1. **Les résultats V6/V6.1 enregistrés n'ont pas été régénérés.**
