# Verdict V12 : **VALIDER AVEC LIMITATION**

Critères du cahier des charges :
| Critère | Résultat |
|---|---|
| Aucune couleur de Paco ajoutée au Beagle | ✔ 0 plaque jaune/rouge ; plus aucun code de couleur de Paco dans le moteur |
| Réduction démontrée des parasites de Paco | ✔ 369 → 114 (noirs sur jaune/rouge/blanc 237 → 25), ΔE moyen 20,4 → 15,5, sans modifier un seuil de mesure |
| Fixations d'oreilles plus cachées sans dégradation mécanique ni difficulté d'assemblage | ✔ pour la fixation (106 → 20 cellules visibles, graphe de tenons identique, mêmes chemins/pièces de contact, 0 collision, séquence V9.1 intacte) — mais la palette automatique ajoute des points faibles (Paco 7 → 8, Beagle 10 → 32 sous-ensembles < 0,5 N) |
| Pas de dégradation majeure silhouette / visage / détails / stabilité | ✔ IoU inchangé (0,867 / 0,998), 0 pièce déconnectée ; stabilité de base Paco (marge 41,1 mm) inchangée ; SF gravité min ≥ 9,8 |
| Pas de code spécifique à un personnage ; tests et rejeu | ✔ 15/15 ; Paco rejoué octet pour octet à V9.1 avec la palette V11 |

Pourquoi « avec limitation » et non « VALIDER V12 » : points faibles supplémentaires sur le Beagle, écart de l'oreille haute non expliqué (aucune oreille déplacée faute de preuve), 20 cellules de fixation encore visibles et quelques taches orange à la racine des oreilles. Pourquoi pas « CORRIGER » : les gains de couleur sont mesurés et reproductibles et aucun défaut bloquant (collision, déconnexion) ne subsiste.
Pistes (hors mission) : contrainte de continuité de plaques dans le choix de palette ; mesure d'oreille avec un GLB d'oreille segmenté.
