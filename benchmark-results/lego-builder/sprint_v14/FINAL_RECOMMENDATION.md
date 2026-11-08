# Sprint V14 — Recommandation finale (imprimante, procédé, coûts)

**Statut des preuves** : toutes les spécifications machine viennent de pages constructeur/revendeur du 2026-11-08 ; **aucune performance n'a été mesurée sur machine réelle** (aucune des trois n'est disponible), les tranchages sont faits par PrusaSlicer sous profil proxy, les purges/temps de changement/prix de CFS/durées humaines sont des **hypothèses explicites** (`BUSINESS_COST_MODEL.md`). Les conclusions ci-dessous ne sont énoncées que lorsqu'elles résistent à la plage bas/haut de ces hypothèses ; sinon « non démontré ».

## 1. Constat structurant (démontré sur nos fichiers)
1. **Aucun de nos modules ne tient dans 4 couleurs** : Paco 5–6 couleurs par module (jusqu'à 5 par couche), Hyrule 5–12 (jusqu'à 7 par couche). L'A1 + AMS Lite et le Snapmaker U1 (4 emplacements/têtes) **ne peuvent pas imprimer les modules multicolores en une passe** ; seul le Creality Hi, extensible à 16 couleurs avec 4 CFS, le peut.
2. Pour les procédés **monochromes** (briques, pièces séparées), les trois machines donnent des coûts **équivalents à quelques euros près** (Paco 291 / 291 / 297 €) : l'avantage éventuel du U1 (têtes indépendantes) ou de l'AMS ne joue pas, et **aucune différence de vitesse n'a été mesurée**.
3. Les **heures machine** (Paco ≈ 128 h, Hyrule ≈ 180–208 h par modèle sous profil proxy) dominent la capacité : une machine à 500 h/mois produit ≈ 3,9 Paco ou ≈ 2,4–2,8 Hyrule par mois.
4. Les briques imprimées une à une (procédé 1) sont **exclues** : 116 (Paco) / 515 (Hyrule) pièces non imprimables (dégradation visible), 1 180 € de coût pour Hyrule, emboîtement non démontré.

## 2. Décisions chiffrées
| Question | Réponse | Solidité |
|---|---|---|
| **Meilleure machine pour démarrer** | **Bambu Lab A1 Combo (469,95 € TTC, en stock)** avec le **procédé monochrome** : mêmes coûts que les concurrentes sur ce procédé, prix le plus bas, disponibilité vérifiée. | **Par défaut de preuve** : la supériorité de l'A1 sur le Hi n'est **pas démontrée** (écart de coût 0–6 €/modèle, prix à 5 € près) ; le choix repose sur le prix et le stock vérifiés, pas sur une performance mesurée. |
| **Meilleure machine pour 20 modèles/mois** | **Creality Hi Combo + 3 CFS** pour **Hyrule** (seule machine à pouvoir imprimer des modules multicolores) : coût 349 € HT (plage 304–419) contre 527 € en monochrome, ≈ 8 machines pour 20 Hyrule/mois. Pour **Paco** : pas de différence démontrée entre A1 et Hi (≈ 6 machines). | Moyenne : l'avantage Hyrule tient tant que la purge reste < ≈ 3 g par changement (hypothèse haute 1,5 g) **et** que l'assemblage monochrome coûte > ≈ 14 s/pièce ; il dépend du prix (non vérifié) et de la fiabilité des 3 CFS supplémentaires (non testée). |
| Snapmaker U1 | **Non recommandé sur preuves actuelles — non démontré qu'il soit moins bon.** Son atout (purge −85 %, 5 s par changement) n'est pas exploitable avec des modules à > 4 couleurs ; 699 € TTC, page « Unavailable ». À réévaluer si les modèles sont redécoupés en dalles de 8–10 plots (`PRINT_OPTIMIZATION.md` §3), ce qui n'a pas été tranché. | Faible |
| **Seuil de rentabilité** (retour de la machine en 12 mois, au prix médian ; 1 machine) | A1 : ≈ 0,5 Paco/mois (399 € TTC). Hi + CFS : ≈ 0,2 Hyrule/mois (699 € TTC). U1 : ≈ 0,8 Paco ou 0,5 Hyrule/mois. Le seuil *commercial* réel est plus haut : la marge unitaire est fine (voir §3). | Conditionnel aux hypothèses de coût |
| **Meilleur procédé — Paco** | **Modules monochromes assemblés (291 € HT)** : le multicolore Hi/A1 (319–326 € médian, plage 231–459) n'est pas démontré meilleur, et exige 4–6 emplacements. Supports organiques (−26 %) à valider. | Moyenne (supports Paco +63 % de masse) |
| **Meilleur procédé — Hyrule** | **Modules multicolores sur Hi + CFS (349 € HT)** ; à défaut, modules monochromes (527 € HT, 594 pièces à assembler, assemblage non résolu). Les supports sont négligeables (+1 %). | Moyenne (cf. conditions ci-dessus) |
| **Coût complet estimé par produit** | **Paco ≈ 291 € HT** · **Hyrule ≈ 349 € HT (Hi, multicolore) ou 527 € HT (monochrome)** | Hypothèses : filament 18 € HT/kg, main-d'œuvre 25 €/h, +10 % d'échecs |

## 3. Marges (prix TTC → HT, procédé retenu)
| Produit | 249 / 399 € TTC | 599 € TTC | 699 € TTC | 999 € TTC |
|---|---|---|---|---|
| Paco (291 € HT) | **−83 € / +42 € (13 %)** | +208 € (42 %) | — | — |
| Hyrule, Hi multicolore (349 € HT) | −16 € à 399 € TTC | — | +234 € (40 %) | +484 € (58 %) |
Un Paco à 399 € TTC ne dégage que 13 % de marge brute ; ≥ 30 % demande ≈ 499 € TTC. Prix de vente = points de test, pas une étude de marché.

## 4. Scénarios mensuels (prix médian, capacité 500 h/mois/machine)
| Modèles / mois | Paco (mono, A1) : machines / investissement HT / marge mensuelle | Hyrule (Hi multicolore) : machines / investissement HT / marge mensuelle |
|---|---|---|
| 5 | 2 / 783 € / 209 € | 2 / 1 392 € / 1 170 € |
| 20 | 6 / 2 350 € / 836 € | 8 / 5 566 € / 4 678 € |
| 50 | 13 / 5 091 € / 2 090 € | 18 / 12 524 € / 11 695 € |
La **capacité** est le facteur limitant (6 à 18 machines et leur surveillance pour 20–50 modèles), avant le coût de la machine ; au-delà de quelques machines, l'espace, la main-d'œuvre et le taux d'échec réel (supposé 10 %) deviennent déterminants.

## 5. Risques et tests physiques encore nécessaires
1. **Imprimer le coupon de tolérance** (`sprint_v13/TOLERANCE_TEST.md`) : sans lui, ni les briques imprimées ni les liaisons de modules ne sont démontrées.
2. **Mesurer sur une machine réelle** : temps d'impression réels (le profil proxy est lent/arbitraire), masse de purge par changement, durée d'un changement, fiabilité du CFS/AMS/têtes sur 24 h.
3. **Valider dans le slicer natif** (Bambu Studio, Creality Print, Snapmaker Orca) : import des 3MF multi-corps, affectation des couleurs aux emplacements, supports organiques, avertissements (PrusaSlicer a aussi planté sur 1 plaque Paco).
4. **Prix** : confirmer le prix et le stock du Hi Combo (promos 359–474 €), du U1 (indisponible), le prix d'un CFS supplémentaire, le filament réel acheté.
5. **Un module Hyrule complet (240 × 240 mm, ≈ 20 h)** : gauchissement, adhérence, rendement ; **un module Paco** (supports organiques, orientation sur le dos).
6. **Assemblage** : tenons/colle entre modules et entre pièces monochromes (aucun tenon inter-couleurs n'existe), durée réelle par pièce.
7. **Esthétique** : le rendu actuel de Hyrule est jugé *moyen* (relief faible, littoral réduit) — voir `HYRULE_CURRENT_RENDER.md` ; l'optimisation du coût ne la corrige pas.

Aucun achat, aucune fabrication, aucune fusion dans `main`.
