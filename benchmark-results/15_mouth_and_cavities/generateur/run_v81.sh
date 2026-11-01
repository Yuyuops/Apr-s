#!/bin/bash
# V8.1 chain (from ~/bench): V8 micro-details without the mouth -> assembly + lines-and-cavities module (variant A or B) -> notice -> validate_v3
# usage: run_v81.sh <A|B>
set -e
V=${1:-A}; cd ~/bench; R=proto/v81/run$V; LD=ldraw-parts-library/complete/ldraw; mkdir -p $R proto/v81/md
[ -f proto/v81/md/microdetails.pkl ] || MD_SKIP_MOUTH=1 venv/bin/python proto/v8/microdetails.py proto/v8/details.json proto/v7/run proto/v81/md 2>&1 | grep -v Warn
venv/bin/python proto/v8/assemble_v81.py proto/v7/run proto/v81/md/microdetails.pkl $R proto/v8/details.json $V | tail -1 | head -c 700; echo
DROP_UNATTACHED=1 venv/bin/python tools/reorder_notice.py $R/paco_V81.ldr $R/notice.ldr | tail -1
echo "raw $(grep -c '^1' $R/paco_V81.ldr) notice $(grep -c '^1' $R/notice.ldr)"
venv/bin/python tools/validate_v3.py --ldr $R/notice.ldr --ldraw $LD --rbdb data/rb.db --out $R --name val3 > $R/val3_stdout.txt
head -c 330 $R/val3_stdout.txt; echo
venv/bin/python tools/ldr_expand.py --ldr $R/notice.ldr --ldraw $LD --json $R/s.json --glb $R/g.glb | tail -1
