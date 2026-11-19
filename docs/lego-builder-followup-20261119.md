# Suivi LEGO Builder — 2026-11-19

Branche : `research/lego-builder-commercial-outputs-20261108`. Aucun achat, aucune fusion main, aucune modification des baselines.

## Sources consultées
- `docs/lego-builder-followup-20261117.md`, `docs/lego-builder-execution-status.md` ; V17 `sprint_v17/FINAL_VERDICT.md` ; script `sprint_v16/baseline_maps_build.sh` et validateur `tests/check_regression.py` ; workflow Maps et historique GitHub Actions.
- Branches/modules : Maps (8 baselines, Hyrule V17), Sculptures (Paco/Beagle), Photos→3D (Paco connu), Builder unifié (régression historique). Aucune exécution indépendante de ces quatre moteurs dans cette revue.

## 1 — Non-régression
**Blocage de déclenchement manuel levé.** Le workflow `lego-builder-maps-eight-proof.yml` est désormais également déclenché par un push modifiant ce fichier sur la branche autorisée. Commit `f568c160942f54d9198b0df3198766458867913e`. Run spécialisé [44482060610](https://github.com/Yuyuops/Apr-s/actions/runs/44482060610) créé le 19/11/2026 07:45 UTC, état **QUEUED** lors du contrôle. Ne pas confondre run créé et PASS. Le workflow exécute le script 8 Maps et le validateur SHA bloquant, archive log, SHA et commit, si le runner termine. CI générique [44482060435](https://github.com/Yuyuops/Apr-s/actions/runs/44482060435) également queued.

Dernier PASS spécialisé historique : [43387810132](https://github.com/Yuyuops/Apr-s/actions/runs/43387810132) le 13/11, sculptures, Photos→3D Paco et coupon Paco, **pas** 8 Maps. Empreintes historiques : Italie `17d9bdc60637614404494517c1736906ec238b1310257f2f9563d7c750cd776f`, Paco `9d07c041a4968245228c016c651fef0710fd26fee68f67eac771df261c28089a`, Beagle `551bde0f77f20c227b4c4fde7f9c286c32139c4c6ac2b458edc0b8cedf31808f`. **Aucun SHA de sortie recalculé pendant cette revue.**

## 2 — Moteurs
**PARTIAL/BLOCKED** : Hyrule V17 zone château techniquement validée historiquement, NO-GO artistique ; carte entière non lancée. Sculptures et Builder unifié : références historiques, pas de nouveau run. Photos→3D : Paco connu PASS historique, sujet inédit non testé. Aucun défaut moteur nouvellement reproduit : aucune correction spéculative.

## 3 — Exports STL/3MF
**PARTIAL/BLOCKED** : Hyrule/Paco individuels et modules validés seulement en partie par V13/V14 ; export complet, couverture BOM, notices, nouveaux SHA et coûts non rejoués. Estimations PrusaSlicer proxy seulement ; Bambu Studio et impression physique BLOCKED. Aucun export nouveau pendant cette revue.

## Prochaines actions
1. Vérifier la conclusion du run 44482060610 et télécharger les artefacts SHA/logs ; si FAIL, reproduire et corriger uniquement le défaut observé.
2. Étendre ensuite la CI aux exports complets Hyrule/Paco (pièces et modules, BOM/notice, SHA, temps/coûts proxy) avec artefacts et codes de sortie.
3. Garder NO-GO fabrication et commercial tant que Bambu Studio, impression et droits ne sont pas validés.

**Verdict :** déclenchement Maps rétabli, validation 8/8 en attente de preuve ; trois étapes non prêtes pour revue Claude.
