# 09 : preuve de faisabilité par conception directe (V5)

Verdict : **VALIDER LA MÉTHODE**, avec 3 réserves (`DECISION.md`). La conception et la validation sont dans `DESIGN_REPORT.md`, le montage dans `NOTICE.md`.

| Fichier | Contenu |
|---|---|
| `comparaison_ref_C_V5.png` | Référence 3D / C / V5 : face, profil, trois quarts, raccord au crâne, oreille face extérieure, oreille face intérieure. Mêmes vues, lumière et échelle que dans 08 ; vraies pièces LDraw. |
| `module_oreille.ldr` | Module seul (79 pièces, repère de la tête), en 5 étapes : bases, mécanisme et pied, couche A, couche B, tuiles |
| `tete_C_avec_oreille_V5.ldr` | Tête C (poche de 08) + oreille V5, notice réordonnée et validée (84 étapes) |
| `nomenclature.csv` / `nomenclature_modele_complet.csv` | Module (28 références, nombre de sets Rebrickable) / modèle complet |
| `validation_technique.json` | Contrôles de conception (recouvrements, tenons visibles, écart au contour) + `validate_v2.py` sur le modèle complet, avec les chiffres de C et de V4.1 |
| `plan_couche_B_vs_reference.txt` | Contour de la couche B superposé à la silhouette mesurée (pas de 5 LDU) |
| `rendus/` | Vues V5 individuelles (celles de la référence et de C sont dans `08_.../rendus/`) |
| `scripts/design_ear.py` | La liste explicite des pièces et sa conversion en LDraw (aucune recherche automatique) |

## Reproduire (depuis `~/bench`, outils de `benchmark-results/tools`)

```bash
python scripts/design_ear.py out09     # lit proto/ear09/sil_mesh.npy et le repère V4.1 (module_report.json de 08)
DROP_UNATTACHED=1 python tools/reorder_notice.py out09/tete_C_avec_oreille_V5.ldr out09/notice.ldr
python tools/validate_v2.py --ldr out09/notice.ldr --ldraw <ldraw> --rbdb data/rb.db --out out09 --name tete_v5 --npz <paco_head400.npz>
python tools/ldr_expand.py --ldr out09/notice.ldr --ldraw <ldraw> --json s.json --glb g.glb
node tools/render_ldr.js s.json scripts/views.json rendus/r_V5
```

Outils inchangés depuis 08 : aucun outil commun modifié.
