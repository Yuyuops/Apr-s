#!/bin/bash
cd "$(dirname "$0")"; . ./env.sh
MERGE=1 $PY colosseum_study57.py work/c57 A,A5,A3,A5b          # Colosseum variants (validate with check_render/fragility, render with render_views)
$PY module_pisa_vesuvio.py work/mod
OFFSHORE_COLMAX=30 $PY placement_options.py results/B_colisee 20 26
BASEFIT=2 $PY italia_full.py results/E_italie/it57_b2 && $PY views_italia.py results/E_italie/it57_b2
D=results/E_italie/it57_b2; $PY check_render.py $D --no-render; $PY verify_bom.py $D; $PY fragility.py $D; $PY render_views.py $D $D/views.json
$PY notice_steps.py $D && $PY make_step_pdf.py $D $D/notice_pas_a_pas.pdf && (cd $D && NODE_PATH=$LEGO_NODE_MODULES node ../../../viewer_check.js step_viewer.html viewer_check)
$PY extract_test_sector.py $D results/essai_secteur_S11
