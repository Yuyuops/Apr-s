# Product V1 Beagle — Validation de la nomenclature (BOM)

Fichiers (dans le kit, `bom/`) : `Beagle_V1_BOM.csv`, `Beagle_V1_BOM.json`, `Beagle_V1_ldraw_parts.csv`, `Beagle_V1_rebrickable_import.csv`, `Beagle_V1_rare_parts.csv`, `bom_cross_check.json`. Générés par `tools/product_bom_v1.py` à partir du catalogue validé V12.1 (`beagle_catalogue.csv`) et recoupés avec le modèle LDraw lui-même.

| Contrôle | Résultat | Preuve |
|---|---|---|
| Total BOM = lignes `1 …` du modèle `Beagle_V1.ldr` | **PASS** : 10 567 = 10 567 | `bom/bom_cross_check.json` (`exact: true`, 0 écart, 0 pièce du modèle hors BOM) |
| Lignes (pièce x couleur) | **64** BOM = 64 modèle | idem |
| Formes de pièces / couleurs | **23** numéros de pièces, **5** couleurs (Dark Orange 484, White 15, Dark Tan 28, Reddish Brown 70, Black 0) | `Beagle_V1_BOM.json` |
| CSV = JSON = liste LDraw = import Rebrickable = modèle (mêmes quantités) | **PASS** | `validate_product_v1.py` contrôle 3, sur le ZIP livré |
| Modèle d'étapes (`Beagle_V1_steps.ldr`) a les mêmes pièces que le modèle | **PASS** | idem |
| Fichiers `.dat` LDraw existent, couleurs valides, paires pièce/couleur cataloguées (Rebrickable) | **PASS** : 0 paire hors catalogue | contrôle 5 + `validation/bom_verification.json` (moteur) |
| Quantités par étape (notice) = BOM | **PASS** : somme par pièce et couleur sur les 554 étapes (hors étapes « fixer ») = BOM | contrôle 4, `INSTRUCTIONS_VALIDATION.md` |
| Pièces rares / difficiles | **12 références signalées** : 1 rare (≤ 30 sets Rebrickable) — **plaque 4 x 6 (3032) Dark Orange, 945 pièces, 21 sets** — et 11 peu courantes (31–100 sets) dont plaques 2 x 3 (3021) Dark Orange x244, 2 x 6 (3795) x509, 1 x 6 (3666) x397, 1 x 3 (3623) x469 ; `bom/Beagle_V1_rare_parts.csv` | proxy de rareté = nombre de sets Rebrickable contenant la paire ; **ce n'est ni un stock ni une disponibilité** |
| Prix, disponibilité, coût | **NON FOURNIS** (aucun prix inventé) | `Beagle_V1_BOM.json` : `price: not provided`, `availability: not checked` |
| Liste BrickLink | **NON PRODUITE** : correspondances numéros de pièces et couleurs BrickLink absentes de nos données (aucune invention) ; liste Rebrickable fournie à la place | — |
Masse théorique du modèle : 5 253 g (convention du validateur, 0,10 g par tenon x tenon x plaque ; non pesée).
**Limite** : la couleur « Dark Orange » (484), qui représente 6 263 pièces sur 10 567, est une couleur récente ; sa disponibilité réelle dans toutes les formes n'est pas vérifiée.
