#!/usr/bin/env bash
# Fetch the third-party dependencies of the engine into ./.deps (never committed to Git) at pinned versions, and verify them.
# usage: bash scripts/fetch_deps.sh        (from the portable engine folder ; needs git, curl, xz)
set -euo pipefail
cd "$(dirname "$0")/.."; ROOT=$(pwd); DEPS=${LEGO_DEPS:-$ROOT/.deps}; mkdir -p "$DEPS"
PY=${PYTHON:-$ROOT/.venv/bin/python}; [ -x "$PY" ] || PY=python3
lock() { "$PY" -c "import json,sys; d=json.load(open('$ROOT/locks/deps.lock.json')); print(eval('d'+sys.argv[1]))" "$1"; }
pin_git() {   # name url commit
  local dir="$DEPS/$1" url="$2" sha="$3"
  if [ ! -d "$dir/.git" ]; then git init -q "$dir"; git -C "$dir" remote add origin "$url"; fi
  if [ "$(git -C "$dir" rev-parse HEAD 2>/dev/null || true)" != "$sha" ]; then
    git -C "$dir" fetch -q --depth 1 origin "$sha"; git -C "$dir" checkout -q FETCH_HEAD
  fi
  [ "$(git -C "$dir" rev-parse HEAD)" = "$sha" ] || { echo "BLOCKED: $1 is not at $sha"; exit 3; }
  echo "ok  $1 @ $sha"
}
pin_git brickify "$(lock "['brickify']['url']")" "$(lock "['brickify']['commit']")"
pin_git ldraw-parts-library "$(lock "['ldraw']['url']")" "$(lock "['ldraw']['commit']")"
if [ ! -f "$DEPS/rb.db" ]; then
  echo "downloading Rebrickable database (rolling release latest-v8)"
  curl -fL --retry 3 -o "$DEPS/rb.db.xz" "$(lock "['rebrickable_db']['url']")"
  xz -dc "$DEPS/rb.db.xz" > "$DEPS/rb.db"
  "$PY" - "$DEPS/rb.db" <<'PYE'
import sqlite3, sys
c = sqlite3.connect(sys.argv[1])
c.execute('create table if not exists pcs_mat as select part_num,color_id,num_sets,min_year,max_year from part_color_stats')
c.execute('create index if not exists pcs_i on pcs_mat(part_num,color_id)'); c.commit()
PYE
fi
"$PY" scripts/check_rb_db.py "$DEPS/rb.db" refs/rb_db_drift.json
