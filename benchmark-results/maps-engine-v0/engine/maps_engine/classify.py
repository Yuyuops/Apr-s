"""Image -> semantic class map. Generic : colours are grouped by clustering, then labelled by colour FAMILY (hue / lightness) and by shape (border contact, thinness, size, enclosure).
No hex value of any test map appears here."""
import colorsys
import numpy as np
from PIL import Image
from scipy import ndimage
from .common import lab

MIN_PX = 100          # a colour must cover at least this many pixels (of 512 x 512) to be a seed : keeps a 1-stud village marker, drops anti-aliasing
MERGE_DE = 8.0        # seeds closer than this (Lab) are one colour
THIN_PX_PER_CELL = 1.0  # a class whose widest part is narrower than one cell is a "thin" class (river, road)

def load(path, size=512):
    return np.asarray(Image.open(path).convert("RGB").resize((size, size), Image.Resampling.LANCZOS if Image.open(path).size[0] > size else Image.Resampling.NEAREST))

def seeds(img):
    q = (img >> 3).reshape(-1, 3); key = q[:, 0].astype(int) * 1024 + q[:, 1] * 32 + q[:, 2]
    vals, inv, cnt = np.unique(key, return_inverse=True, return_counts=True); flat = img.reshape(-1, 3).astype(float)
    mean = np.stack([np.bincount(inv, flat[:, i]) / cnt for i in range(3)], 1)
    keep = np.where(cnt >= MIN_PX)[0]; order = keep[np.argsort(-cnt[keep])]; S = []   # [colour, count]
    for i in order:
        for s in S:
            if np.linalg.norm(lab(s[0]) - lab(mean[i])) < MERGE_DE: s[0] = (s[0] * s[1] + mean[i] * cnt[i]) / (s[1] + cnt[i]); s[1] += cnt[i]; break
        else: S.append([mean[i].copy(), int(cnt[i])])
    return np.array([s[0] for s in S])

def family(rgb):
    h, s, v = colorsys.rgb_to_hsv(*(np.asarray(rgb) / 255.0)); h *= 360
    if s < 0.12: return "gris"
    if 185 <= h <= 265: return "bleu"
    if 70 <= h < 185: return "vert"
    if h < 16 or h >= 335: return "rouge"
    if 16 <= h < 70: return "chaud"
    return "autre"

def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]; return x * x + y * y <= r * r

def segment(img, cell_px):
    """clusters -> parts. A part is the 'body' (what survives an opening of one cell) or the 'thin' remainder (rivers, roads : narrower than a cell) of a colour cluster."""
    S = seeds(img); L = lab(img.reshape(-1, 3)); d = np.linalg.norm(L[:, None, :] - lab(S)[None, :, :], axis=2); lab_id = d.argmin(1).reshape(img.shape[:2])
    h, w = lab_id.shape; border = np.zeros((h, w), bool); border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
    parts = []; part_id = -np.ones((h, w), int); se = disk(max(2, cell_px // 2))
    for k in range(len(S)):
        m = lab_id == k; body = ndimage.binary_opening(m, structure=se); rest = m & ~ndimage.binary_dilation(body, iterations=2)
        for kind, mk in (("body", body), ("thin", rest)):
            cc, nc = ndimage.label(mk)
            for c in range(1, nc + 1):
                mc = cc == c; a = int(mc.sum())
                if a < (60 if kind == "thin" else MIN_PX // 2): continue
                dt = ndimage.distance_transform_edt(mc); pid = len(parts); part_id[mc] = pid
                parts.append(dict(id=pid, cluster=k, kind=kind, rgb=S[k], area=a, width=float(2 * dt.max()), border=bool((mc & border).any()), family=family(S[k]), L=float(lab(S[k])[0]), mask=mc))
    return lab_id, parts, part_id

def label(lab_id, parts, cell_px):
    """semantic name of every part"""
    names = {}; big = lambda p: p["area"] > 3 * cell_px * cell_px
    bodies = [p for p in parts if p["kind"] == "body"]
    for p in parts:
        f = p["family"]
        if f == "bleu": names[p["id"]] = "riviere" if p["kind"] == "thin" else ("mer" if p["border"] else "lac")
        elif f == "vert": names[p["id"]] = "foret"
        elif f == "rouge": names[p["id"]] = "village" if p["area"] < 12 * cell_px * cell_px else "autre"
    warm = [p for p in parts if p["family"] == "chaud"]
    wc = {}
    for p in warm: wc[p["cluster"]] = wc.get(p["cluster"], 0) + (p["area"] if p["kind"] == "body" else 0)
    land_cluster = max(wc, key=wc.get) if wc else None
    thick_clusters = sorted([k for k in wc if k != land_cluster and wc[k] > 0], key=lambda k: -wc[k])
    hill = thick_clusters[0] if thick_clusters else None
    for p in warm:
        if p["cluster"] == land_cluster: names[p["id"]] = "terre"
        elif p["kind"] == "thin": names[p["id"]] = "route"
        elif p["cluster"] == hill: names[p["id"]] = "colline"
        else:
            m = p["mask"]; ring = ndimage.binary_dilation(m, iterations=8) & ~ndimage.binary_dilation(m, iterations=2)
            hm = np.isin(part_id_global[0], [q["id"] for q in parts if q["cluster"] == hill and q["kind"] == "body"]) if hill is not None else np.zeros_like(m)
            share = float(hm[ring].mean()) if ring.any() else 0.0
            hl = next(q["L"] for q in parts if q["cluster"] == hill) if hill is not None else 0
            names[p["id"]] = "sommet" if share >= 0.5 and p["L"] > hl else "autre"
    for p in parts: names.setdefault(p["id"], "autre")
    return names

part_id_global = [None]

def cell_grid(sem, names_list, n=32, thin_threshold=0.2):
    """majority vote per cell ; thin classes (narrower than a cell) and point features win as soon as `thin_threshold` of the cell is theirs ; thin features are then made connected"""
    cell = sem.shape[0] // n; cls = sorted(set(names_list)); ncls = len(cls)
    frac = np.zeros((n, n, ncls))
    for i, nm in enumerate(cls):
        frac[:, :, i] = (sem == i).reshape(n, cell, n, cell).mean(axis=(1, 3))
    grid = frac.argmax(2)
    prio = [cls.index(nm) for nm in cls if nm in ("riviere", "route", "village")]
    for ci in prio:
        sel = frac[:, :, ci] >= thin_threshold; grid[sel] = ci
        if cls[ci] == "village":                                               # a point feature never disappears
            if not (grid == ci).any() and (frac[:, :, ci] > 0).any(): a = np.unravel_index(frac[:, :, ci].argmax(), (n, n)); grid[a] = ci
    # connectivity of thin classes : two thin parts that are one object at pixel level must stay one object at cell level
    for ci in prio:
        nm = cls[ci]
        if nm == "village": continue
        pix = sem == ci; pc, pn = ndimage.label(pix, structure=np.ones((3, 3)))
        for c in range(1, pn + 1):
            cells = np.unique(np.argwhere(pc == c) // cell, axis=0)
            if len(cells) < 2: continue
            sel = np.zeros((n, n), bool); sel[tuple(cells.T)] = True
            sel &= grid == ci; cc, k = ndimage.label(sel, structure=np.ones((3, 3)))
            while k > 1:                                                       # bridge the closest pair of pieces with the cells of the pixel object that are on the way
                best = None
                for a in range(1, k + 1):
                    for b in range(a + 1, k + 1):
                        pa, pb = np.argwhere(cc == a), np.argwhere(cc == b); dd = np.abs(pa[:, None, :] - pb[None, :, :]).max(2); i, j = np.unravel_index(dd.argmin(), dd.shape)
                        if best is None or dd[i, j] < best[0]: best = (dd[i, j], pa[i], pb[j])
                _, p, q = best; steps = max(abs(q[0] - p[0]), abs(q[1] - p[1]))
                for t in range(1, steps):
                    r = np.round(p + (q - p) * t / steps).astype(int); grid[r[0], r[1]] = ci if grid[r[0], r[1]] not in prio else grid[r[0], r[1]]; sel[r[0], r[1]] = True
                cc, k = ndimage.label(sel | (grid == ci) & np.zeros((n, n), bool) | sel, structure=np.ones((3, 3)))
                if k > 1 and best[0] <= 1: break
    return grid, cls, frac

def classify(path, n=32, size=512):
    img = load(path, size); cell_px = size // n
    lab_id, parts, part_id = segment(img, cell_px); part_id_global[0] = part_id; names = label(lab_id, parts, cell_px)
    # pixels not in any part (anti-aliasing, tiny specks) take the class of the nearest part pixel
    idx = ndimage.distance_transform_edt(part_id < 0, return_distances=False, return_indices=True); part_id = part_id[tuple(idx)]
    cls_names = sorted(set(names.values())); sem = np.vectorize(lambda p: cls_names.index(names[p]))(part_id)
    grid, cls, frac = cell_grid(sem, [names[p] for p in range(len(parts))] if False else cls_names, n)
    colour = {nm: img[sem == i].mean(0) for i, nm in enumerate(cls_names)}
    return dict(img=img, sem=sem, parts=[{k: v for k, v in p.items() if k != "mask"} for p in parts], names=names, grid=grid, classes=cls, colour=colour, frac=frac, cell_px=cell_px)
