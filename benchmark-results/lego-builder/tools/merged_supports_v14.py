#!/usr/bin/env python3
"""Sprint V14 correction : slicing the colour bodies of a module as SEPARATE objects makes PrusaSlicer build supports for each body through its neighbours ('gcode path conflicts between b0 and b1'), which overstates support mass. Here every module is first UNIONED into one solid (as a multicolour slicer sees one object with several coloured parts) and sliced with / without supports (proxy profile A1). usage : merged_supports_v14.py OUT.json WORKDIR MODEL:DIR ..."""
import json, sys, importlib.util
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np, manifold3d as M
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / "tools"))
import render_3mf as R
from lego_builder.print3d.common import write_3mf
spec = importlib.util.spec_from_file_location("sp", HERE / "tools/slice_proxy_v14.py"); sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
out, work = sys.argv[1], Path(sys.argv[2]); work.mkdir(parents=True, exist_ok=True); jobs = []
for spec_ in sys.argv[3:]:
    model, d = spec_.split(":")
    for f in sorted(Path(d).glob("*.3mf")):
        ms = [M.Manifold(M.Mesh(v.astype(np.float32), t.astype(np.uint32))) for v, t, _ in R.load(f)]; u = M.Manifold.batch_boolean(ms, M.OpType.Add); mm = u.to_mesh()
        g = work / ("%s_%s_merged.3mf" % (model, f.stem)); write_3mf([dict(name="module", v=np.asarray(mm.vert_properties)[:, :3], f=np.asarray(mm.tri_verts), colour_hex="888888", offset=(1, 1, 0))], g); jobs.append((model, f.stem, g))
def run(j):
    model, stem, g = j; res = []
    for sup in (False, True): r = sp.slice_(g, "%s_%s_merged" % (model, stem), "A1", sup); r.update(model=model, module=stem); res.append(r)
    print(model, stem, [(x.get("seconds"), x.get("filament_g")) for x in res], flush=True); return res
with ThreadPoolExecutor(3) as ex: allr = [r for rs in ex.map(run, jobs) for r in rs]
json.dump(allr, open(out, "w"), indent=1, default=str)
