#!/usr/bin/env python3
"""Region builder (V0.5.5) : any window of the Italia grid -> base + sculpted DEM terrain + monument modules + conifers. Monuments flatten their footprint in the relief field
(terrain is removed under the plaza and the ring around it is lowered to level 1) so the module stands on a coherent podium. usage as module : build_region(...)."""
import json, os, random, sys
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import Scene
from tiler import tile, PLATES
import relief, sculpt, colosseum, colosseum_v2, pisa, finish
def base(S, R, C, rng):
    cells = {(r, c) for r in range(R) for c in range(C)}
    for (r, c, nr, nc, part, rot) in tile(cells, PLATES, rng, 3.5, 64): S.add(part, 72, r, c, 0, rot, "backing")
    for (r, c, nr, nc, part, rot) in tile(cells, PLATES, rng, 2.3, 64): S.add(part, 72, r, c, 1, rot, "backing")
    for (r, c, nr, nc, part, rot) in tile(cells, PLATES, rng, 2.3, 64): S.add(part, 272, r, c, 2, rot, "sea")
COL_VARIANTS = {"full": dict(n_oval=3.9, gaps=False, ruin_min=2, scale=(18, 22)), "simplified": dict(n_oval=3.9, gaps=False, ruin_min=2, scale=(15, 18)), "icon": dict(n_oval=2.3, gaps=True, ruin_min=2, scale=(14, 17)), "icon28": dict(n_oval=2.8, gaps=True, ruin_min=2, scale=(22, 28)), "icon26": dict(n_oval=2.6, gaps=True, ruin_min=2, scale=(20, 26)), "arcA": dict(v2="A", scale=(20, 26)), "arcB": dict(v2="B", scale=(20, 26)), "arcC": dict(v2="C", scale=(20, 26))}
def colosseum_geometry(rows, cols, pm=1):
    a = (cols - 2 * pm) / 2 - 1.2; b = (rows - 2 * pm) / 2 - 1.2; return a, b, 1.2 + pm
def build_region(out, r0, c0, R, C, monuments=(), seed=7, relief_kw=None, sculpt_P=None, trees=True, title="", frame=0, sea=False, zones=None, leader=None):
    rng = random.Random(seed); F = relief.make_field(r0, c0, R, C, **(relief_kw or {})); f = frame; S = Scene(R + 2 * f, C + 2 * f); S.do_merge = True; base(S, R + 2 * f, C + 2 * f, rng); mods = {}; podium = np.zeros((R, C), bool)
    for m in monuments:        # flatten relief under each monument
        if m["type"] == "colosseum":
            v = COL_VARIANTS[m["variant"]]; rows, cols = m.get("footprint", v["scale"]); a, b, pe = colosseum_geometry(rows, cols); cr, cc = m["row"] + rows // 2 - r0, m["col"] + cols // 2 - c0
            cells = colosseum.oval_cells(cr, cc, a + pe, b + pe, 3.0); m["_cells"] = cells; m["_geom"] = (cr, cc, a, b, pe)
            for (r, c) in cells: podium[r, c] = True
    cones = []
    for m in monuments:
        if m["type"] == "pisa":
            rows, cols = m.get("footprint", (6, 6)); lr, lc = m["row"] - r0, m["col"] - c0; m["_local"] = (lr, lc)
            for i in range(rows):
                for j in range(cols): podium[lr + i, lc + j] = True
        if m["type"] == "vesuvio":
            rows, cols = m.get("footprint", (9, 9)); cones.append(dict(cr=m["row"] - r0 + rows / 2.0, cc=m["col"] - c0 + cols / 2.0, rows=rows, cols=cols))
    ring = ndimage.binary_dilation(podium, iterations=2) & ~podium
    F["h"] = np.where(podium, 0.0, np.where(ring & F["land"], np.minimum(F["h"], 3.0), F["h"])); F["land"] = F["land"] & ~podium; F["forbid"] = ndimage.binary_dilation(podium, iterations=1)
    F["override"] = None
    for cn in cones:      # Vesuvius : ONE massif = cone + lopsided Somma shoulder (no ring), irregular rim, breach to the south-west, cavity with sloped walls
        rr, cc = np.mgrid[0:R, 0:C].astype(float); dy, dx = rr + .5 - cn["cr"], cc + .5 - cn["cc"]; d = np.hypot(dy, dx); ang = np.degrees(np.arctan2(dy, dx)); Rb = max(cn["rows"], cn["cols"]) / 2.0 + 2.6; H = 3 * 9.0
        nz = np.random.RandomState(31); rim_noise = sum(a_ * np.cos(np.radians(k * ang) + p_) for k, a_, p_ in ((2, .35, .4), (3, .3, 1.7), (5, .22, 2.6)))
        R0 = 3.4 + 1.3 * rim_noise                                          # irregular rim radius (studs)
        cone = H * np.clip(1 - d / Rb, 0, 1) ** 1.1
        sect = np.exp(-(((ang + 90 + 180) % 360 - 180) / 70.0) ** 2)                         # Somma : north sector
        shoulder = 0.62 * H * np.clip(1 - np.maximum(d - 2.6, 0) / 4.2, 0, 1) * sect         # attached shoulder, merged by max : same massif, asymmetric crest
        top = np.maximum(cone, shoulder); rim_h = H * (0.9 + 0.08 * np.sin(np.radians(3 * ang + 40))); breach = np.exp(-(((ang - 140 + 180) % 360 - 180) / 28.0) ** 2)    # lower rim to the south-west
        rim_h = rim_h - 0.34 * H * breach
        inside = d < R0 + 0.9; floor = 0.34 * H; wall = floor + (np.clip((d - 1.6) / (R0 - 1.6), 0, 1.2)) * (rim_h - floor)
        prof = np.where(inside, np.minimum(wall, rim_h), np.minimum(top, rim_h + 0.0 * top))
        prof = np.where(d < 1.6, floor, prof); prof = np.where((~inside) & (d < Rb), np.maximum(prof, np.minimum(top, rim_h)), prof)
        F["h"] = np.maximum(F["h"] * (d > Rb), 0) + np.where(d <= Rb + 1e-9, np.maximum(prof, 3.0 * (d < Rb)), 0)
        F["land"] = F["land"] | (d < Rb); F["elev"] = np.where(d < Rb * 0.85, np.maximum(F["elev"], 1700.0), np.where(d < Rb, np.maximum(F["elev"], 800.0), F["elev"])); cn.update(d=d, Rb=Rb, R0=R0, ang=ang)
    if cones:
        def override(r, c, k, K, cones=cones):
            for cn in cones:
                d = cn["d"][r, c]
                if d > cn["Rb"] + 0.3: continue
                R0 = cn["R0"][r, c]; top = K[r, c] - 1; lv = K[r, c]
                if d < 1.7: return 0 if (k >= top and (r + c) % 2 == 0) else 72                  # cavity floor : only the central cells are black
                if d < R0 + 0.5:                                              # crater walls : dark rock, red-brown strata, ash
                    return (72, 70, 72, 0, 71)[(r * 5 + c * 3 + k) % 5]
                if d < R0 + 1.5 and k >= top - 1: return (71, 19, 71, 28)[(r + 2 * c + k) % 4]   # pale rim (ash / tuff)
                if lv >= 3: return (72, 71, 72, 70, 28)[(r * 7 + c * 3 + k) % 5] if k >= top - 2 else 72
            return None
        F["override"] = override
    K, cat, info, aux = sculpt.build_terrain(S, f, f, F, seed, P=sculpt_P)
    deco = sculpt.decorate(S, K, cat, aux, f, f, seed, beach_ok=F["beach_ok"] & ~podium)
    for cn in cones: mods['vesuvio'] = dict(type='terrain-integrated cone', footprint=[cn['rows'], cn['cols']], base_radius_studs=round(float(cn['Rb']), 1), crater_radius_studs=1.7, somma_arc=True)
    for m in monuments:
        if m["type"] == "pisa": mods["pisa"] = pisa.build_pisa(S, m["_local"][0] + f, m["_local"][1] + f, random.Random(5), m.get("lean", 1))
        if m["type"] == "colosseum":
            v = COL_VARIANTS[m["variant"]]; cr, cc, a, b, pe = m["_geom"]; mods["colosseum"] = dict(variant=m["variant"], **(colosseum_v2.build(S, cr + f, cc + f, a, b, pe, 2.6, v["v2"]) if "v2" in v else colosseum.build_colosseum(S, cr + f, cc + f, a=a, b=b, plaza_extra=pe, n_oval=v["n_oval"], gaps=v["gaps"], ruin_min=v["ruin_min"])))
    if zones: mods["decor_tiles"] = finish.decor(S, zones, f, rng)
    if leader: mods["leader_tiles"] = finish.leader(S, leader, f, rng)
    if sea:
        d = ndimage.distance_transform_edt(~F["land"] & ~podium) if False else ndimage.distance_transform_edt(~ (F["land"] | podium)); land_d = ndimage.distance_transform_edt(~(F["land"] | podium)); mods["sea_tiles"] = finish.sea_tiles(S, R, C, f, land_d, rng)
    if f: mods["frame_cells"] = finish.frame(S, R, C, f, rng)
    met = S.write(out, "V0.5.5 region " + title, dict(window=[r0, c0, R, C], relief=F["info"], terrain=info, deco=deco, modules=mods)); return S, met, F
