"""LEGO V7 - phase 3: first complete automatic sculpture of Paco (400 mm).

Reuses, unchanged: brickify_plus (volume, prototype-C settings), the V6.1 contour generator (autogen61 selection on
the V6 generator), its automatic turned-plate fixation search, conn/partlib geometry, validate_v3, reorder_notice.
Adapters (this file):
  * whole-character grid (fullgrid.py) instead of the head crop; the head frame of V4.1 is moved by the head offset;
  * both ears removed from the volume with the V4.1 rule (ear cells, their black skin, the floating core);
  * protection mask = eyes, mouth and nose zones of the automatic segmentation (segment.py);
  * one frame per ear: same 3-4-5 rotation (both ear planes are parallel: normals 0.80/-0.60 and 0.78/-0.62), the
    origin moved down by a whole number of plates so that the ear's lowest point is at v ~ 52 (generator convention);
  * one carving of the whole grid for both ears, one brickify_plus rebuild, seats of every turned plate;
  * colour rule for a turned plate that reaches the surface: the colour of the surface it replaces, and tiles of that
    colour on its studs left free (hides the plate; no new part type, no fragile part).
usage: integrate.py <outdir>
"""
import json, os, pickle, subprocess, sys
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.expanduser("~/bench/tools")); sys.path.insert(0, os.path.expanduser("~/bench/proto"))
sys.path.insert(0, os.path.expanduser("~/bench/proto/ear11")); sys.path.insert(0, os.path.expanduser("~/bench/proto/ear12"))
import conn, partlib as PL
import autogen as A6
import autogen61 as G61
import contour as CT
D = A6.D
BLACK = 0
FULL = os.path.expanduser("~/bench/proto/v7/paco_full400.npz")
SEG = os.path.expanduser("~/bench/proto/v7/segmentation.npz")
REP41 = json.load(open(os.path.expanduser("~/bench/proto/ear08/run/module_report.json")))
R_MOD = np.array(REP41["R_mod"]); O_HEAD = np.array(REP41["O"])

def prepare(out):
    d = np.load(FULL); G = d["grid"].astype(int); F = d["fine"]; K = int(d["k"]); NX, NY, NZ = G.shape
    hif = d["head_in_full"]; delta = np.array([20.0 * hif[0], -8.0 * hif[1], 20.0 * hif[2]])
    fr = F.reshape(NX, K, NY, K, NZ, K).mean(axis=(1, 3, 5)); occ = (G >= 0) & (fr >= 0.5)
    s = np.load(SEG); lab = s["labels"]; names = {int(k): v for k, v in json.loads(str(s["names"])).items()}
    idx = {v: k for k, v in names.items()}
    ears = np.isin(lab, [idx["oreille_haute"], idx["oreille_basse"]])
    # V4.1 removal rule: ear cells, the black skin connected to them, then the yellow core left floating near them
    black = (G == BLACK); black[:, :hif[1], :] = False
    lb, _ = ndimage.label(black, structure=np.ones((3, 3, 3)))
    skin = np.isin(lb, np.unique(lb[ears])) & (lb > 0) & ndimage.binary_dilation(ears, iterations=1)
    G2 = G.copy(); G2[skin | ears] = -1
    occ2 = (G2 >= 0) & (fr >= 0.5); l3, n3 = ndimage.label(occ2)
    sz = ndimage.sum(occ2, l3, range(1, n3 + 1)); main = 1 + int(np.argmax(sz))
    core = occ2 & (l3 != main) & ndimage.binary_dilation(skin | ears, iterations=3)
    G2[core] = -1
    protect = np.isin(lab, [idx[n] for n in ("yeux", "bouche", "truffe") if n in idx])
    npz2 = os.path.join(out, "paco_full_sans_oreilles.npz")
    np.savez_compressed(npz2, grid=G2, surface=d["surface"], fine=F, k=K, neck=d["neck"], full_shape=d["full_shape"], hoff=d["hoff"],
                        head_in_full=hif, protect=protect)
    return npz2, delta, dict(ear_cells=int(ears.sum()), skin_cells=int(skin.sum()), core_cells=int(core.sum()), protect_cells=int(protect.sum()))

def lower_target(O_full, name):
    """silhouette of the lower ear (lower k-means cluster of the dark ear faces) in its frame, from the WHOLE GLB placed
    in the LEGO frame (ref_glb_fullframe.py): the head-only GLB of the earlier iterations is cut at the neck"""
    import trimesh
    from sklearn.cluster import KMeans
    m = trimesh.load(os.path.expanduser("~/bench/proto/v7/ref_full_frame.glb"), force="mesh", process=False)
    V = m.vertices; C = np.asarray(m.visual.vertex_colors)[:, :3].astype(float)
    L = np.c_[V[:, 0] / 0.4, -V[:, 1] / 0.4, -V[:, 2] / 0.4]
    dark = C.mean(1) < 75; f = m.faces[dark[m.faces].all(1)]
    sub = trimesh.Trimesh(L, f, process=False); big = sorted(sub.split(only_watertight=False), key=lambda c: -c.area)[0]
    rel = (big.vertices - O_full) @ R_MOD; u = rel[:, 0]; v = -rel[:, 1]
    cen = np.c_[u[big.faces].mean(1), v[big.faces].mean(1)]
    km = KMeans(2, n_init=10, random_state=0).fit(cen); lo = int(np.argmin([cen[km.labels_ == k, 1].mean() for k in range(2)]))
    S, u0, v0 = CT.raster(big.faces[km.labels_ == lo], u, v)
    S = CT.cleanup(S)
    tdir = os.path.join(os.path.dirname(A6.__file__), "targets")
    np.save(os.path.join(tdir, f"{name}_silhouette.npy"), S)
    feats, summ, _ = CT.analyse(S, u0, v0)
    json.dump(dict(u0=u0, v0=v0, res=CT.RES, shape=list(S.shape), frame="V7 oreille basse (repere V4.1 abaisse), GLB complet", analyse=summ),
              open(os.path.join(tdir, f"{name}_contour.json"), "w"), indent=1)
    return S

def find_fixation_v7(occ, E, R, O, lobe_cells):
    """joint search (V7): every valid primary plate (levels 48 + 40 n), each with its best secondary plate (rules of
    V6: rests on the block plate or sits on a core course, seats >= 30 LDU from the core row (tier 1, hidden) or
    >= 20 LDU with <= 6 visible cells (tier 2)). Ranking: two paths first, then hidden secondary, then total studs."""
    V0 = A6.V0
    sizes = [(6, 4, "3032"), (4, 4, "3031"), (8, 4, "3035"), (6, 2, "3795"), (4, 2, "3020"), (8, 2, "3034")]
    imax = max(i for i, k in lobe_cells)
    P1s = []
    for (w, l, num) in sizes:
        for xm0 in range(0, 341, 20):
            for zm0 in range(-20 * l, 1, 20):
                if not (zm0 <= -20 and zm0 + 20 * l >= 0) or xm0 > 20 * (imax + 3): continue
                for L in A6.P1_LEVELS:
                    if L > 48 and not any(xm0 - 40 <= 20 * i < xm0 + 20 * w and L - 20 <= V0 + 20 * k <= L + 40 for (i, k) in lobe_cells): continue
                    coin, expo, bad = A6.plate_seats(occ, E, R, O, xm0, zm0, w, l, L)
                    if bad or expo or len(coin) < 2: continue
                    P1s.append(dict(num=num, w=w, l=l, xm0=xm0, zm0=zm0, vp=L, coin=coin))
    P1s.sort(key=lambda p: (-len(p["coin"]), p["xm0"]))
    best = None
    for P1 in P1s[:25]:
        inP1 = lambda xm, zm: P1["xm0"] <= xm < P1["xm0"] + 20 * P1["w"] and P1["zm0"] <= zm < P1["zm0"] + 20 * P1["l"]
        b2 = None
        for tier, marg, max_expo in ((1, 30, 1), (2, 20, 6)):
            nb = lambda xm, zm, m=marg: ((P1["xm0"] - 20 <= xm < P1["xm0"] + 20 * P1["w"] + 20 and P1["zm0"] - 20 <= zm < P1["zm0"] + 20 * P1["l"] + 20) or abs(zm + 10) < m)
            for vp2 in (P1["vp"] + 40, P1["vp"] + 80):
                for (w, l, num) in sizes:
                    for xm0 in range(P1["xm0"] - 120, P1["xm0"] + 20 * P1["w"] + 61, 20):
                        for zm0 in range(-20 * l, 1, 20):
                            if not (zm0 <= -20 and zm0 + 20 * l >= 0): continue
                            over = sum(1 for a in range(w) for b in range(l) if inP1(xm0 + 10 + 20 * a, zm0 + 10 + 20 * b))
                            if vp2 == P1["vp"] + 40 and over < 2: continue
                            coin, expo, bad = A6.plate_seats(occ, E, R, O, xm0, zm0, w, l, vp2, forbid=nb, above=4.5)
                            if bad or expo > max_expo or len(coin) < 2: continue
                            sc = (len(coin), -expo, -vp2, -w * l)
                            if b2 is None or (tier, ) + tuple(-x for x in ()) and sc > b2[0]: b2 = (sc, dict(num=num, w=w, l=l, xm0=xm0, zm0=zm0, vp=vp2, coin=coin, tier=tier, exposed_cells=expo))
            if b2: break
        P2 = b2[1] if b2 else None
        key = (P2 is not None, P2 is not None and P2["tier"] == 1, len(P1["coin"]) + (len(P2["coin"]) if P2 else 0), -P1["xm0"])
        if best is None or key > best[0]: best = (key, P1, P2)
    if best is None: return None, None
    return best[1], best[2]

def build_ear(name, npz2, O_full, outdir):
    D.HEAD_NPZ = npz2; D.O = O_full; D.R_MOD = R_MOD
    A6.layout = G61.layout61
    A6.P1_LEVELS = tuple(48 + 40 * n for n in range(7))       # 48 .. 288
    A6.find_fixation = find_fixation_v7
    mod, rep, fp, Tset, inside = A6.build(name, outdir, True)
    return mod, rep

def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    npz2, delta, prep = prepare(out)
    O_up = O_HEAD + delta
    lowest = None
    # lower ear frame: same rotation, origin lowered by whole plates so that the lowest point of the ear is at v ~ 52
    S_tmp = None
    tdir = os.path.join(os.path.dirname(A6.__file__), "targets")
    import shutil
    for ext in ("silhouette.npy", "contour.json"):
        shutil.copy(os.path.join(tdir, f"A_paco_{ext}"), os.path.join(tdir, f"V7_oreille_haute_{ext}"))
    probe = lower_target(O_up, "V7_oreille_basse")
    meta = json.load(open(os.path.join(tdir, "V7_oreille_basse_contour.json")))
    vmin = meta["v0"] + 4.0 * np.argwhere(probe)[:, 1].min()
    shift = 8 * int(np.ceil((56 - vmin) / 8.0))                    # plates
    O_low = O_up + np.array([0.0, float(shift), 0.0])
    lower_target(O_low, "V7_oreille_basse")
    ears = {}
    for name, O_f in (("V7_oreille_haute", O_up), ("V7_oreille_basse", O_low)):
        mod, rep = build_ear(name, npz2, O_f, os.path.join(out, name))
        ears[name] = dict(mod=mod, rep={k: v for k, v in rep.items() if k != "settings_tried"}, O=O_f.tolist())
        print(name, "fixation", json.dumps(rep["fixation"], default=str)[:300], "parts", len(mod))
    pickle.dump(dict(ears=ears, npz2=npz2, delta=delta.tolist(), prep=prep, R=R_MOD.tolist(), lower_shift_ldu=shift), open(os.path.join(out, "ears.pkl"), "wb"))

if __name__ == "__main__":
    main()
