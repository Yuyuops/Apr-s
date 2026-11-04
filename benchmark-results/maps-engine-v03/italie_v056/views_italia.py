#!/usr/bin/env python3
"""writes views.json for a full Italia model folder from placements (scene coordinates = field + frame offset 2)"""
import json, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); out = sys.argv[1]; pl = json.load(open(os.path.join(HERE, "italia/output/placements.json"))); opt = json.load(open(os.path.join(HERE, "results/B_colisee/placement_options.json")))["offshore_medallion"]; f = 2
mon = {m["id"]: m for m in pl["monuments"]}; z = pl["zones"]; v = {}
v["full_face"] = dict(box=[0, 0, 132, 132], h=50, az=0, el=89, w=1600, hpx=1600, zoom=0.92)
v["full_trois_quarts"] = dict(box=[0, 0, 132, 132], h=50, az=28, el=38, w=1700, hpx=1200, zoom=0.78)
v["full_nord_ouest"] = dict(box=[0, 0, 132, 132], h=50, az=200, el=36, w=1700, hpx=1200, zoom=0.78)
v["alpes_trois_quarts"] = dict(box=[f + 6, f + 18, f + 44, f + 70], h=60, az=15, el=26, w=1500, hpx=1000, zoom=0.55)
v["alpes_face"] = dict(box=[f + 6, f + 18, f + 44, f + 70], h=60, az=0, el=89, w=1400, hpx=1100, zoom=0.78)
r, c = opt["row"], opt["col"]; v["colisee_trois_quarts"] = dict(box=[f + r - 1, f + c - 1, f + r + 21, f + c + 27], h=30, az=28, el=30, w=1300, hpx=950, zoom=0.5)
p = mon["pisa_tower"]; v["pise"] = dict(box=[f + p["row"] - 2, f + p["col"] - 3, f + p["row"] + 8, f + p["col"] + 9], h=34, az=25, el=22, w=1100, hpx=900, zoom=0.5)
vs = mon["vesuvio"]; v["vesuve"] = dict(box=[f + vs["row"] - 4, f + vs["col"] - 5, f + vs["row"] + 14, f + vs["col"] + 15], h=34, az=25, el=28, w=1200, hpx=900, zoom=0.55)
t = z["title"]; v["titre"] = dict(box=[f + t["row"] - 3, f + t["col"] - 3, f + t["row"] + 11, f + t["col"] + 38], h=8, az=0, el=65, w=1500, hpx=700, zoom=0.7)
k = z["compass"]; v["rose_des_vents"] = dict(box=[f + k["row"] - 3, f + k["col"] - 3, f + k["row"] + 18, f + k["col"] + 18], h=8, az=0, el=70, w=900, hpx=900, zoom=0.7)
v["cadre_coin"] = dict(box=[0, 0, 22, 22], h=20, az=35, el=30, w=1000, hpx=800, zoom=0.6)
v["littoral_tyrrhenien"] = dict(box=[f + 30, f + 36, f + 70, f + 72], h=40, az=40, el=30, w=1500, hpx=1000, zoom=0.6)
json.dump(v, open(os.path.join(out, "views.json"), "w"), indent=1)
