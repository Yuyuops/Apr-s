# Suivi exécution LEGO Builder

Date initiale : 2026-11-08. Branche : research/lego-builder-commercial-outputs-20261108.

| Étape | Statut | Preuve requise |
|---|---|---|
| 1. Rejouer les moteurs | DONE | `benchmark-results/lego-builder/REVALIDATION_20261108.md` ; CI runs 42243682363, 42256747041 |
| 2. Fiabiliser | PARTIAL | 4 défauts corrigés (notice, Space, cadre impair, CI bloquante) ; esthétique Maps (19/25), bouche/couleurs Paco, sujet inconnu : non résolus |
| 3. Export Bambu | PROTOTYPE (validation numérique seulement) | `BAMBU_EXPORT.md`, `print_export_results/` ; Bambu Studio et imprimante : non testés |

## Conditions d'alerte
- Intervention humaine nécessaire (accès, décision artistique, validation physique).
- Blocage non résolu après deux tentatives documentées.
- Trois étapes terminées avec preuves : prêt pour revue indépendante Claude.

## Journal
- 2026-11-08 : suivi quotidien configuré ; feuille de route ajoutée au dépôt. Aucun test d'exécution ni export 3MF vérifié à cette date. Ne pas assimiler l'automatisation à une CI ou à un runner de tests.

- 2026-11-08 (exécution) : revalidation faite (CI + mesures), Nova évalué (pas d'intégration), export STL/3MF briques et modules généré et validé numériquement pour Hyrule et Paco. Voir `FINAL_STATE_20261108.md`. Aucune validation Bambu Studio ni physique.

## Sprint V13 — qualité finale et préparation fabrication (2026-11-08)

| Chantier | Statut | Preuve |
|---|---|---|
| Run Maps 42510458950 | DONE (succès, étape SHA-256 bloquante PASS) | https://github.com/Yuyuops/Apr-s/actions/runs/42510458950 |
| A1 Italy Premium | DONE — 21/25 auto-évalué en 3 cycles (baseline 19) ; GO artistique **sous réserve de validation visuelle humaine** | `benchmark-results/lego-builder/sprint_v13/ARTISTIC_COMPARISON.md`, `italy_v13c3/` |
| A2 Paco | DONE — V12.1 conservé (5 variantes de config : aucune amélioration) | `ARTISTIC_COMPARISON.md`, `paco_variants/` |
| A3 Beagle | NO CHANGE | non touché |
| B1 audit export | DONE — défauts trouvés : tenons non exportés, 109 pièces Paco ignorées, temps sous-estimés ×2,5–5 | `print_audit.json`, `BAMBU_READINESS.md` |
| B2 modules fidèles | DONE (enveloppe convexe LDraw, option `--shape-aware`) | `BAMBU_READINESS.md`, `shape_aware/`, rendus |
| B3 Bambu Studio | **BLOCKED** (non installable ici) ; tranchage indépendant PrusaSlicer fait | `BAMBU_READINESS.md`, `slicing/` |
| B4 coupon de tolérance | PREPARED — **BLOCKED** : impression et mesures par un humain | `TOLERANCE_TEST.md`, `tolerance_coupon/` |
| C généralisation | PROTOCOLE PRÊT — **BLOCKED** : photos d'un sujet inédit à fournir | `GENERALIZATION_TEST.md`, `tools/generalization_test.py` |
| Verdict | GO limité | `FINAL_VERDICT.md` |

## Sprint V14 — benchmark imprimantes et rendu Hyrule (2026-11-08)

| Chantier | Statut | Preuve |
|---|---|---|
| Rendu Hyrule réel (moteur, SHA = référence CI) | DONE | `benchmark-results/lego-builder/sprint_v14/HYRULE_CURRENT_RENDER.md`, `hyrule_render/` |
| Comparaison imprimantes (A1 Combo / Hi Combo / U1) | DONE (spécifications vérifiées ; **aucune mesure sur machine**) | `PRINTER_COMPARISON.md` |
| Benchmark de tranchage (PrusaSlicer, profils proxy — pas de slicer constructeur) | DONE avec limites | `SLICING_BENCHMARK.md`, `bench.json`, `merged_supports.json` |
| Modèle de coûts / marges / scénarios 5-20-50 | DONE (hypothèses explicites) | `BUSINESS_COST_MODEL.md`, `cost.json` |
| Optimisation d'impression | DONE | `PRINT_OPTIMIZATION.md` |
| Recommandation | DONE — A1 Combo pour démarrer (monochrome) ; Hi + CFS pour Hyrule multicolore ; U1 non démontré | `FINAL_RECOMMENDATION.md` |
| Tests physiques (coupon, purge réelle, slicers natifs, prix) | **BLOCKED** (intervention humaine) | `FINAL_RECOMMENDATION.md` §5 |

## Sprint V15 — Hyrule reconstruit à partir du besoin (2026-11-09)

| Chantier | Statut | Preuve |
|---|---|---|
| Audit de la détection du besoin | DONE : n'existait que comme classifieur de type heuristique ; ni interprétation de demande, ni contraintes, ni sémantique, ni version | `benchmark-results/lego-builder/sprint_v15/INTENT_DETECTION_AUDIT.md` |
| Composant minimal `intent` + manifeste d'exigences + `semantic_map` | DONE (hors ligne, sans API payante ; 9/9 tests) | `lego_builder/intent.py`, `semantic_map.py`, `HYRULE_REQUIREMENTS.json` |
| Version de Hyrule | Breath of the Wild (lecture visuelle de la plaque-titre) ; aucune carte originale fournie | `REFERENCE_ANALYSIS.md` |
| Pipelines A/B/C (+2 cycles C2, C3), moteur inchangé | DONE : B 12 543 pièces, C3 23 420 pièces ; 0 collision/îlot ; reconstruction identique ; V14 = référence CI inchangée | `PIPELINE_COMPARISON.md`, `builds/`, `SHA256SUMS.txt` |
| Verdict | GO artistique **limité** (reconnaissance, sous validation humaine) ; NO-GO « égale la référence » ; GO technique non acquis (règle de fragilité) ; **aucun gel CI** | `FINAL_VERDICT.md`, `ARTISTIC_EVALUATION.md` |
| Validation visuelle humaine / carte originale / plaque-titre / travail moteur (pentes, décor) | **BLOCKED** (décisions humaines) | `FINAL_VERDICT.md` |

## Revue de suivi — 2026-11-09 (lecture des preuves existantes)

**Périmètre de cette revue :** lecture GitHub des rapports V13/V14 et du journal. Aucun runner de test, trancheur natif ou imprimante n'a été exécuté dans cette revue ; les PASS ci-dessous sont des résultats *rapportés par les artefacts des sprints*, non des tests relancés ici.

| Étape / moteur | Statut | Preuve / limite |
|---|---|---|
| (1) Régression Maps | PASS rapporté | run 42510458950 (SHA-256 bloquant PASS) ; Hyrule référence SHA-256 `5afb9ac8fe80f0089542e33ba639950251ce372d392512dbc29f777877a9ab8b` ; 10 682 pièces / 134 références ; `sprint_v14/HYRULE_CURRENT_RENDER.md`. Aucun nouveau run lancé ici. |
| (1) Sculptures / Builder unifié | PASS rapporté, pas de nouveau test | Paco V12.1 et Beagle conservés ; rapports `sprint_v13/FINAL_VERDICT.md` et révalidation antérieure. |
| (1) Photos→3D | BLOCKED pour généralisation | seuls sujets historiques rejoués ; protocole `sprint_v13/GENERALIZATION_TEST.md` ; quatre photos inédites nécessaires. |
| (2) Maps artistique | FAIL pour Hyrule commercial | rendu moteur actuel jugé insuffisamment reconnaissable ; ne pas confondre 0 collision / SHA stable et fidélité cartographique. Italie C3 : 21/25 auto-noté, validation humaine encore nécessaire. |
| (2) Sculptures Paco | PARTIAL | V12.1 conservé ; bouche/lèvre et couleurs non améliorées, cinq variantes rejetées. |
| (3) STL/3MF | PASS numérique rapporté / BLOCKED physique | exports V13 ; V14 tranchage PrusaSlicer sous profils proxy, pas de slicer natif ni de machine. Coupon et mesure de tolérances absents. |
| (3) Économie | ESTIMATION | Paco ≈291 € HT, Hyrule ≈349 € HT en multicolore Hi (hypothèses fragiles) ; temps machine proxy ≈128 h / 180–208 h ; ne pas utiliser pour un devis ferme. |

**Prochaines actions sans dégrader les références :** (a) fidélité Hyrule : fixer une source cartographique et produire une hauteur/segmentation comparée en variante isolée, sans remplacer le SHA de référence ; (b) conserver Paco/Beagle et isoler l'étude de lèvre courbe ; (c) ne pas acheter d'imprimante avant essai coupon, slicer natif et mesure purge/temps. Les trois étapes ne sont **pas** prêtes pour GO commercial ni revue de validation physique.

**Traçabilité de cette revue :** seuls des fichiers texte du dépôt ont été inspectés ; pas de vérification indépendante de la dernière exécution CI, pas de calcul de nouveaux SHA ni de génération de rendu. Les rapports V13/V14 constituent les preuves disponibles.

## Sprint V16 — relief organique, détails et solidité de Hyrule (exécuté)

| Étape | Statut | Preuve / limite |
|---|---|---|
| Moteur Maps (options OFF par défaut) | PASS | `tests/test_engine_v16.py` 2/2 ; 8 baselines IDENTICAL après gel final (`sprint_v16/regression/maps_post_final.log`) |
| 3 zones pilotes A/B/C | PARTIAL | relief/détails enrichis ; pire défaillance 10→7, 14→8, 18→7 ; % 1 tenon total non réduit ; dépassement de 3 cycles déclaré |
| Hyrule complet 96×78 | PARTIAL | 11 187 pièces, validé 0/0/0/0 ; pire défaillance 45→17 ; 1 tenon 20,6→24,3 % (échec du critère) |
| Builder unifié Italie / Paco | PASS | LDraw identiques (`regression/builder_post.log`) |
| Photos→3D | BLOCKED | `gradio_client` absent du venv moteur + service HF Space externe |
| Validation artistique humaine | ABSENTE | aucun GO artistique ; **NO-GO gel** ; voir `sprint_v16/FINAL_VERDICT.md` |

## Clôture Sprint V16 et préparation V17

| Étape | Statut | Preuve / limite |
|---|---|---|
| Non-régression après `f962b6a` | PASS (exécuté) | 8 baselines Maps IDENTICAL, unit 9/9, engine V16 2/2, Italie/Paco/Beagle identiques à V12.1, GLB inputs OK ; `sprint_v16_closure/REGRESSION_FINAL.md` |
| Photos→3D | PASS (exécuté) | GLB reconstruit identique, Paco IDENTICAL 9d07c041… ; dépend de la disponibilité du Space HF ; l'ancien blocage venait de `gradio_client` absent |
| Solidité V16 | ACCEPTABLE techniquement | indicateur « % 1 tenon » mal adapté : liens porteurs faibles (≤2 tenons) 185→12→3, pièces à 1 tenon porteuses 670→108 ; hausse du % due à 1 879 petits éléments décoratifs exposés (+68 %) ; numérique ≠ physique |
| Correction des faiblesses porteuses | FAIT (candidat) | 5 piliers 1×2 → briques 3004 : −10 pièces, voxels identiques, 0 collision ; non gelé |
| Écart artistique | DOCUMENTÉ | pas de note ; rivières fines, repères, chemins, volcan, texture ; 351 composantes de classes vs ≈ 950 |
| V17 | PROPOSÉ, non développé | 3 améliorations avec coût/risque/tests/abandon : `V17_PROPOSAL.md` ; aucun gel, aucune fusion dans `main` |

## Sprint V17 — reconstruction fidèle de Hyrule : zone du château (prototype)

| Étape | Statut | Preuve / limite |
|---|---|---|
| Référence MOC-193441 | PARTIEL | identifié via moteur de recherche et fiches revendeurs ; page Rebrickable **inaccessible** (403/402, non contournée) ; PDF payant non acheté ; aucun fichier 3D/LDraw légalement accessible prouvé ; vues : 1 dessus + 3 trois-quarts, ni latérale ni gros plans (`sprint_v17/REFERENCE_AUDIT.md`) |
| Bibliothèque d'objets (arbre, rocher, tour, château, pont, monument) + rivières/chemins | PASS (technique) | 12 assemblages validés par le validateur indépendant ; reproductible ; désactivée par défaut |
| Zone du château (32×32) | PARTIEL | 1 750 → 1 950 pièces, 0/0/0/0, BOM valide ; amélioration visible (volumes, ponts, rivières) mais château trop massif, détails encore loin de la référence ; **aucun GO artistique** |
| Non-régression | PASS | 8 baselines IDENTICAL, unit 9/9, engine 2/2, objets, Italie/Paco/Beagle identiques |
| Photos→3D | **BLOCKED** | quota ZeroGPU du Space Hugging Face épuisé (`Try again in 7:28:02`) ; dernier PASS : clôture V16 |
| Hyrule complet | NON LANCÉ | manifeste planifié à blanc sur 96×78 (272 arbres, 11 rochers, 4 tours, 4 ponts, 1 château), en attente de votre validation visuelle ; voir `sprint_v17/FINAL_VERDICT.md` |

## Revue automatisée — 2026-11-10 (lecture GitHub, sans runner)

**Méthode :** consultation directe des rapports versionnés V13/V14/V16 et clôture V16, du journal et des propositions V17. Cette revue n'a exécuté ni Python moteur, ni workflow CI, ni trancheur, ni impression. Les PASS ci-dessous sont des **preuves rapportées par la clôture V16**, pas des PASS nouvellement obtenus aujourd'hui. Les empreintes complètes citées viennent du rapport de clôture ; elles n'ont pas été recalculées ici.

| Étape | Statut au 10/11 | Preuves et réserves |
|---|---|---|
| (1) LEGO Maps | PASS rapporté | Clôture V16 : 8/8 baselines IDENTICAL ; `sprint_v16_closure/REGRESSION_FINAL.md`, `regression/04_maps_8_baselines.log`. |
| (1) Sculptures et Builder unifié | PASS rapporté | Italie SHA-256 `17d9bdc60637614404494517c1736906ec238b1310257f2f9563d7c750cd776f` ; Paco `9d07c041a4968245228c016c651fef0710fd26fee68f67eac771df261c28089a` ; Beagle `551bde0f77f20c227b4c4fde7f9c286c32139c4c6ac2b458edc0b8cedf31808f`. Logs `05` à `09` de la clôture. |
| (1) Photos→3D | PASS historique, disponibilité non garantie | Clôture V16 : HF Space accessible, GLB Paco reconstruit et modèle LEGO identiques ; logs `10` à `12`. Généralisation à un sujet inédit toujours non validée. |
| (2) Hyrule V16 | PARTIAL, **NO-GO gel** | 11 187 pièces ; 0 collision/déconnexion/îlot ; pire défaillance 45→17 ; liens faibles ≤2 tenons 185→12, puis 3 dans variante corrigée de 11 177 pièces. **1 879 éléments décoratifs exposés** ; validation artistique humaine absente ; pas de test physique. |
| (2) V17 | PROPOSÉ, non exécuté | `sprint_v16_closure/V17_PROPOSAL.md` : rivières fines, texture/chemins, 8–12 repères. Aucune nouvelle itération déclenchée sans accord explicite (condition préalable du rapport). |
| (3) Exports STL/3MF Hyrule et Paco | PROTOTYPE numérique, **BLOCKED validation native/physique** | V13 `BAMBU_READINESS.md` : modules et corps 3MF fermés, dimensions contrôlées ; PrusaSlicer 2.7.2 uniquement, non Bambu Studio ; support Paco pouvant augmenter fortement la masse, couleurs et tolérances non testées en machine. V14 coûts/temps proxy, non devis. |

**Action suivante :** préserver les références CI et les modèles existants. Ne pas lancer V17 avant accord artistique ; ne pas déclarer les exports Bambu prêts à fabriquer sans import/tranchage Bambu Studio et coupon physique. Pour généralisation Photos→3D, sujet inédit à 4 vues nécessaire. Aucun achat ni fusion.
