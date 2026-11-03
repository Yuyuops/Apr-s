"""Renders with the real LDraw part geometry : engine-1 ldr_expand.py (read-only) + a copy of the engine-1 three.js renderer with neutral lighting. Colours are the REAL LEGO values (Rebrickable), not the LDraw library table."""
import json, os, subprocess, sys
from .common import ROOT, E1, rb_colours
from _paths import LDRAW
NODE_MODULES = os.environ.get("LEGO_NODE_MODULES") or os.path.join(ROOT, "..", "20_portable_engine", "node_modules")

def real_colours(scene_json):
    s = json.load(open(scene_json)); rb = rb_colours()
    for k, v in s["colours"].items():
        if int(k) in rb: v["hex"] = "#%02X%02X%02X" % rb[int(k)]["rgb"]
    json.dump(s, open(scene_json, "w"))

def render_all(ldr, outdir, N=32, height_plates=8, zooms=None, w=1400, size_px=None):
    """face (top view), profil, trois-quarts, 3 rotations, close-ups. N = studs side of the whole board (frame included) ; zooms {name: (col0,row0,col1,row1)} in studs of the global grid"""
    os.makedirs(outdir, exist_ok=True); tmp = os.path.join(outdir, "_scene"); os.makedirs(tmp, exist_ok=True)
    subprocess.run([sys.executable, os.path.join(E1, "ldr_expand.py"), "--ldr", ldr, "--ldraw", LDRAW, "--json", tmp + "/s.json", "--glb", tmp + "/g.glb"], check=True, capture_output=True)
    real_colours(tmp + "/s.json")
    s = N * 8.0; H = height_plates * 3.2 + 12; fb = [[-8, -2, -8], [s + 8, H, s + 8]]; views = [dict(name="face", az=0, el=89, w=w, h=w, frameBox=fb, edges=True)]
    views.append(dict(name="profil", az=90, el=4, w=2600, h=1000, frameBox=[[-40, -2, -8], [s + 40, 40, s + 8]], edges=True))
    for nm, az, el in (("trois_quarts", 30, 38), ("rotation_090", 120, 38), ("rotation_180", 210, 38), ("rotation_270", 300, 38)):
        views.append(dict(name=nm, az=az, el=el, w=w, h=int(w * 0.75), frameBox=fb, edges=True))
    for nm, (c0, r0, c1, r1) in (zooms or {}).items():
        x0, x1 = c0 * 8.0, c1 * 8.0; z0, z1 = r0 * 8.0, r1 * 8.0; hz = max(x1 - x0, z1 - z0) / 2 + 8; cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
        box = [[cx - hz, -2, cz - hz], [cx + hz, H, cz + hz]]
        views.append(dict(name="zoom_" + nm, az=0, el=89, w=1000, h=1000, frameBox=box, edges=True)); views.append(dict(name="zoom_%s_relief" % nm, az=25, el=32, w=1000, h=800, frameBox=box, edges=True))
    json.dump(views, open(tmp + "/views.json", "w")); env = dict(os.environ, LEGO_NODE_MODULES=NODE_MODULES, NODE_PATH=NODE_MODULES)
    subprocess.run(["node", os.path.join(ROOT, "engine", "render_map.js"), tmp + "/s.json", tmp + "/views.json", outdir], check=True, capture_output=True, env=env)
    from PIL import Image, ImageChops
    im = Image.open(os.path.join(outdir, "profil.png")).convert("RGB"); bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if bb: im.crop((max(0, bb[0] - 30), max(0, bb[1] - 30), min(im.width, bb[2] + 30), min(im.height, bb[3] + 30))).save(os.path.join(outdir, "profil.png"))
    return [v["name"] for v in views], tmp + "/g.glb"
