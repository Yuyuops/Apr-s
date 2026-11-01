#!/bin/bash
# V8 chain (from ~/bench): detection -> micro-details -> assembly -> notice -> validate_v3
set -e
cd ~/bench; R=proto/v8/run; LD=ldraw-parts-library/complete/ldraw
venv/bin/python proto/v8/detect.py proto/v7/ref_full_frame.glb proto/v7/paco_full400.npz proto/v7/segmentation.npz proto/v7/segmentation.json proto/v8/details.json > $R/detect_stdout.txt
venv/bin/python proto/v8/microdetails.py proto/v8/details.json proto/v7/run $R 2>&1 | grep -v Warn
venv/bin/python proto/v8/assemble_v8.py proto/v7/run $R/microdetails.pkl $R | tail -1 | head -c 600; echo
DROP_UNATTACHED=1 venv/bin/python tools/reorder_notice.py $R/paco_V8.ldr $R/notice.ldr | tail -1
echo "raw $(grep -c '^1' $R/paco_V8.ldr) notice $(grep -c '^1' $R/notice.ldr)"
venv/bin/python tools/validate_v3.py --ldr $R/notice.ldr --ldraw $LD --rbdb data/rb.db --out $R --name val3 > $R/val3_stdout.txt
head -c 330 $R/val3_stdout.txt; echo
