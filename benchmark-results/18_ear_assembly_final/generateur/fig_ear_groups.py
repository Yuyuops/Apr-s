"""highlight fragile ear groups on the ear: usage fig_ear_groups.py <scene.json> <weak.json> <out_prefix>"""
import json, sys, copy, subprocess, os
import numpy as np
scene, weakf, out = sys.argv[1:4]
S = json.load(open(scene)); W = json.load(open(weakf))["groupes"]
cols = {"6": 4, "5": 14, "1": 2, "8": 1}      # group id -> LDraw colour (red, yellow, green, blue)
pal = [4, 14, 2, 1, 5, 25]
S2 = copy.deepcopy(S)
for k in ("2", "1", "5"):
    S2["colours"].setdefault(k, dict(name=k, hex={"2": "#237841", "1": "#0055BF", "5": "#C870A0"}[k], edge="#333333", alpha=1.0))
ear = [i for i, p in enumerate(S["parts"]) if False]
sub = {}
for l_i, l in enumerate(open(os.path.expanduser("~/bench/proto/v9/a2.ldr"))):
    pass
import re
cur = None; idx = 0; part_sub = {}
for l in open(os.path.expanduser("~/bench/proto/v9/a2.ldr")):
    t = l.split()
    if len(t) > 4 and t[0] == "0" and t[1] == "BRICKIFY" and t[2] == "SUBASSEMBLY": cur = t[4] if t[3] == "BEGIN" else None; continue
    if t and t[0] == "1" and len(t) >= 15: part_sub[idx] = cur; idx += 1
gi = 0; legend = []
for g in W:
    if not list(g["sous_ensemble"])[0].startswith("V7_oreille"): continue
    c = pal[gi % len(pal)]; gi += 1; legend.append((g["id"], c, len(g["parts_ids"]), g["masse_g"], g["force_N"]))
    for i in g["parts_ids"]: S2["parts"][i]["c"] = c
json.dump(S2, open(out + "_scene.json", "w"))
views = []
def box(ids):
    lo = np.array([1e9] * 3); hi = -lo
    for i in ids:
        p = S["parts"][i]; lo = np.minimum(lo, np.array(p["o"])); hi = np.maximum(hi, np.array(p["o"]))
    a = np.array([lo[0] * 0.4, -hi[1] * 0.4, -hi[2] * 0.4]); b = np.array([hi[0] * 0.4, -lo[1] * 0.4, -lo[2] * 0.4]); return a, b
weakids = {i for g in W for i in g["parts_ids"]}
for name in ("V7_oreille_basse", "V7_oreille_haute"):
    ids = [i for i, s in part_sub.items() if s == name]
    a, b = box(ids); ctr = (a + b) / 2; h = float(max((b - a) / 2)) + 45; fb = [(ctr - h).tolist(), (ctr + h).tolist()]
    for az, tag in ((37, "face"), (217, "dos")):
        views.append(dict(name="%s_%s" % (name.split("_")[-1], tag), az=az, el=12, w=900, h=900, frameBox=fb, edges=True,
                          items=[[i, "new" if i in weakids else "old"] for i in ids]))
json.dump(views, open(out + "_views.json", "w"))
os.makedirs(out + "_r", exist_ok=True)
env = dict(os.environ)
subprocess.run(["node", os.path.expanduser("~/bench/tools/render_steps.js"), out + "_scene.json", out + "_views.json", out + "_r"], check=True, env=env)
print(legend)
