"""Image -> map data, with no manual step : board detection + perspective rectification + colour-cluster labelling into biome classes. Outputs terrain_classes.tif (internal format), preview.png, palette.json,
composition.json, style.json. Nothing is invented : every class comes from a colour found in the picture ; the relief is an ESTIMATE (shape heuristic) and the manifest says so."""
import json, math
import numpy as np
from PIL import Image
from scipy import ndimage
from .paths import DATA, MAPS
def _hsv(rgb):
    return np.asarray(Image.fromarray(rgb).convert("HSV")).astype(float) * np.array([360 / 255, 1 / 255, 1 / 255])
def detect_board(img, work=640):
    """-> (corners TL,TR,BR,BL in source pixels, info). A dark frame/background around a bright board is detected ; a picture without such a frame is taken as a flat map (corners = picture corners)."""
    W, H = img.size; s = work / max(W, H); small = img.resize((max(8, int(W * s)), max(8, int(H * s)))); v = _hsv(np.asarray(small.convert("RGB")))[..., 2]; h, w = v.shape
    fg = v > 0.30; frac = float(fg.mean()); info = dict(foreground_fraction=round(frac, 3))
    border = np.concatenate([v[: h // 25].ravel(), v[-(h // 25):].ravel(), v[:, : w // 25].ravel(), v[:, -(w // 25):].ravel()]); info["border_median_value"] = round(float(np.median(border)), 3)
    bright_bg = np.median(border) > 0.35
    if bright_bg:                                                          # light uniform background (studio render) : board = pixels that differ from the background colour
        a = np.asarray(small.convert("RGB")).astype(float) / 255; bgc = np.median(np.concatenate([a[: h // 25].reshape(-1, 3), a[-(h // 25):].reshape(-1, 3), a[:, : w // 25].reshape(-1, 3), a[:, -(w // 25):].reshape(-1, 3)]), axis=0)
        fg = np.linalg.norm(a - bgc, axis=2) > 0.16; info["background"] = "light_uniform" if float(border.std()) < 0.12 else "light_textured"; frac = float(fg.mean()); info["foreground_fraction"] = round(frac, 3)
        if float(border.std()) > 0.12 or frac > 0.92 or frac < 0.08: info["mode"] = "flat_map_no_frame"; return [(0, 0), (W, 0), (W, H), (0, H)], info
    elif frac > 0.92:
        info["mode"] = "flat_map_no_frame"; return [(0, 0), (W, 0), (W, H), (0, H)], info
    k = max(3, int(w * 0.012)) | 1; op = ndimage.binary_opening(fg, structure=np.ones((k, k))); lab, n = ndimage.label(op)
    if n == 0: info["mode"] = "fallback_full_picture"; return [(0, 0), (W, 0), (W, H), (0, H)], info
    big = int(np.argmax(ndimage.sum(op, lab, range(1, n + 1)))) + 1; m = ndimage.binary_fill_holes(lab == big); ys, xs = np.where(m)
    from scipy.spatial import ConvexHull
    pts = np.stack([xs, ys], 1).astype(float); hull = pts[ConvexHull(pts).vertices]
    if len(hull) > 48: hull = hull[np.linspace(0, len(hull) - 1, 48).astype(int)]
    import itertools
    def area(q): x, y = q[:, 0], q[:, 1]; return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
    q = max((hull[list(i)] for i in itertools.combinations(range(len(hull)), 4)), key=area)          # the 4 hull points enclosing the largest area = the board corners (exact for a convex board)
    cen0 = q.mean(0); ang = np.arctan2(q[:, 1] - cen0[1], q[:, 0] - cen0[0]); q = q[np.argsort(ang)]; i0 = int(np.argmin(q[:, 0] + q[:, 1])); q = np.roll(q, -i0, axis=0); tl, tr, br, bl = q
    c = np.array([tl, tr, br, bl]); cen = c.mean(0); c = cen + (c - cen) * (0.95 if info.get("background") else 0.985)          # inset : stay inside the frame (5 % when the hull is the outer frame of a board on a light background)
    info.update(mode="framed_board", board_area_fraction=round(float(m.mean()), 3)); return [(float(x / s), float(y / s)) for x, y in c], info
def estimate_aspect(corners, size):
    """True width/height of a planar rectangle seen in perspective, from its 4 image corners, assuming square pixels and the principal point at the image centre (Zhang's constraint). Returns (aspect, focal_px) or None."""
    W, H = size; cx, cy = W / 2, H / 2; src = [(0, 0), (1, 0), (1, 1), (0, 1)]; A = []
    for (x, y), (u, v) in zip(src, corners):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y, u]); A.append([0, 0, 0, x, y, 1, -v * x, -v * y, v])
    Hm = np.linalg.svd(np.array(A, float))[2][-1].reshape(3, 3); h1, h2 = Hm[:, 0], Hm[:, 1]; best = None
    for f in np.linspace(0.3, 6.0, 2400) * max(W, H):
        Ki = np.array([[1 / f, 0, -cx / f], [0, 1 / f, -cy / f], [0, 0, 1]]); w = Ki.T @ Ki; c = abs(h1 @ w @ h2) / np.sqrt((h1 @ w @ h1) * (h2 @ w @ h2))
        if best is None or c < best[0]: best = (c, f, np.sqrt((h1 @ w @ h1) / (h2 @ w @ h2)))
    return (float(best[2]), float(best[1])) if best and best[0] < 0.03 and best[1] > 0.35 * max(W, H) and 0.2 < best[2] < 5 else None
def rectify(img, corners, W, H):
    dst = [(0, 0), (W, 0), (W, H), (0, H)]; A = []; B = []
    for (x, y), (u, v) in zip(dst, corners):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u); A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    coef = np.linalg.solve(np.array(A, float), np.array(B, float)); return img.transform((W, H), Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)
def _rule_for(mean_hsv, rules):
    h, s, v = mean_hsv; best = None
    for r in rules:                                                         # first rule containing the mean colour
        if r["hue"][0] <= h <= r["hue"][1] and r["sat"][0] <= s <= r["sat"][1] and r["val"][0] <= v <= r["val"][1]: return r, 0.0
    def d(lo, hi, x): return 0.0 if lo <= x <= hi else min(abs(x - lo), abs(x - hi))
    for r in rules:                                                         # else the nearest rule (hue distance in degrees/180, others as is)
        dist = d(*r["hue"], h) / 180 + d(*r["sat"], s) + d(*r["val"], v)
        if best is None or dist < best[1]: best = (r, dist)
    return best
def classify_pixels(rect, rules, K):
    """Per-pixel colour rules -> soft membership (blurred by `smooth` studs, times `weight`) -> argmax ; regions under `min_region_studs2` take the majority of their surroundings."""
    arr = np.asarray(rect.convert("RGB")); H, W, _ = arr.shape; hsv = _hsv(arr); score = np.zeros((len(rules), H, W))
    for i, c in enumerate(rules):
        m = ((hsv[..., 0] >= c["hue"][0]) & (hsv[..., 0] <= c["hue"][1]) & (hsv[..., 1] >= c["sat"][0]) & (hsv[..., 1] <= c["sat"][1]) & (hsv[..., 2] >= c["val"][0]) & (hsv[..., 2] <= c["val"][1])).astype(float)
        score[i] = ndimage.gaussian_filter(m, K * c.get("smooth", 0.8)) * c.get("weight", 1.0)
    best = score.argmax(0); none = score.max(0) < 0.04
    if none.any(): idx = ndimage.distance_transform_edt(none, return_distances=False, return_indices=True); best = best[tuple(idx)]
    for i, c in enumerate(rules):
        mn = c.get("min_region_studs2", 0)
        if mn:
            lab, n = ndimage.label(best == i); sz = ndimage.sum(best == i, lab, range(1, n + 1)); small = np.isin(lab, [j + 1 for j, z in enumerate(sz) if z < mn * K * K])
            if small.any(): sc = score.copy(); sc[i] = -1; best = np.where(small, sc.argmax(0), best)
    nm = {c["name"]: i for i, c in enumerate(rules)}
    if "water" in nm:                                                                                 # contextual rule : a snow/stone region whose border is mostly water is water
        for nme in ("snow", "stone"):
            if nme not in nm: continue
            lab, n = ndimage.label(best == nm[nme])
            for j in range(1, n + 1):
                reg = lab == j; ring = ndimage.binary_dilation(reg, iterations=max(2, K // 3)) & ~reg
                if ring.any() and float((best[ring] == nm["water"]).mean()) > 0.6: best[reg] = nm["water"]
    codes = np.zeros((H, W), np.uint8)
    for i, c in enumerate(rules): codes[best == i] = c["code"]
    return codes, {c["name"]: round(float((best == i).mean()), 4) for i, c in enumerate(rules)}
def prepare_map(src, outdir, size_mm=400, frame_studs=4, rules_file=None, corners=None, aspect=None, title=None, k=12):
    outdir = __import__("pathlib").Path(outdir); outdir.mkdir(parents=True, exist_ok=True); img = Image.open(src).convert("RGB"); rules = json.load(open(rules_file or DATA / "biome_rules_default.json"))["classes"]
    if corners: cinfo = dict(mode="user_corners"); cor = [tuple(c) for c in corners]
    else: cor, cinfo = detect_board(img)
    top = np.hypot(*(np.array(cor[1]) - cor[0])); bot = np.hypot(*(np.array(cor[2]) - cor[3])); lef = np.hypot(*(np.array(cor[3]) - cor[0])); rig = np.hypot(*(np.array(cor[2]) - cor[1]))
    persp = max(top, bot) / max(1e-6, min(top, bot)); cinfo["perspective_ratio_top_bottom"] = round(float(persp), 3)
    if aspect is None:                                                                  # unknown true proportions
        if persp < 1.04 and abs(top / max(bot, 1e-6) - 1) < 0.04: aspect = ((top + bot) / 2) / ((lef + rig) / 2); cinfo["aspect_source"] = "measured_flat"
        else:
            est = estimate_aspect(cor, img.size)
            if est: aspect, f = est; cinfo["aspect_source"] = "estimated_from_perspective (square pixels, principal point at centre)"; cinfo["focal_px_estimate"] = round(f, 0)
            else: aspect = 1.0; cinfo["aspect_source"] = "assumed_square_perspective_view"
    cinfo["aspect_used"] = round(float(aspect), 3)
    n_long = int(round(size_mm / 8)) - 2 * frame_studs; R, C = (n_long, max(8, int(round(n_long * aspect)))) if aspect <= 1 else (max(8, int(round(n_long / aspect))), n_long)
    if aspect <= 1: R, C = n_long, max(8, int(round(n_long * aspect)))
    Kpx = 12; rect = rectify(img, cor, C * Kpx, R * Kpx); codes, labels = classify_pixels(rect, rules, Kpx)
    Image.fromarray(codes).save(outdir / "terrain_classes.tif", compression="tiff_lzw")
    names = {r["code"]: r["name"] for r in rules}; pv = np.zeros(codes.shape + (3,), np.uint8)
    for r in rules: pv[codes == r["code"]] = r["preview"]
    prev = Image.new("RGB", (C * Kpx * 2, R * Kpx)); prev.paste(rect, (0, 0)); prev.paste(Image.fromarray(pv), (C * Kpx, 0)); prev.save(outdir / "preview.png")
    stl = json.load(open(DATA / "biome_styles_default.json")); present = sorted({int(c) for c in np.unique(codes)}); used = {names[c] for c in present}
    palette = {"biomes": {n: stl["biomes"][n] for n in used}, "relief_is_estimated": True, "share": {names[c]: round(float((codes == c).mean()), 4) for c in present}}; json.dump(palette, open(outdir / "palette.json", "w"), indent=1)
    comp = {"_doc": "generated by lego_builder from %s" % __import__("pathlib").Path(src).name, "biome_map": {"file": str((outdir / "terrain_classes.tif").resolve()), "classes": {str(c): names[c] for c in present}, "majority_passes": 1}, "grid_studs": [R, C], "sub": 8}
    json.dump(comp, open(outdir / "composition.json", "w"), indent=1)
    base = json.load(open(MAPS / "styles" / "premium_biomes_hyrule.json")); base["name"] = "premium_biomes_auto"; base["biomes"] = palette["biomes"]
    import importlib.util
    spec = importlib.util.spec_from_file_location("lb_decor", MAPS / "decor.py"); dec = importlib.util.module_from_spec(spec); spec.loader.exec_module(dec)       # the title font of the maps generator
    ok = bool(title) and all(ch in dec.FONT for ch in title.upper())
    if ok: base["title"]["text"] = title.upper()
    else: base.pop("title", None)
    json.dump(base, open(outdir / "style.json", "w"), indent=1)
    return dict(corners=[[round(x, 1), round(y, 1)] for x, y in cor], board=cinfo, grid_studs=[R, C], size_mm=[(C + 2 * frame_studs) * 8, (R + 2 * frame_studs) * 8], clusters=labels, biome_share=palette["share"], title_used=title.upper() if ok else None)
