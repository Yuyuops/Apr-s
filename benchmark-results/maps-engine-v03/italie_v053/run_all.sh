#!/bin/bash
# V0.5.3 : regenerates the consolidated diorama, independent validation, BOM check, fragility audit (V0.5.2 audited with the same tool) and every real render.
cd "$(dirname "$0")"; . ./env.sh
$PY diorama_v053.py --out results/diorama_v053 --seed ${SEED:-7}
$PY check_render.py results/diorama_v053 > results/check_v053.log 2>&1
$PY verify_bom.py results/diorama_v053
$PY fragility.py results/diorama_v053 > /dev/null
$PY fragility.py v052_reference > /dev/null
$PY render_views.py results/diorama_v053 views_v053.json
