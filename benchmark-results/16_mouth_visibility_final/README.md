# 16 : Visibilité finale de la bouche (LEGO V8.2)

**Verdict : VALIDER AVEC LIMITATION.** Voir `VERDICT.md`.

| Fichier | Contenu |
|---|---|
| `RAPPORT_OCCULTATION_VISIBILITE.md` | Diagnostic complet : méthode, occultation et silhouette par caméra, couleurs exposées, origine du sombre, cellules visibles, cause, correction, contrôles. **Contient la correction de mes résultats V8.1 et de ma première mesure.** |
| `CONCLUSION_MOTEUR.md` | Capacité du moteur à générer les détails de visage |
| `PROBLEMES_NON_RESOLUS.md` | Limitations restantes, avec leur cause |
| `comparaisons/` | GLB / V8.1 / V8.2 : personnage entier, tête, gros plans de la bouche |
| `modeles/` | `paco_V82_notice.ldr` (ordonné, pour Studio ou LeoCAD), `paco_V82_brut.ldr`, `corps_seul_V82.ldr` |
| `nomenclature_complete.csv` | 2 756 pièces, 73 couples pièce × couleur, disponibilité Rebrickable |
| `validation/` | `validate_v3` (V8.2 et références V8, V8.1), comparaison chiffrée, différences de nomenclature |
| `analyse/` | Visibilité par caméra (mesure corrigée), cellules recolorées visibles, rapport du module. Les mesures `*CONTAMINEE*` sont conservées pour trace et **ne sont pas utilisées**. |
| `rendus/` | Vues séparées : GLB, V8.1, V8.2 |
| `generateur/` | `lcm82.py` (variante C), `assemble_v82.py`, `run_v82.sh`, outils de visibilité, `darkcells.py` |

Les rendus utilisent de vraies pièces LDraw (`render_ldr.js`), sans image générée par IA. Le GLB source n'est pas modifié. Les calculs mécaniques sont indicatifs.

Reproduction (depuis `~/bench`, avec V7 à V8.1 présents) : `bash proto/v82/run_v82.sh`.
