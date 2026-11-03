# Verdict V0.1 : **VALIDER AVEC LIMITATIONS**

*Pas de recommandation de finition tant que la comparaison visuelle A / B n'a pas été validée par l'utilisateur : voir `comparatifs/A_vs_B_dessus.png`, `A_vs_B_trois_quarts.png`, `A_vs_B_profil.png`, `gros_plan_*_A_vs_B.png`, `cote_a_cote_*.png` (source / V0 / V0 en couleurs réelles / A / B).*

**Ce qui est acquis (mesuré)**
* Les deux finitions sont générées **automatiquement** depuis l'image (`run_all.sh`), sur l'île témoin, la carte à trois zones et une variante 48 × 48, sans retouche manuelle ni code propre à l'île : LDraw, nomenclature, rendus (dessus, trois-quarts, profil, rotations, gros plans), viewer, notice PDF, contrôles.
* Couleurs : V0 était mesuré avec de mauvaises valeurs de couleur ; avec les valeurs réelles, ΔE2000 4,21 → 3,49 (A) et 3,54 (B), forêt 22,7 → 8,0 et sommet 20,4 → 8,2, 13 / 13 paires de zones adjacentes lisibles, 3 couleurs partagées de façon contrôlée.
* 0 collision, 0 pièce déconnectée, 1 composante connexe ; LDraw = nomenclature = étapes, chaque pièce exactement une fois ; étapes de 20 pièces au plus en trois sections (dos, relief, cadre).

**Pourquoi pas « VALIDER V0.1 »**
* Contours : gain modeste à 32 × 32 (côte 1,64 → 1,49 mm, avec 18 plaques biseautées en A) ; rivière et route toujours 2,3 × et 1,7 × trop larges ; 48 × 48 donne un gain réel (IoU de cellules 0,905 → 0,952) mais coûte 393 pièces, 384 mm, 2 kg.
* Structure : plus de pièces sur un seul tenon que V0 (9 → 15 en A, 23 en B) et B porte beaucoup plus de porteuses faibles (10 → 42) : « aucun nouveau groupe fragile non justifié » n'est pas tenu pour B.
* Pièces : 153 → 221 (A, +44 %) et 365 (B, +139 %) ; le surcoût de A vient du cadre (33), du dos agrandi et des 18 plaques biseautées ; B ajoute les petites tuiles.
* Esthétique non mesurable par un score ; fixation murale non validée ; prix et stock inconnus (Briquestore : HTTP 202, aucune valeur inventée).
Pas « À CORRIGER » : l'amélioration visuelle de A est nette (couleurs réelles, cadre, diagonales, relief lisible), la construction reste raisonnable (≤ 20 pièces par étape) et aucun défaut bloquant (collision, déconnexion) n'est apparu.

**Pour décider** : A est le candidat le plus proche de V0 (structure, nombre de pièces) ; B apporte un fini lisse au prix de pièces, de masse et de porteuses faibles supplémentaires. Choix à faire sur les rendus.
