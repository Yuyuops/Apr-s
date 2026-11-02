# 19 : second sujet complet : le Beagle (LEGO V10)

**Verdict : GÉNÉRALISATION PARTIELLE** (`VERDICT.md`). Départ : commit `5b9e734` (V9.1). Aucun achat, aucune fusion dans `main`, GLB source non modifié, moteur 2 non touché, **aucun essai physique**.

| Fichier | Contenu |
|---|---|
| `VERDICT.md` | Décision sur le moteur 1 |
| `RAPPORT_ESSAI1_SANS_MODIFICATION.md` | Premier essai, moteur gelé : échecs archivés |
| `RAPPORT_GENERALISATION.md` | Génération complète, fidélité mesurée, constructibilité |
| `RAPPORT_NON_REGRESSION_PACO.md` | Évolutions génériques E1 à E3 et rejeu de Paco |
| `RAPPORT_REPRODUCTIBILITE.md` | Ce qui est et n'est pas reproductible |
| `RISQUES_PHYSIQUES.md` | Limites et risques |
| `BILAN_MOTEUR1.md` | Bilan par axe, Paco et Beagle |

Dossiers : `essai1/` (journal du premier essai, segmentation fausse, état du corps seul), `modeles/` (LDraw : `beagle_V10_notice.ldr` ordonné, `beagle_V10_brut.ldr`, `beagle_avant_renforts.ldr`), `comparaisons/` et `rendus/` (GLB / LDraw réel, mêmes vues), `validation/` (validations, catalogue, stabilité, fidélité, pièces par le bas, scope, journal de la chaîne), `notice/` (plan, étapes, PDF), `nomenclature_complete.csv`, `generateur/` (script de la chaîne, outils V10, brickify_plus gelé et corrigé), `paco_non_regression/`.

Commande (depuis `~/bench`, voir les limites de reproductibilité) : `bash proto/v10/run_beagle.sh <dossier>`.
