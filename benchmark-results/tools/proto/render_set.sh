#!/usr/bin/env bash
# identical render protocol for every version: same frame boxes (mm, glTF axes), same lights, same size
set -euo pipefail
LDR=$1; OUT=$2; L=$HOME/bench/ldraw-parts-library/complete/ldraw
mkdir -p "$OUT"; cd $HOME/bench
venv/bin/python -I tools/ldr_expand.py --ldr "$LDR" --ldraw $L --json "$OUT/scene.json" --glb /tmp/_unused.glb >/dev/null
FULL='[[0,0,-280],[216,179.2,0]]'; SNOUT='[[56,51.2,-280],[208,115.2,-150]]'; EARS='[[0,0,-150],[120,179.2,0]]'
cat > "$OUT/views.json" <<J
[{"name":"1_face","az":180,"el":8,"frameBox":$FULL},
 {"name":"2_trois_quarts","az":225,"el":20,"frameBox":$FULL},
 {"name":"3_profil","az":270,"el":5,"frameBox":$FULL},
 {"name":"4_oreilles_fixations","az":${EAR_AZ:-40},"el":25,"frameBox":$EARS},
 {"name":"5_museau","az":235,"el":18,"frameBox":$SNOUT}]
J
node tools/render_ldr.js "$OUT/scene.json" "$OUT/views.json" "$OUT" >/dev/null
rm -f "$OUT/scene.json"
