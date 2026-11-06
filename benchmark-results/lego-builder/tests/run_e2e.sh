#!/bin/bash
# End-to-end tests A (Italy), B (Hyrule), C (Paco), D (new map image). usage : run_e2e.sh OUTROOT PICTURE_HYRULE PICTURE_NEW_MAP   (pictures are third-party images : not versioned)
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"; BR="$HERE/.."; M="$BR/maps-engine-v03/style_fidelity_v062"; OUT=${1:?}; HY=${2:?}; NEW=${3:?}
export PYTHONPATH="$HERE:$M"; PY="$LEGO_ENGINE_HOME/.venv/bin/python"
$PY -m lego_builder geo --composition "$M/compositions/italia_portrait_64x96.json" --style "$M/styles/premium_noyer_or_lagon_c2i.json" --out "$OUT/A_italia"
$PY -m lego_builder run "$HY" --out "$OUT/B_hyrule_400mm" --size-mm 400 --title Hyrule
$PY -m lego_builder run "$HY" --out "$OUT/B_hyrule_704mm" --size-mm 704 --title Hyrule
$PY -m lego_builder run "$BR/02_glb_gratuit_hunyuan2mv/paco.glb" --out "$OUT/C_paco" --size-mm 400
$PY -m lego_builder run "$NEW" --out "$OUT/D_new_map" --size-mm 400
python3 - "$OUT" "$M" "$BR" <<'PY'
import hashlib, json, sys
o, M, BR = sys.argv[1:4]; sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
man = json.load(open(M + "/livraison_v09/deliverables_manifest.json"))["italia"]["ldr_sha256"]
print("A Italy LDraw identical to the reference :", sha(o + "/A_italia/model/diorama.ldr") == man)
print("C Paco LDraw identical to the accepted V12.1 model :", sha(o + "/C_paco/model/diorama.ldr") == sha(BR + "/22_color_structural_regression/modeles/paco_V121_A_palette_V12/paco_brut.ldr"))
PY
