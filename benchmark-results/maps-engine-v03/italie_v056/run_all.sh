#!/bin/bash
cd "$(dirname "$0")"; . ./env.sh
MERGE=1 $PY colosseum_study.py work/n A,B,C         # 3 Colosseum architectures (then validate with check_render/fragility/verify_bom)
$PY alps_test.py work/o2 --VE 2.0 --detail 8 --ridge_gain 3.2 --valley_depth 7 --sharpen 1.2 --steep 1 --snow_m 1900 --rock_m 1000 --p75 0.45 --open 1
OFFSHORE_COLMAX=30 $PY placement_options.py results/B_colisee 20 26
$PY italia_full.py results/E_italie/it_v6 && $PY views_italia.py results/E_italie/it_v6 && ./run_pipeline.sh results/E_italie/it_v6
$PY notice_sectors.py results/E_italie/it_v6 && $PY make_notice.py results/E_italie/it_v6 results/E_italie/it_v6/notice_montage.pdf
