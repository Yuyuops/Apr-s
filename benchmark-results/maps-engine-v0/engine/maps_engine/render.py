"""Renders with the real LDraw geometry : engine-1 ldr_expand.py (read-only) + a map copy of the engine-1 three.js renderer (neutral tone mapping, truer colours)."""
import json, os, subprocess, sys
from .common import ROOT, E1
import numpy as np
_deps = os.environ.get("LEGO_DEPS")
from _paths import LDRAW
NODE_MODULES = os.environ.get("LEGO_NODE_MODULES") or os.path.join(ROOT, "..", "20_portable_engine", "node_modules")

def board_box(n=32, plates=7):
    s = n * 8.0; return [[-8, -2, -8], [s + 8, plates * 3.2 + 14, s + 8]]

def render_all(ldr, outdir, n=32, layers=7, zooms=None, w=1400, tag=""):
    """face (top view), profil (side), trois-quarts and rotations ; zooms = {name: (col0, row0, col1, row1)} in studs for close-ups"""
    os.makedirs(outdir, exist_ok=True); tmp = os.path.join(outdir, "_scene"); os.makedirs(tmp, exist_ok=True)
    subprocess.run([sys.executable, os.path.join(E1, "ldr_expand.py"), "--ldr", ldr, "--ldraw", LDRAW, "--json", tmp + "/s.json", "--glb", tmp + "/g.glb"], check=True, capture_output=True)
    s = n * 8.0; fb = board_box(n, layers); views = []
    views.append(dict(name="face", az=0, el=89, w=w, h=w, frameBox=fb, edges=True))
    views.append(dict(name="profil", az=90, el=4, w=2600, h=1000, frameBox=[[-40, -2, -8], [s + 40, 40, s + 8]], edges=True))
    for nm, az, el in (("trois_quarts", 30, 38), ("rotation_090", 120, 38), ("rotation_180", 210, 38), ("rotation_270", 300, 38)):
        views.append(dict(name=nm, az=az, el=el, w=w, h=int(w * 0.75), frameBox=fb, edges=True))
    for nm, (c0, r0, c1, r1) in (zooms or {}).items():
        x0, x1 = c0 * 8.0, c1 * 8.0; z0, z1 = r0 * 8.0, r1 * 8.0; hz = max(x1 - x0, z1 - z0) / 2 + 8; cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
        views.append(dict(name="zoom_" + nm, az=0, el=89, w=1000, h=1000, frameBox=[[cx - hz, -2, cz - hz], [cx + hz, layers * 3.2 + 14, cz + hz]], edges=True))
        views.append(dict(name="zoom_%s_relief" % nm, az=25, el=32, w=1000, h=800, frameBox=[[cx - hz, -2, cz - hz], [cx + hz, layers * 3.2 + 14, cz + hz]], edges=True))
    json.dump(views, open(tmp + "/views.json", "w"))
    env = dict(os.environ, LEGO_NODE_MODULES=NODE_MODULES, NODE_PATH=NODE_MODULES)
    subprocess.run(["node", os.path.join(ROOT, "engine", "render_map.js"), tmp + "/s.json", tmp + "/views.json", outdir], check=True, capture_output=True, env=env)
    from PIL import Image, ImageChops                                       # the side view is cropped to the board (a thin board in a square frame is otherwise tiny)
    im = Image.open(os.path.join(outdir, "profil.png")).convert("RGB"); bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if bb: Image.open(os.path.join(outdir, "profil.png")).convert("RGB").crop((max(0, bb[0] - 30), max(0, bb[1] - 30), min(im.width, bb[2] + 30), min(im.height, bb[3] + 30))).save(os.path.join(outdir, "profil.png"))
    return [v["name"] for v in views], tmp + "/g.glb"
