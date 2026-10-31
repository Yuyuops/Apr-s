# Reproduire

```bash
mkdir -p ~/bench && cd ~/bench
git clone https://github.com/hamnaanaa/brickify && git -C brickify checkout 1564bb3b2704c522e084fdb1b2a3ce9d3f11d300
git clone --depth 1 https://github.com/gkjohnson/ldraw-parts-library          # bibliothèque LDraw officielle (miroir)
git clone https://github.com/7kzaincode/autotile
mkdir -p data && curl -L https://github.com/ojuuji/rb.db/releases/download/latest-v8/rb.db.xz | xz -d > data/rb.db
python3 -m venv venv && venv/bin/pip install -r brickify/requirements.txt networkx
python3 -c "import sqlite3;c=sqlite3.connect('data/rb.db');c.execute('create table pcs_mat as select part_num,color_id,num_sets,min_year,max_year from part_color_stats');c.execute('create index pcs_i on pcs_mat(part_num,color_id)');c.commit()"
cp -r <benchmark-results>/tools . && (cd tools && npm i three@0.160.0)   # + playwright/chromium

# passage brut, paramètres du README, 250 mm
tools/run_model.sh model.glb nom runs/nom_raw --height-mm 250 --colour-mode palette --gain 1.3 --interior dominant
tools/render_glb.sh model.glb runs/nom_raw/glb_renders
venv/bin/python tools/make_board.py board.png "titre" "Référence:img1,img2" "GLB:..." "LEGO:..."
```

## Passage du 2026-10-31 : GLB gratuits (Hunyuan3D-2mv) et chiens

```bash
venv/bin/pip install gradio_client embreex scikit-learn rtree
cp <benchmark-results>/tools/{hf_gen.py,colorize_from_views.py,vcol_to_texture.py,mirror_x.py,boards.sh,sheet.py} scripts/
# fond blanc (les images transparentes donnent une boîte)
venv/bin/python -c "from PIL import Image;import glob,os
for f in glob.glob('<benchmark-results>/01_inputs_prepared/*_rgba.png'):
  im=Image.open(f).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);bg.convert('RGB').save('inputs_blanc/'+os.path.basename(f).replace('_rgba','_blanc'))"
# forme seule, 4 vues (face, dos, profil_gauche -> left, profil_droit -> right)
INDIR=$HOME/bench/inputs_blanc/ SUF=blanc EP=/shape_generation venv/bin/python scripts/hf_gen.py tencent/Hunyuan3D-2mv paco runs/paco_hf2mv_shape_blanc 30 256
venv/bin/python scripts/colorize_from_views.py runs/paco_hf2mv_shape_blanc/paco_out0.glb paco runs/paco_hf2mv_shape_blanc/paco_couleur.glb runs/paco_hf2mv_shape_blanc/paco_couleur_report.json
venv/bin/python scripts/vcol_to_texture.py runs/paco_hf2mv_shape_blanc/paco_couleur.glb runs/paco_hf2mv_shape_blanc/paco_couleur_tex.glb
# brut (commande du README fourni)
tools/run_model.sh runs/paco_hf2mv_shape_blanc/paco_couleur_tex.glb paco runs/paco_raw250 --height-mm 250 --colour-mode palette --palette-passes 2 --interior dominant
# réglé : miroir pré-corrigé + palette restreinte, 250 et 400 mm (codes exclus : voir *_command.txt)
venv/bin/python scripts/mirror_x.py runs/paco_hf2mv_shape_blanc/paco_couleur_tex.glb runs/paco_hf2mv_shape_blanc/paco_couleur_tex_miroirX.glb
tools/run_model.sh runs/paco_hf2mv_shape_blanc/paco_couleur_tex_miroirX.glb paco runs/paco_tuned250 --height-mm 250 --colour-mode palette --palette-passes 4 --interior dominant --exclude <codes>
# AutoTile (mêmes GLB colorés, sans IA)
(cd autotile && ../venv/bin/python pipeline.py --mesh ../runs/paco_hf2mv_shape_blanc/paco_couleur.glb --resolution 32 --out ../runs/autotile/paco_r32.json)
```
Idem pour `beagle` (AutoTile : `--resolution 37`).
