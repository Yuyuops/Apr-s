# 10 : finalisation de l'oreille conçue directement (V5.1)

Verdict : **CHANGER LA FIXATION** (`DECISION.md`) : forme réussie, fixation encore insuffisante. Détails dans `TECHNICAL_REPORT.md`, automatisation dans `AUTOMATISATION.md`, montage dans `NOTICE.md`.

| Fichier | Contenu |
|---|---|
| `comparaison_ref_C_V5_V51.png` | Référence 3D / C / V5 / V5.1 : face, profil, trois quarts, raccord, faces extérieure et intérieure. Mêmes vues, lumière et échelle qu'en 08 et 09 ; vraies pièces LDraw. |
| `zooms/` | Gros plans V5.1 : raccord (2 angles) et bord supérieur |
| `rendus/` | Vues V5.1 individuelles |
| `module_oreille.ldr` | Module seul (142 pièces), repère de la tête |
| `tete_C_avec_oreille_V51.ldr` | Tête C reconstruite autour de l'oreille + oreille, notice réordonnée et validée (85 étapes) |
| `nomenclature.csv` / `nomenclature_modele_complet.csv` | Module (29 références, nombre de sets Rebrickable) / modèle complet |
| `validation_technique.json` | Contrôles de conception + `validate_v2.py`, avec les chiffres de C et de V5 |
| `scripts/design_v51.py` | Conception (liste manuelle du contour) et règles (miroir, âme, tuiles, assise, creusement, reconstruction de la tête) |

## Reproduire (depuis `~/bench`)

```bash
python scripts/design_v51.py out10     # lit le repère et la tête sans oreille de 08 (proto/ear08/run/)
DROP_UNATTACHED=1 python tools/reorder_notice.py out10/tete_C_avec_oreille_V51.ldr out10/notice.ldr
python tools/validate_v2.py --ldr out10/notice.ldr --ldraw <ldraw> --rbdb data/rb.db --out out10 --name tete_v51 --npz <paco_head400.npz>
python tools/ldr_expand.py --ldr out10/notice.ldr --ldraw <ldraw> --json s.json --glb g.glb
node tools/render_ldr.js s.json scripts/views.json rendus/
```

`DROP_UNATTACHED` ne retire aucune pièce dans la version livrée (1 321 pièces avant et après). Aucun outil commun n'a été modifié.
