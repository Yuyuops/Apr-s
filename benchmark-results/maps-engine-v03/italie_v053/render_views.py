#!/usr/bin/env python3
"""Real renders (three.js on the expanded LDraw part meshes, real Rebrickable colours) of named views in stud coordinates.
usage: render_views.py FOLDER views.json   views = {name: {box:[r0,c0,r1,c1] studs, h:plates, az, el, w, hpx, zoom}}   (camera az 0 = looking from row+ toward row-)"""
import json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))
from maps_engine.common import E1
from maps_engine.render import real_colours, NODE_MODULES
from _paths import LDRAW
folder = Path(sys.argv[1]); spec = json.load(open(sys.argv[2])); out = folder / "renders"; tmp = out / "_scene"; tmp.mkdir(parents=True, exist_ok=True)
subprocess.run([sys.executable, os.path.join(E1, "ldr_expand.py"), "--ldr", str(folder / "diorama.ldr"), "--ldraw", LDRAW, "--json", str(tmp / "s.json"), "--glb", str(tmp / "g.glb")], check=True, capture_output=True)
real_colours(str(tmp / "s.json")); views = []
for name, v in spec.items():
    r0, c0, r1, c1 = v["box"]; H = v.get("h", 30) * 3.2
    views.append(dict(name=name, az=v.get("az", 0), el=v.get("el", 35), w=v.get("w", 1300), h=v.get("hpx", 975), zoom=v.get("zoom", 1.0), edges=True, frameBox=[[c0 * 8, -2, r0 * 8], [c1 * 8, H, r1 * 8]]))
json.dump(views, open(tmp / "views.json", "w")); env = dict(os.environ, LEGO_NODE_MODULES=NODE_MODULES, NODE_PATH=NODE_MODULES)
here = Path(__file__).resolve().parents[1] / "engine" / "render_map.js"
subprocess.run(["node", str(here), str(tmp / "s.json"), str(tmp / "views.json"), str(out)], check=True, capture_output=True, env=env); print([v["name"] for v in views])
