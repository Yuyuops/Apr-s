#!/usr/bin/env python3
"""V0.5.5 chantier E : full Italia 128 x 128 studs model (102.4 cm field, 105.6 cm with the 2-stud frame) : real DEM relief sculpted, offshore Colosseum medallion, Pisa tower, Vesuvius,
solid conifers, smooth sea tiles, ITALIA title + compass rose in tiles, frame. usage: italia_full.py OUT [--no-sea]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "italia"))
import region, colosseum
HERE = os.path.dirname(os.path.abspath(__file__)); pl = json.load(open(os.path.join(HERE, "italia/output/placements.json"))); cfg = json.load(open(os.path.join(HERE, "italia/artistic_scale_config.json")))
def monuments():
    opt = json.load(open(os.path.join(HERE, "results/B_colisee/placement_options.json")))["offshore_medallion"]; mons = [dict(type="colosseum", variant="arcA", row=opt["row"], col=opt["col"], footprint=[20, 26])]
    for m in pl["monuments"]:
        if m["id"] == "pisa_tower": mons.append(dict(type="pisa", row=m["row"], col=m["col"], footprint=[6, 6], lean=1))
        if m["id"] == "vesuvio": mons.append(dict(type="vesuvio", row=m["row"] - 2, col=m["col"] - 2, footprint=[12, 12]))
    return mons
RELIEF = dict(VE=2.0, detail=8, ridge_gain=3.2, valley_depth=7, sharpen=1.2, band=3); SCULPT = dict(steep=1, snow_m=1900, rock_m=1000, p75=0.45)
if __name__ == "__main__":
    out = sys.argv[1]; mons = monuments()
    import numpy as np, geo
    land = np.load(os.path.join(HERE, "italia/output/land_128.npy")); ar, ac = geo.to_grid(12.4924, 41.8902); col_ = mons[0]; cr, cc = col_["row"] + 10, col_["col"] + 13
    n = int(max(abs(ar - cr), abs(ac - cc)) * 2); lead = []
    for t in range(n + 1):
        rr, c2 = int(round(cr + (ar - cr) * t / n)), int(round(cc + (ac - cc) * t / n))
        if land[rr, c2]: break
        if not (col_["row"] - 2 <= rr <= col_["row"] + 22 and col_["col"] - 2 <= c2 <= col_["col"] + 28) and (rr, c2) not in lead: lead.append((rr, c2))
    zones = {k: dict(v, text="ITALIA") if k == "title" else dict(v, d=15) for k, v in pl["zones"].items()}
    S, met, F = region.build_region(out, 0, 0, 128, 128, mons, relief_kw=RELIEF, sculpt_P=SCULPT, title="Italia 128", frame=2, sea="--no-sea" not in sys.argv, zones={"title": dict(row=zones["title"]["row"], col=zones["title"]["col"], text="ITALIA"), "compass": dict(row=zones["compass"]["row"], col=zones["compass"]["col"], d=15)}, leader=lead)
    print(json.dumps({k: met[k] for k in ("pieces", "references", "max_height_mm", "physical_size_mm")}), json.dumps(met["modules"]), json.dumps(met["terrain"]))
