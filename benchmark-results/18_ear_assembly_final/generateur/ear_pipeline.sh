#!/bin/bash
# LEGO V9.1 - ear pipeline (generic, same commands for every ear) : generator V6.1 (unchanged) -> validation + fragile groups -> seam stitching -> validation -> sequencing + independent replay
# usage: ear_pipeline.sh <ear.ldr> <outdir> <name>      (from ~/bench ; an ear without a head is validated alone)
set -e
cd ~/bench; OUT=$2; N=$3; mkdir -p $OUT
bash proto/v9/validate_model.sh $1 $OUT/avant $N
venv/bin/python proto/v91/stitch.py $OUT/avant/${N}_notice.ldr $OUT/avant/weak_$N.json $OUT/${N}_V91.ldr $OUT/stitch_log.json 3 --all
bash proto/v9/validate_model.sh $OUT/${N}_V91.ldr $OUT/apres ${N}_V91
venv/bin/python proto/v91/run_ears_v91.py $OUT/${N}_V91.ldr $OUT/sequences.json --all
