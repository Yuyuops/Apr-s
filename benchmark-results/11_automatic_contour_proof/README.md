# 11 : preuve de contour automatique (V6)

Verdict : **CORRIGER L'ALGORITHME** (`RAPPORT_DECISION.md`). Le générateur produit les deux oreilles sans liste de positions et tous les contrôles passent, mais les grands bouts arrondis ne sont pas reproduits.

| Élément | Contenu |
|---|---|
| `A_comparaison.png` | Paco : référence / C / V5 / V5.1 / **V6 automatique**, mêmes 6 vues qu'en 08-10, vraies pièces LDraw |
| `B_comparaison.png` | Beagle : oreille de référence (vue du GLB), contour cible et pièces choisies, 4 rendus LDraw |
| `A_contour_overlay.png`, `B_contour_overlay.png` | Silhouette du GLB (gris), pièces de forme (bleu), plaques (noir) |
| `generateur/` | `contour.py` (extraction et analyse), `autogen.py` (générateur), `rig.py` (banc d'essai), `run_all.sh` (tout reproduire), `validate_v2_bigcases.py` (copie du validateur qui liste aussi les grands découpages), vues de rendu |
| `exemples/A_paco/` | Silhouette cible et analyse, rapport du générateur (réglages essayés, pièces, fixation), module `.ldr`, tête + oreille avec notice validée (78 étapes), validation, nomenclatures |
| `exemples/B_beagle/` | Idem pour le Beagle (module seul, notice de 63 étapes) |
| `banc_essai/` + `PROTOCOLE_ESSAI_FIXATION.md` | Banc d'essai réel de la fixation seule : `.ldr` validé, nomenclature, protocole |
| `rendus/` | Vues individuelles |

## Reproduire (depuis `~/bench`)

```bash
bash proto/ear11/run_all.sh     # = generateur/run_all.sh ; utilise les aides géométriques de proto/ear10/design_v51.py (10/scripts)
```

Dépendances : le repère et la tête sans oreille de 08 (`proto/ear08/run/`), la bibliothèque LDraw, `data/rb.db`.

`autogen.py` n'utilise aucune position de pièce écrite à la main. La liste manuelle de V5.1 (`design_v51.OUTER`) n'est lue que pour calculer la mesure de comparaison avec V5.1.
