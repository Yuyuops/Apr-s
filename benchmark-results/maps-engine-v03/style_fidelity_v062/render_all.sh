#!/bin/bash
cd "$(dirname "$0")"; . ./env.sh
for d in "$@"; do $PY render_views.py work/$d work/$d/views.json >/dev/null 2>&1; echo $d >> work/RENDERED; done; echo ok > work/ZONESDONE
