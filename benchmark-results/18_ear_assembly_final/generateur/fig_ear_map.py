"""2D maps of an ear in its own (axis-aligned) frame : layers outer tile / outer plate / core / inner plate, groups highlighted.
usage: fig_ear_map.py <model.ldr> <sub> <weak.json|-> <out.png>"""
import sys, json
sys.path.insert(0, "/root/bench/proto/v9"); sys.path.insert(0, "/root/bench/tools")
import numpy as np, notice_plan as N, conn
from PIL import Image, ImageDraw, ImageFont
model, sub, weakf, out = sys.argv[1:5]
P = N.parse(model)
R = np.array([[0.6, 0, -0.8], [0, 1, 0], [0.8, 0, 0.6]])
ids = [p["i"] for p in P if p["sub"] == sub]
def loc(i):
    p = P[i]; Ml = R.T @ p["M"]; ol = R.T @ p["o"]; st, rc, lo, hi = conn.world(p["num"], Ml, ol); return lo, hi
grp = {}
if weakf != "-":
    for g in json.load(open(weakf))["groupes"]:
        for i in g["parts_ids"]: grp[i] = g["id"]
colors = {6: "#d62728", 5: "#ffbf00", 1: "#2ca02c", 8: "#1f77b4"}
zl = [(-90, -76, "face externe (tuile)"), (-76, -68, "face externe (plaque)"), (-68, -48, "noyau"), (-48, -40, "face interne (plaque)")]
L = [loc(i) for i in ids]; x0 = min(l[0][0] for l in L) - 10; x1 = max(l[1][0] for l in L) + 10; y0 = min(l[0][1] for l in L) - 10; y1 = max(l[1][1] for l in L) + 10
sc = 2.2; W = int((x1 - x0) * sc); H = int((y1 - y0) * sc)
f = ImageFont.load_default()
img = Image.new("RGB", (W * 2 + 30, H * 2 + 60), "white"); d = ImageDraw.Draw(img)
for k, (z0, z1, name) in enumerate(zl):
    ox = (k % 2) * (W + 20) + 5; oy = (k // 2) * (H + 40) + 30
    d.text((ox, oy - 20), name, fill="black", font=f)
    for i, (lo, hi) in zip(ids, L):
        if hi[2] <= z0 + 0.5 or lo[2] >= z1 - 0.5: continue
        g = grp.get(i)
        a = ((lo[0] - x0) * sc + ox, (lo[1] - y0) * sc + oy); b = ((hi[0] - x0) * sc + ox, (hi[1] - y0) * sc + oy)
        d.rectangle([a, b], fill=colors.get(g, "#e4e4e4"), outline="black")
        d.text((a[0] + 2, a[1] + 1), "%s %d" % (P[i]["num"], i), fill="black", font=f)
img.save(out)
