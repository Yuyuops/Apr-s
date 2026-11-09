#!/bin/bash
# Sprint V16 closure : full regression at commit f962b6a. usage: closure_reg.sh  (logs in $L)
B=/home/user/v062/benchmark-results/lego-builder; L=$B/sprint_v16_closure/regression; O=/tmp/closure_out; mkdir -p $O
E1=/tmp/claude-0/clean/Apr-s/benchmark-results/20_portable_engine; export LEGO_ENGINE_HOME=$E1 LEGO_DEPS=$E1/.deps LEGO_NODE_MODULES=$E1/node_modules NODE_PATH=$E1/node_modules; PY=$E1/.venv/bin/python
cd /home/user/v062; echo "HEAD $(git rev-parse --short HEAD)" > $L/commit.txt; git status --short | grep -v '^??' >> $L/commit.txt
run(){ n=$1; shift; echo "== $n: $*" > $L/$n.log; s=$(date +%s); "$@" >> $L/$n.log 2>&1; rc=$?; echo "exit=$rc seconds=$(( $(date +%s)-s ))" >> $L/$n.log; echo "$n rc=$rc"; }
cd $B/..; 
run 01_glb_inputs python3 lego-builder/tests/check_regression.py glb
run 02_unit python3 lego-builder/tests/test_unit.py
run 03_engine_v16 $PY lego-builder/tests/test_engine_v16.py
run 04_maps_8_baselines lego-builder/sprint_v16/baseline_maps_build.sh $O/maps
cd $B/..; export PYTHONPATH=$B
run 05_builder_geo_italy $PY -m lego_builder geo --composition maps-engine-v03/style_fidelity_v062/compositions/italia_portrait_64x96.json --style maps-engine-v03/style_fidelity_v062/styles/premium_noyer_or_lagon_c2i.json --out $O/italia
run 06_paco_glb $PY -m lego_builder run 02_glb_gratuit_hunyuan2mv/paco.glb --out $O/paco --size-mm 400 --notice off
run 07_paco_sha python3 lego-builder/tests/check_regression.py sculpture paco $O/paco/model/diorama.ldr paco_V121_A_palette_V12
run 08_beagle_glb $PY -m lego_builder run 02_glb_gratuit_hunyuan2mv/beagle.glb --out $O/beagle --size-mm 400 --notice off
run 09_beagle_sha python3 lego-builder/tests/check_regression.py sculpture beagle $O/beagle/model/diorama.ldr beagle_V121
sha256sum $O/italia/model/diorama.ldr $O/paco/model/diorama.ldr $O/beagle/model/diorama.ldr > $L/artefact_sha256.txt
I=01_inputs_prepared; export PYTHONPATH=$B:/tmp/gradio_site
run 10_photos_to_3d timeout 1700 $PY -m lego_builder run --photos $I/paco_face_rgba.png $I/paco_dos_rgba.png $I/paco_profil_gauche_rgba.png $I/paco_profil_droit_rgba.png --out $O/paco_photos --size-mm 400 --notice off
[ -f $O/paco_photos/derived/paco_photos_couleur.glb ] && { run 11_photos_glb_compare $PY lego-builder/tests/compare_glb.py $O/paco_photos/derived/paco_photos_couleur.glb 02_glb_gratuit_hunyuan2mv/paco.glb; run 12_photos_sha python3 lego-builder/tests/check_regression.py sculpture paco_from_photos $O/paco_photos/model/diorama.ldr paco_V121_A_palette_V12; sha256sum $O/paco_photos/model/diorama.ldr >> $L/artefact_sha256.txt; }
echo ALLDONE > $L/ALLDONE
