#!/usr/bin/env python3
"""V0.5.5 chantier A : Alpine sector (32x32 studs) from real altitude, sculpted. usage: alps_test.py OUT [r0 c0] [--VE x]"""
import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import Scene
from tiler import tile, PLATES
import relief, sculpt
def base(S, R, C, rng):
    cells = {(r, c) for r in range(R) for c in range(C)}
    for r in range(0, R, 8):
        for c in range(0, C, 8): S.add("41539", 72, r, c, 0, 0, "backing")
    for (r, c, nr, nc, part, rot) in tile(cells, PLATES, rng, 2.3, 64): S.add(part, 72, r, c, 1, rot, "backing")
    for (r, c, nr, nc, part, rot) in tile(cells, PLATES, rng, 2.3, 64): S.add(part, 272, r, c, 2, rot, "sea")
def build(out, r0=10, c0=20, R=32, C=32, seed=7, steep=1, snow_m=2300, rock_m=1500, **kw):
    kw_steep = int(steep); kw_snow = float(snow_m); kw_rock = float(rock_m)
    F = relief.make_field(r0, c0, R, C, **kw); S = Scene(R, C); base(S, R, C, random.Random(seed))
    K, cat, info, aux = sculpt.build_terrain(S, 0, 0, F, seed, P=dict(steep=kw_steep, snow_m=kw_snow, rock_m=kw_rock)); deco = sculpt.decorate(S, K, cat, aux, 0, 0, seed, beach_ok=F["beach_ok"])
    m = S.write(out, "V0.5.5 Alpine sector from real DEM", dict(window=[r0, c0, R, C], relief=F["info"], terrain=info, deco=deco)); print(json.dumps(m)[:600]); return S
if __name__ == "__main__":
    a = sys.argv[1:]; kw = {}
    for key in ("VE", "detail", "ridge_gain", "valley_depth", "sharpen", "steep", "snow_m", "rock_m"):
        if "--" + key in a: i = a.index("--" + key); kw[key] = float(a[i + 1]) if key not in ("steep",) else int(a[i + 1]); del a[i:i + 2]
    out = a[0]; r0, c0 = (int(a[1]), int(a[2])) if len(a) > 2 else (10, 20); build(out, r0, c0, **kw)
