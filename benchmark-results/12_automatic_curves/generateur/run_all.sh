#!/bin/bash
# Reproduce LEGO V6.1 (from ~/bench): generation A (head, fixation of V6) and B, validation v2 + v3, renders, metrics
set -e
cd ~/bench; LD=ldraw-parts-library/complete/ldraw; P=proto/ear12
venv/bin/python $P/autogen61.py A_paco $P/runA --head > $P/runA/gen_stdout.txt
venv/bin/python $P/autogen61.py B_beagle $P/runB > $P/runB/gen_stdout.txt
for X in A B; do
  R=$P/run$X; if [ $X = A ]; then IN=$R/tete_oreille_A_paco.ldr; NPZ="--npz proto/out/paco_head400.npz"; else IN=$R/oreille_B_beagle.ldr; NPZ=""; fi
  DROP_UNATTACHED=1 venv/bin/python tools/reorder_notice.py $IN $R/notice.ldr | tail -1
  echo "$X raw $(grep -c '^1' $IN) notice $(grep -c '^1' $R/notice.ldr)"
  venv/bin/python tools/validate_v3.py --ldr $R/notice.ldr --ldraw $LD --rbdb data/rb.db --out $R --name val3 $NPZ > $R/val3_stdout.txt
  venv/bin/python tools/validate_v2.py --ldr $R/notice.ldr --ldraw $LD --rbdb data/rb.db --out $R --name val2 $NPZ > $R/val2_stdout.txt
  venv/bin/python tools/ldr_expand.py --ldr $R/notice.ldr --ldraw $LD --json $R/s.json --glb $R/g.glb | tail -1
done
cd tools
node render_ldr.js ../$P/runA/s.json ../proto/ear08/views.json ../$P/r_A | tail -1
node render_ldr.js ../$P/runB/s.json ../proto/ear11/viewsB.json ../$P/r_B | tail -1
cd ..; venv/bin/python $P/metrics61.py $P/metrics.json > $P/metrics_stdout.txt
