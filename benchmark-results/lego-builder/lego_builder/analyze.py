"""Source analysis : nature, probable construction type, views, resolution, perspective, subject/background, dominant colours, depth needs, uncertainties. Heuristics are explicit and every decision lists its evidence ;
a wrong guess is corrected with --type. Nothing here claims a 3D geometry that is not observable."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
from .manifest import sha256
IMG = {".jpg", ".jpeg", ".png", ".webp"}
def analyse_glb(p):
    import trimesh
    sc = trimesh.load(str(p), force="scene"); geoms = list(sc.geometry.values()); ext = sc.bounds[1] - sc.bounds[0]; faces = sum(len(g.faces) for g in geoms)
    mats = {type(getattr(g.visual, "material", None)).__name__ for g in geoms}; vc = any(getattr(g.visual, "kind", "") == "vertex" for g in geoms); tex = any(getattr(g.visual, "kind", "") == "texture" for g in geoms)
    wt = all(g.is_watertight for g in geoms) if geoms else False; ev = []; unc = []
    up = int(np.argmax(ext)); ev.append("GLB mesh : %d geometries, %d faces, extents %s (units unknown)" % (len(geoms), faces, [round(float(x), 3) for x in ext]))
    ev.append("colour source : %s" % ("texture" if tex else "vertex colours" if vc else "none found"))
    if not (tex or vc): unc.append("no colour information in the GLB : colours cannot be reproduced")
    if not wt: unc.append("mesh is not watertight : the volume is filled by the voxeliser (check internal cavities)")
    return dict(kind="glb", construction_type="sculpture_3d", confidence=0.95, evidence=ev, alternatives=[], uncertainties=unc, faces=int(faces), extents=[float(x) for x in ext], watertight=bool(wt), colour_source="texture" if tex else "vertex" if vc else "none", longest_axis=["x", "y", "z"][up])
def analyse_image(p):
    im = Image.open(p); W, H = im.size; alpha = im.mode in ("RGBA", "LA") and np.asarray(im.convert("RGBA"))[..., 3].min() < 250; rgb = im.convert("RGB"); s = 256 / max(W, H); small = rgb.resize((max(8, int(W * s)), max(8, int(H * s))))
    a = np.asarray(small).astype(float) / 255; hsv = np.asarray(small.convert("HSV")).astype(float) * np.array([360 / 255, 1 / 255, 1 / 255]); h, w, _ = a.shape; ev = []; unc = []
    b = max(2, h // 20); border = np.concatenate([a[:b].reshape(-1, 3), a[-b:].reshape(-1, 3), a[:, :b].reshape(-1, 3), a[:, -b:].reshape(-1, 3)]); bstd = float(border.std(0).mean()); bmean = border.mean(0)
    cen = a[h // 4: 3 * h // 4, w // 4: 3 * w // 4].reshape(-1, 3); cdist = float(np.linalg.norm(cen.mean(0) - bmean))
    water = float(((hsv[..., 0] > 185) & (hsv[..., 0] < 250) & (hsv[..., 1] > 0.12) & (hsv[..., 2] > 0.25)).mean()); green = float(((hsv[..., 0] > 75) & (hsv[..., 0] < 170) & (hsv[..., 1] > 0.3)).mean())
    snow = float(((hsv[..., 1] < 0.10) & (hsv[..., 2] > 0.72)).mean()); sand = float(((hsv[..., 0] > 28) & (hsv[..., 0] < 62) & (hsv[..., 1] > 0.10) & (hsv[..., 2] > 0.62)).mean())
    classes = sum(x > 0.04 for x in (water, green, snow, sand)); q = (a * 7).astype(int); keys = q[..., 0] * 64 + q[..., 1] * 8 + q[..., 2]; counts = np.bincount(keys.ravel(), minlength=512); ncol = int((counts > 0.002 * keys.size).sum())
    dark = (hsv[..., 2] < 0.25); framed = float(np.median(np.concatenate([hsv[:b, :, 2].ravel(), hsv[-b:, :, 2].ravel()]))) < 0.35 and float(dark.mean()) > 0.15
    ev.append("%dx%d px, %s%s" % (W, H, im.mode, ", transparent background" if alpha else "")); ev.append("border uniformity (colour std) %.3f ; subject/background contrast %.2f" % (bstd, cdist))
    ev.append("land-cover colours : water %.0f %%, vegetation %.0f %%, snow-like %.0f %%, sand-like %.0f %% (%d classes > 4 %%)" % (100 * water, 100 * green, 100 * snow, 100 * sand, classes)); ev.append("%d dominant colours" % ncol); ev.append("dark frame around a brighter board : %s" % ("yes" if framed else "no"))
    obj = (2.0 if alpha else 0) + (1.5 if (bstd < 0.06 and cdist > 0.12 and classes < 3) else 0); mp = (1.5 if classes >= 3 else 0) + (1.0 if water > 0.04 and (green > 0.04 or sand > 0.04 or snow > 0.04) else 0) + (0.5 if framed else 0) - (1.0 if bstd < 0.04 and classes < 3 else 0)
    mos = (1.5 if max(W, H) <= 160 else 0) + (1.5 if ncol <= 14 and classes < 3 else 0)
    sc = {"map_relief_25d": mp, "sculpture_3d": obj, "mosaic_2d": mos}; order = sorted(sc, key=lambda k: -sc[k]); top, second = order[0], order[1]; margin = sc[top] - sc[second]
    if sc[top] < 1.0 or margin < 0.4: ctype = "undetermined"; unc.append("the type of construction is uncertain (scores %s) : give --type map|sculpture|mosaic" % {k: round(v, 2) for k, v in sc.items()})
    else: ctype = top
    if ctype == "sculpture_3d": unc.append("a single photograph does not give the 3D geometry : multiple views, a 3D model (GLB) or a reconstruction service is needed ; hidden volumes would be estimated")
    if ctype == "map_relief_25d":
        unc.append("relief is ESTIMATED from terrain classes (no altitude data) unless a height source is supplied")
        if framed: unc.append("oblique view of a board : perspective is rectified from the detected quadrilateral ; true proportions are assumed square")
    return dict(kind="image", construction_type=ctype, confidence=round(min(0.99, 0.5 + 0.15 * margin), 2), scores={k: round(v, 2) for k, v in sc.items()}, evidence=ev, alternatives=[k for k in order[1:] if sc[k] > 0], uncertainties=unc,
                size_px=[W, H], has_alpha=bool(alpha), framed_board=bool(framed), land_cover=dict(water=round(water, 3), vegetation=round(green, 3), snow=round(snow, 3), sand=round(sand, 3)), dominant_colours=ncol)
def analyse(path):
    p = Path(path); ext = p.suffix.lower()
    if ext in (".glb", ".gltf"): r = analyse_glb(p)
    elif ext in IMG: r = analyse_image(p)
    elif ext in (".svg",): r = dict(kind="svg", construction_type="undetermined", confidence=0.3, evidence=["SVG vector file"], alternatives=[], uncertainties=["SVG is not rasterised by this version : convert to PNG"])
    else: r = dict(kind="unknown", construction_type="undetermined", confidence=0.0, evidence=["unsupported extension %s" % ext], alternatives=[], uncertainties=["unsupported file"])
    r["sha256"] = sha256(p); r["file"] = p.name; return r
