#!/bin/bash
cd "$(dirname "$0")"; . ./env.sh; D=$1
$PY check_render.py $D --no-render > $D/check.log 2>&1; $PY verify_bom.py $D > $D/bom.log 2>&1; $PY fragility.py $D > $D/frag.log 2>&1; $PY render_views.py $D $D/views.json > $D/render.log 2>&1; echo done > $D/ALLDONE
