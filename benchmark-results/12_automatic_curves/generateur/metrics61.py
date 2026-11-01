"""Fidelity metrics of LEGO V6.1, one protocol for every version (V5, V5.1, V6, V6.1 on Paco; V6, V6.1 on the Beagle).

All on the 4 LDU raster of the panel plane, outer face footprints (real solid, joints closed), evaluation region:
  Paco: v >= 52 LDU and outside the skull (pixels whose whole panel slab is in the head grid), the same for all versions;
  Beagle: whole silhouette.
Metrics:
  iou_glb       : IoU with the silhouette extracted from the GLB (contour.py);
  iou_manual    : IoU with the manual V5 outline (Paco only);
  arcs          : for every characteristic arc of the GLB contour (>= 60 LDU), distance from its pixels to the generated
                  contour: mean, max, share within 8 LDU;
  hausdorff     : max distance GLB contour -> generated contour and generated -> GLB contour (LDU).
usage: metrics61.py <out.json>
"""
import json, os, sys
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.expanduser("~/bench/proto/ear12")); sys.path.insert(0, os.path.expanduser("~/bench/proto/ear09"))
import autogen61 as G
A = G.A6; D = A.D
import design_ear as D5

def fp_of(layout, frame="V6"):
    fp = set()
    for (n, r, i, k, role) in layout:
        if frame == "V5": M, o = D5.panel_piece(n, r, i, k, "B")
        else: M, o = D.outer_piece(n, r, int(i), int(k), "P")
        fp |= A.fp4(n, M, o)
    a = np.array(sorted(fp)); lo = a.min(0) - 2; img = np.zeros(tuple(a.max(0) - lo + 3), bool); img[tuple((a - lo).T)] = True
    img = ndimage.binary_closing(img, structure=np.ones((3, 3)), iterations=1)
    return {(int(x + lo[0]), int(y + lo[1])) for x, y in np.argwhere(img)}

def skull_pixels(ia0, ib0, shape):
    d0 = np.load(D.HEAD_NPZ); G0 = d0["grid"]; F0 = d0["fine"]; K0 = int(d0["k"]); NX, NY, NZ = G0.shape
    occ0 = (G0 >= 0) & (F0.reshape(NX, K0, NY, K0, NZ, K0).mean(axis=(1, 3, 5)) >= 0.5)
    inside = set()
    for a in range(ia0 - 15, ia0 + shape[0] + 15):
        for b in range(ib0 - 15, ib0 + shape[1] + 15):
            ok = True
            for zm in (-34, -10, 14):
                w = D.O + D.R_MOD @ np.array([a * 4 + 2.0, -(b * 4 + 2.0), zm]); x, y, z = int(np.floor(w[0] / 20)), int(np.floor(-w[1] / 8)), int(np.floor(w[2] / 20))
                if not (0 <= x < NX and 0 <= y < NY and 0 <= z < NZ and occ0[x, y, z]): ok = False; break
            if ok: inside.add((a, b))
    return inside

def boundary(px):
    return {p for p in px if any((p[0] + dx, p[1] + dy) not in px for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}

def measure(fp, T, segs, region, ref_manual=None):
    inR = lambda p: region(p)
    Tr = {p for p in T if inR(p)}; Fr = {p for p in fp if inR(p)}
    out = dict(iou_glb=round(len(Tr & Fr) / len(Tr | Fr), 4))
    if ref_manual is not None:
        Mr = {p for p in ref_manual if inR(p)}; out["iou_manual_V5"] = round(len(Mr & Fr) / len(Mr | Fr), 4)
    Gb = np.array(sorted(boundary(fp))); Tb = np.array(sorted(boundary(T)))
    from scipy.spatial import cKDTree
    tg, tt = cKDTree(Gb), cKDTree(Tb)
    arcs = []
    for s in segs:
        if not s["characteristic"]: continue
        px = np.array([p for p in s["pixels"] if inR(p)])
        if len(px) == 0: continue
        d, _ = tg.query(px); d = d * 4.0
        # excess around the arc: generated contour pixels within 40 LDU of the arc, distance to the GLB contour
        near = np.array([g for g in Gb if np.min(np.abs(px - g).sum(1)) <= 10 and inR(tuple(g))])
        ex = tt.query(near)[0] * 4.0 if len(near) else np.zeros(1)
        arcs.append(dict(radius_ldu=round(s["radius"]), length_ldu=s["length_ldu"], centre_uv=(px.mean(0) * 4).round().tolist(),
                         mean_ldu=round(float(d.mean()), 1), max_ldu=round(float(d.max()), 1), share_within_8ldu=round(float((d <= 8).mean()), 3),
                         excess_max_ldu=round(float(ex.max()), 1), excess_mean_ldu=round(float(ex.mean()), 1)))
    Tbr = np.array([p for p in map(tuple, Tb) if inR(p)]); Gbr = np.array([p for p in map(tuple, Gb) if inR(p)])
    out["hausdorff_glb_to_gen_ldu"] = round(float(tg.query(Tbr)[0].max() * 4), 1)
    out["hausdorff_gen_to_glb_ldu"] = round(float(tt.query(Gbr)[0].max() * 4), 1)
    out["arcs"] = arcs
    # end caps: the 80 LDU at both ends of the principal axis of the GLB silhouette (generic: free end, hanging end...)
    Ta = np.array(sorted(Tr)); c0 = Ta.mean(0); _, _, vt = np.linalg.svd(Ta - c0, full_matrices=False); ax = vt[0]
    t_T = (Ta - c0) @ ax; tmin, tmax = t_T.min(), t_T.max()
    caps = {}
    for name, sel in (("bout_min", lambda t: t < tmin + 20), ("bout_max", lambda t: t > tmax - 20)):
        inc = lambda p: sel((np.array(p) - c0) @ ax)
        Tc = {p for p in Tr if inc(p)}; Fc = {p for p in Fr if inc(p)}
        tb = [p for p in map(tuple, Tb) if inR(p) and inc(p)]; gb = [p for p in map(tuple, Gb) if inR(p) and inc(p)]
        caps[name] = dict(centre_uv=(np.array(sorted(Tc)).mean(0) * 4).round().tolist() if Tc else None,
                          iou=round(len(Tc & Fc) / max(len(Tc | Fc), 1), 3), ecart_surface_ldu2=int(len(Tc ^ Fc) * 16),
                          ecart_max_ldu=round(float(max(tg.query(np.array(tb))[0].max() if tb else 0, tt.query(np.array(gb))[0].max() if gb else 0) * 4), 1))
    out["extremites"] = caps
    return out

def main():
    out = sys.argv[1]; res = {}
    tdir = os.path.expanduser("~/bench/proto/ear11/targets")
    for tg in ("A_paco", "B_beagle"):
        S = np.load(os.path.join(tdir, f"{tg}_silhouette.npy")); m = json.load(open(os.path.join(tdir, f"{tg}_contour.json")))
        ia0, ib0 = int(round(m["u0"] / 4)), int(round(m["v0"] / 4))
        T = {(ia0 + a, ib0 + b) for a, b in np.argwhere(S)}
        Tm = S.copy()
        if tg == "A_paco":
            Tm[:, :max(0, 13 - ib0)] = False
            inside = skull_pixels(ia0, ib0, S.shape)
            region = lambda p, ins=inside: p[1] * 4 >= 52 and p not in ins
        else:
            region = lambda p: True
        segs = G.arc_segments(Tm, ia0, ib0)
        versions = {}
        if tg == "A_paco":
            versions["V5 manuelle"] = fp_of(D5.LAYER_B, "V5")
            versions["V5.1 manuelle"] = fp_of(D.OUTER)
            versions["V6 automatique"] = fp_of(json.load(open(os.path.expanduser("~/bench/proto/ear11/runA/oreille_A_paco_report.json")))["outer_layout"])
            versions["V6.1 automatique"] = fp_of(json.load(open(os.path.expanduser("~/bench/proto/ear12/runA/oreille_A_paco_report.json")))["outer_layout"])
            ref = versions["V5 manuelle"]
        else:
            versions["V6 automatique"] = fp_of(json.load(open(os.path.expanduser("~/bench/proto/ear11/runB/oreille_B_beagle_report.json")))["outer_layout"])
            versions["V6.1 automatique"] = fp_of(json.load(open(os.path.expanduser("~/bench/proto/ear12/runB/oreille_B_beagle_report.json")))["outer_layout"])
            ref = None
        res[tg] = {k: measure(v, T, segs, region, ref) for k, v in versions.items()}
        res[tg]["_arcs_detectes"] = [dict(radius_ldu=round(s["radius"]), length_ldu=s["length_ldu"]) for s in segs if s["characteristic"]]
    json.dump(res, open(out, "w"), indent=1)
    for tg, r in res.items():
        print(tg)
        for k, v in r.items():
            if k.startswith("_"): print("  arcs:", v); continue
            print("  %-18s ends %s" % (k, {n: (e["iou"], e["ecart_surface_ldu2"], e["ecart_max_ldu"]) for n, e in v["extremites"].items()}))
            print("  %-18s IoU_glb %.3f %s H %5.1f/%5.1f  arcs %s" % (k, v["iou_glb"], ("IoU_V5 %.3f" % v["iou_manual_V5"]) if "iou_manual_V5" in v else "", v["hausdorff_glb_to_gen_ldu"], v["hausdorff_gen_to_glb_ldu"],
                  [(a["radius_ldu"], a["mean_ldu"], a["max_ldu"], a["share_within_8ldu"], a["excess_max_ldu"]) for a in v["arcs"]]))

if __name__ == "__main__":
    main()
