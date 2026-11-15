# Suivi LEGO Builder — 2026-11-15

Branche autorisée : `research/lego-builder-commercial-outputs-20261108`. HEAD initial vérifié via GitHub : `f3667eb866335734657bcd35a8c0b6aaabb34bc2`. Aucun achat, aucune fusion `main`, aucune baseline modifiée.

## Périmètre vérifié
Branches présentes : `research/lego-brickify-benchmark`, `research/lego-builder-photos-to-lego`, `research/lego-builder-unified`, plusieurs `research/lego-maps-*`. Rapports inspectés : `docs/lego-builder-followup-20261114.md`, `docs/lego-builder-product-direction-20261108.md`, `benchmark-results/lego-builder/sprint_v13/BAMBU_READINESS.md`, `sprint_v16_closure/REGRESSION_FINAL.md` ; workflow LEGO et script `sprint_v16/baseline_maps_build.sh` lus.

## (1) Non-régression : PASS historique / nouveau rejeu BLOCKED
- Dernier workflow LEGO vérifié dans le rapport précédent : [43387810132](https://github.com/Yuyuops/Apr-s/actions/runs/43387810132), trois jobs success au 13/11, sculpture Paco/Beagle, Photos→3D Paco connu, export échantillon Paco. Ce n'est PAS un rejeu 8/8 Maps.
- Le run CI général [43574624767](https://github.com/Yuyuops/Apr-s/actions/runs/43574624767), commit `f3667eb`, s'est terminé success le 14/11 ; il ne prouve pas les baselines Maps.
- Nouveau workflow isolé ajouté : `.github/workflows/lego-builder-maps-eight-proof.yml`, commit `a826ef1b73d6617e3f4947b7aeaaa324130dfc42`. Exécution **manuelle uniquement** pour limiter les coûts : construit 8 cartes, compare les SHA-256 bloquants, archive log, SHA et commit. **Non exécuté pendant cette revue : BLOCKED / PENDING**. Ne pas annoncer PASS.
- Les SHA historiques du rapport V16 ne sont pas recalculés aujourd'hui : Italie `17d9bdc60637614404494517c1736906ec238b1310257f2f9563d7c750cd776f`, Paco `9d07c041a4968245228c016c651fef0710fd26fee68f67eac771df261c28089a`, Beagle `551bde0f77f20c227b4c4fde7f9c286c32139c4c6ac2b458edc0b8cedf31808f`.

## (2) Blocages moteurs : PARTIAL / BLOCKED
- Maps Hyrule V17 : zone château numériquement valide, fidélité artistique NO-GO ; ne pas figer de baseline.
- Sculptures : Paco/Beagle PASS historique ; Beagle V1 kit numérique PASS selon rapport, construction physique et licences BLOCKED.
- Photos→3D : Paco déjà connu PASS historique, généralisation sujet inédit BLOCKED.
- Builder unifié : régression historique, nouveau rejeu de bout en bout BLOCKED.
- Aucun correctif moteur sans défaut nouvellement reproduit ; le seul changement est un workflow manuel de vérification.

## (3) STL/3MF Hyrule/Paco : PARTIAL / BLOCKED
- Échantillon Paco et coupon : PASS numérique historique CI.
- V13 : Hyrule 9 modules, Paco 8 modules ; fichiers individuels non exhaustifs, géométries approchées et supports multicolores risqués.
- Tranchage PrusaSlicer proxy uniquement ; Bambu Studio, impression et mesures de tolérances **BLOCKED**. Aucun nouveau STL/3MF ni SHA d'export complet produit aujourd'hui.

## Prochaines actions
1. Exécuter manuellement le workflow `LEGO Builder - eight Maps baseline proof` et inspecter artefact `lego-builder-maps-eight-proof` ; corriger seulement un échec reproduit.
2. Étendre les jobs aux exports **complets** Hyrule/Paco avec inventaire des pièces omises, BOM, SHA, rendus et estimation de durée/masse avec hypothèses, sans déclencher de reconstruction HF inutile.
3. Bambu Studio et essais physiques restent bloqués par l'absence d'environnement/machine ; ne pas annoncer GO fabrication ni commercial.

**Verdict :** amélioration vérifiable du dispositif CI, mais aucune nouvelle validation moteur, Maps 8/8 ou Bambu revendiquée. Pas de revue finale Claude.
