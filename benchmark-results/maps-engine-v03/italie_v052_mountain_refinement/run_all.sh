#!/bin/bash
# V0.5.2 : regenerates the diorama, independent validation, BOM verification, fragility audit and every real render (V0.5.1 reference audited with the same tools).
cd "$(dirname "$0")"; . ./env.sh
$PY diorama_v052.py --out results/diorama_v052 --seed ${SEED:-7}
$PY check_render.py results/diorama_v052 > results/check_v052.log 2>&1
$PY verify_bom.py results/diorama_v052
$PY fragility.py results/diorama_v052 > /dev/null
$PY fragility.py v051_reference > /dev/null
$PY verify_bom.py v051_reference
$PY render_views.py results/diorama_v052 views_v052.json
