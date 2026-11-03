# Verdict V12.1 : **VALIDER AVEC COMPROMIS**

Beagle : objectifs atteints (régression corrigée). Paco : objectifs incompatibles à un cas près ; compromis mesuré, deux options présentées sans en choisir une artificiellement.

| Objectif | Beagle V12.1 | Paco option A (palette V12) | Paco option B (palette V11 + réparation) |
|---|---|---|---|
| Cas < 0,5 N ≤ V11 (V11 : 10 / 7) | **0** (V12 : 32) ✔ | **8** (V12 : 8) ✘ de 1 | **6** ✔ |
| FS gravité minimal ≥ V11 (38,2 / 11,15) | **43,25** ✔ | 9,82 ✘ (−1,3) | **11,15** ✔ |
| Force de bout minimale (V11 : 0,10 / 0,19 N) | **0,52 N** ✔ | 0,19 ✔ | 0,17 (≈) |
| 0 collision, 0 pièce déconnectée, 0 sans appui | ✔ | ✔ | ✔ |
| Aucun jaune/rouge de Paco dans le Beagle | ✔ | — | — |
| Gains de couleur V12 conservés (parasites / ΔE) | ✔ 30 (V12 : 31) / 14,7 (=) | ✔ 114 / 15,5 (=) | ≈ 101 / 16,4 (+0,9 ; 467 cellules sans correspondance contre 182) |
| Visage, silhouette (IoU) | ✔ 0,998 | ✔ 0,867 | ✔ 0,867 |
| Fixations d'oreille et séquence d'assemblage | — | ✔ 8/7 pièces de contact, 1/1 chemin, 89 couples vérifiés, plan hiérarchique 207 étapes, 0 contrôle en défaut | ✔ 8/7, 1/1 ; 74 couples vérifiés |
| Seuils / coefficients de tenue inchangés | ✔ | ✔ | ✔ |
Non-régression : Paco à palette V11 figée = V9.1 octet pour octet ; Beagle V11 revalidé = valeurs archivées ; 18/18 tests ; archives V9.1 / V10 / V11 / V12 non modifiées.

Cause racine : le plafond de 60 pièces de `reinforce.py` (un groupe fragile de 69 pièces, 3 tenons, jamais renforcé : 24 des 32 cas) et l'abandon des ponts qui coupaient un lien. Ni la palette, ni la réparation de couleur n'augmentent la fragilité de départ (148 contre 155 cas avant renfort). Correction : plafond paramétrable et ponts raccourcis, qui ne recolorent que des cellules cachées (0 cellule exposée modifiée par le renfort).

Compromis Paco : les cinq groupes restants (1 à 2 g, extrémités minces) n'ont ni cellule voisine cachée ni liaison de remplacement ; l'option A garde les tons orangés (182 cellules sans correspondance) au prix d'un cas faible de plus (8) et d'un FS gravité de 9,8 ; l'option B retrouve les marges de V11 (6 cas, FS 11,15) au prix de ΔE +0,9 et de 467 cellules sans correspondance. **Décision à prendre par l'utilisateur** ; le dépôt garde A par défaut (`subjects/paco.json`), B est `subjects/paco_option_B.json`.

Oreille haute de Paco : différence de forme / d'épaisseur (largeur −20 %, épaisseur −13 %) et volume de racine absent du GLB ; **aucune erreur de placement démontrée**, aucune oreille déplacée.
Notices : 202 → 371 est un changement de format (hiérarchique 201 → plate 288 pour la même géométrie), puis le re-découpage de la palette (+82 étapes plates) ; comparaison équivalente : 201 → 207 étapes hiérarchiques, 0 pièce absente, 0 contrôle de mouvement en défaut. Étapes numériques seulement : aucun montage physique.

Pas de V13 engagé : décision attendue sur A ou B.
