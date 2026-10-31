#!/usr/bin/env bash
# render (real LDraw parts) + independent validation of one LDR
set -euo pipefail
LDR=$1; NAME=$2; O=$(dirname "$LDR"); L=$HOME/bench/ldraw-parts-library/complete/ldraw
cd $HOME/bench
venv/bin/python -I tools/ldr_expand.py --ldr "$LDR" --ldraw $L --json "$O/scene.json" --glb "$O/${NAME}_lego_geometry.glb" >/dev/null
cat > "$O/views.json" <<'J'
[{"name":"1_face","az":180,"el":8},{"name":"2_profil_gauche","az":270,"el":5},{"name":"3_trois_quarts","az":225,"el":20},
 {"name":"4_dos","az":0,"el":8},{"name":"5_profil_droit","az":90,"el":5},{"name":"6_dessus","az":180,"el":80}]
J
node tools/render_ldr.js "$O/scene.json" "$O/views.json" "$O/renders" >/dev/null
venv/bin/python -I tools/validate_ldr.py --ldr "$LDR" --ldraw $L --rbdb data/rb.db --out "$O" --name "$NAME" >/dev/null
