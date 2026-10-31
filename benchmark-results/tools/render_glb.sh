#!/usr/bin/env bash
# 4 views of a textured GLB (scaled to 250 mm height, Y up, front = +Z as in glTF)
set -euo pipefail
GLB=$1; OUT=$2; T=$(cd "$(dirname "$0")" && pwd); mkdir -p "$OUT"
echo '[{"name":"glb_front","az":0,"el":8},{"name":"glb_left","az":90,"el":5},{"name":"glb_three_quarter","az":40,"el":20},{"name":"glb_back","az":180,"el":8}]' > "$OUT/glb_views.json"
node $T/render_ldr.js "$GLB" "$OUT/glb_views.json" "$OUT"
