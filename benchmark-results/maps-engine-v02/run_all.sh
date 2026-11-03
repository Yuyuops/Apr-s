#!/bin/bash
# V0.2 : regenerates every V0.2 output. The V0 and V0.1 results are NOT touched.
cd "$(dirname "$0")/engine"; R=../results; F=../fixtures; PY=${PY:-python}
$PY -m maps_engine.run_map full --input $F/ecosse_carte.png --out $R/ecosse/A_32 --finish A
$PY -m maps_engine.run_map full --input $F/ecosse_carte.png --out $R/ecosse/H_32 --finish A --smooth mer,lac,riviere --mat 1
$PY -m maps_engine.run_map full --input $F/ecosse_carte_inscription.png --out $R/ecosse/A_32_inscription --finish A
$PY -m maps_engine.run_map full --input $F/ecosse_carte.png --out $R/ecosse/A_48 --finish A --n 48
$PY -m maps_engine.run_map full --input $F/../../maps-engine-v01/fixtures/ile_temoin.svg --out $R/ile_temoin/A_corrigee --finish A
$PY -m maps_engine.run_map full --input $F/../../maps-engine-v01/fixtures/ile_temoin.svg --out $R/ile_temoin/H_mat1 --finish A --smooth mer,lac,riviere --mat 1
$PY -m maps_engine.run_map full --input $F/../../maps-engine-v01/fixtures/test_3_zones.svg --out $R/test_3_zones/A_corrigee --finish A
$PY -m maps_engine.run_map full --input $F/../../maps-engine-v01/fixtures/test_3_zones.svg --out $R/test_3_zones/H_mat1 --finish A --smooth mer,lac,riviere --mat 1
