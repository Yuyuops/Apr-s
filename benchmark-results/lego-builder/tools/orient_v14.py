#!/usr/bin/env python3
"""Sprint V14 : orientation / support experiments on one real module (proxy profile A1, PrusaSlicer). usage : orient_v14.py MODULE.3mf OUT.json WORKDIR"""
import json, sys, importlib.util
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / "tools"))
import render_3mf as R
from lego_builder.print3d.common import write_3mf
spec = importlib.util.spec_from_file_location("slicer_proxy", HERE / "tools/slice_proxy_v14.py"); sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
src, out, work = sys.argv[1], sys.argv[2], Path(sys.argv[3]); work.mkdir(parents=True, exist_ok=True); objs = R.load(src)
def rot(angles):
    ax, ay = np.radians(angles); Rx = np.array([[1, 0, 0], [0, np.cos(ax), -np.sin(ax)], [0, np.sin(ax), np.cos(ax)]]); Ry = np.array([[np.cos(ay), 0, np.sin(ay)], [0, 1, 0], [-np.sin(ay), 0, np.cos(ay)]]); return Ry @ Rx
res = []
for name, ang in (("upright", (0, 0)), ("on_back_x90", (90, 0)), ("on_side_y90", (0, 90)), ("upside_down_x180", (180, 0))):
    M = rot(ang); vs = [o[0] @ M.T for o in objs]; lo = np.min([v.min(0) for v in vs], 0); ob = []
    for i, (v, (_, t, rgb)) in enumerate(zip(vs, objs)):
        if np.linalg.det(M) > 0: tt = t
        ob.append(dict(name="b%d" % i, v=v - lo, f=t, colour_hex="%02X%02X%02X" % rgb, offset=(1, 1, 0)))
    f = work / ("orient_%s.3mf" % name); write_3mf(ob, f); ext = np.max([o["v"].max(0) for o in ob], 0)
    for label, sup, extra in (("no_support", False, ()), ("support_45", True, ()), ("support_60", True, ("--support-material-threshold", "60")), ("support_buildplate_only", True, ("--support-material-buildplate-only",)), ("support_organic", True, ("--support-material-style", "organic"))):
        if name != "upright" and label not in ("no_support", "support_45"): continue
        r = sp.slice_(f, "%s_%s" % (name, label), "A1", sup, extra); r.update(orientation=name, variant=label, extent_mm=[round(float(x), 1) for x in ext]); res.append(r); print(name, label, r.get("seconds"), r.get("filament_g"), r.get("warn"), flush=True)
json.dump(res, open(out, "w"), indent=1, default=str)
