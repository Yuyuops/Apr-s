# LEGO Maps Italie V0.5.7 — qualité artistique et robustesse

Branche `research/lego-maps-italie-v057-quality-convergence` (départ V0.5.6). Rendus = géométrie LDraw réelle. Aucun achat, moteur 1 inchangé, pas de fusion dans `main`, **aucun essai physique**, aucun seuil de validation modifié, aucun rendu IA.

## Phase 1 — Colisée (`comparatifs/B_colisee_variantes_57.png`)
| Variante | Idée | Pièces | Résultat |
|---|---|---|---|
| **A** (V0.5.6) 20×26 | arches 6182 sur pans rectilignes, fenêtres 60592, murs pleins sur les pas d'escalier | 755 | référence |
| **A5** 20×26 (retenue) | A + **ouvertures de 1 tenon alignées sur les deux étages** entre les piliers des pans courbes, **course de plaques-pont** sous l'attique qui enjambe chaque ouverture | 755 | 18 ouvertures sur les pas d'escalier ; rythme d'ouvertures visible, mais discret |
| **A3** 28×36 | A à échelle agrandie | 1 255 | arcades plus nombreuses (12 arches + 16 fenêtres), ovale net |
| **A5b** 28×36 | A5 agrandie | 1 284 | meilleure reconnaissance (30 ouvertures courbes) |
| A4 24×31 | intermédiaire | 961 | — |
Constat important : à 20×26, les pas d'escalier de l'ovale ont 2 tenons : aucune arche 1×3 (4490) n'est possible (variante « arche 1×3 sur pans courbes » identique à A, **non retenue comme distincte**). Les ouvertures courbes sont donc des fentes de 1 tenon entre piliers, pas des arches ; **elles ne sont pas des arcades courbes**. Aucune pièce n'est inclinée pour suivre la courbe : tout est orthogonal ; la validité est celle du moteur 1 (0 pièce posée sans appui, 0 déconnexion).
**Médaillon agrandi** : A5b est la plus reconnaissable, mais **aucune fenêtre de mer libre 28×36 (marge 3 tenons) n'existe à moins de 60 tenons de Rome** ; 24×31 ne tient qu'à 378 km dans le coin sud-ouest. Décision : **A5 à 20×26 dans la composition**, A5b conservée comme module isolé (pistes : agrandir la marge, déplacer le titre).
Médaillon : plaza dans la mer ouest (≥ 3 tenons de mer partout, pas de contact avec la Sardaigne), **non présenté comme situé à Rome** (308 km déclarés), lien en tuiles blanches vers la côte romaine ; **effet de lagon supprimé** (le dégradé de profondeur ne traite plus le podium comme une côte).

## Phase 2 — Fragilité (`fragility.json`, `baseline_V056_measured.json`)
Catégories mesurées séparément : pièces à un tenon **décoratives** (feuilles) vs **porteuses** ; points d'articulation qui isolent **une seule pièce** (feuille) vs qui font **cascade** (≥ 2 pièces) avec la masse entraînée.
| | V0.5.6 | V0.5.7 (retenue, b2) | V0.5.7 base classique (b0) |
|---|---|---|---|
| Pièces | 9 507 | **10 441** (+10 %) | 9 016 |
| À un tenon | 1 181 | **1 065** | 1 004 |
| … décoratives / porteuses | 755 / 426 | 587 / **478 (+12 %)** | 579 / 425 |
| Points d'articulation | 1 076 | **1 020** (cible < 997 **non atteinte**) | 1 046 |
| AP isolant 1 pièce (feuille) | 570 | 596 | 558 |
| AP en cascade (≥ 2 pièces) | 506 | **424** | 488 |
| Masse cumulée des cascades | 867 g | **565 g** (−35 %) | 955 g |
| Pire cascade « mer » | 8,7 g | **2,6 g** | 11,1 g |
| Pire défaillance isolée | 10,0 g (base Pise) | 13,2 g (base Pise, chaîne de 17 pièces) | 13,2 g |
Ce qui a été fait : (1) **plaques de la couche de mer (y=2) re-pavées après coup** avec des joints qui coupent les pièces du dessus (`basefit.py`) ; (2) dégranulation des couleurs des tuiles de mer ; (3) tuiles 2×3/2×4/2×6 en plus ; (4) fusion neutre des pièces voisines. **Ce qui n'a pas marché (arrêté après deux cycles sans gain sur le nombre d'AP)** : refaire les trois couches de socle (plaques minuscules, +65 % de pièces, AP en hausse) ; régler les poids du pavage (5 configurations). Cause : le **nombre** d'AP compte les plaques qui portent seules une pièce ; plus de plaques = plus d'AP, même si la masse perdue à la défaillance diminue. Le chiffre d'AP n'est donc pas une preuve de solidité ; la **masse entraînée** est l'indicateur retenu. Compromis : −35 % de masse en cascade et pire cascade de mer ÷ 3,4, au prix de +10 % de pièces et de +12 % de porteuses à un tenon.
Mode de rupture dominant (`ap_inspect.py`) : une plaque de la couche y=2 qui porte seule des tuiles de mer ou des briques de relief (cascade ≤ 21 pièces, ≤ 11 g dans la base classique, ≤ 2,6 g en b2) ; hors mer, chaîne verticale des monuments (Pise).
**Pas de ponts cachés supplémentaires ni de renfort de jonctions entre secteurs** : le pavage croisé des plaques de mer tient lieu de pont sur toute la grille (les jonctions de secteurs ne sont pas des plans de coupe : les plaques de base traversent les limites des secteurs).

## Phase 3 — Vésuve et Pise (`comparatifs/D_pise_vesuve_57.png`, `V056_vs_V057_pise/vesuve.png`)
**Pise v2** : 8 étages distincts (rez-de-chaussée plein, 6 loggias en briques rondes à grille 92947, belvédère), **corniche (plaque ronde 2×2) à chaque étage**, plinthe, marche d'entrée, calotte ; inclinaison d'un tenon tous les deux étages (3 tenons au total, ~10° à l'échelle du modèle) ; 22 pièces (13 avant), 552 pièces avec le terrain de test, 0/0/0/0. Nette progression de lecture (étages et loggias), mais toujours une tour à tronc de 2×2 tenons, inclinaison en paliers, pas de colonnes individuelles. Hauteur 35 plaques (11 cm) : volontairement non agrandie en emprise (6×6).
**Vésuve v3** : empreinte locale 12×12 (au lieu de 9×9), cône unique avec épaulement, contour de cratère irrégulier (rayon ≈ 4,3 ± 1,5 tenons), brèche sud-ouest, cavité profonde de 3 briques, anneau de roches nuancées, sol sombre central. 673 pièces (module), 0/0/0/0. Le **cratère est lisible en vue de dessus et sur la composition complète** (anneau sombre) ; en vue rasante la cavité reste modeste. Limite : parois en pentes 65–75° verticales, pas de rebord lisse.

## Phase 4 — Italie 128×128 (`results/E_italie/it57_b2`, `comparatifs/V056_vs_V057_*.png`)
**10 441 pièces, 226 références, 124,8 mm de haut, 10,5 kg estimés (±30 %)**. Validation moteur 1 : **0 collision, 0 pièce déconnectée, 0 îlot, 0 pose sans appui, 0 tenon bloqué** ; LDraw = JSON = nomenclature ; 226/226 couples catalogués Rebrickable. Contours, relief alpin (volumes inchangés), cadre et mer lissée conservés ; mer sans lagon. Vues : face, trois-quarts, nord-ouest, Alpes, Colisée (3/4, façade, courbe, vers Rome), Pise, Vésuve, titre, rose, cadre, littoral.

## Phase 5 — Notice et faisabilité (`assembly_plan_v2.json`, `step_viewer.html`, `notice_pas_a_pas.pdf`)
**354 étapes** (≤ 36 pièces) : socle par secteur, couches du tableau par (niveau, secteur), sous-ensembles Colisée puis Pise (assemblés hors tableau), finitions, cadre. Chaque pièce : référence, couleur, **orientation (0/90/180/270°)**, position (rangée, colonne, niveau), tenons d'enclenchement ; contrôles par étape (planéité, pièces à un seul tenon, pièces à cheval sur deux secteurs, sous-ensembles) ; table des pièces inter-secteurs. **Visualiseur HTML** autonome (three.js, maillages LDraw réels, étapes précédentes pâles, étape courante en couleur, précédent/suivant/lecture/aller à/zoom). **PDF de 100 pages** : un bloc par étape. Test automatisé du visualiseur en Chromium sans GPU (`viewer_check.js`) : chargement et captures aux étapes 1, 40, 150 et 354 **réussis** (`viewer_check/*.png`) ; le clic sur « précédent » a dépassé 30 s en rendu logiciel, donc **la navigation par boutons n'est pas vérifiée automatiquement** (aucun JSON de contrôle écrit). **Ce n'est pas une notice illustrée image par image** ; elle n'a pas été suivie à la main.
**Secteur d'essai** (`results/essai_secteur_S11`) : S11 (Toscane) + bandes de jonction 8 tenons vers S12/S21, 1 576 pièces, 58×74 tenons, LDraw/BOM autonomes validés 0/0/0/0 (pièces débordantes conservées avec leurs supports) ; protocole dans `PROTOCOLE_ESSAI.md`.

## Limites
Colisée : pas d'arcades courbes réelles à 20×26 ; médaillon agrandi impossible à placer sans éloignement. AP total 1 020 > 997. Porteuses à un tenon +12 %. Pise : paliers. Vésuve : cavité modeste en rasant. Notice : tableaux + visualiseur, pas de dessins d'étape. Aucun essai physique.
