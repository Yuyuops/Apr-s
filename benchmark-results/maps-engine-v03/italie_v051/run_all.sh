#!/bin/bash
# V0.5.1 : regenerates the diorama, the independent validation, the BOM verification and every real render (V0.5.1 and the archived V0.5 for the comparison).
cd "$(dirname "$0")"; . ./env.sh
$PY build_catalog.py
$PY diorama_v051.py --out results/diorama_v051 --seed ${SEED:-7}
$PY check_render.py results/diorama_v051
$PY verify_bom.py results/diorama_v051
$PY render_views.py results/diorama_v051 views_v051.json
$PY ../italie_v05/prototype_diorama.py --out v05_reference >/dev/null
$PY - <<'PY'
import json; p='v05_reference/metrics.json'; m=json.load(open(p)); m['size_studs']=[48,32]; m['height_plates']=21; json.dump(m,open(p,'w'),indent=2)
PY
$PY check_render.py v05_reference
$PY verify_bom.py v05_reference
$PY render_views.py v05_reference views_v05.json
