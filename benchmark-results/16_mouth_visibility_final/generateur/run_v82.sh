#!/bin/bash
# V8.2 chain (from ~/bench): V8 micro-details without the mouth (same as V8.1) -> assembly + lcm82 variant C -> notice -> validate_v3
set -e
cd ~/bench; R=proto/v82/runC; LD=ldraw-parts-library/complete/ldraw; mkdir -p $R
export GLB_REF=proto/v7/ref_full_frame.glb
venv/bin/python proto/v82/assemble_v82.py proto/v7/run proto/v81/md/microdetails.pkl $R proto/v8/details.json C | tail -1 | head -c 700; echo
DROP_UNATTACHED=1 venv/bin/python tools/reorder_notice.py $R/paco_V82.ldr $R/notice.ldr | tail -1
echo "raw $(grep -c '^1' $R/paco_V82.ldr) notice $(grep -c '^1' $R/notice.ldr)"
venv/bin/python tools/validate_v3.py --ldr $R/notice.ldr --ldraw $LD --rbdb data/rb.db --out $R --name val3 > $R/val3_stdout.txt
head -c 330 $R/val3_stdout.txt; echo
venv/bin/python tools/ldr_expand.py --ldr $R/notice.ldr --ldraw $LD --json $R/s.json --glb $R/g.glb | tail -1
