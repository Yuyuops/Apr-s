#!/usr/bin/env python3
"""Product V1 : high-resolution renders of the shipped LDraw model (real LDraw part geometry, three.js, same generic bounding-box framing as engine render_compare.py), a turntable GIF preview and a GLB export (ldr_expand).
usage : product_renders_v1.py MODEL.ldr OUTDIR [--px 2400]   (env LEGO_ENGINE_HOME LEGO_DEPS LEGO_NODE_MODULES NODE_PATH)"""
import os, sys, json, subprocess
sys.path.insert(0, os.path.join(os.environ["LEGO_ENGINE_HOME"], "engine"))
from _paths import ENGINE_DIR, LDRAW
import numpy as np
from PIL import Image
import notice_plan as N
ldr, out = [os.path.abspath(x) for x in sys.argv[1:3]]; px = int(sys.argv[sys.argv.index("--px") + 1]) if "--px" in sys.argv else 2400; os.makedirs(out, exist_ok=True)
P = N.parse(ldr); lo = np.min([p["lo"] for p in P], 0); hi = np.max([p["hi"] for p in P], 0); a = np.array([lo[0] * 0.4, -hi[1] * 0.4, -hi[2] * 0.4]); b = np.array([hi[0] * 0.4, -lo[1] * 0.4, -lo[2] * 0.4])
c = (a + b) / 2; h = float(max(b - a)) / 2 * 1.04; fb = [(c - h).tolist(), (c + h).tolist()]
V = [("face", 180, 8), ("dos", 0, 8), ("profil_gauche", 270, 5), ("profil_droit", 90, 5), ("trois_quarts", 225, 18), ("trois_quarts_arriere", 315, 18), ("dessus", 200, 80)]
views = [dict(name="Beagle_V1_" + n, az=az, el=el, w=px, h=px, frameBox=fb, edges=True) for n, az, el in V] + [dict(name="turn_%02d" % i, az=i * 30, el=14, w=700, h=700, frameBox=fb, edges=True) for i in range(12)]
tmp = os.path.join(out, "_tmp"); os.makedirs(tmp, exist_ok=True); json.dump(views, open(tmp + "/views.json", "w"))
subprocess.run([sys.executable, ENGINE_DIR + "/ldr_expand.py", "--ldr", ldr, "--ldraw", LDRAW, "--json", tmp + "/s.json", "--glb", out + "/Beagle_V1.glb"], check=True, capture_output=True)
subprocess.run(["node", ENGINE_DIR + "/render_ldr.js", tmp + "/s.json", tmp + "/views.json", tmp + "/r"], check=True, cwd=ENGINE_DIR, capture_output=True)
for n, _, _ in V: os.replace("%s/r/Beagle_V1_%s.png" % (tmp, n), "%s/Beagle_V1_%s.png" % (out, n))
fr = [Image.open("%s/r/turn_%02d.png" % (tmp, i)).convert("P", palette=Image.ADAPTIVE, colors=128) for i in range(12)]
fr[0].save(out + "/Beagle_V1_turntable.gif", save_all=True, append_images=fr[1:], duration=160, loop=0, optimize=True)
import shutil; shutil.rmtree(tmp); print(sorted(os.listdir(out)), "bbox mm", a.round(0).tolist(), b.round(0).tolist())
