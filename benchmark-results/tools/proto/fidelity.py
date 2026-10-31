"""Shape fidelity of an LDR against the mesh, on the fine grid of headgrid.py (same frame as the head grid).
Every LDR part is rasterised from its real LDraw shape (partlib). Reports volume IoU, mismatch volume, and
silhouette IoU from the front, side and top (orthographic), i.e. what a viewer sees as outline.
usage: fidelity.py <head.npz> <model.ldr> [<out.json>]"""
import json, sys, os
import numpy as np
sys.path.insert(0, os.path.expanduser("~/bench/tools"))
import partlib as PL

def rasterise(ldr, shape, K, KY):
    S = np.zeros(shape, bool)
    for line in open(ldr):
        t = line.split()
        if len(t) < 15 or t[0] != "1": continue
        num = t[14].lower().replace(".dat", "")
        o = np.array(t[2:5], float); M = np.array(t[5:14], float).reshape(3, 3)
        r = next((k for k in range(4) if np.allclose(PL.rot_y(k), M, atol=1e-6)), None)
        if r is None: raise SystemExit(f"unsupported rotation in {line}")
        P = PL.part(num); Q = PL.placed(num, r)
        corners = np.array([[x, y, z] for x in (P["lo"][0], P["hi"][0]) for y in (P["lo"][1], P["hi"][1]) for z in (P["lo"][2], P["hi"][2])]) @ M.T + o
        mn, mx = corners.min(0), corners.max(0)
        x0 = int(round(mn[0] / 20)); z0 = int(round(mn[2] / 20)); y0 = int(round(-mx[1] / 8))
        sl = (slice(x0 * K, (x0 + Q["nx"]) * K), slice(y0 * KY, (y0 + Q["nh"]) * KY), slice(z0 * K, (z0 + Q["nz"]) * K))
        sub = S[sl]; sol = Q["solid"][:sub.shape[0], :sub.shape[1], :sub.shape[2]]
        S[sl] = sub | sol
    return S

def main():
    d = np.load(sys.argv[1]); F = d["fine"]; K = int(d["k"])
    S = rasterise(sys.argv[2], F.shape, K, K)
    inter = np.count_nonzero(S & F); uni = np.count_nonzero(S | F)
    res = dict(volume_iou=round(inter / uni, 4), lego_volume_cells=round(S.sum() / K**3, 1), mesh_volume_cells=round(F.sum() / K**3, 1),
               excess_cells=round(np.count_nonzero(S & ~F) / K**3, 1), missing_cells=round(np.count_nonzero(F & ~S) / K**3, 1))
    for name, ax in (("face", 2), ("profil", 0), ("dessus", 1)):
        a, b = S.any(axis=ax), F.any(axis=ax)
        res[f"silhouette_iou_{name}"] = round(np.count_nonzero(a & b) / np.count_nonzero(a | b), 4)
    print(json.dumps(res))
    if len(sys.argv) > 3: json.dump(res, open(sys.argv[3], "w"), indent=1)

if __name__ == "__main__":
    main()
