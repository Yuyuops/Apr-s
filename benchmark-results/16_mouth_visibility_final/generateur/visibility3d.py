"""LEGO V8.2 - mouth visibility diagnosis (corrected selection: 3D pocket component, see keep_mouth_3d) by projection and depth buffering (orthographic z-buffer, pure numpy).

For the same cameras as the renders (azimuth / elevation of the view JSON) and for three models (GLB source, LEGO V8, LEGO V8.1; the LEGO
meshes are the real expanded LDraw parts, g.glb) it measures, in a window around the mouth cavity:
  * the projected area of the cavity (pocket cells of the V8 grid, the empty volume between lip and jaw),
  * the part of it where the FIRST visible surface is a cavity surface (surface point whose outward neighbour lies in the cavity, dilated by
    one cell): the visible opening; the rest is hidden by an occluder (cheek, snout, jaw) in front,
  * the colours actually exposed on those first-hit pixels (dark / red / light / skin),
  * the kinds of wall seen (floor / ceiling / side), from the first-hit face normal,
  * the silhouette (hit mask) and depth differences between the GLB and a LEGO model over the window,
  * for given cells (the cells recoloured by a treatment), whether each is visible from each camera (a face sample not hidden by the depth map).
usage: visibility.py <details.json> <pre_lcm.npz> <out.json> name=mesh.glb ... (views read from the VIEWS env variable json)
"""
import json, os, sys
import numpy as np, trimesh
from scipy import ndimage

S = 5.0                      # pixels per mm

def pocket_cells(pre):
    d = np.load(pre); G = d["grid"].astype(int); F = d["fine"]; K = int(d["k"]); NX, NY, NZ = G.shape
    occ = (G >= 0) & (F.reshape(NX, K, NY, K, NZ, K).mean(axis=(1, 3, 5)) >= 0.5)
    lab, n = ndimage.label(~occ)
    b = np.unique(np.concatenate([lab[0].ravel(), lab[-1].ravel(), lab[:, 0].ravel(), lab[:, -1].ravel(), lab[:, :, 0].ravel(), lab[:, :, -1].ravel()]))
    outside = np.isin(lab, b[b > 0]); cells = {}
    for x in range(NX):
        for z in range(NZ):
            for y in range(6, NY - 6):
                if occ[x, y, z] or not outside[x, y, z]: continue
                u = next((k for k in range(1, 6) if occ[x, y + k, z]), None); dn = next((k for k in range(1, 7) if occ[x, y - k, z]), None)
                if u is None or dn is None: continue
                cells.setdefault((x, z), []).append(y)
    return cells, occ

def keep_mouth(cells, details):
    cols = sorted(cells); S_ = set(cols); comp = {}; cid = 0
    for c in cols:
        if c in comp: continue
        cid += 1; st = [c]; comp[c] = cid
        while st:
            x, z = st.pop()
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, z + dz)
                if q in S_ and q not in comp: comp[q] = cid; st.append(q)
    P = [p for p in details if p["classe"] == "bouche"]; keep = set()
    for k in range(1, cid + 1):
        mem = [c for c in cols if comp[c] == k]
        for p in P:
            cen = np.array(p["centre_mm"])
            if min(np.linalg.norm(np.array([(x + .5) * 8, (int(np.median(cells[(x, z)])) + .5) * 3.2, -(z + .5) * 8]) - cen) for x, z in mem) <= p["longueur_mm"] / 2 + 8: keep.add(k)
    return {c: cells[c] for c in cols if comp[c] in keep}


def keep_mouth_3d(occ, cells, details):
    """cavity = the 6-connected 3D component(s) of pocket cells that touch a mouth patch (V8.2: the first run used (x, z) columns with all heights and measured
    the legs as well)"""
    arr = np.zeros(occ.shape, bool)
    for (x, z), ys in cells.items():
        for y in ys: arr[x, y, z] = True
    lab, n = ndimage.label(arr); P = [p for p in details if p["classe"] == "bouche"]; out = {}
    for k in range(1, n + 1):
        idx = np.argwhere(lab == k)
        for p in P:
            cen = np.array(p["centre_mm"])
            if min(np.linalg.norm(np.array([(a + .5) * 8, (b + .5) * 3.2, -(c + .5) * 8]) - cen) for a, b, c in idx) <= p["longueur_mm"] / 2 + 8:
                for a, b, c in idx: out.setdefault((int(a), int(c)), []).append(int(b))
                break
    return out

def basis(az, el):
    a, e = np.radians(az), np.radians(el)
    c = np.array([np.cos(e) * np.sin(a), np.sin(e), np.cos(e) * np.cos(a)])        # direction towards the camera
    r = np.cross([0, 1, 0], c); r /= np.linalg.norm(r); u = np.cross(c, r)
    return c, r, u

def load_mesh(path, lo, hi):
    m = trimesh.load(path, force="mesh", process=False); V = np.asarray(m.vertices); F = np.asarray(m.faces)
    C = np.asarray(m.visual.vertex_colors)[:, :3].astype(float)
    inb = ((V >= lo) & (V <= hi)).all(1); F = F[inb[F].any(1)]
    P = V[F]; n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    return V, F, C[F].mean(1), n

def raster(V, F, FC, FN, cam, lo, hi, win):
    c, r, u = cam; (x0, x1, y0, y1) = win; W = int((x1 - x0) * S) + 1; H = int((y1 - y0) * S) + 1
    P = V[F]; X = (P @ r - x0) * S; Y = (P @ u - y0) * S; Z = P @ c
    depth = np.full((H, W), -1e9); fid = np.full((H, W), -1, np.int64)
    order = np.argsort(Z.mean(1))                                     # far to near; the z-test still protects crossings
    for i in order:
        xs, ys, zs = X[i], Y[i], Z[i]
        ax, bx = int(np.floor(xs.min())), int(np.ceil(xs.max())); ay, by = int(np.floor(ys.min())), int(np.ceil(ys.max()))
        if bx < 0 or ax >= W or by < 0 or ay >= H: continue
        ax, bx, ay, by = max(ax, 0), min(bx, W - 1), max(ay, 0), min(by, H - 1)
        gx, gy = np.meshgrid(np.arange(ax, bx + 1) + 0.5, np.arange(ay, by + 1) + 0.5)
        d = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if abs(d) < 1e-9: continue
        l0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / d; l1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / d; l2 = 1 - l0 - l1
        ins = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        if not ins.any(): continue
        z = l0 * zs[0] + l1 * zs[1] + l2 * zs[2]
        sub = depth[ay:by + 1, ax:bx + 1]; win_ = ins & (z > sub)
        sub[win_] = z[win_]; fid[ay:by + 1, ax:bx + 1][win_] = i
    return depth, fid

def cell_of(p): return np.floor(np.c_[p[:, 0] / 8, p[:, 1] / 3.2, -p[:, 2] / 8]).astype(int)

def classify_rgb(rgb):
    r, g, b = rgb.T; mx = rgb.max(1); mn = rgb.min(1); out = np.full(len(rgb), "peau", object)
    out[(r > 140) & (g < 120) & (b < 120)] = "rouge"; out[mn > 185] = "clair"; out[mx < 85] = "sombre"
    return out

def main():
    det_json, pre, out = sys.argv[1:4]; models = dict(a.split("=", 1) for a in sys.argv[4:])
    views = json.load(open(os.environ["VIEWS"]))
    D = json.load(open(det_json))["details"]; cells, occ = pocket_cells(pre); pk = keep_mouth_3d(occ, cells, D)
    cav = {(x, y, z) for (x, z), ys in pk.items() for y in ys}
    cdil = set((x + dx, y + dy, z + dz) for (x, y, z) in cav for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1))
    arr = np.array(sorted(cav)); lo = (arr.min(0) - 3) * np.array([8, 3.2, 8]) * np.array([1, 1, 1]); hi = (arr.max(0) + 4) * np.array([8, 3.2, 8])
    zlo, zhi = -hi[2], -lo[2]; lo3 = np.array([lo[0], lo[1], zlo]); hi3 = np.array([hi[0], hi[1], zhi])
    res = {"fenetre_mm": [lo3.tolist(), hi3.tolist()], "cellules_cavite": len(cav), "colonnes": len(pk), "cameras": {}}
    meshes = {k: load_mesh(v, lo3, hi3) for k, v in models.items()}
    corners = np.array([[x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)], float)
    cav_pts = np.array([[(c[0] + cc[0]) * 8, (c[1] + cc[1]) * 3.2, -(c[2] + cc[2]) * 8] for c in cav for cc in corners])
    for v in views:
        name = v["name"]; cam = basis(v["az"], v["el"]); c, r, u = cam
        pr, pu = cav_pts @ r, cav_pts @ u; win = (pr.min() - 6, pr.max() + 6, pu.min() - 6, pu.max() + 6)
        W = int((win[1] - win[0]) * S) + 1; H = int((win[3] - win[2]) * S) + 1
        # projected cavity mask (union of the projected cell boxes)
        pc = np.zeros((H, W), bool)
        for cell in cav:
            P = np.array([[(cell[0] + cc[0]) * 8, (cell[1] + cc[1]) * 3.2, -(cell[2] + cc[2]) * 8] for cc in corners])
            ax_, ay_ = (P @ r - win[0]) * S, (P @ u - win[2]) * S
            pc[int(ay_.min()):int(ay_.max()) + 1, int(ax_.min()):int(ax_.max()) + 1] = True
        # exact projection: convex hull of each cell box is a hexagon; fill via closing to remove the rectangle over-estimate
        pc = ndimage.binary_erosion(pc, iterations=2) | ndimage.binary_erosion(pc, iterations=1) & pc
        res["cameras"][name] = {"az": v["az"], "el": v["el"], "surface_projetee_cavite_mm2": round(float(pc.sum() / S ** 2), 1), "modeles": {}}
        maps = {}
        for k, (V, F, FC, FN) in meshes.items():
            depth, fid = raster(V, F, FC, FN, cam, lo3, hi3, win); hit = fid >= 0
            ii = np.where(hit); f = fid[hit]; col = FC[f]; nrm = FN[f] * np.sign((FN[f] @ c))[:, None]
            # hit point: pixel centre back-projected on the face plane
            xs = (ii[1] + .5) / S + win[0]; ys = (ii[0] + .5) / S + win[2]; Pf = V[F[f, 0]]
            zz = depth[hit]; pts = np.outer(xs, r) + np.outer(ys, u) + np.outer(zz, c)
            cl = cell_of(pts + 1.2 * nrm)
            incav = np.array([tuple(t) in cdil for t in cl]) if len(cl) else np.zeros(0, bool)
            vis = np.zeros_like(hit); vis[ii[0][incav], ii[1][incav]] = True
            visc = vis & pc; occl = pc & ~vis
            cls = classify_rgb(col[incav & pc[ii]]); nn = nrm[incav & pc[ii]]
            kinds = np.where(nn[:, 1] > 0.5, "plancher (face vers le haut)", np.where(nn[:, 1] < -0.5, "plafond (face vers le bas)", "paroi laterale")) if len(nn) else np.array([])
            def frac(arr, key): return round(float((arr == key).mean()), 3) if len(arr) else 0.0
            res["cameras"][name]["modeles"][k] = dict(
                cavite_visible_mm2=round(float(visc.sum() / S ** 2), 1), cavite_masquee_mm2=round(float(occl.sum() / S ** 2), 1),
                part_visible=round(float(visc.sum() / max(pc.sum(), 1)), 3),
                couleurs_exposees={q: frac(cls, q) for q in ("sombre", "rouge", "clair", "peau")}, surfaces_vues={q: frac(kinds, q) for q in ("plancher (face vers le haut)", "plafond (face vers le bas)", "paroi laterale")},
                pixels_rouges_mm2=round(float((cls == "rouge").sum() / S ** 2), 2), pixels_sombres_mm2=round(float((cls == "sombre").sum() / S ** 2), 2))
            maps[k] = (hit, depth)
        g = maps.get("GLB")
        if g is not None:
            for k in maps:
                if k == "GLB": continue
                h1, d1 = maps[k]; both = g[0] & h1; reg = pc
                res["cameras"][name]["modeles"][k]["silhouette_IoU_fenetre_cavite"] = round(float(((g[0] & h1 & reg).sum()) / max(((g[0] | h1) & reg).sum(), 1)), 3)
                res["cameras"][name]["modeles"][k]["ecart_profondeur_median_mm"] = round(float(np.median(np.abs(g[1][both & reg] - d1[both & reg]))), 2) if (both & reg).any() else None
        print(name, {k: (m["part_visible"], m["couleurs_exposees"]) for k, m in res["cameras"][name]["modeles"].items()}, flush=True)
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main()
