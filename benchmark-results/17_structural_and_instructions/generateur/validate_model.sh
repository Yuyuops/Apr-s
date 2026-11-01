#!/bin/bash
# usage: validate_model.sh <in.ldr (brut or notice)> <outdir> <name> : reorder, validate_v4 (+dump), weak groups
set -e
cd ~/bench; mkdir -p $2
DROP_UNATTACHED=1 venv/bin/python tools/reorder_notice.py $1 $2/$3_notice.ldr | tail -1
venv/bin/python proto/v9/validate_v4.py --ldr $2/$3_notice.ldr --ldraw ldraw-parts-library/complete/ldraw --rbdb data/rb.db --out $2 --name $3 --dump $2/$3_dump.pkl | tail -2 | cut -c1-420
venv/bin/python proto/v9/weak_groups.py $2/$3_dump.pkl proto/v7/segmentation.npz $2/weak_$3.json | head -40
