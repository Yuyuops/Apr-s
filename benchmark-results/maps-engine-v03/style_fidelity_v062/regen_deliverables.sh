#!/bin/bash
# Regenerates every V0.9 deliverable from source (nothing heavy is versioned in Git).
# usage : regen_deliverables.sh OUTROOT [--render] [--pdf]     (needs the engine-1 portable install : LEGO_ENGINE_HOME, see env.sh)
set -euo pipefail
cd "$(dirname "$0")"; . ./env.sh; OUT=${1:?OUTROOT}; shift || true; RENDER=0; PDF=0
for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; [ "$a" = "--pdf" ] && PDF=1; done
mkdir -p "$OUT"; declare -A STYLE=([italia]=premium_noyer_or_lagon_c2i [ecosse]=premium_noyer_or_lagon_ecosse [japon]=premium_noyer_or_lagon_japon [royaume_uni]=premium_noyer_or_lagon_royaume_uni)
for k in italia ecosse japon royaume_uni; do d="$OUT/$k"; mkdir -p "$d"
  $PY build_style.py styles/${STYLE[$k]}.json compositions/${k}_portrait_64x96.json "$d" --flank vertical >/dev/null
  $PY check_render.py "$d" --no-render >/dev/null; $PY verify_bom.py "$d" >/dev/null; $PY fragility.py "$d" >/dev/null; $PY notice_steps.py "$d" >/dev/null
  cp views_cards.json "$d/views.json"; [ $RENDER = 1 ] && $PY render_views.py "$d" "$d/views.json" >/dev/null
  [ $PDF = 1 ] && $PY make_step_pdf.py "$d" "$d/notice_pas_a_pas.pdf" >/dev/null
  $PY check_delivery.py "$d"
done
# reduced prototypes extracted from the final Italy model (A : coast + relief, B : frame + medallion + title)
$PY extract_box.py "$OUT/italia" "$OUT/protoA_littoral" 68 84 40 56 "Prototype A littoral+relief" >/dev/null; $PY extract_box.py "$OUT/italia" "$OUT/protoB_cadre_titre" 0 14 0 40 "Prototype B cadre+medaillon+titre" >/dev/null
for p in protoA_littoral protoB_cadre_titre; do d="$OUT/$p"; $PY check_render.py "$d" --no-render >/dev/null; $PY verify_bom.py "$d" >/dev/null; $PY fragility.py "$d" >/dev/null; $PY notice_steps.py "$d" >/dev/null; $PY check_delivery.py "$d"
  [ $PDF = 1 ] && $PY make_visual_notice.py "$d" "$d/notice_illustree.pdf" --jobs 4 >/dev/null; done
$PY - "$OUT" <<'PY'
import hashlib, json, sys, os
o = sys.argv[1]; m = {}
for k in ("italia", "ecosse", "japon", "royaume_uni", "protoA_littoral", "protoB_cadre_titre"):
    d = json.load(open(f"{o}/{k}/metrics.json")); m[k] = dict(pieces=d["pieces"], references=d["references"], ldr_sha256=hashlib.sha256(open(f"{o}/{k}/diorama.ldr", "rb").read()).hexdigest())
json.dump(m, open(f"{o}/deliverables_manifest.json", "w"), indent=1); print(json.dumps(m))
PY
