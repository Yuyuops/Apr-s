#!/bin/bash
# Build ONLY the 8 CI map baselines (no validation, no render) with the CURRENT engine and compare their LDraw SHA-256 with ci/reference_hashes.json.  usage: baseline_maps_build.sh OUTDIR
set -e; OUT=$1; E1=${LEGO_ENGINE_HOME:-/tmp/claude-0/clean/Apr-s/benchmark-results/20_portable_engine}; export LEGO_ENGINE_HOME=$E1; export LEGO_DEPS=$E1/.deps; PY=$E1/.venv/bin/python
cd "$(dirname "$0")/../../maps-engine-v03/style_fidelity_v062"; mkdir -p "$OUT"
declare -A STYLE=([italia]=premium_noyer_or_lagon_c2i [ecosse]=premium_noyer_or_lagon_ecosse [japon]=premium_noyer_or_lagon_japon [royaume_uni]=premium_noyer_or_lagon_royaume_uni)
for k in italia ecosse japon royaume_uni; do mkdir -p "$OUT/$k"; $PY build_style.py styles/${STYLE[$k]}.json compositions/${k}_portrait_64x96.json "$OUT/$k" --flank vertical >/dev/null; done
mkdir -p "$OUT/hyrule"; $PY build_style.py styles/premium_noyer_or_lagon_hyrule.json compositions/hyrule_80x80.json "$OUT/hyrule" --flank vertical >/dev/null
mkdir -p "$OUT/hyrule_biomes"; $PY build_style.py styles/premium_biomes_hyrule.json compositions/hyrule_biomes_80x80.json "$OUT/hyrule_biomes" --flank vertical >/dev/null
mkdir -p "$OUT/protoA_littoral" "$OUT/protoB_cadre_titre"; $PY build_style.py styles/premium_noyer_or_lagon_c2i.json compositions/proto_a_eolie_36x36.json "$OUT/protoA_littoral" --flank vertical >/dev/null; $PY build_style.py styles/premium_noyer_or_lagon_c2i.json compositions/proto_b_titre_24x48.json "$OUT/protoB_cadre_titre" --flank vertical >/dev/null
cd ../../lego-builder; $PY tests/check_regression.py maps "$(cd "$OLDPWD" && cd "$OUT" && pwd)"
