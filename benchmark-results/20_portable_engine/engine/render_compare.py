"""V10 generic comparison renders (no subject coordinates): the views are derived from the bounding box of the model.
usage: render_compare.py <model.ldr> <ref_frame.glb> <outdir> [--zoom name:x0,y0,z0,x1,y1,z1:az:el ...]"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import sys, os, json, subprocess
import numpy as np
sys.path.insert(0, ENGINE_DIR)
import notice_plan as N
ldr, refglb, out = [os.path.abspath(x) for x in sys.argv[1:4]]; os.makedirs(out, exist_ok=True)
P = N.parse(ldr); lo = np.min([p["lo"] for p in P], 0); hi = np.max([p["hi"] for p in P], 0)
a = np.array([lo[0] * 0.4, -hi[1] * 0.4, -hi[2] * 0.4]); b = np.array([hi[0] * 0.4, -lo[1] * 0.4, -lo[2] * 0.4])
c = (a + b) / 2; h = float(max(b - a)) / 2 * 1.04; fb = [(c - h).tolist(), (c + h).tolist()]; fb[0][1] = max(fb[0][1], 0 - 5) if False else fb[0][1]
V = [("1_face", 180, 8), ("2_dos", 0, 8), ("3_profil_gauche", 270, 5), ("4_profil_droit", 90, 5), ("5_trois_quarts", 225, 18), ("6_dessus", 200, 80)]
views = [dict(name=n, az=az, el=el, w=900, h=900, frameBox=fb, edges=True) for n, az, el in V]
for z in sys.argv[4:]:
    if z == "--zoom": continue
    n, bx, az, el = z.split(":"); x0, y0, z0, x1, y1, z1 = map(float, bx.split(","))
    views.append(dict(name=n, az=float(az), el=float(el), w=900, h=900, frameBox=[[x0, y0, z0], [x1, y1, z1]], edges=True))
json.dump(views, open(os.path.join(out, "views.json"), "w"))
T = ENGINE_DIR; LD = LDRAW
subprocess.run([sys.executable, T + "/ldr_expand.py", "--ldr", ldr, "--ldraw", LD, "--json", out + "/s.json", "--glb", out + "/g.glb"], check=True, capture_output=True)
subprocess.run(["node", T + "/render_ldr.js", out + "/s.json", out + "/views.json", out + "/r_lego"], check=True, cwd=T, capture_output=True)
subprocess.run(["node", T + "/render_ldr.js", refglb, out + "/views.json", out + "/r_ref"], check=True, cwd=T, capture_output=True, env=dict(os.environ, GLB_NATIVE="1"))
print("bbox mm", a.round(0).tolist(), b.round(0).tolist(), "frame", np.round(fb, 0).tolist())
