#!/bin/bash
# validation + renders of the assembled V7 sculpture (from ~/bench)
set -e
cd ~/bench; R=proto/v7/run; LD=ldraw-parts-library/complete/ldraw
DROP_UNATTACHED=1 venv/bin/python tools/reorder_notice.py $R/paco_V7.ldr $R/notice.ldr | tail -1
echo "raw $(grep -c '^1' $R/paco_V7.ldr) notice $(grep -c '^1' $R/notice.ldr)"
venv/bin/python tools/validate_v3.py --ldr $R/notice.ldr --ldraw $LD --rbdb data/rb.db --out $R --name val3 > $R/val3_stdout.txt
head -c 420 $R/val3_stdout.txt; echo
venv/bin/python tools/ldr_expand.py --ldr $R/notice.ldr --ldraw $LD --json $R/s.json --glb $R/g.glb | tail -1
cd tools; node render_ldr.js ../$R/s.json ../proto/v7/viewsV7.json ../proto/v7/r_lego | tail -1; cd ..
V="1_face 2_dos 3_profil_gauche 4_profil_droit 5_trois_quarts 6_dessus"; row(){ d=$1; s=""; for v in $V; do s="$s,$d/$v.png"; done; echo "${s#,}"; }
venv/bin/python tools/make_board.py proto/v7/comparaison_GLB_LEGO_V7.png "Paco 400 mm : GLB source / sculpture LEGO V7 automatique (vraies pieces LDraw, memes vues et lumiere)" "GLB source:$(row proto/v7/r_ref)" "LEGO V7:$(row proto/v7/r_lego)" | tail -1
Z="7_gros_plan_tete 8_gros_plan_oreilles 9_gros_plan_mains_pieds"; zrow(){ d=$1; s=""; for v in $Z; do s="$s,$d/$v.png"; done; echo "${s#,}"; }
venv/bin/python tools/make_board.py proto/v7/gros_plans_GLB_LEGO_V7.png "Paco : gros plans tete, oreilles, mains et pieds (GLB / LEGO V7)" "GLB source:$(zrow proto/v7/r_ref)" "LEGO V7:$(zrow proto/v7/r_lego)" | tail -1
