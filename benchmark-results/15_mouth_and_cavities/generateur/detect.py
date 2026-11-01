"""LEGO V8 - phase 1: automatic analysis of the small facial details on the GLB (no Paco-specific value).

Inputs : the whole GLB placed in the LEGO frame (ref_full_frame.glb, mm, vertex colours), the whole-character grid
         (fullgrid.py) and the V7 segmentation (segment.py: zones and labels).
Method (generic rules):
  1. faces of the head (above the neck) are classed by colour (white / black / red / skin); connected patches of one
     class on the mesh; patches of one class closer than MERGE_MM are merged (texture noise splits a blob);
  2. patches lying on an ear zone of the segmentation are ignored (the ears have their own generator);
  3. per patch: area, centroid, OUTWARD normal (sign checked on the fine occupancy grid, the mirrored GLB has
     reversed windings), in-plane PCA extents (length, width), equivalent diameter, bulge (height of the patch above
     the plane of its rim / diameter), elongation;
  4. nesting: a dark patch whose centre lies inside a light patch is its pupil;
  5. head frame: snout axis = crane centroid -> snout centroid (segmentation zones); sagittal plane = vertical plane
     containing it, refined by mirror matching of the head vertices; every detail gets its mirrored partner if any;
  6. classes: light patch with a pupil -> 'oeil'; dark patch at the front end of the snout -> 'truffe';
     patch between the snout and the lower jaw, facing up or down (|n.y| > 0.6), red or dark -> 'bouche';
     anything else -> 'marque' (eyebrows, stripes, spots: reported, left to the volume colours);
  7. eyes come in mirrored pairs: when a side carries two eye patches, the one whose mirror image best matches an eye
     of the other side is kept, the other is reported as 'oeil_douteux' (generation artefact) and not built.
usage: detect.py <ref_full_frame.glb> <full.npz> <segmentation.npz> <segmentation.json> <out.json>
"""
import json, sys
import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

MERGE_MM = 6.0
MIN_AREA = 25.0
NOSE_GAP_REL = 0.35  # dark patches of the snout front closer than 0.35 x snout length to the frontmost one belong to the nose (set on Paco: the GLB nose is two black faces 25 mm apart)
EAR_ZONES = ("oreille_haute", "oreille_basse")

def classify(Cf):
    r, g, b = Cf.T; mx = Cf.max(1); mn = Cf.min(1)
    lab = np.full(len(Cf), "peau", object)
    lab[(r > 140) & (g < 110)] = "rouge"; lab[mn > 185] = "blanc"; lab[mx < 75] = "noir"
    return lab

def to_ldu(p):
    p = np.atleast_2d(p); return np.c_[p[:, 0] / 0.4, -p[:, 1] / 0.4, -p[:, 2] / 0.4]

def main():
    glb, npz, segnpz, segjson, out = sys.argv[1:6]
    d = np.load(npz); G = d["grid"].astype(int); F = d["fine"]; K = int(d["k"]); neck = int(d["neck"]); NX, NY, NZ = G.shape
    s = np.load(segnpz); lab = s["labels"]; names = {int(k): v for k, v in json.loads(str(s["names"])).items()}
    idx = {v: k for k, v in names.items()}
    m = trimesh.load(glb, force="mesh", process=False)
    V = m.vertices; Fc = m.faces; C = np.asarray(m.visual.vertex_colors)[:, :3].astype(float)
    cen = V[Fc].mean(1); area = m.area_faces; nrm = m.face_normals
    cl = classify(C[Fc].mean(1))
    cenL = to_ldu(cen)
    ci = np.floor(np.c_[cenL[:, 0] / 20, -cenL[:, 1] / 8, cenL[:, 2] / 20]).astype(int)
    inb = (ci >= 0).all(1) & (ci < [NX, NY, NZ]).all(1)
    head_face = inb & (ci[:, 1] >= neck)
    # nearest labelled cell of every face (labels of the segmentation, 2 cells around)
    labc = np.argwhere(lab > 0); tree_l = cKDTree(labc * np.array([20.0, 8.0, 20.0]))
    dd, ii = tree_l.query(ci * np.array([20.0, 8.0, 20.0]) + [10, 4, 10])
    face_zone = np.array([names[int(lab[tuple(labc[j])])] for j in ii], object)
    face_zone[dd > 45] = "?"
    # fine occupancy, for outward normals
    occf = F.astype(bool); fs = np.array(occf.shape)
    def occ_at(pL):
        q = np.floor(np.c_[pL[:, 0] / 20 * K, -pL[:, 1] / 8 * K, pL[:, 2] / 20 * K]).astype(int)
        ok = (q >= 0).all(1) & (q < fs).all(1); r = np.zeros(len(pL), bool); r[ok] = occf[tuple(q[ok].T)]; return r
    # mesh adjacency on welded vertices
    _, inv = np.unique(np.round(V, 3), axis=0, return_inverse=True); inv = inv.ravel()
    mt = trimesh.Trimesh(np.zeros((inv.max() + 1, 3)), inv[Fc], process=False); adj = mt.face_adjacency
    patches = []
    def stats(f, colour):
        Ar = area[f].sum()
        c = (cen[f] * area[f, None]).sum(0) / Ar
        nn = (nrm[f] * area[f, None]).sum(0); nn /= np.linalg.norm(nn) + 1e-9
        # outward sign on the fine grid (5 mm each side)
        cL = to_ldu(c)[0]; nL = np.array([nn[0], -nn[1], -nn[2]])
        pin = occ_at(np.array([cL - 12.5 * nL]))[0]; pout = occ_at(np.array([cL + 12.5 * nL]))[0]
        flip = (not pin) and pout
        if pin == pout:   # ambiguous: test further
            pin2 = occ_at(np.array([cL - 25 * nL]))[0]; pout2 = occ_at(np.array([cL + 25 * nL]))[0]
            flip = (not pin2) and pout2
        if flip: nn = -nn
        P = cen[f] - c; w = np.sqrt(area[f])[:, None]
        _, sv, vt = np.linalg.svd(P * w, full_matrices=False)
        t1 = vt[0] - np.dot(vt[0], nn) * nn; t1 /= np.linalg.norm(t1); t2 = np.cross(nn, t1)
        e1 = np.percentile(P @ t1, 97) - np.percentile(P @ t1, 3); e2 = np.percentile(P @ t2, 97) - np.percentile(P @ t2, 3)
        h = P @ nn; rad = np.sqrt((P @ t1) ** 2 + (P @ t2) ** 2); rim = rad > 0.7 * rad.max()
        bulge = float((h[~rim].mean() - h[rim].mean()) if (~rim).any() and rim.any() else 0.0)
        zones = {}
        for z_, a_ in zip(face_zone[f], area[f]): zones[z_] = zones.get(z_, 0) + a_
        return dict(couleur=colour, aire_mm2=round(float(Ar), 1), centre_mm=np.round(c, 2).tolist(),
                            normale=np.round(nn, 3).tolist(), axe_long=np.round(t1, 3).tolist(),
                            longueur_mm=round(float(e1), 1), largeur_mm=round(float(e2), 1),
                            diametre_eq_mm=round(float(2 * np.sqrt(Ar / np.pi)), 1), bombe_mm=round(bulge, 2),
                            zone=max(zones, key=zones.get), n_faces=int(len(f)), _faces=f)
    for colour in ("blanc", "noir", "rouge"):
        sel = head_face & (cl == colour) & ~np.isin(face_zone, EAR_ZONES)
        a = adj[sel[adj[:, 0]] & sel[adj[:, 1]]]
        n = len(Fc); A = coo_matrix((np.ones(len(a)), (a[:, 0], a[:, 1])), shape=(n, n))
        _, cc = connected_components(A, directed=False)
        groups = [np.where((cc == i) & sel)[0] for i in np.unique(cc[sel])]
        groups = [g for g in groups if area[g].sum() >= 4.0]
        # merge groups closer than MERGE_MM
        parent = list(range(len(groups)))
        def find(i):
            while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
            return i
        trees = [cKDTree(cen[g]) for g in groups]
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                if np.linalg.norm(cen[groups[i]].mean(0) - cen[groups[j]].mean(0)) > 80: continue
                dmin, _ = trees[j].query(cen[groups[i]], k=1, distance_upper_bound=MERGE_MM)
                if np.isfinite(dmin).any(): parent[find(i)] = find(j)
        merged = {}
        for i, g in enumerate(groups): merged.setdefault(find(i), []).append(g)
        for gs in merged.values():
            f = np.concatenate(gs); Ar = area[f].sum()
            if Ar < MIN_AREA: continue
            patches.append(stats(f, colour))
    # ---- head frame
    def zone_centroid(z):
        c = np.argwhere(lab == idx[z]) if z in idx else np.zeros((0, 3))
        return (c * np.array([8.0, 3.2, -8.0]) + [4, 1.6, -4]).mean(0) if len(c) else None
    cc_ = zone_centroid("crane"); cs_ = zone_centroid("museau")
    ax = cs_ - cc_; ax[1] = 0; ax /= np.linalg.norm(ax)
    lat = np.cross([0, 1, 0], ax); lat /= np.linalg.norm(lat)
    headv = cen[head_face & np.isin(face_zone, ("crane", "museau", "yeux", "truffe", "bouche"))]
    tree_h = cKDTree(headv[::7])
    best = None
    for ang in np.radians(np.arange(-20, 20.1, 1.0)):
        ca, sa = np.cos(ang), np.sin(ang); l2 = ca * lat + sa * ax; l2[1] = 0; l2 /= np.linalg.norm(l2)
        o0 = np.dot(headv.mean(0), l2)
        for off in np.arange(-20, 20.1, 1.0):
            dist = headv[::23] @ l2 - (o0 + off)
            mir = headv[::23] - 2 * dist[:, None] * l2[None, :]
            sc = np.median(tree_h.query(mir)[0])
            if best is None or sc < best[0]: best = (sc, l2, o0 + off)
    _, lat, off = best
    ax = np.cross(lat, [0, 1, 0]); ax = ax if np.dot(ax, cs_ - cc_) > 0 else -ax
    def mirror(p): p = np.asarray(p, float); return p - 2 * (np.dot(p, lat) - off) * lat
    snout_tip = float(np.max(headv @ ax)); snout_root = float(np.dot(cs_, ax))
    # ---- nesting, classes
    for p in patches: p["parent"] = None
    light = [p for p in patches if p["couleur"] == "blanc"]
    for p in patches:
        if p["couleur"] == "blanc": continue
        for q in light:
            dpq = np.array(p["centre_mm"]) - np.array(q["centre_mm"])
            if np.linalg.norm(dpq - np.dot(dpq, q["normale"]) * np.array(q["normale"])) < 0.45 * min(q["longueur_mm"], q["largeur_mm"]) and abs(np.dot(dpq, q["normale"])) < 6:
                p["parent"] = id(q); q.setdefault("_kids", []).append(p)
    for p in patches:
        c = np.array(p["centre_mm"]); n = np.array(p["normale"])
        along = (np.dot(c, ax) - snout_root) / max(snout_tip - snout_root, 1e-6)
        p["position_museau"] = round(float(along), 2); p["cote"] = "droite" if np.dot(c, lat) - off > 0 else "gauche"
        p["ecart_plan_sagittal_mm"] = round(float(np.dot(c, lat) - off), 1)
        p["remplissage"] = round(float(p["aire_mm2"] / (np.pi / 4 * max(p["longueur_mm"], 1) * max(p["largeur_mm"], 1))), 2)
        if p["parent"] is not None: p["classe"] = "pupille"
        elif p["couleur"] == "blanc" and p.get("_kids"): p["classe"] = "oeil"
        else: p["classe"] = None
    # nose: the frontmost dark patch, plus the dark patches of the front half of the snout within NOSE_GAP of it
    dark = [p for p in patches if p["classe"] is None and p["couleur"] == "noir" and p["position_museau"] > 0.5]
    if dark:
        tip = max(dark, key=lambda p: p["position_museau"]); tt = cKDTree(cen[tip["_faces"]])
        group = [q for q in dark if q is tip or np.isfinite(tt.query(cen[q["_faces"]], distance_upper_bound=NOSE_GAP_REL * (snout_tip - snout_root))[0]).any()]
        fN = np.concatenate([q["_faces"] for q in group])
        nose = stats(fN, "noir")
        nsum = sum(q["aire_mm2"] * np.array(q["normale"]) for q in group); nn_ = nsum / np.linalg.norm(nsum)
        if np.dot(nn_, ax) < 0.3: nn_ = nn_ + ax; nn_ /= np.linalg.norm(nn_)   # faces on both sides of the tip: the snout axis
        nose["normale"] = np.round(nn_, 3).tolist(); nose["membres"] = [q["centre_mm"] for q in group]
        nose["bombe_membres"] = round(float(sum(q["aire_mm2"] * q["bombe_mm"] for q in group) / sum(q["aire_mm2"] for q in group)), 2)
        nose.update(classe="truffe", parent=None, fusion=len(group), position_museau=tip["position_museau"],
                                            cote="centre", ecart_plan_sagittal_mm=round(float(np.dot(nose["centre_mm"], lat) - off), 1))
        nose["remplissage"] = round(float(nose["aire_mm2"] / (np.pi / 4 * nose["longueur_mm"] * nose["largeur_mm"])), 2)
        patches = [q for q in patches if not any(q is g for g in group)] + [nose]
    eyes0 = [p for p in patches if p["classe"] == "oeil"]
    y_eye = min(p["centre_mm"][1] for p in eyes0) if eyes0 else 1e9
    a_eye = min(np.dot(p["centre_mm"], ax) for p in eyes0) if eyes0 else -1e9
    for p in patches:
        if p["classe"] is not None: continue
        c = np.array(p["centre_mm"]); n = np.array(p["normale"])
        # mouth: red or dark, facing up or down, below the eyes and in front of the rearmost eye
        if p["couleur"] in ("rouge", "noir") and abs(n[1]) > 0.6 and c[1] < y_eye - 10 and np.dot(c, ax) > a_eye - 5: p["classe"] = "bouche"
        else: p["classe"] = "marque"
    # eyes come in mirrored pairs (score: mirror distance + size + normal + disc completeness)
    def mirror_n(n): n = np.asarray(n, float); return n - 2 * np.dot(n, lat) * lat
    def pair_score(p, o):
        return (np.linalg.norm(mirror(p["centre_mm"]) - np.array(o["centre_mm"])) + 30 * abs(1 - p["aire_mm2"] / o["aire_mm2"])
                + 20 * (1 - np.dot(mirror_n(p["normale"]), o["normale"])) + 40 * max(0.0, 0.85 - p["remplissage"]))
    eyes = [p for p in patches if p["classe"] == "oeil"]
    for side in ("gauche", "droite"):
        mine = [p for p in eyes if p["cote"] == side]; other = [p for p in eyes if p["cote"] != side]
        if len(mine) <= 1 or not other: continue
        sc = [min(pair_score(p, o) for o in other) for p in mine]
        keep = int(np.argmin(sc)); srt = sorted(sc)
        for j, p in enumerate(mine):
            p["score_paire"] = round(float(sc[j]), 1); p["marge_choix_paire"] = round(float(srt[1] - srt[0]), 1)
            if j != keep:
                p["classe"] = "oeil_douteux"
                for k_ in p.get("_kids", []): k_["classe"] = "pupille_douteuse"
    eyes = [p for p in patches if p["classe"] == "oeil"]
    for p in eyes:
        o = [q for q in eyes if q is not p]
        if o: p["ecart_miroir_mm"] = round(float(min(np.linalg.norm(mirror(p["centre_mm"]) - np.array(q["centre_mm"])) for q in o)), 1)
    for i, p in enumerate(patches): p["id"] = f"{p['classe']}_{i}"
    for p in patches:
        p["pupille"] = [k_["id"] for k_ in p.get("_kids", [])] or None
        for k_ in ("_kids", "parent", "_faces"): p.pop(k_, None)
    res = dict(repere=dict(axe_museau=np.round(ax, 3).tolist(), normale_plan_sagittal=np.round(lat, 3).tolist(), plan_offset_mm=round(float(off), 1),
                           ecart_symetrie_median_mm=round(float(best[0]), 2), museau_racine_mm=round(snout_root, 1), museau_bout_mm=round(snout_tip, 1)),
               regles=dict(fusion_mm=MERGE_MM, aire_min_mm2=MIN_AREA), details=sorted(patches, key=lambda p: (p["classe"], -p["aire_mm2"])))
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    for p in res["details"]:
        print("%-16s %-6s %6.0f mm2  c %-24s n %-22s %5.1f x %4.1f  bombe %5.2f  pos %5.2f  %s %s" % (p["id"], p["couleur"], p["aire_mm2"], p["centre_mm"], p["normale"], p["longueur_mm"], p["largeur_mm"], p["bombe_mm"], p["position_museau"], p["cote"], p["zone"]))
    print(json.dumps(res["repere"]))

if __name__ == "__main__":
    main()
