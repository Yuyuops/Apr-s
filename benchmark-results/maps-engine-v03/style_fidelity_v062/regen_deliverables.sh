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
# Hyrule visual demonstrator (NOT part of the geographic validation) : built from the committed land/sea/desert mask derived from a user-supplied render (see livraison_v09/HYRULE_SHOWCASE.md)
d="$OUT/hyrule"; mkdir -p "$d"; $PY build_style.py styles/premium_noyer_or_lagon_hyrule.json compositions/hyrule_80x80.json "$d" --flank vertical >/dev/null
$PY check_render.py "$d" --no-render >/dev/null; $PY verify_bom.py "$d" >/dev/null; $PY fragility.py "$d" >/dev/null; $PY notice_steps.py "$d" >/dev/null
$PY - "$d" <<'PY3'
import json, sys
d = sys.argv[1]; json.dump({"face": dict(box=[0, 0, 88, 88], h=28, az=0, el=89, w=1100, hpx=1100, zoom=0.92), "trois_quarts": dict(box=[0, 0, 88, 88], h=28, az=20, el=38, w=1300, hpx=950, zoom=0.8), "zoom": dict(box=[30, 40, 70, 88], h=28, az=25, el=34, w=1200, hpx=900, zoom=0.6)}, open(d + "/views.json", "w"))
PY3
[ $RENDER = 1 ] && $PY render_views.py "$d" "$d/views.json" >/dev/null
[ $PDF = 1 ] && $PY make_step_pdf.py "$d" "$d/notice_pas_a_pas.pdf" >/dev/null
$PY check_delivery.py "$d"
# Hyrule BIOMES + RELIEF mode (V1.0) : class raster produced by biomes_from_render.py from the user-supplied picture (committed TIFF), style premium_biomes_hyrule
d="$OUT/hyrule_biomes"; mkdir -p "$d"; $PY build_style.py styles/premium_biomes_hyrule.json compositions/hyrule_biomes_80x80.json "$d" --flank vertical >/dev/null
$PY check_render.py "$d" --no-render >/dev/null; $PY verify_bom.py "$d" >/dev/null; $PY fragility.py "$d" >/dev/null; $PY notice_steps.py "$d" >/dev/null
$PY - "$d" <<'PY4'
import json, sys
d = sys.argv[1]; json.dump({"face": dict(box=[0, 0, 88, 88], h=26, az=0, el=89, w=1100, hpx=1100, zoom=0.92), "trois_quarts": dict(box=[0, 0, 88, 88], h=26, az=20, el=38, w=1300, hpx=950, zoom=0.8), "zoom": dict(box=[30, 40, 70, 88], h=26, az=25, el=34, w=1200, hpx=900, zoom=0.6)}, open(d + "/views.json", "w"))
PY4
[ $RENDER = 1 ] && $PY render_views.py "$d" "$d/views.json" >/dev/null
[ $PDF = 1 ] && $PY make_step_pdf.py "$d" "$d/notice_pas_a_pas.pdf" >/dev/null
$PY check_delivery.py "$d"
# reduced prototypes : stand-alone engine windows (same style, same studs per degree as the 64x96 cards, own frame) : A = coast + 5 strata levels + islets, B = frame + medallions + title
$PY build_style.py styles/premium_noyer_or_lagon_c2i.json compositions/proto_a_eolie_36x36.json "$OUT/protoA_littoral" --flank vertical >/dev/null; $PY build_style.py styles/premium_noyer_or_lagon_c2i.json compositions/proto_b_titre_24x48.json "$OUT/protoB_cadre_titre" --flank vertical >/dev/null
for p in protoA_littoral protoB_cadre_titre; do d="$OUT/$p"; $PY check_render.py "$d" --no-render >/dev/null; $PY verify_bom.py "$d" >/dev/null; $PY fragility.py "$d" >/dev/null; $PY notice_steps.py "$d" >/dev/null; $PY check_delivery.py "$d"
  $PY - "$d" <<'PY2'
import json, sys
d = sys.argv[1]; m = json.load(open(d + "/metrics.json")); R, C = m["grid_studs"]; H = m["height_plates"] + 4
json.dump({"face": dict(box=[0, 0, R, C], h=H, az=0, el=89, w=1100, hpx=int(1100 * R / C) + 40, zoom=0.92), "trois_quarts": dict(box=[0, 0, R, C], h=H, az=20, el=38, w=1300, hpx=950, zoom=0.8), "zoom": dict(box=[0, 0, min(R, 30), min(C, 40)], h=H, az=25, el=34, w=1200, hpx=900, zoom=0.6)}, open(d + "/views.json", "w"))
PY2
  [ $RENDER = 1 ] && $PY render_views.py "$d" "$d/views.json" >/dev/null
  [ $PDF = 1 ] && $PY make_visual_notice.py "$d" "$d/notice_illustree.pdf" --jobs 4 >/dev/null; done
$PY - "$OUT" <<'PY'
import hashlib, json, sys, os
o = sys.argv[1]; m = {}
for k in ("italia", "ecosse", "japon", "royaume_uni", "hyrule", "hyrule_biomes", "protoA_littoral", "protoB_cadre_titre"):
    d = json.load(open(f"{o}/{k}/metrics.json")); m[k] = dict(pieces=d["pieces"], references=d["references"], ldr_sha256=hashlib.sha256(open(f"{o}/{k}/diorama.ldr", "rb").read()).hexdigest())
json.dump(m, open(f"{o}/deliverables_manifest.json", "w"), indent=1); print(json.dumps(m))
PY
