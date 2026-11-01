"""LEGO V7 - phase 2: automatic segmentation of the whole character grid and treatment decision per zone.

Input: the whole grid of the character (fullgrid.py: brickify colours, fine occupancy).
Zones (rules on colours, layers and connected components; nothing is drawn by hand):
  head / body       : split at the neck (narrowest layer between 55 and 80 % of the height, found by headgrid.py);
  ears              : black components touching the head on its back half (also below the neck), k-means split;
  eyes              : white components of the head; pupils = black cells touching them;
  nose (truffe)     : black component of the head at its front end;
  snout             : head cells in front of the eyes (depth beyond the eye plane);
  mouth             : red cells of the head;
  legs / feet       : per-layer connected components below the torso (2 components = legs; lowest 12 % = feet);
  arms / hands      : per-layer components of the body layers that are not the largest one (torso);
  torso             : the rest of the body; overall colour areas reported (red = overalls, white = logo).
Decision rule per zone (same rule for every character):
  thin and wide (PCA: 3rd axis < 0.30 x 1st and < 0.45 x 2nd, thickness < 35 mm = sandwich 20.8 mm + 1 voxel of inflation + margin, >= 60 cells) -> V6.1 contour generator;
  colour patch smaller than 2 studs across                                              -> grid colour only (no part
                                                                                            shape can render it: flagged);
  otherwise                                                                              -> brickify_plus volume.
usage: segment.py <full.npz> <out.json> [<out.npz>]
"""
import json, sys
import numpy as np
from scipy import ndimage
from sklearn.cluster import KMeans

COL = {0: "noir", 14: "jaune", 4: "rouge", 15: "blanc"}

def pca_ratio(cells):
    """(3rd/1st singular value, 3rd/2nd, thickness along the 3rd axis in mm: 5-95 % span)"""
    if len(cells) < 4: return None
    P = cells * np.array([20.0, 8.0, 20.0]); c = P.mean(0); _, s, vt = np.linalg.svd(P - c, full_matrices=False)
    t = (P - c) @ vt[2]; th = (np.percentile(t, 95) - np.percentile(t, 5) + 20.0) * 0.4
    return float(s[2] / max(s[0], 1e-9)), float(s[2] / max(s[1], 1e-9)), float(th)

def main():
    npz, out = sys.argv[1], sys.argv[2]; out_npz = sys.argv[3] if len(sys.argv) > 3 else None
    d = np.load(npz); G = d["grid"].astype(int); F = d["fine"]; K = int(d["k"]); neck = int(d["neck"]); NX, NY, NZ = G.shape
    fr = F.reshape(NX, K, NY, K, NZ, K).mean(axis=(1, 3, 5)); occ = (G >= 0) & (fr >= 0.5)
    lab = np.zeros(G.shape, np.int16); names = {}
    def put(mask, name):
        k = len(names) + 1; names[k] = name; lab[mask & (lab == 0)] = k; return k
    head = occ.copy(); head[:, :neck, :] = False; body = occ & ~head
    # ---- head details
    hz = np.argwhere(head)[:, 2]; z_mid = (hz.min() + hz.max()) / 2.0
    black_all = occ & (G == 0)
    lb, nb = ndimage.label(black_all, structure=np.ones((3, 3, 3)))
    comps = [(k, np.argwhere(lb == k)) for k in range(1, nb + 1)]
    # ears: black components that touch the head on its back half (they may hang below the neck)
    back = [c for k, c in comps if len(c) >= 30 and (c[:, 1] >= neck).any() and c[c[:, 1] >= neck][:, 2].mean() < z_mid]
    black = head & (G == 0)
    front = [c[c[:, 1] >= neck] for k, c in comps if (c[:, 1] >= neck).sum() >= 4 and c[c[:, 1] >= neck][:, 2].mean() >= z_mid]
    ears = np.concatenate(back) if back else np.zeros((0, 3), int)
    zones = []
    if len(ears):
        km = KMeans(2, n_init=10, random_state=0).fit(ears * np.array([20, 8, 20]))
        order = np.argsort([-ears[km.labels_ == j][:, 1].mean() for j in range(2)])
        for rank, j in enumerate(order):
            m = np.zeros(G.shape, bool); m[tuple(ears[km.labels_ == j].T)] = True
            put(m, ["oreille_haute", "oreille_basse"][rank])
    white = head & (G == 15)
    lw, nw = ndimage.label(white, structure=np.ones((3, 3, 3)))
    eyes = np.zeros(G.shape, bool)
    for k in range(1, nw + 1):
        if (lw == k).sum() >= 3: eyes |= lw == k
    pupils = black & ndimage.binary_dilation(eyes, iterations=1) & (lab == 0)
    put(eyes | pupils, "yeux")
    if front:
        nose = max(front, key=lambda c: c[:, 2].max())
        m = np.zeros(G.shape, bool); m[tuple(nose.T)] = True; put(m & (lab == 0), "truffe")
    z_eye = np.argwhere(eyes)[:, 2].mean() if eyes.any() else z_mid
    snout = head.copy(); snout[:, :, :int(np.ceil(z_eye)) + 1] = False
    put(head & (G == 4), "bouche")
    put(snout & (lab == 0), "museau")
    put(head & (lab == 0), "crane")
    # ---- body: per-layer components
    area = body.sum(axis=(0, 2))
    legs = np.zeros(G.shape, bool); arms = np.zeros(G.shape, bool)
    crotch = 0
    for y in range(neck):
        l2, n2 = ndimage.label(body[:, y, :])
        if n2 == 0: continue
        sz = sorted([(int((l2 == k).sum()), k) for k in range(1, n2 + 1)], reverse=True)
        big = [k for s, k in sz if s >= 6]
        if len(big) >= 2 and y < 0.45 * NY:
            for k in big[:2]: legs[:, y, :] |= l2 == k
            crotch = y
        elif y > 0.35 * NY:
            for s, k in sz[1:]:
                if s >= 2: arms[:, y, :] |= l2 == k
    feet_top = int(0.12 * NY)
    feet = body.copy(); feet[:, feet_top:, :] = False
    put(feet, "pieds"); put(legs & (lab == 0), "jambes")
    # arms grow into the shoulder region by connectivity in 3D (lateral parts only)
    la, na = ndimage.label(arms)
    keep = np.zeros(G.shape, bool)
    for k in range(1, na + 1):
        if (la == k).sum() >= 20: keep |= la == k
    put(keep & (lab == 0), "bras_mains")
    put(body & (lab == 0), "torse")
    # ---- measures and decisions
    res = []
    for k, name in names.items():
        cells = np.argwhere(lab == k)
        if len(cells) == 0: continue
        cols = {COL.get(int(c), str(int(c))): int(n) for c, n in zip(*np.unique(G[tuple(cells.T)], return_counts=True))}
        pr = pca_ratio(cells)
        ext = (cells.max(0) - cells.min(0) + 1) * np.array([20, 8, 20]) * 0.4
        thin = pr is not None and pr[0] < 0.30 and pr[1] < 0.45 and pr[2] < 35.0 and len(cells) >= 60
        small = (np.sort(ext)[1] < 16.0)            # less than 2 studs across in its 2nd dimension
        touch = ndimage.binary_dilation(lab == k, iterations=1) & occ & (lab != k)
        attach = int(touch.sum())
        if thin and name.startswith("oreille"):
            dec, conf = "generateur V6.1 (contour, panneau a deux faces, fixation 3-4-5)", "haute" if name == "oreille_haute" else "moyenne"
        elif thin:
            dec, conf = "candidat V6.1 (mince) - non teste sur ce type de zone", "faible"
        elif small or name in ("yeux", "truffe", "bouche"):
            dec, conf = "couleur de la grille seulement (detail trop petit pour une piece de forme) - capacite manquante : module de details ronds", "faible"
        else:
            dec, conf = "volume brickify_plus (reglages du prototype C)", "haute" if name in ("crane", "torse", "jambes", "pieds") else "moyenne"
        res.append(dict(zone=name, cellules=int(len(cells)), couleurs=cols, etendue_mm=np.round(ext, 0).tolist(),
                        acp_epaisseur_sur_longueur=None if pr is None else round(pr[0], 3),
                        acp_epaisseur_sur_largeur=None if pr is None else round(pr[1], 3), epaisseur_mm=None if pr is None else round(pr[2], 1), contact_cellules=attach,
                        decision=dec, confiance=conf))
    json.dump(dict(cou=neck, entrejambe=int(crotch), zones=res), open(out, "w"), indent=1, ensure_ascii=False)
    if out_npz: np.savez_compressed(out_npz, labels=lab, names=json.dumps(names))
    for r in res: print("%-14s %5d  ratio %-6s %-6s ep %-5s mm  %s  [%s]" % (r["zone"], r["cellules"], r["acp_epaisseur_sur_longueur"], r["acp_epaisseur_sur_largeur"], r["epaisseur_mm"], r["decision"][:55], r["confiance"]))

if __name__ == "__main__":
    main()
