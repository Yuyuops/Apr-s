"""Semantic preparation of a map picture (Sprint V15) : a reference picture + a structured requirements file -> class raster for the maps generator. No AI model : the classes come from Lab colour PROTOTYPES listed in the
requirements file (calibrated by k-means on the reference itself, then named by the operator), nearest-prototype classification on a smoothed picture, connectivity rules and height bands. Everything is reproducible and data-driven ;
nothing is invented outside the picture (the picture is the only geography source)."""
import json
import numpy as np
from PIL import Image
from scipy import ndimage
_M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]); _W = np.array([0.95047, 1.0, 1.08883])
def rgb2lab(a):
    a = np.asarray(a, float) / 255.0; m = np.where(a > 0.04045, ((a + 0.055) / 1.055) ** 2.4, a / 12.92); xyz = (m @ _M.T) / _W
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116); return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)
def classify(rgb, prototypes, smooth=9):
    """nearest Lab prototype on a box-smoothed picture (the LEGO texture - studs, joints, 1x1 details - is averaged out). -> int array of prototype indices"""
    lab = rgb2lab(rgb); sm = np.stack([ndimage.uniform_filter(lab[..., i], smooth) for i in range(3)], -1); P = np.array([p["lab"] for p in prototypes], float)
    return ((sm[..., None, :] - P) ** 2).sum(-1).argmin(-1)
def to_classes(idx, prototypes, names):
    """prototype index -> class code (index in `names`)"""
    lut = np.array([names.index(p["class"]) for p in prototypes]); return lut[idx]
def mode_filter(codes, n, size):
    cnt = np.stack([ndimage.uniform_filter((codes == k).astype(np.float32), size) for k in range(n)], -1); return cnt.argmax(-1)
def void_vs_crater(codes, names, min_crater_cells, border=3, ring_classes=("mesa", "rust"), ring_share=0.5, max_craters=2):
    """'void' components that touch the picture border stay void. An enclosed dark component becomes 'crater' only if it is large enough AND ringed mostly by `ring_classes` (a crater sits in a volcanic massif) ; the biggest
    `max_craters` qualify ; every other dark spot (shadows, towers, cliff shadows) takes the majority of its ring."""
    v, cr = names.index("void"), names.index("crater"); rc = [names.index(c) for c in ring_classes]; lab, n = ndimage.label(codes == v); out = codes.copy(); cand = []
    for j in range(1, n + 1):
        m = lab == j; ys, xs = np.where(m); touch = ys.min() < border or xs.min() < border or ys.max() >= codes.shape[0] - border or xs.max() >= codes.shape[1] - border
        if touch: continue
        ring = ndimage.binary_dilation(m, iterations=3) & ~m; share = float(np.isin(codes[ring], rc).mean()) if ring.any() else 0.0
        bw, bh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1; compact = m.sum() / (bw * bh) >= 0.5 and max(bw, bh) / min(bw, bh) <= 2.0          # a crater is a compact blob, not a shadow stripe
        if m.sum() >= min_crater_cells and share >= ring_share and compact: cand.append((int(m.sum()), j))
        else:
            vals = codes[ndimage.binary_dilation(m, iterations=2) & ~m]; vals = vals[vals != v]
            if len(vals): out[m] = np.bincount(vals).argmax()
    for _, j in sorted(cand, reverse=True)[:max_craters]: out[lab == j] = cr
    for _, j in sorted(cand, reverse=True)[max_craters:]:
        m = lab == j; vals = codes[ndimage.binary_dilation(m, iterations=2) & ~m]; vals = vals[vals != v]; out[m] = np.bincount(vals).argmax() if len(vals) else codes[m][0]
    return out
def remove_small(codes, n, min_cells):
    out = codes.copy()
    for k in range(n):
        lab, c = ndimage.label(out == k)
        if c == 0: continue
        sz = ndimage.sum(out == k, lab, range(1, c + 1)); small = np.isin(lab, [i + 1 for i, s in enumerate(sz) if s < min_cells])
        if small.any():
            sc = np.stack([ndimage.uniform_filter((out == j).astype(np.float32), 5) if j != k else np.full(out.shape, -1, np.float32) for j in range(n)], -1); out = np.where(small, sc.argmax(-1), out)
    return out
def to_grid(codes, shape):
    """majority downsample (class codes) to the stud grid"""
    R, C = shape; H, W = codes.shape; n = int(codes.max()) + 1; ys = (np.arange(H) * R // H); xs = (np.arange(W) * C // W); cnt = np.zeros((R, C, n), np.int32)
    for k in range(n): cnt[..., k] = ndimage.sum(codes == k, labels=None) * 0 if False else np.bincount((ys[:, None] * C + xs[None, :])[codes == k], minlength=R * C).reshape(R, C)
    return cnt.argmax(-1)
def landmarks(codes, names, family, top=1, min_frac=0.0005):
    """centroid (x, y normalised to width/height) of the `top` largest components of the classes in `family`"""
    m = np.isin(codes, [names.index(c) for c in family]); lab, n = ndimage.label(m); out = []
    if n == 0: return out
    sz = ndimage.sum(m, lab, range(1, n + 1)); H, W = codes.shape
    for j in np.argsort(-sz)[:top]:
        if sz[j] < min_frac * H * W: continue
        cy, cx = ndimage.center_of_mass(lab == j + 1); out.append(dict(x=round(float(cx / W), 4), y=round(float(cy / H), 4), area_frac=round(float(sz[j] / (H * W)), 4)))
    return out
