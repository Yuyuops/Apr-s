#!/usr/bin/env python3
"""views for a local test window : face (top) + oblique + close-up. usage: views_local.py DIR"""
import json, sys
D = sys.argv[1]; m = json.load(open(D + "/metrics.json")); R, C = m["grid_studs"]; F = m["frame_studs"]; H = m["height_plates"] + 4; Rs, Cs = R + 2 * F, C + 2 * F
json.dump({"face": dict(box=[0, 0, Rs, Cs], h=H, az=0, el=89, w=1000, hpx=1000, zoom=0.92), "oblique": dict(box=[0, 0, Rs, Cs], h=H, az=20, el=38, w=1200, hpx=950, zoom=0.78), "zoom": dict(box=[int(Rs * .25), int(Cs * .2), int(Rs * .7), int(Cs * .7)], h=H, az=25, el=34, w=1200, hpx=900, zoom=0.6)}, open(D + "/views.json", "w"))
