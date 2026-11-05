#!/usr/bin/env python3
"""V0.5.6 chantier 1 : three Colosseum facades alone on sea (20x26, n=2.6). usage: colosseum_study.py OUTROOT"""
import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import Scene
import region, colosseum_v2
root = sys.argv[1]; rows, cols = 20, 26; R, C = 32, 40; SNAP = int(sys.argv[3]) if len(sys.argv) > 3 else 0; TAG = sys.argv[4] if len(sys.argv) > 4 else ""
for style in (sys.argv[2].split(",") if len(sys.argv) > 2 else ["A", "B", "C"]):
    S = Scene(R, C); S.do_merge = bool(os.environ.get("MERGE")); region.base(S, R, C, random.Random(1)); a, b, pe = region.colosseum_geometry(rows, cols)
    try: info = colosseum_v2.build(S, R // 2, C // 2, a, b, pe, 2.6 if not SNAP else 2.4, style, snap=SNAP); m = S.write(os.path.join(root, "style_" + style + TAG), "colosseum style " + style, dict(colosseum=info)); print(style, m["pieces"], info)
    except ValueError as e: print(style, "FAILED", str(e)[:100])
