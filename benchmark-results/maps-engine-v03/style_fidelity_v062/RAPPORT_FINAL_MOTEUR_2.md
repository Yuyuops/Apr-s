# Rapport final — Moteur 2 (V0.7)
Branche `research/lego-maps-v07-engine2-final` (depuis V0.6.2). Code et résultats : commit `59c06c9`. Environnement : engine 1 portable en lecture seule (`env.sh`), Python venv du moteur, rendus three.js sur maillages LDraw réels. Génération reproductible : `build_style.py STYLE COMPOSITION OUT --flank vertical` (6,6 s pour le 64×96).

## Décision : **NO-GO** (Italia Prestige 64×96 : 15/25, seuil 20/25 non atteint). Release Candidate 1 non créée.

## 1. Diagnostic et notes (référence : `references/ref_A_italia_prestige.webp`)
Comparatifs : `comparatifs/cycle1_ref_vs_V062_vs_cadreC_face.png`, `cycle1_trois_quarts_base_vs_cadreC.png`, `cycle1_cadre_coin_base_vs_cadreC.png`, `cycle2_cadreC_vs_paletteD_face.png`.
Le prototype de base est reconstruit à l'identique (13 826 pièces, 124 références) : reproductibilité confirmée.

| Critère | V0.6.2 (base) | V0.7 candidat | Justification |
|---|---:|---:|---|
| Composition | 3 | 3 | Même cadrage portrait que la référence ; titre « ITALIA » à plat et drapeau/plaque à la place de la scène à figurines ; terre étrangère beige très étendue en haut à droite. Inchangé. |
| Silhouette | 3 | 3 | Escalier de 1 tenon sur tout le littoral (Adriatique, Sicile, Sardaigne) ; les 312 tuiles 25269 n'arrondissent que les coins convexes du dessus. Aucun profil concave vérifié. Inchangé. |
| Relief | 3 | 3 | Strates de 3 plaques bien lisibles en oblique, quasi absentes en vue de face (V0.6.2 : pentes courbes sans gain de face). Inchangé. |
| Couleurs | 3 | 3 | Terre et sable proches de la référence. Mer plus grise/terne que le menthe de la référence (moyenne du rendu de face (156,183,178) contre (172,228,207), ΔE00 ≈ 19, dont une part due à l'éclairage du rendu). Aqua 118 sans 1×1 impose des compléments. Inchangé. |
| Finition | 3 | 3 | **Gain réel sur le cadre** (filets dorés et médaillons d'angle en pièces réelles, voir §2), mais lettres du titre à plat en tuiles rainurées, aucun ornement en volute, pas de scène de figurines. Gain partiel, pas suffisant pour 4. |
| **Total** | **15** | **15** | Aucun critère < 3, aucune note relevée sans preuve. |

## 2. Cycles (2 maximum après diagnostic)
**Cycle 1 — Cadre premium (accepté).** Hypothèse : des filets dorés et des médaillons d'angle en pièces réelles posés sur la bande du cadre améliorent la finition sans toucher la carte. Modification : option de style `frame.finish` (`filet`, `dots`, `medallion`) dans `build_style.py`, posée sur la couche de couverture, fixée sur les briques du cadre. Pièces : filet en tuiles dorées 3069b/2431/3068b (catalogue Rebrickable : 118 / 5 / 6 sets), médaillon en tuiles rondes 98138 or (102 sets) autour d'un jour blanc 2×2. Tests sur la fenêtre golfe : A filets seuls (propre), B filets + points + médaillons (trop chargé, rejeté), puis C filets + médaillons retenu. Prototype complet C : 13 816 pièces, 124 références, **0 collision, 0 déconnexion, 0 îlot, 0 non supporté**, références toutes catalogues (`verify_bom`). Ancienne erreur corrigée : l'ornement de la V0.6.2 se posait sur la mer ; il est désormais sur la bande du cadre (largeur 4 tenons).
**Cycle 2 — Palette D « champs clairs » (rejeté).** Hypothèse : alterner 323/118/323/118 renforce la lecture des strates en vue de face. Résultat : +1 000 pièces (14 818), bandes verticales parasites dues au pavage partiel d'Aqua, strates plus bruyantes que lisibles. Validation technique 0/0/0/0 mais gain artistique non démontré : rejeté, archivé (`results/proto_c2`).
Non retenus car sans gain démontré : pentes courbes généralisées (V0.6.2), plaques progressives, ornements en points.

## 3. Limites fondamentales identifiées
1. Résolution : 1 tenon = 8 mm ; la côte en escalier est irréductible sans pièce de coin concave vérifiée (93273 absent du catalogue).
2. Le menthe de la référence n'existe pas en teinte standard ; Aqua 118 n'a ni brique ni plaque 1×1 : toute amélioration coûte des centaines de pièces et crée des artefacts de pavage.
3. La note de finition dépend d'éléments (volutes, lettres relevées brillantes, scène de figurines) que le moteur ne peut pas produire avec des pièces vérifiées dans ce périmètre.

## 4. Statut
- Terminé : cadre premium, validation technique, reproductibilité.
- Abandonné : pentes courbes généralisées, ornements en points, palette D.
- Non exécuté : phases B (multi-cartes) et C (stabilisation, RC1), car le seuil 20/25 n'est pas atteint. Aucune donnée multi-cartes n'est inventée.
- Module figurines : isolé, désactivé par défaut, inchangé.
- Aucune validation physique ; aucun stock ni prix vérifié ; aucun achat.
