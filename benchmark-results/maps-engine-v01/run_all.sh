#!/bin/bash
# regenerates every V0.1 output (island A, B, A without cut corners, A at 48x48 ; three-zone map A, B)
cd "$(dirname "$0")/engine"; R=../results; F=../fixtures
PY=${PY:-python}
$PY -m maps_engine.run_map full --input $F/ile_temoin.svg --out $R/ile_temoin/A --finish A
$PY -m maps_engine.run_map full --input $F/ile_temoin.svg --out $R/ile_temoin/B --finish B
$PY -m maps_engine.run_map full --input $F/ile_temoin.svg --out $R/ile_temoin/A_sans_coins_coupes --finish A --no-cut
$PY -m maps_engine.run_map full --input $F/ile_temoin.svg --out $R/ile_temoin/A_48x48 --finish A --n 48
$PY -m maps_engine.run_map full --input $F/test_3_zones.svg --out $R/test_3_zones/A --finish A
$PY -m maps_engine.run_map full --input $F/test_3_zones.svg --out $R/test_3_zones/B --finish B
