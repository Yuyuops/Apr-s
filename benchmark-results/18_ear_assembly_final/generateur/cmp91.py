"""identical-framing renders of V9 and V9.1 (full figure + ear close-ups) and difference boards. usage: cmp91.py <outdir>"""
import sys, os, json, subprocess
import numpy as np
sys.path.insert(0, "/root/bench/proto/v9")
from PIL import Image, ImageChops, ImageDraw, ImageFont
import notice_plan as N
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
models = {"V9": os.path.expanduser("~/bench/proto/v9/a2.ldr"), "V91": os.path.expanduser("~/bench/proto/v91/s2.ldr")}
LD = os.path.expanduser("~/bench/ldraw-parts-library/complete/ldraw")
base_views = json.load(open(os.path.expanduser("~/bench/proto/v9/cmp/views_w9.json")))
P9 = N.parse(models["V9"])
def box_of(ids, P):
    lo = np.min([P[i]["lo"] for i in ids], 0); hi = np.max([P[i]["hi"] for i in ids], 0)
    a = np.array([lo[0] * 0.4, -hi[1] * 0.4, -hi[2] * 0.4]); b = np.array([hi[0] * 0.4, -lo[1] * 0.4, -lo[2] * 0.4]); return a, b
ear_views = []
for sub, nm in (("V7_oreille_basse", "oreille_basse"), ("V7_oreille_haute", "oreille_haute")):
    ids = [p["i"] for p in P9 if p["sub"] == sub]; a, b = box_of(ids, P9); ctr = (a + b) / 2; h = float(max((b - a) / 2)) + 30
    for az, tag in ((37, "face"), (217, "dos")): ear_views.append(dict(name="%s_%s" % (nm, tag), az=az, el=12, w=900, h=900, frameBox=[(ctr - h).tolist(), (ctr + h).tolist()], edges=True))
env = dict(os.environ)
for tag, path in models.items():
    sj = os.path.join(out, "s_%s.json" % tag)
    subprocess.run([sys.executable, os.path.expanduser("~/bench/tools/ldr_expand.py"), "--ldr", path, "--ldraw", LD, "--json", sj, "--glb", os.path.join(out, "g_%s.glb" % tag)], check=True, capture_output=True)
    n = len(json.load(open(sj))["parts"])
    views = []
    for v in base_views + ear_views:
        vv = {k: x for k, x in v.items() if k != "items"}; vv["items"] = [[i, "new"] for i in range(n)]; views.append(vv)
    json.dump(views, open(os.path.join(out, "views_%s.json" % tag), "w"))
    subprocess.run(["node", os.path.expanduser("~/bench/tools/render_steps.js"), sj, os.path.join(out, "views_%s.json" % tag), os.path.join(out, "r_%s" % tag)], check=True, env=env, capture_output=True)
names = [v["name"] for v in base_views + ear_views]
f = ImageFont.load_default(); res = {}
for nm in names:
    A = Image.open(os.path.join(out, "r_V9", nm + ".png")).convert("RGB"); B = Image.open(os.path.join(out, "r_V91", nm + ".png")).convert("RGB")
    d = np.abs(np.asarray(A, int) - np.asarray(B, int)).sum(2); frac = float((d > 30).mean())
    diff = Image.fromarray(np.clip(255 - d * 3, 0, 255).astype(np.uint8)).convert("RGB")
    W, H = A.size; board = Image.new("RGB", (W * 3, H + 30), "white"); dr = ImageDraw.Draw(board)
    for k, (im, t) in enumerate(((A, "V9"), (B, "V9.1"), (diff, "difference (x3), %.3f %% des pixels" % (frac * 100)))): board.paste(im, (k * W, 30)); dr.text((k * W + 10, 8), t, fill="black", font=f)
    board.save(os.path.join(out, "comparaison_%s.png" % nm)); res[nm] = round(frac * 100, 4)
json.dump(res, open(os.path.join(out, "difference_pixels_pct.json"), "w"), indent=1)
print(res)
