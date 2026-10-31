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
