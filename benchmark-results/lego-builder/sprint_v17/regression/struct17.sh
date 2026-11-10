#!/bin/bash
# usage: struct17.sh DIR -> dump + classify + weaklink
cd /home/user/v062/benchmark-results/maps-engine-v03/style_fidelity_v062; E1=/tmp/claude-0/clean/Apr-s/benchmark-results/20_portable_engine; export LEGO_ENGINE_HOME=$E1 LEGO_DEPS=$E1/.deps; d=$1; T=../../lego-builder/tools
$E1/.venv/bin/python $E1/engine/validate_v4.py --ldr $d/diorama.ldr --ldraw $E1/.deps/ldraw-parts-library/complete/ldraw --rbdb $E1/.deps/rb.db --out $d/validation_dump --name map --dump $d/dump.pkl > $d/vdump.log 2>&1
$E1/.venv/bin/python $T/structural_classify_v16.py $d/dump.pkl $d/classes.json | python3 -c "
import sys,json;r=json.loads(sys.stdin.read());print({k:v for k,v in r.items() if k not in('classes','worst10')});print({k:(v['count'],v['max_cut'],v['parts'][:4]) for k,v in r['classes'].items()})"
$E1/.venv/bin/python $T/weaklink_v16.py $d/dump.pkl $d/weak.json
