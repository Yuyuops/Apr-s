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
