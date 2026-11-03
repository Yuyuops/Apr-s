#!/usr/bin/env bash
# V0.3, five independent reproduction cases; no archive is modified.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="$ROOT/../20_portable_engine/.venv/bin/python"
MODE="$1"
if [[ ! -x "$PY" ]]; then echo "Missing V11 Python environment: $PY" >&2; exit 2; fi
if [[ "$MODE" != "--generate" && "$MODE" != "--full" ]]; then
  echo "Usage: bash run_all.sh [--generate|--full]" >&2; exit 2
fi
"$PY" "$ROOT/tests/test_support_opt.py"
COMMAND="generate"
if [[ "$MODE" == "--full" ]]; then COMMAND="full"; fi
run_case() {
  local SOURCE="$1" TARGET="$2" SIZE="$3"
  echo "=== $TARGET ($SIZE studs) ==="
  "$PY" "$ROOT/engine/run_v03.py" "$COMMAND" --input "$SOURCE" --out "$ROOT/results/$TARGET" --finish A --n "$SIZE"
}
run_case "$ROOT/../maps-engine-v02/fixtures/ecosse_carte.png" "ecosse/A_32" 32
run_case "$ROOT/../maps-engine-v02/fixtures/ecosse_carte.png" "ecosse/A_48" 48
run_case "$ROOT/../maps-engine-v01/fixtures/ile_temoin.svg" "ile_temoin/A_32" 32
run_case "$ROOT/../maps-engine-v01/fixtures/test_3_zones.svg" "test_3_zones/A_32" 32
run_case "$ROOT/fixtures/archipel_original.svg" "archipel/A_32" 32
echo "All cases processed. Review support_report_v03.json inside results."
