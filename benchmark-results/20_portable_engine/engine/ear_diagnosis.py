"""Geometric diagnosis of one ear (V12.1) : placement error, shape / thickness difference, or insufficient information. NOTHING is moved.

Same segmentation for both sides : the cells the segmentation labels as the ear (segmentation.npz) select, in the GLB, the surface triangles whose three vertices lie in those cells
(dilated by one cell, any colour), and, in the LEGO model, the parts of the ear sub-assembly (all points) and the points of those parts that lie in the labelled cells and in exposed cells
(what a viewer sees). Both clouds are expressed in mm in the GLB frame.
Measured : centroid, principal axes (PCA : length, width, thickness = 2 sigma and 5-95 % range along the minor axis), unit normal, root (end of the main axis nearest to the head) and tip,
and the contour on the principal plane of the GLB ear (raster 4 mm) : area, IoU as placed, IoU after superposing the centroids (shape alone), and after superposing centroids and axes.
Conclusion rule (stated, not tuned per subject), applied to the `zone` cloud (the part of the module that stands for the ear : dense enough to be compared ; the `visible` cloud is a sparse subset and is
reported only) :
  placement   : the contour IoU improves by >= 0.15 when the centroids are superposed AND the shape difference (|area ratio - 1|, |thickness ratio - 1|) is < 0.25
  shape       : the shape difference is >= 0.25 (area or thickness) whatever the placement
  insufficient: fewer than 300 GLB triangles or fewer than 300 LEGO points on the visible surface, or the two criteria disagree.
usage: ear_diagnosis.py --glb ref_full_frame.glb --ldr model.ldr --grid full400.npz --seg segmentation.npz --details details.json --ear oreille_haute --out out.json"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import argparse, json
import numpy as np, trimesh
from scipy import ndimage
import conn, scope

R4 = 4.0
def pca(A):
    c = A.mean(0); u, s, vt = np.linalg.svd(A - c, full_matrices=False); return c, vt, s / np.sqrt(len(A))
def stats(A, head):
    c, vt, s = pca(A)
    p = (A - c) @ vt.T; t = np.percentile(p[:, 2], [5, 95]); w = np.percentile(p[:, 1], [5, 95]); l = np.percentile(p[:, 0], [2, 98])
    ends = (c + vt[0] * l[0], c + vt[0] * l[1]); near = int(np.argmin([np.linalg.norm(e - head) for e in ends]))
    return dict(centroide=c, axes=vt, longueur=float(l[1] - l[0]), largeur=float(w[1] - w[0]), epaisseur=float(t[1] - t[0]), normale=vt[2], racine=ends[near], pointe=ends[1 - near])
def raster(P2, lo, shape):
    g = np.zeros(shape, bool); ij = np.floor((P2 - lo) / R4).astype(int); ok = (ij >= 0).all(1) & (ij < shape).all(1); g[tuple(ij[ok].T)] = True
    return ndimage.binary_closing(g, iterations=1)
def iou(a, b): return float((a & b).sum() / max(1, (a | b).sum()))
def main():
    ap = argparse.ArgumentParser()
    for k in ("glb", "ldr", "grid", "seg", "details", "ear", "out"): ap.add_argument("--" + k, required=True)
    a = ap.parse_args(); shape = np.load(a.grid)["grid"].shape; scope.SHAPE = tuple(max(s, 8) for s in shape)
    P = scope.read_parts(a.ldr); V = scope.voxelise(P); seg = np.load(a.seg); lab = seg["labels"]; names = {int(k): v for k, v in json.loads(str(seg["names"])).items()}
    lid = [k for k, v in names.items() if v == a.ear][0]; zone = lab == lid; dil = ndimage.binary_dilation(zone, iterations=1)
    mm = np.array([1, -1, -1]) * 0.4
    m = trimesh.load(a.glb, force="mesh", process=False); Vx = np.asarray(m.vertices); L = np.c_[Vx[:, 0] / 0.4, -Vx[:, 1] / 0.4, -Vx[:, 2] / 0.4]
    vc = np.floor(np.c_[L[:, 0] / 20, -L[:, 1] / 8, L[:, 2] / 20]).astype(int); ok = (vc >= 0).all(1) & (vc < lab.shape).all(1)
    inz = np.zeros(len(Vx), bool); inz[ok] = dil[tuple(vc[ok].T)]; fsel = inz[m.faces].all(1)
    sub = trimesh.Trimesh(Vx, m.faces[fsel], process=False); nfaces = int(fsel.sum())
    G = sub.sample(20000, return_index=False) if nfaces else np.zeros((0, 3))
    pts, vis = [], []
    for p in P:
        if not p["sub"] or a.ear not in p["sub"] or p["sub"].endswith("_1"): continue
        q = conn.solid_points(p["num"]) @ p["M"].T + p["o"]; cell = np.floor(np.c_[q[:, 0] / 20, -q[:, 1] / 8, q[:, 2] / 20]).astype(int)
        okc = (cell >= 0).all(1) & (cell < lab.shape).all(1); cell = np.where(okc[:, None], cell, 0)
        iz = okc & zone[tuple(cell.T)]; ex = iz & V["exposed"][tuple(cell.T)]; pts.append(q * mm); vis.append(((q * mm)[iz], (q * mm)[ex]))
    ALL = np.vstack(pts); ZONE = np.vstack([v[0] for v in vis]); VIS = np.vstack([v[1] for v in vis])
    # head reference = centroid of the head cells that touch the ear (the ear root is the end of the main axis nearest to them)
    touch = ndimage.binary_dilation(zone, iterations=2) & ~zone & (lab != 0); hc = np.argwhere(touch); head = np.array([(hc[:, 0] + .5).mean() * 20 * .4, (hc[:, 1] + .5).mean() * 8 * .4, -(hc[:, 2] + .5).mean() * 20 * .4]) if len(hc) else ALL.mean(0)
    res = dict(ear=a.ear, triangles_glb=nfaces, points_lego=dict(tout=int(len(ALL)), zone=int(len(ZONE)), visible=int(len(VIS))))
    if len(G) < 300 or len(VIS) < 300: res["conclusion"] = "information insuffisante"; json.dump(res, open(a.out, "w"), indent=1); print(res); return
    sg = stats(G, head); out = {}
    for nm, A in (("tout", ALL), ("zone", ZONE), ("visible", VIS)):
        sl = stats(A, head); ang = float(np.degrees(np.arccos(min(1, abs(sl["normale"] @ sg["normale"])))))
        # contour on the principal plane of the GLB ear (axes 0 and 1 of the GLB)
        f = lambda X, c0: ((X - c0) @ sg["axes"].T)[:, :2]
        g2 = f(G, sg["centroide"]); l2 = f(A, sg["centroide"]); lo = np.minimum(g2.min(0), l2.min(0)) - 20; hi = np.maximum(g2.max(0), l2.max(0)) + 20; sh = tuple(np.ceil((hi - lo) / R4).astype(int))
        Rg = raster(g2, lo, sh); Rl = raster(l2, lo, sh)                             # as placed
                # axes superposed too : LEGO cloud expressed in its own axes, GLB in its own
        gl = ((G - sg["centroide"]) @ sg["axes"].T)[:, :2]; ll = ((A - sl["centroide"]) @ sl["axes"].T)[:, :2]
        Rg2 = raster(gl, lo, sh); Rl2 = raster(ll, lo, sh)
        out[nm] = dict(ecart_centroide_mm=round(float(np.linalg.norm(sl["centroide"] - sg["centroide"])), 1), ecart_normale_deg=round(ang, 1),
                       ecart_racine_mm=round(float(np.linalg.norm(sl["racine"] - sg["racine"])), 1), ecart_pointe_mm=round(float(np.linalg.norm(sl["pointe"] - sg["pointe"])), 1),
                       longueur_mm=[round(sg["longueur"], 1), round(sl["longueur"], 1)], largeur_mm=[round(sg["largeur"], 1), round(sl["largeur"], 1)], epaisseur_mm=[round(sg["epaisseur"], 1), round(sl["epaisseur"], 1)],
                       rapport_epaisseur=round(sl["epaisseur"] / max(sg["epaisseur"], 1e-6), 2), rapport_longueur=round(sl["longueur"] / sg["longueur"], 2), rapport_largeur=round(sl["largeur"] / sg["largeur"], 2),
                       surface_contour_cm2=[round(float(Rg.sum()) * R4 * R4 / 100, 1), round(float(Rl.sum()) * R4 * R4 / 100, 1)],
                       iou_contour_en_place=round(iou(Rg, Rl), 3), iou_contour_centroides_superposes=round(iou(raster(((G - sg["centroide"]) @ sg["axes"].T)[:, :2], lo, sh), raster(((A - sl["centroide"]) @ sg["axes"].T)[:, :2], lo, sh)), 3),
                       iou_contour_axes_et_centroides_superposes=round(iou(Rg2, Rl2), 3))
    v = out["zone"]; dshape = max(abs(v["surface_contour_cm2"][1] / max(v["surface_contour_cm2"][0], 1e-6) - 1), abs(v["rapport_epaisseur"] - 1))
    gain = v["iou_contour_centroides_superposes"] - v["iou_contour_en_place"]
    if dshape >= 0.25: concl = "difference de forme / d'epaisseur" + (" (le placement n'est pas demontre errone)" if gain < 0.15 else " (et decalage de centre associe)")
    elif gain >= 0.15: concl = "erreur de placement demontree"
    else: concl = "information insuffisante (ni forme ni placement ne se separent)"
    res.update(glb=dict(centroide=np.round(sg["centroide"], 1).tolist(), longueur_mm=round(sg["longueur"], 1), largeur_mm=round(sg["largeur"], 1), epaisseur_mm=round(sg["epaisseur"], 1), normale=np.round(sg["normale"], 3).tolist()),
               mesures=out, critere=dict(ecart_de_forme=round(dshape, 3), gain_iou_par_superposition=round(gain, 3)), conclusion=concl)
    json.dump(res, open(a.out, "w"), indent=1, ensure_ascii=False); print(json.dumps(res["critere"]), concl)
main()
