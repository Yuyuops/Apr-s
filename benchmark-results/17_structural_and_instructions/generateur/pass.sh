#!/bin/bash
# usage: pass.sh <in.ldr> <weak.json> <out.ldr> <per_layer> <tag> : reinforce, validate_v4 (dump), weak groups
set -e
cd ~/bench; D=proto/v9/$5; mkdir -p $D
venv/bin/python proto/v9/reinforce.py $1 $2 $3 $D/log.json $4 ${6:-1} 2>&1 | grep -v Warn | tail -1
venv/bin/python proto/v9/validate_v4.py --ldr $3 --ldraw ldraw-parts-library/complete/ldraw --rbdb data/rb.db --out $D --name m --dump $D/dump.pkl 2>&1 | grep -v Warn | tail -2 | cut -c1-300
venv/bin/python proto/v9/weak_groups.py $D/dump.pkl proto/v7/segmentation.npz $D/weak.json 2>&1 | grep -v Warn | cut -c1-190
