"""Contour extraction and analysis (LEGO V6, automatic contour).

extract_*  : silhouette of an ear of a GLB, projected in the ear plane, as a 5 LDU raster in a panel frame (u, v up).
analyse    : boundary of the silhouette, local slope (PCA over 40 LDU) and curvature radius (circle fit over 60 LDU),
             classification of each boundary pixel as axis-aligned edge, slope (with its dv/du) or arc (with its radius).
The same cleanup is applied to every silhouette: opening of 25 LDU (5 pixels), then the largest connected component.
"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import json, os, sys
import numpy as np
from scipy import ndimage
import trimesh
from PIL import Image, ImageDraw

RES = 4.0

def raster(faces, u, v, res=RES, pad=20):
    u0, v0 = np.floor(u.min() / res) * res - pad, np.floor(v.min() / res) * res - pad
    W = int((u.max() - u0 + pad) / res) + 1; H = int((v.max() - v0 + pad) / res) + 1
    img = Image.new("L", (W, H), 0); dr = ImageDraw.Draw(img)
    for tri in faces: dr.polygon([((u[k] - u0) / res, (v[k] - v0) / res) for k in tri], fill=255)
    S = ndimage.binary_fill_holes(np.array(img).T > 0)
    return S, u0, v0

def cleanup(S, open_px=5):
    S2 = ndimage.binary_opening(S, structure=np.ones((3, 3)), iterations=open_px)
    lab, n = ndimage.label(S2)
    if n == 0: return S
    sz = ndimage.sum(S2, lab, range(1, n + 1)); S3 = lab == (1 + int(np.argmax(sz)))
    return ndimage.binary_closing(S3, iterations=1) & S | S3

def extract_paco():
    """upper ear of Paco in the module frame of V4.1 (same selection as the V5 measurement: dark faces, 2 clusters)"""
    from sklearn.cluster import KMeans
    m = trimesh.load(LEGACY_DATA("proto/ear07/ref_head_frame.glb"), force="mesh", process=False)
    V = m.vertices; C = np.asarray(m.visual.vertex_colors)[:, :3].astype(float)
    L = np.c_[V[:, 0] / 0.4, -V[:, 1] / 0.4, -V[:, 2] / 0.4]
    rep = json.load(open(EAR_FRAME_JSON)); R = np.array(rep["R_mod"]); O = np.array(rep["O"])
    dark = C.mean(1) < 75; f = m.faces[dark[m.faces].all(1)]
    sub = trimesh.Trimesh(L, f, process=False); big = sorted(sub.split(only_watertight=False), key=lambda c: -c.area)[0]
    rel = (big.vertices - O) @ R; u = rel[:, 0]; v = -rel[:, 1]
    cen = np.c_[u[big.faces].mean(1), v[big.faces].mean(1)]
    km = KMeans(2, n_init=10, random_state=0).fit(cen); up = int(np.argmax([cen[km.labels_ == k, 1].mean() for k in range(2)]))
    S, u0, v0 = raster(big.faces[km.labels_ == up], u, v)
    return dict(S=cleanup(S), u0=u0, v0=v0, frame="module V4.1 (u = x module, v = -y module)")

def extract_beagle(side=+1, long_side_studs=20.0):
    """right ear of the Beagle (x > 0): dark brown faces, plane by PCA, v = world up projected in the plane.
    Scale: the largest dimension of the ear is set to long_side_studs studs (the Paco ear is 21.6 studs long)."""
    m = trimesh.load(CTX("source_glb"), force="mesh", process=False)
    V = m.vertices; C = np.asarray(m.visual.vertex_colors)[:, :3].astype(float)
    sel = (V[:, 1] > 0.25) & (C.mean(1) < 90) & (C[:, 0] > C[:, 2] + 10) & (side * V[:, 0] > 0.2)
    f = m.faces[sel[m.faces].all(1)]
    sub = trimesh.Trimesh(V, f, process=False); big = sorted(sub.split(only_watertight=False), key=lambda c: -c.area)[0]
    P = big.vertices; c0 = P.mean(0); _, _, vt = np.linalg.svd(P - c0, full_matrices=False); n = vt[2]
    up = np.array([0, 1.0, 0]); vax = up - n * (up @ n); vax /= np.linalg.norm(vax); uax = np.cross(vax, n)
    if uax[2] < 0: uax = -uax                                  # u towards the front of the dog (+z)
    u = (P - c0) @ uax; v = (P - c0) @ vax
    scale = long_side_studs * 20.0 / max(u.max() - u.min(), v.max() - v.min())
    u = u * scale; v = v * scale
    v = v - v.min() + 52.0; u = u - u.min() - 200.0             # same placement range as the Paco panel (lobe from v = 52)
    S, u0, v0 = raster(big.faces, u, v)
    return dict(S=cleanup(S), u0=u0, v0=v0, frame="plan PCA de l'oreille droite, v = vertical, echelle %.1f LDU par unite GLB" % scale,
                plane_normal=n.round(3).tolist(), scale_ldu_per_unit=float(scale))

def analyse(S, u0, v0, res=RES):
    """local slope and curvature on the boundary; returns per-pixel features and a summary of segments"""
    B = S & ~ndimage.binary_erosion(S)
    pts = (np.argwhere(B) + 0.5) * res + [u0, v0]
    feats = []
    for p in pts:
        d = np.linalg.norm(pts - p, axis=1)
        w = pts[d < 40]
        c = w.mean(0); _, sv, vt = np.linalg.svd(w - c, full_matrices=False); t = vt[0]
        ang = np.degrees(np.arctan2(t[1], t[0])) % 180
        w2 = pts[d < 60]; A = np.c_[2 * w2, np.ones(len(w2))]; bb = (w2 ** 2).sum(1)
        try:
            sol = np.linalg.lstsq(A, bb, rcond=None)[0]; r = float(np.sqrt(sol[2] + sol[0] ** 2 + sol[1] ** 2))
        except Exception: r = 1e9
        straight = sv[1] / max(sv[0], 1e-9) < 0.12
        if straight and (min(ang, 180 - ang) < 8 or abs(ang - 90) < 8): kind = "axe"
        elif straight: kind = "pente"
        else: kind = "arc"
        feats.append(dict(u=float(p[0]), v=float(p[1]), angle=float(ang), radius=r if kind == "arc" else None, kind=kind,
                          slope=float(np.tan(np.radians(ang))) if kind == "pente" else None))
    summ = {}
    for k in ("axe", "pente", "arc"):
        fk = [f for f in feats if f["kind"] == k]
        summ[k] = dict(pixels=len(fk))
        if k == "pente" and fk: summ[k]["pentes_dv_du_quartiles"] = np.round(np.percentile([abs(f["slope"]) for f in fk], [25, 50, 75]), 2).tolist()
        if k == "arc" and fk: summ[k]["rayons_ldu_quartiles"] = np.round(np.percentile([min(f["radius"], 400) for f in fk], [25, 50, 75]), 0).tolist()
    return feats, summ, B

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for name, fn in (("A_paco", extract_paco), ("B_beagle", extract_beagle)):
        d = fn(); S = d.pop("S")
        feats, summ, B = analyse(S, d["u0"], d["v0"])
        np.save(os.path.join(out, f"{name}_silhouette.npy"), S)
        json.dump(dict(d, res=RES, shape=list(S.shape), area_ldu2=float(S.sum() * RES * RES), analyse=summ), open(os.path.join(out, f"{name}_contour.json"), "w"), indent=1)
        print(name, S.shape, summ)
