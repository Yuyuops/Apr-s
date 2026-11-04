#!/usr/bin/env python3
"""Validate + render every variant folder of results/B_colisee with identical cameras. usage: render_variants.py ROOT"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); root = sys.argv[1]; import glob
res = {}
for f in glob.glob(os.path.join(root, "variants_metrics*.json")): res.update(json.load(open(f)))
for v in (sys.argv[2].split(",") if len(sys.argv) > 2 else ("full", "simplified", "icon", "no_monument")):
    d = os.path.join(root, v); spec = {"region_trois_quarts": {"box": [0, 0, 64, 64], "h": 40, "az": 30, "el": 38, "w": 1400, "hpx": 1050, "zoom": 0.85}, "region_face": {"box": [0, 0, 64, 64], "h": 40, "az": 0, "el": 89, "w": 1200, "hpx": 1200, "zoom": 0.9}}
    if v != "no_monument":
        r0, c0 = res[v]["placed_row"] - 32, res[v]["placed_col"] - 32; fr, fc = res[v]["footprint"]; spec["colosseum_trois_quarts"] = {"box": [r0 - 1, c0 - 1, r0 + fr + 1, c0 + fc + 1], "h": 24, "az": 30, "el": 32, "zoom": 0.62, "w": 1200, "hpx": 900}; spec["colosseum_face"] = {"box": [r0 - 1, c0 - 1, r0 + fr + 1, c0 + fc + 1], "h": 24, "az": 0, "el": 89, "zoom": 0.7, "w": 1000, "hpx": 1000}
    json.dump(spec, open(os.path.join(d, "views.json"), "w"))
    for cmd in (["check_render.py", d], ["fragility.py", d], ["verify_bom.py", d], ["render_views.py", d, os.path.join(d, "views.json")]):
        r = subprocess.run([sys.executable, os.path.join(HERE, cmd[0])] + cmd[1:], capture_output=True, text=True); print(v, cmd[0], r.returncode, r.stdout[-200:].replace("\n", " "))
