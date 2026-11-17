# Suivi LEGO Builder — 2026-11-17 (lecture GitHub, sans runner)

Branche autorisée : `research/lego-builder-commercial-outputs-20261108`. HEAD avant rapport : `adbb8da3cb59b024245e6388226abd7d854b8be1` (API Git refs). Aucun achat, aucune fusion dans `main`, aucune baseline modifiée.

## Sources réellement consultées
- API GitHub Actions : 37 runs sur la branche ; derniers runs du 15/11 : [43694644903](https://github.com/Yuyuops/Apr-s/actions/runs/43694644903) et [43694631931](https://github.com/Yuyuops/Apr-s/actions/runs/43694631931), tous deux **CI générique success** (commits `adbb8da` et `a826ef1`). Aucun run nommé `LEGO Builder - eight Maps baseline proof` dans la liste de runs consultée.
- Dernier run spécialisé LEGO : [43387810132](https://github.com/Yuyuops/Apr-s/actions/runs/43387810132), **success** le 13/11, SHA `4775268911c217df6999a5b1a19c00908c6d599c`. Il couvre sculptures, Photos→3D Paco connu et échantillon export Paco, **pas** les huit Maps ni les exports complets.
- Rapports lus : `docs/lego-builder-followup-20261114.md`, `docs/lego-builder-followup-20261115.md`, `benchmark-results/lego-builder/sprint_v16_closure/REGRESSION_FINAL.md`, `sprint_v17/FINAL_VERDICT.md`, `sprint_v13/BAMBU_READINESS.md`, `FINAL_STATE_20261108.md`, et `.github/workflows/lego-builder-maps-eight-proof.yml`.
- Branches historiques Maps, Sculptures, Photos→3D, Builder unifié : inventaire documenté dans les suivis du 14–15/11 ; aucun nouveau résultat d'exécution indépendant de ces branches durant cette revue.

## 1. Non-régression : PASS historique / BLOCKED nouveau rejeu
- V16 : 8/8 Maps, Italie `17d9bdc60637614404494517c1736906ec238b1310257f2f9563d7c750cd776f`, Paco `9d07c041a4968245228c016c651fef0710fd26fee68f67eac771df261c28089a`, Beagle `551bde0f77f20c227b4c4fde7f9c286c32139c4c6ac2b458edc0b8cedf31808f` — **empreintes historiques citées, non recalculées le 17/11**.
- Workflow huit Maps existe et est **workflow_dispatch uniquement** ; aucun lancement nouveau effectué. Le connecteur GitHub disponible n'expose pas le dispatch initial ; le conteneur local n'a pas accès à github.com (DNS). Les succès CI génériques du 15/11 ne prouvent pas les 8/8.
- **BLOCKED** pour nouveau rejeu, SHA de sortie et artefacts neufs. Aucun PASS nouveau revendiqué.

## 2. Moteurs : PARTIAL / BLOCKED
- Maps Hyrule V17 : zone château PASS numérique historique, NO-GO artistique ; carte complète non lancée.
- Sculptures Paco/Beagle : PASS historique/CI 13/11, pas de nouvelle correction.
- Photos→3D : Paco connu PASS 13/11 ; sujet inédit non prouvé.
- Builder unifié : preuves historiques, pas de nouveau test complet.
- Aucun défaut moteur nouvellement reproduit ; aucune modification spéculative.

## 3. STL/3MF Hyrule/Paco : PARTIAL / BLOCKED
- V13 : 9 modules Hyrule, 8 modules Paco, contrôles numériques historiques ; exports individuels incomplets (V14 : Paco 3077/3193, Hyrule 10167/10682), formes concaves et supports multicolores non résolus.
- Run 13/11 : échantillon Paco/coupon PASS numérique, pas les exports complets.
- Aucun STL/3MF, BOM, notice, rendu, SHA, temps ni coût **nouvellement généré ou mesuré** le 17/11.
- PrusaSlicer proxy seulement ; Bambu Studio et impression physique BLOCKED.

## Actions et alerte
1. Déclencher le workflow manuel `LEGO Builder - eight Maps baseline proof` sur la branche de travail (GitHub Actions → Run workflow), puis archiver logs/SHA/commit ; ce déclenchement initial n'est pas accessible via les outils de cette exécution.
2. Sur runner, étendre la preuve aux exports complets Hyrule/Paco, avec couverture exacte des pièces, BOM/notice, SHA, rendus et estimations explicitement proxy ; corriger uniquement un défaut reproduit.
3. Bambu Studio et coupon physique exigent un environnement réel ; ne pas annoncer GO fabrication.
4. Conserver le NO-GO artistique Hyrule et le NO-GO commercial.

**Verdict :** aucun GO nouveau ; blocage de lancement du workflow Maps persistant. Pas prêt pour revue finale Claude.
