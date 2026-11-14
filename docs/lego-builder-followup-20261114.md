# Suivi LEGO Builder — 2026-11-14 (contrôle GitHub vérifié)

Branche : `research/lego-builder-commercial-outputs-20261108`. HEAD consulté : `b23023703a2ed04ea9cfb0993a08aa2f247719ab` (documentation, descendant du correctif `4775268911c217df6999a5b1a19c00908c6d599c`). Aucun achat, aucune fusion dans main, aucune modification des baselines.

## 1. Non-régression — PASS sur CI existante, aucun nouveau run aujourd'hui

**Vérification directe GitHub Actions le 14/11/2026** : run LEGO [43387810132](https://github.com/Yuyuops/Apr-s/actions/runs/43387810132), commit exact `4775268911c217df6999a5b1a19c00908c6d599c`, exécuté le 13/11 07:43–07:59 UTC, **completed/success**. Trois jobs terminés **success** :
- `print-export` [131760321637](https://github.com/Yuyuops/Apr-s/actions/runs/43387810132/job/131760321637) : export échantillon Paco briques et modules, validation numérique bloquante, génération `shape-aware`, tenon et coupon de tolérance, tranchage informatif PrusaSlicer, publication artefact ; toutes les étapes success. Le `ModuleNotFoundError: manifold3d` du run précédent est donc résolu **dans ce workflow**.
- `photos-to-lego` [131760322039](https://github.com/Yuyuops/Apr-s/actions/runs/43387810132/job/131760322039) : 4 photos Paco → GLB → LEGO, comparaison GLB et SHA Paco avec la référence, success ; **ceci ne prouve pas la généralisation à un sujet inédit**.
- `sculpture-regression` [131760322041](https://github.com/Yuyuops/Apr-s/actions/runs/43387810132/job/131760322041) : GLB sources, unitaires, V16/V17, Paco et Beagle, SHA bloquants, success.

Artefacts Actions **existants et non expirés**, IDs vérifiés : `lego-builder-print-export` 14019865214 (6111 octets), `lego-builder-photos-to-lego` 14019770951 (1945476 octets), `lego-builder-sculptures` 14019582801 (1999333 octets). Leur contenu binaire n'a pas été extrait/recalculé pendant cette revue. Les SHA de référence **rapportés historiquement, pas recalculés ce jour** : Paco `9d07c041a4968245228c016c651fef0710fd26fee68f67eac771df261c28089a`, Beagle `551bde0f77f20c227b4c4fde7f9c286c32139c4c6ac2b458edc0b8cedf31808f`, Italie `17d9bdc60637614404494517c1736906ec238b1310257f2f9563d7c750cd776f`.

**Limite** : le workflow LEGO ne démontre pas ici le rejeu complet des huit baselines Maps, des exports Hyrule complets ni des imports Bambu. Le CI générique [43387858520](https://github.com/Yuyuops/Apr-s/actions/runs/43387858520) a également réussi, mais ne remplace pas le workflow LEGO. Aucun nouveau workflow déclenché par cette revue ; aucune prétention à un nouveau calcul de SHA.

## 2. Moteurs — blocage CI corrigé ; artistique et généralisation PARTIAL/BLOCKED

- Maps : rapports V13/V14/V17 lus, branches `research/lego-maps-*` présentes. Hyrule V17 : château pilote valide numériquement, **NO-GO artistique** et pas de validation de la carte complète.
- Sculptures : Paco/Beagle **PASS CI** sur leurs SHA de référence ; Beagle V1 package numérique validé dans ses rapports, construction réelle et droits **BLOCKED**.
- Photos→3D : **PASS CI sur Paco déjà connu** ; **BLOCKED pour généralisation** faute de sujet inédit et de validation humaine.
- Builder unifié : rapport et baselines historiques, pas de nouveau rejeu de bout en bout des huit modèles dans le run consulté.
- Aucun correctif moteur supplémentaire apporté : aucun échec nouveau démontré sur la campagne du 13/11 ; ne pas changer les baselines sans reproduction.

## 3. STL/3MF Bambu Hyrule/Paco — PARTIAL numérique, BLOCKED natif/physique

- `print-export` : **PASS CI** pour l'échantillon Paco et le coupon ; les validations de géométrie sont exécutées sur cet échantillon.
- Exports historiques V13 : Paco 8 modules, Hyrule 9 modules ; les pièces individuelles et modules complets **n'ont pas été régénérés dans cette revue**. V14 : PrusaSlicer 2.7.2 sur profils proxy ; estimation de temps/coûts, **pas** mesure Bambu.
- Points à qualifier : pièces ignorées/approximées dans les exports individuels, formes concaves, supports et chemins multicolores, répartition couleurs AMS, BOM/notice exactes et SHA des exports complets. L'exemple V14 affiche 3077/3193 briques Paco et 10167/10682 Hyrule imprimables individuellement ; ces couvertures sont historiques et ne doivent pas être assimilées à 100 %.
- Bambu Studio non exécuté, aucun coupon imprimé, aucun coût réel : **BLOCKED**.

## Actions suivantes / portes de sortie

1. Sur runner CI, ajouter un **job distinct** de régression Maps 8/8 et Builder unifié complet, avec logs, commit et SHA des sorties ; éviter de confondre la réussite des tests V16/V17 avec les huit baselines.
2. Faire tourner sur runner des exports **complets** Hyrule et Paco, briques individuelles et modules ; publier manifeste pièces prises en charge/ignorées, BOM, notice, SHA, rendus et tranchage proxy avec bornes de temps/coût. Si budget Actions trop élevé, découper en jobs manuels isolés ; ne pas annoncer PASS avant artefacts.
3. Maintenir **BLOCKED** pour Bambu Studio et tests physiques jusqu'à import/tranchage et coupon mesuré. Hyrule : conserver NO-GO artistique. Ne pas fusionner ni acheter.

**Verdict :** correction `manifold3d` confirmée PASS sur CI LEGO ; les trois étapes du programme **ne sont pas toutes vérifiées**. Aucune intervention utilisateur indispensable aujourd'hui, mais validation physique et artistique nécessaire avant GO fabrication/commercial.
