#!/usr/bin/env python3
"""Sprint V15 : semantic preparation (reference -> class rasters for pipelines B and C) and automated evaluation (frozen grid). usage :
   hyrule_v15.py prepare REQUIREMENTS.json REFERENCE.png OUTDIR      -> reference class map, B raster (96x78), C raster (128x104 with altitude classes), previews, measures
   hyrule_v15.py eval REQUIREMENTS.json REFERENCE_CLASSES.npy RENDER.png STYLE.json R C F OUT.json  -> automated measures of one rendered variant"""
import json, sys, sqlite3, os
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lego_builder import semantic_map as SM
FAMILY = {"water": "water", "lake": "water", "void": "void", "grass": "grass", "forest": "forest", "desert": "desert", "shore": "desert", "stone": "stone", "stone_hi": "stone", "snow": "snow", "snow_hi": "snow", "mesa": "mesa_rust", "mesa_hi": "mesa_rust", "rust": "mesa_rust", "rust_hi": "mesa_rust", "crater": "mesa_rust", "rock": "mesa_rust"}
FAMS = ["water", "void", "grass", "forest", "desert", "stone", "snow", "mesa_rust"]
def reference_classes(req, ref_png, fine_px=3):
    r = req["reference"]; x0, y0, x1, y1 = r["map_rect_px"]; im = Image.open(ref_png).convert("RGB").crop((x0, y0, x1, y1)); names = req["classes"]; protos = req["reference_prototypes"]["list"]
    idx = SM.classify(np.asarray(im), protos); codes = SM.to_classes(idx, protos, names); n = len(names)
    codes = SM.mode_filter(codes, n, 7); codes = SM.void_vs_crater(codes, names, min_crater_cells=600); codes = SM.remove_small(codes, n, 150); return codes, im
def fam_array(codes, names):
    lut = np.array([FAMS.index(FAMILY[nm]) for nm in names]); return lut[codes]
def resize_codes(codes, shape):
    R, C = shape; return np.asarray(Image.fromarray(codes.astype(np.uint8)).resize((C, R), Image.NEAREST))
def prepare(req_path, ref_png, out):
    req = json.load(open(req_path)); out = Path(out); out.mkdir(parents=True, exist_ok=True); names = req["classes"]; codes, rect = reference_classes(req, ref_png); H, W = codes.shape
    np.save(out / "reference_classes_full.npy", codes); sc = {nm: round(float((codes == i).mean()), 4) for i, nm in enumerate(names) if (codes == i).any()}
    pal = {"water": (46, 91, 159), "lake": (64, 160, 170), "void": (40, 38, 34), "grass": (75, 159, 74), "forest": (24, 90, 60), "desert": (228, 205, 158), "shore": (160, 140, 100), "stone": (160, 165, 169), "snow": (250, 250, 250), "mesa": (170, 125, 85), "rust": (120, 60, 40), "crater": (10, 10, 10), "stone_hi": (108, 110, 104), "snow_hi": (235, 235, 245), "mesa_hi": (208, 145, 104), "rust_hi": (114, 14, 15)}
    prev = np.zeros((H, W, 3), np.uint8)
    for i, nm in enumerate(names): prev[codes == i] = pal[nm]
    Image.fromarray(prev).save(out / "reference_classes_preview.png")
    meas = dict(map_px=[W, H], aspect=round(W / H, 4), class_share=sc, landmarks={})
    lm = {"snow_main": (["snow"], 1), "desert_main": (["desert", "shore"], 1), "crater": (["crater"], 1), "sea_main": (["water", "lake"], 1), "stone_main": (["stone"], 1), "forest_main": (["forest"], 1), "mesa_main": (["mesa", "rust"], 1)}
    for k, (fam, top) in lm.items(): meas["landmarks"][k] = SM.landmarks(codes, names, fam, top)
    # --- pipeline B : 96 x 78 raster (base classes only)
    RB, CB = req["board"]["detail_levels"]["standard"]["grid_studs_rows_cols"]; gb = SM.to_grid(codes, (RB, CB)); gb = SM.mode_filter(gb, len(names), 3)
    Image.fromarray(gb.astype(np.uint8)).save(out / "hyrule_B_classes.tif", compression="tiff_lzw"); np.save(out / "hyrule_B_classes.npy", gb)
    # --- pipeline C : 128 x 104 raster with altitude variants, local adjustments
    RC, CC = req["board"]["detail_levels"]["fine"]["grid_studs_rows_cols"]; gc = SM.to_grid(codes, (RC, CC)); gc = SM.mode_filter(gc, len(names), 3); gc = altitude_classes(gc, names, req)
    Image.fromarray(gc.astype(np.uint8)).save(out / "hyrule_C_classes.tif", compression="tiff_lzw"); np.save(out / "hyrule_C_classes.npy", gc)
    g2 = SM.to_grid(codes, (RC, CC)); g2 = SM.mode_filter(g2, len(names), 3); g2 = altitude_classes_massif(g2, names); Image.fromarray(g2.astype(np.uint8)).save(out / "hyrule_C2_classes.tif", compression="tiff_lzw"); np.save(out / "hyrule_C2_classes.npy", g2)
    for tag, g in (("B", gb), ("C", gc)):
        pv = np.zeros(g.shape + (3,), np.uint8)
        for i, nm in enumerate(names): pv[g == i] = pal[nm]
        Image.fromarray(pv).resize((g.shape[1] * 8, g.shape[0] * 8), Image.NEAREST).save(out / ("hyrule_%s_classes_preview.png" % tag))
    meas["B_share"] = {nm: round(float((gb == i).mean()), 4) for i, nm in enumerate(names) if (gb == i).any()}; meas["C_share"] = {nm: round(float((gc == i).mean()), 4) for i, nm in enumerate(names) if (gc == i).any()}
    json.dump(meas, open(out / "reference_measures.json", "w"), indent=1); print(json.dumps(meas)[:1200])
def altitude_classes(g, names, req):
    """Pipeline C : split mountain classes into low / high bands by the distance to the edge of their massif (progressive relief, tonal progression), soften the crater and keep plains low. Heights stay an ESTIMATE."""
    ix = {n: i for i, n in enumerate(names)}; out = g.copy()
    for base, hi, d in (("snow", "snow_hi", 3.0), ("stone", "stone_hi", 3.0), ("mesa", "mesa_hi", 3.5), ("rust", "rust_hi", 2.5)):
        m = g == ix[base]; dist = ndimage.distance_transform_edt(np.pad(m, 1, constant_values=False))[1:-1, 1:-1]; out[m & (dist >= d)] = ix[hi]
    return out
def altitude_classes_massif(g, names, d_hi=3.5):
    """Correction cycle 1 (pipeline C2) : altitude bands are computed on the whole MASSIF (union of snow, stone, mesa, rust cells) instead of class by class, so that a stone patch inside a snow range does not become an isolated 'high' island ;
    the high variant of each class is used where the distance to the edge of the massif is >= d_hi. Heights remain an ESTIMATE."""
    ix = {n: i for i, n in enumerate(names)}; out = g.copy(); base = ["snow", "stone", "mesa", "rust"]; hi = {"snow": "snow_hi", "stone": "stone_hi", "mesa": "mesa_hi", "rust": "rust_hi"}
    mass = np.isin(g, [ix[b] for b in base]); dist = ndimage.distance_transform_edt(np.pad(mass, 1, constant_values=False))[1:-1, 1:-1]
    for b in base: out[(g == ix[b]) & (dist >= d_hi)] = ix[hi[b]]
    return out
def merge_family(codes, names): return fam_array(codes, names)
def eval_variant(req_path, ref_npy, render, style_json, R, C, F, out):
    req = json.load(open(req_path)); names = req["classes"]; ref = np.load(ref_npy); rf = fam_array(ref, names)
    im = np.asarray(Image.open(render).convert("RGB")).astype(float); lum = im.mean(2); dark = lum < 100; ys, xs = np.where(dark); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    pps = (x1 - x0) / (C + 2 * F); ppy = (y1 - y0) / (R + 2 * F); ix0, ix1, iy0, iy1 = int(x0 + F * pps), int(x1 - F * pps), int(y0 + F * ppy), int(y1 - F * ppy); inner = im[iy0:iy1, ix0:ix1]
    st = json.load(open(style_json)); db = sqlite3.connect(os.environ["LEGO_ENGINE_HOME"] + "/.deps/rb.db"); proto = []
    for nm, d in st["biomes"].items():
        rgb = tuple(int(db.execute("select rgb from colors where id=?", (d["top"],)).fetchone()[0][i:i + 2], 16) for i in (0, 2, 4)); proto.append((rgb, FAMILY.get(nm, "mesa_rust")))
    P = np.array([p[0] for p in proto], float); sm = np.stack([ndimage.uniform_filter(inner[..., i], 5) for i in range(3)], -1); lab = ((sm[..., None, :] - P) ** 2).sum(-1).argmin(-1); fam = np.array([FAMS.index(p[1]) for p in proto])[lab]
    GH, GW = ref.shape if False else (rf.shape[0] // 4, rf.shape[1] // 4)
    def down(a, shape):
        Hh, Ww = shape; out_ = np.zeros(shape, int); yy = (np.arange(a.shape[0]) * Hh // a.shape[0]); xx = (np.arange(a.shape[1]) * Ww // a.shape[1]); cnt = np.zeros((Hh, Ww, len(FAMS)), int)
        for k in range(len(FAMS)): cnt[..., k] = np.bincount((yy[:, None] * Ww + xx[None, :])[a == k], minlength=Hh * Ww).reshape(Hh, Ww)
        return cnt.argmax(-1)
    shape = (78, 96); a = down(fam, shape); b = down(rf, shape); acc = float((a == b).mean()); iou = {}
    for k, f in enumerate(FAMS):
        if f == "void": continue
        i_ = float(((a == k) & (b == k)).sum()); u = float(((a == k) | (b == k)).sum()); iou[f] = round(i_ / u, 3) if u else None
    miou = float(np.mean([v for v in iou.values() if v is not None]))
    def cen(arr, fams):
        m = np.isin(arr, [FAMS.index(x) for x in fams]); lab_, n_ = ndimage.label(m)
        if n_ == 0: return None
        sz = ndimage.sum(m, lab_, range(1, n_ + 1)); cy, cx = ndimage.center_of_mass(lab_ == int(np.argmax(sz)) + 1); return (cx / arr.shape[1], cy / arr.shape[0])
    errs = {}
    for k, fams in (("snow_main", ["snow"]), ("desert_main", ["desert"]), ("sea_main", ["water"]), ("stone_main", ["stone"]), ("forest_main", ["forest"]), ("mesa_main", ["mesa_rust"])):
        ca, cb = cen(a, fams), cen(b, fams); errs[k] = round(float(np.hypot(ca[0] - cb[0], ca[1] - cb[1])), 3) if ca and cb else None
    ve = [v for v in errs.values() if v is not None]; res = dict(map_pixels=[int(ix1 - ix0), int(iy1 - iy0)], aspect=round((ix1 - ix0) / (iy1 - iy0), 3), aspect_error=round(abs((ix1 - ix0) / (iy1 - iy0) - req["board"]["aspect_width_over_height"]) / req["board"]["aspect_width_over_height"], 3),
        pixel_accuracy=round(acc, 3), mean_IoU=round(miou, 3), IoU_by_family=iou, landmark_errors=errs, landmark_error_mean=round(float(np.mean(ve)), 3), family_share={FAMS[k]: round(float((a == k).mean()), 3) for k in range(len(FAMS))})
    def extras(arr):
        bnd = float(((arr[:, 1:] != arr[:, :-1]).sum() + (arr[1:, :] != arr[:-1, :]).sum()) / arr.size); ncomp = 0; big = {}
        for k, f in enumerate(FAMS):
            lab_, n_ = ndimage.label(arr == k); ncomp += n_
            if n_: big[f] = round(float(ndimage.sum(arr == k, lab_, range(1, n_ + 1)).max() / arr.size), 3)
        return dict(boundary_density=round(bnd, 3), components=int(ncomp), largest_component_share=big)
    res["descriptive_variant"] = extras(a); res["descriptive_reference"] = extras(b)
    json.dump(res, open(out, "w"), indent=1); print(json.dumps(res))
if __name__ == "__main__":
    c = sys.argv[1]
    if c == "prepare": prepare(*sys.argv[2:5])
    else: eval_variant(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8]), sys.argv[9])
