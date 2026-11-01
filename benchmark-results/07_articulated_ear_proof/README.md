# 07 : démonstrateur d'oreille articulée

Lire dans cet ordre :
- `DECISION.md` (verdict : **CORRIGER LE MODULE**) ;
- `TECHNICAL_REPORT.md` ;
- `ASSEMBLY_STEPS.md`.

| Fichier | Contenu |
|---|---|
| `reference_vs_C_vs_module.png` | Prototype C / module / référence 3D : face, profil, trois quarts, fixation. Cadrage, angles et lumière identiques ; images LEGO calculées à partir des vraies pièces LDraw. |
| `detail_fixation.png` | Fixation en place (3 angles), module seul (face, dos, dessus), C et référence. |
| `module_oreille.ldr` | Module seul, dans son repère (notice réordonnée) |
| `tete_C_avec_module.ldr` | Tête C + module, notice réordonnée (référence). `*_brut.ldr` : sortie directe du générateur. |
| `nomenclature.csv` | Pièces du module, couleurs et statut Rebrickable. `nomenclature_modele_complet.csv` : tête + module. |
| `validation_connexions.json` | Contrôles `validate_v2.py` (module seul, tête + module, C de référence) et paramètres de génération |
| `rendus/` | Toutes les vues individuelles |
| `scripts/` | Copie des scripts propres à cette itération (outils communs dans `benchmark-results/tools/`) |

## Reproduire (depuis `~/bench`, outils de `benchmark-results/tools`)

```bash
H=benchmark-results/05_demonstrateur_tete_paco/paco_head400.npz
python tools/proto/ear_module.py $H out07                     # tête C sans oreille haute + module
python tools/reorder_notice.py out07/tete_C_avec_module.ldr tete_C_avec_module.ldr
python tools/reorder_notice.py out07/module_oreille.ldr module_oreille.ldr
python tools/validate_v2.py --ldr tete_C_avec_module.ldr --ldraw <ldraw> --rbdb data/rb.db --out out07 --name tete --npz $H
python tools/proto/ref_glb_headframe.py <paco_couleur_tex_miroirX.glb> <paco_couleur.glb> $H ref_head_frame.glb
python tools/ldr_expand.py --ldr tete_C_avec_module.ldr --ldraw <ldraw> --json s.json --glb g.glb
node tools/render_ldr.js s.json scripts/views.json rendus/r_module
GLB_NATIVE=1 node tools/render_ldr.js ref_head_frame.glb scripts/views.json rendus/r_ref
```

**Versions :** identiques à `VERSIONS.md` et à l'itération 06 : brickify `1564bb3`, LDraw `1f24cac`, rb.db latest-v8, Python 3.13.18, trimesh 5.2.0, numpy 2.5.4, scikit-learn 1.9.1, embreex 4.4.0.post1, three.js 0.160.0.

**Outils modifiés dans cette itération :**
- `conn.py` : équerres « Down », dessus de plateau tournant, points de volume réel ;
- `validate_v2.py` : pivot, collisions sur géométrie réelle, masse des pièces tournées ;
- `reorder_notice.py` : pivot ; aucun bloc ne peut plus disparaître ;
- `render_ldr.js` : option `GLB_NATIVE`.

Après ces modifications, les notices de C, D et E de l'itération 06 se régénèrent à l'identique.
