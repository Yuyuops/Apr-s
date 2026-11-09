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
