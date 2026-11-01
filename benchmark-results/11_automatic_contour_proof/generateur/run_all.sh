#!/bin/bash
# Reproduce LEGO V6 (from ~/bench): targets, generation A (with head) and B, validation, renders, test rig
set -e
cd ~/bench; LD=ldraw-parts-library/complete/ldraw; P=proto/ear11
venv/bin/python $P/contour.py $P/targets
venv/bin/python $P/autogen.py A_paco $P/runA --head | tail -1 | cut -c1-200
venv/bin/python $P/autogen.py B_beagle $P/runB | tail -1 | cut -c1-200
for X in A B; do
  R=$P/run$X; if [ $X = A ]; then IN=$R/tete_oreille_A_paco.ldr; NPZ="--npz proto/out/paco_head400.npz"; else IN=$R/oreille_B_beagle.ldr; NPZ=""; fi
  DROP_UNATTACHED=1 venv/bin/python tools/reorder_notice.py $IN $R/notice.ldr | tail -1
  echo "$X raw $(grep -c '^1' $IN) notice $(grep -c '^1' $R/notice.ldr)"
  venv/bin/python tools/validate_v2_bigcases.py --ldr $R/notice.ldr --ldraw $LD --rbdb data/rb.db --out $R --name val $NPZ > $R/val_stdout.txt; head -c 330 $R/val_stdout.txt; echo
  venv/bin/python tools/ldr_expand.py --ldr $R/notice.ldr --ldraw $LD --json $R/s.json --glb $R/g.glb | tail -1
done
venv/bin/python $P/rig.py $P/runA $P/rig
R=$P/rig; DROP_UNATTACHED=1 venv/bin/python tools/reorder_notice.py $R/banc_essai_fixation.ldr $R/notice.ldr | tail -1
venv/bin/python tools/validate_v2_bigcases.py --ldr $R/notice.ldr --ldraw $LD --rbdb data/rb.db --out $R --name val > $R/val_stdout.txt; head -c 300 $R/val_stdout.txt; echo
venv/bin/python tools/ldr_expand.py --ldr $R/notice.ldr --ldraw $LD --json $R/s.json --glb $R/g.glb | tail -1
cd tools
node render_ldr.js ../$P/runA/s.json ../proto/ear08/views.json ../$P/r_A | tail -1
node render_ldr.js ../$P/runB/s.json ../$P/viewsB.json ../$P/r_B | tail -1
node render_ldr.js ../$P/rig/s.json ../$P/viewsRig.json ../$P/r_rig | tail -1
