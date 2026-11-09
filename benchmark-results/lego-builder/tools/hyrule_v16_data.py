#!/usr/bin/env python3
"""Sprint V16 data preparation : B16 = the V15 B raster (96 x 78) with two refinements measured on the reference, contours untouched :
   - meadow : the 2nd grass prototype (sage green) of the reference becomes its own class (colour variation inside the plains instead of one uniform green) ;
   - shallow : water cells within 2 studs of land (depth gradient of the sea/lake margin, same level).
Also cuts the three 32x32 pilot zones. usage : hyrule_v16_data.py REQUIREMENTS.json REFERENCE.png OUTDIR"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lego_builder import semantic_map as SM
req = json.load(open(sys.argv[1])); out = Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True); names = req["classes"][:12] + ["shallow", "meadow", "spare1", "spare2"]
r = req["reference"]; x0, y0, x1, y1 = r["map_rect_px"]; im = np.asarray(Image.open(sys.argv[2]).convert("RGB").crop((x0, y0, x1, y1))); protos = req["reference_prototypes"]["list"]
idx = SM.classify(im, protos); proto_class = [p["class"] for p in protos]
sage = [i for i, p in enumerate(protos) if p["class"] == "grass" and tuple(p["lab"]) == (53, -20, 11)]
cls = np.array([names.index(p["class"]) for p in protos])[idx]; n = len(names)
cls = SM.mode_filter(cls, n, 7); cls = SM.void_vs_crater(cls, names, min_crater_cells=600); cls = SM.remove_small(cls, n, 150)          # identical to the V15 pipeline : contours cannot move
RB, CB = req["board"]["detail_levels"]["standard"]["grid_studs_rows_cols"]; g = SM.to_grid(cls, (RB, CB)); g = SM.mode_filter(g, n, 3)
# meadow : grass cells of the grid whose pixels are mostly the sage prototype (relabel only, never moves a boundary)
H, W = idx.shape; ys = (np.arange(H) * RB // H); xs = (np.arange(W) * CB // W); sage_px = np.isin(idx, sage).astype(float); cnt = np.bincount((ys[:, None] * CB + xs[None, :]).ravel(), weights=sage_px.ravel(), minlength=RB * CB).reshape(RB, CB); tot = np.bincount((ys[:, None] * CB + xs[None, :]).ravel(), minlength=RB * CB).reshape(RB, CB)
g[(g == names.index("grass")) & (cnt / np.maximum(tot, 1) > 0.5)] = names.index("meadow")
water = np.isin(g, [names.index("water")]); land = ~np.isin(g, [names.index(k) for k in ("water", "lake", "void")]); d = ndimage.distance_transform_edt(~land)
core = ndimage.binary_erosion(water, iterations=2); near_core = ndimage.binary_dilation(core, iterations=3)          # shallows only around WIDE water bodies : thin rivers and moats stay deep blue (fidelity to the reference)
g16 = g.copy(); g16[water & (d <= 1.5) & near_core] = names.index("shallow")
np.save(out / "B16_classes.npy", g16); Image.fromarray(g16.astype(np.uint8)).save(out / "B16_classes.tif", compression="tiff_lzw")
Z = {"A": (0, 56), "B": (24, 36), "C": (46, 56)}; rep = {"names": names, "shares_full": {names[i]: round(float((g16 == i).mean()), 4) for i in range(n) if (g16 == i).any()}, "zones": {}}
for k, (rr, cc) in Z.items():
    z = g16[rr:rr + 32, cc:cc + 32]; np.save(out / ("zone_%s_classes_v16.npy" % k), z); Image.fromarray(z.astype(np.uint8)).save(out / ("zone_%s_classes_v16.tif" % k), compression="tiff_lzw"); rep["zones"][k] = {names[i]: round(float((z == i).mean()), 3) for i in range(n) if (z == i).any()}
json.dump(rep, open(out / "B16_report.json", "w"), indent=1); print(json.dumps(rep["shares_full"]))
