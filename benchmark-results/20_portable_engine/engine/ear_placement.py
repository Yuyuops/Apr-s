"""Placement of the ear modules against the GLB with COMPARABLE surfaces (V12).

V11 compared the dark cloud of the GLB (visible surface) with ALL the points of the ear module (including the fixation plates buried in the head) : its centre error was an upper bound.
Here three LEGO clouds are compared with the same GLB cloud, on the same definitions of centre :
  all     : every point of the sub-assembly (fixation block included)                                     (V11 definition)
  zone    : the points of the sub-assembly that lie in the cells labelled as this ear by the segmentation   (the part of the module that stands for the ear)
  visible : the points of `zone` that belong to EXPOSED cells (the part a viewer sees)                      (comparable with the GLB surface)
Definitions of the centre : centroid, centre of the bounding box, tip (the point farthest from the sagittal plane along the ear), plus the vertical offset between the two ears (denivele)
and the normal of the principal plane. The ears are never made symmetric : the source is not.
usage: ear_placement.py --glb ref_full_frame.glb --ldr model.ldr --grid full400.npz --seg segmentation.npz --details details.json --out out.json"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import argparse, json, os
import numpy as np
import trimesh
import conn, scope

def cloud_stats(A, n, off):
    c = A.mean(0); bb = (A.min(0) + A.max(0)) / 2; d = A @ n - off; tip = A[int(np.argmax(np.abs(d)))]
    u, s, vt = np.linalg.svd(A - c, full_matrices=False)
    return dict(centroide=c, centre_boite=bb, pointe=tip, normale=vt[2], hauteur_centroide=float(c[1]), hauteur_pointe=float(tip[1]))

def run(glb, ldr, grid_npz, seg_npz, details_json, out):
    shape = np.load(grid_npz)["grid"].shape; scope.SHAPE = tuple(max(s, 8) for s in shape)
    P = scope.read_parts(ldr); V = scope.voxelise(P); seg = np.load(seg_npz); labels = seg["labels"]; names = {int(k): v for k, v in json.loads(str(seg["names"])).items()}
    det = json.load(open(details_json))["repere"]; n = np.array(det["normale_plan_sagittal"], float); off = float(det["plan_offset_mm"])
    m = trimesh.load(glb, force="mesh", process=False); Vx = np.asarray(m.vertices); col = np.asarray(m.visual.vertex_colors)[:, :3].astype(float)
    L = np.c_[Vx[:, 0] / 0.4, -Vx[:, 1] / 0.4, -Vx[:, 2] / 0.4]; mm = np.array([1, -1, -1]) * 0.4
    res = {}
    for s in sorted({p["sub"] for p in P if p["sub"] and "oreille" in p["sub"] and not p["sub"].endswith("_1")}):
        lid = [k for k, v in names.items() if v == s.replace("V7_", "")]
        if not lid: continue
        zc = np.argwhere(labels == lid[0]); lo, hi = zc.min(0) - 1, zc.max(0) + 2
        box = np.c_[lo * [20, -8, 20], hi * [20, -8, 20]]; lo_l = np.minimum(box[:, 0], box[:, 1]); hi_l = np.maximum(box[:, 0], box[:, 1])
        gsel = (col.mean(1) < 80) & np.all((L >= lo_l) & (L <= hi_l), axis=1); G = L[gsel] * mm                                   # GLB definition 1 : dark vertices of the ear box (V11)
        from scipy import ndimage
        dil = ndimage.binary_dilation(labels == lid[0], iterations=1); vc = np.floor(np.c_[L[:, 0] / 20, -L[:, 1] / 8, L[:, 2] / 20]).astype(int); okv = (vc >= 0).all(1) & (vc < labels.shape).all(1)
        G2 = L[okv & dil[tuple(np.where(okv[:, None], vc, 0).T)]] * mm                                                           # GLB definition 2 : every vertex of the cells the segmentation labels as this ear (any colour)
        pts, inzone, exposed = [], [], []
        for p in P:
            if p["sub"] != s: continue
            q = conn.solid_points(p["num"]) @ p["M"].T + p["o"]; cell = np.floor(np.c_[q[:, 0] / 20, -q[:, 1] / 8, q[:, 2] / 20]).astype(int)
            ok = (cell >= 0).all(1) & (cell < labels.shape).all(1); cell = np.where(ok[:, None], cell, 0)
            iz = ok & (labels[tuple(cell.T)] == lid[0]); ex = ok & V["exposed"][tuple(np.minimum(cell, np.array(V["exposed"].shape) - 1).T)] if V["exposed"].shape == labels.shape else ok
            pts.append(q); inzone.append(iz); exposed.append(ex)
        Q = np.vstack(pts) * mm; IZ = np.concatenate(inzone); EX = np.concatenate(exposed)
        clouds = {"all": Q, "zone": Q[IZ], "visible": Q[IZ & EX]}
        r = dict(points_glb=int(len(G)), points_lego={k: int(len(v)) for k, v in clouds.items()})
        gs = cloud_stats(G, n, off); gs2 = cloud_stats(G2, n, off) if len(G2) > 30 else None
        r["glb_cellules_etiquetees"] = None if gs2 is None else dict(points=int(len(G2)), centroide=np.round(gs2["centroide"], 1).tolist(), hauteur_centroide=round(gs2["hauteur_centroide"], 1))
        r["glb"] = {k: (np.round(v, 1).tolist() if isinstance(v, np.ndarray) else round(v, 1)) for k, v in gs.items()}
        for k, A in clouds.items():
            if len(A) < 30: r[k] = "trop peu de points"; continue
            cs = cloud_stats(A, n, off)
            r[k] = dict(ecart_centroide_mm=round(float(np.linalg.norm(cs["centroide"] - gs["centroide"])), 1), ecart_centre_boite_mm=round(float(np.linalg.norm(cs["centre_boite"] - gs["centre_boite"])), 1),
                        ecart_pointe_mm=round(float(np.linalg.norm(cs["pointe"] - gs["pointe"])), 1), ecart_normale_deg=round(float(np.degrees(np.arccos(min(1.0, abs(cs["normale"] @ gs["normale"]))))), 1),
                        hauteur_centroide_mm=round(cs["hauteur_centroide"], 1), hauteur_pointe_mm=round(cs["hauteur_pointe"], 1),
                        ecart_centroide_vs_glb_cellules_mm=None if gs2 is None else round(float(np.linalg.norm(cs["centroide"] - gs2["centroide"])), 1))
        res[s] = r
    if len(res) == 2:
        a, b = list(res.values()); den = {}
        for key in ("centroide", "pointe"):
            hg = abs(a["glb"]["hauteur_" + key] - b["glb"]["hauteur_" + key])
            for k in ("all", "zone", "visible"):
                if isinstance(a[k], dict) and isinstance(b[k], dict): den["%s_%s" % (k, key)] = dict(glb_mm=round(hg, 1), lego_mm=round(abs(a[k]["hauteur_" + key + "_mm"] - b[k]["hauteur_" + key + "_mm"]), 1))
        res["denivele_entre_les_deux_oreilles"] = den
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False); return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for k in ("glb", "ldr", "grid", "seg", "details", "out"): ap.add_argument("--" + k, required=True)
    a = ap.parse_args(); r = run(a.glb, a.ldr, a.grid, a.seg, a.details, a.out); print(json.dumps(r.get("denivele_entre_les_deux_oreilles", {}), ensure_ascii=False))
