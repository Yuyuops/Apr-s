# Suivi LEGO Builder — 2026-11-13 (GitHub, exécution CI)

Branche : `research/lego-builder-commercial-outputs-20261108`. Baseline avant correction : `adc628ee558c1232bd167ab0ca6a898564bd443d`. Aucun achat, aucune fusion main, aucun changement de hash de référence.

## 1. Non-régression et preuves
- Workflow LEGO Builder du 2026-11-12 : [run 43127586851](https://github.com/Yuyuops/Apr-s/actions/runs/43127586851) = **FAIL** global. Job `sculpture-regression` **PASS** (GLB références, tests unitaires, V16, V17, Paco SHA, Beagle SHA). Job `photos-to-lego` **PASS** (reconstruction GLB et Paco SHA). Job `print-export` **FAIL** à l'étape coupon, voir ci-dessous.
- Le workflow `CI` du 2026-11-12 [run 43178911560](https://github.com/Yuyuops/Apr-s/actions/runs/43178911560) est **PASS**, mais teste le projet Après et **ne remplace pas** le workflow LEGO.
- Nouveau run LEGO [43387810132](https://github.com/Yuyuops/Apr-s/actions/runs/43387810132) déclenché par le correctif ; résultat **PENDING à la rédaction**. Ne pas attribuer PASS avant son achèvement. Aucun SHA de modèle recalculé localement pendant cette revue.
- Baselines historiques documentées : Paco SHA-256 `9d07c041a4968245228c016c651fef0710fd26fee68f67eac771df261c28089a`, Beagle `551bde0f77f20c227b4c4fde7f9c286c32139c4c6ac2b458edc0b8cedf31808f`, Italie `17d9bdc60637614404494517c1736906ec238b1310257f2f9563d7c750cd776f`. Empreintes historiques, non recalculées ici.

## 2. Blocage reproduit et correctif isolé
- Log réel du job `print-export` [130883488272](https://github.com/Yuyuops/Apr-s/actions/runs/43127586851/job/130883488272) : les exporteurs STL/3MF Paco sample et les validations géométriques passent ; l'appel `python -m lego_builder.print3d.coupon` échoue avec `ModuleNotFoundError: No module named 'manifold3d'` (exit 1).
- Cause : `manifold3d` installé dans `/tmp/print_site` via `pip --target`, mais le `PYTHONPATH` n'est préfixé que sur les appels au validateur, pas sur la commande coupon.
- Correction minimale dans `.github/workflows/lego-builder-regression.yml` : préfixer l'appel coupon par `PYTHONPATH=/tmp/print_site:$PYTHONPATH`. Commit `4775268911c217df6999a5b1a19c00908c6d599c`. Aucun changement de géométrie, moteur ou référence CI.
- Validation du correctif : **PENDING** sur run 43387810132, ne pas considérer comme résolu avant PASS du job.

## 3. État STL/3MF et Bambu
- Export sample Paco : job 43127586851, **PASS numérique** avant le coupon : 24 STL / 6 3MF pour briques, 1 STL / 8 3MF pour modules, contrôles watertight, indices, plateau et chevauchements à 0 défaut. Shape-aware a généré son rapport avant l'échec coupon.
- Hyrule/Paco complets : exports V13/V14 et rapports de BOM, masse, temps et coûts **historiques**, non régénérés pendant cette revue. Les temps restent des estimations proxy PrusaSlicer/formules, pas des mesures Bambu.
- Bambu Studio : **BLOCKED** (non ouvert ici). Test d'impression, ajustement des tenons, résistance : **BLOCKED physique**.

## 4. Branches inspectées
- Maps : branches `research/lego-maps-*` présentes ; rapport V13/V14/V17 sur branche produit, baselines 8/8 historiques ; Hyrule V17 **NO-GO artistique**.
- Sculptures : Beagle V12.1 et Paco V12.1, SHA historiques ; package Beagle V1 **GO numérique**, **NO-GO utilisateur/commercial** (test réel, licences).
- Photos→3D : `research/lego-builder-photos-to-lego` et `PHOTOS_TO_LEGO.md` consultés ; PASS sur Paco du workflow 43127586851 ; sujet inédit toujours non validé.
- Builder unifié : `research/lego-builder-unified` et `FINAL_VERDICT.md` consultés ; validation des entrées historiques, généralisation inconnue.
- `research/lego-brickify-benchmark` : README racine concerne encore Après ; ne pas l'utiliser comme preuve LEGO.

## Prochaines actions
1. Attendre le verdict du nouveau run LEGO 43387810132 ; en cas de FAIL, relever le log exact, corriger au plus près, relancer et enregistrer la preuve.
2. Réviser les exports Hyrule/Paco complets, y compris l'écart pièces prises en charge/ignorées, BOM et notice ; exiger SHA et artefacts du run courant.
3. Bambu Studio et coupon physique demeurent BLOCKED sans environnement matériel ; ne pas annoncer GO fabrication.
