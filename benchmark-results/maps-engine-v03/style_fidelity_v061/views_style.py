#!/usr/bin/env python3
"""views.json for a style prototype folder (scene coordinates incl. frame). usage: views_style.py OUTDIR"""
import json, os, sys
D = sys.argv[1]; m = json.load(open(D + "/metrics.json")); R, C = m["grid_studs"]; F = m["frame_studs"]; H = m["height_plates"] + 6; Rs, Cs = R + 2 * F, C + 2 * F
v = {"face": dict(box=[0, 0, Rs, Cs], h=H, az=0, el=89, w=1100, hpx=1500, zoom=0.93),
     "trois_quarts": dict(box=[0, 0, Rs, Cs], h=H, az=22, el=40, w=1400, hpx=1300, zoom=0.80),
     "cote_nord_adriatique": dict(box=[int(Rs * .08), int(Cs * .38), int(Rs * .42), Cs], h=H, az=-25, el=34, w=1300, hpx=900, zoom=0.62),
     "strates_golfe": dict(box=[int(Rs * .55), int(Cs * .18), int(Rs * .85), int(Cs * .62)], h=H, az=15, el=30, w=1300, hpx=900, zoom=0.62),
     "cote_sicile": dict(box=[int(Rs * .70), int(Cs * .30), int(Rs * .95), int(Cs * .85)], h=H, az=30, el=36, w=1300, hpx=900, zoom=0.62),
     "cadre_coin": dict(box=[0, 0, 24, 24], h=H, az=35, el=30, w=1100, hpx=850, zoom=0.62),
     "cadre_titre": dict(box=[Rs - 22, 0, Rs, int(Cs * .7)], h=H, az=10, el=32, w=1300, hpx=800, zoom=0.62),
     "laterale": dict(box=[0, 0, Rs, Cs], h=H, az=92, el=6, w=1600, hpx=700, zoom=0.85)}
json.dump(v, open(D + "/views.json", "w"), indent=1)
