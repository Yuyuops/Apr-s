# 08 : correction finale de l'oreille articulée (V4.1)

Verdict : **CHANGER DE MÉTHODE** (`DECISION.md`). Détails dans `TECHNICAL_REPORT.md`, montage dans `NOTICE.md`.

| Fichier | Contenu |
|---|---|
| `comparaison_ref_C_V4_V41.png` | Référence 3D / C / V4 / V4.1 : face, profil, trois quarts, raccord au crâne, oreille face extérieure, oreille face intérieure. Cadrage, angles, lumière et échelle identiques ; vraies pièces LDraw. |
| `detail_raccord_et_faces.png` | Raccord au crâne et deux faces de l'oreille, pour les 4 versions |
| `tete_C_avec_module.ldr` | Tête C (avec poche) + module V4.1, notice réordonnée (référence). `*_brut.ldr` : sortie directe du générateur. |
| `module_oreille.ldr` | Module seul (mêmes pièces, mêmes positions, repère de la tête) |
| `nomenclature.csv` / `nomenclature_modele_complet.csv` | Module / modèle complet, avec couleur et statut Rebrickable |
| `validation_connexions.json` | Contrôles `validate_v2.py` pour V4.1, V4 et C ; paramètres de génération ; poche et pièces retirées |
| `rendus/` | Vues individuelles (`r_ref`, `r_C`, `r_V4`, `r_V41`) |
| `scripts/` | `ear_module_v41.py`, `keep_bracket_component.py`, `views.json` |

## Reproduire (depuis `~/bench`, outils de `benchmark-results/tools`)

```bash
H=benchmark-results/05_demonstrateur_tete_paco/paco_head400.npz
python tools/proto/ear_module_v41.py $H out08
DROP_UNATTACHED=1 python tools/reorder_notice.py out08/tete_C_avec_module.ldr out08/notice.ldr
python scripts/keep_bracket_component.py out08/notice.ldr tete_C_avec_module.ldr
python tools/validate_v2.py --ldr tete_C_avec_module.ldr --ldraw <ldraw> --rbdb data/rb.db --out out08 --name tete --npz $H
python tools/ldr_expand.py --ldr tete_C_avec_module.ldr --ldraw <ldraw> --json s.json --glb g.glb
node tools/render_ldr.js s.json scripts/views.json rendus/r_V41
GLB_NATIVE=1 node tools/render_ldr.js <ref_head_frame.glb> scripts/views.json rendus/r_ref
```

**Versions :** inchangées (voir `07_articulated_ear_proof/README.md`).

**Outil modifié :** `tools/reorder_notice.py`. L'option `DROP_UNATTACHED=1` retire, en les comptant, les morceaux de sous-ensemble qui ne touchent rien hors de leur bloc. Sans cette option, son comportement est inchangé.
