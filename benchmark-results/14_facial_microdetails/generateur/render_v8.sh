#!/bin/bash
# V8 renders (from ~/bench): GLB / V7 / V8, same views and light, real LDraw parts
set -e
cd ~/bench; R=proto/v8/run; LD=ldraw-parts-library/complete/ldraw
venv/bin/python tools/ldr_expand.py --ldr $R/notice.ldr --ldraw $LD --json $R/s.json --glb $R/g.glb | tail -1
cd tools; node render_ldr.js ../$R/s.json ../proto/v8/viewsV8.json ../proto/v8/r_v8 | tail -1
[ -d ../proto/v8/r_v7 ] || node render_ldr.js ../proto/v7/run/s.json ../proto/v8/viewsV8.json ../proto/v8/r_v7 | tail -1
[ -d ../proto/v8/r_ref ] || GLB_NATIVE=1 node render_ldr.js ../proto/v7/ref_full_frame.glb ../proto/v8/viewsV8.json ../proto/v8/r_ref | tail -1
cd ..
row(){ d=$1; shift; s=""; for v in "$@"; do s="$s,$d/$v.png"; done; echo "${s#,}"; }
V="1_face 2_dos 3_profil_gauche 4_profil_droit 5_trois_quarts 6_dessus"
venv/bin/python tools/make_board.py proto/v8/comparaison_GLB_V7_V8.png "Paco 400 mm : GLB source / LEGO V7 / LEGO V8 (vraies pieces LDraw, memes vues et lumiere)" "GLB source:$(row proto/v8/r_ref $V)" "LEGO V7:$(row proto/v8/r_v7 $V)" "LEGO V8:$(row proto/v8/r_v8 $V)" | tail -1
Z="7_visage_gauche 8_visage_droit 9_visage_avant 10_visage_trois_quarts 11_bouche 12_oreilles"
venv/bin/python tools/make_board.py proto/v8/gros_plans_visage_GLB_V7_V8.png "Visage de Paco : GLB source / LEGO V7 / LEGO V8 (micro-details automatiques)" "GLB source:$(row proto/v8/r_ref $Z)" "LEGO V7:$(row proto/v8/r_v7 $Z)" "LEGO V8:$(row proto/v8/r_v8 $Z)" | tail -1
B="7_visage_gauche 8_visage_droit 10_visage_trois_quarts"
venv/bin/python tools/make_board.py proto/v8/visage_grand_format.png "Visage : GLB / V7 / V8 (grand format)" "GLB source:$(row proto/v8/r_ref $B)" "LEGO V7:$(row proto/v8/r_v7 $B)" "LEGO V8:$(row proto/v8/r_v8 $B)" | tail -1
