#!/usr/bin/env bash
# Full chain for one GLB: brickify (original, unmodified) -> real-part renders -> independent validation -> instructions PDF.
# usage: tools/run_model.sh <glb> <name> <outdir> [extra brickify args...]
# env: BENCH (workspace root, default dir of this script/..), LDRAW (LDraw library root)
set -euo pipefail
GLB=$1; NAME=$2; OUT=$3; shift 3
BENCH=${BENCH:-$(cd "$(dirname "$0")/.." && pwd)}
LDRAW=${LDRAW:-$BENCH/ldraw-parts-library/complete/ldraw}
PY=$BENCH/venv/bin/python; T=$BENCH/tools
mkdir -p "$OUT"
$PY $BENCH/brickify/pipeline/brickify.py --glb "$GLB" --out "$OUT" --name "$NAME" --ldconfig $LDRAW/LDConfig.ldr "$@" > "$OUT/${NAME}_brickify.log" 2>&1
echo "brickify $* " > "$OUT/${NAME}_command.txt"
$PY $T/ldr_expand.py --ldr "$OUT/$NAME.ldr" --ldraw $LDRAW --json "$OUT/scene.json" --glb "$OUT/${NAME}_lego_geometry.glb"
cat > "$OUT/views.json" <<'J'
[{"name":"1_front","az":180,"el":8},{"name":"2_left_profile","az":270,"el":5},{"name":"3_three_quarter_front","az":225,"el":20},
 {"name":"4_back","az":0,"el":8},{"name":"5_top","az":180,"el":80},{"name":"6_exploded","az":225,"el":18,"explode":40,"explodeEvery":12}]
J
node $T/render_ldr.js "$OUT/scene.json" "$OUT/views.json" "$OUT/renders"
$PY $T/validate_ldr.py --ldr "$OUT/$NAME.ldr" --ldraw $LDRAW --rbdb $BENCH/data/rb.db --out "$OUT" --name "$NAME"
$PY $T/make_instructions.py --scene "$OUT/scene.json" --out "$OUT" --name "$NAME"
rm -rf "$OUT/_instr_png"
