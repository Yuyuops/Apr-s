"""Brickify V4 demonstrator: Paco's upper ear as a parametric LEGO module on the prototype-C head.

Module (real parts, see TECHNICAL_REPORT.md):
  head top --(4 studs each)--> 2 x Turntable 2x2 base (3680, black, axis-aligned)
           --(turntable pivot)--> 2 x Turntable 2x2 top (3679, light bluish grey: only colour produced)
           --(2x2 studs each)--> Plate 2x8 (3034, black) rotated 53.13 deg: the two turntables sit 3 x 4 studs apart,
                                 i.e. exactly 5 studs along the plate (3-4-5 triangle), so the plate locks the angle
           --(2 studs each)--> 2 x Bracket 1x2 - 2x2 Down (44728, black), hanging past the plate edge
           --(4 side studs each)--> ear panel: 2 layers of black plates in the ear plane, outer layer outlined with
                                 round-corner plates and wedge plates fitted to the mesh silhouette.
The panel plane is set by the bracket faces (24 LDU outside the turntable line); the turntable line is searched on
the head top so that the panel plane is as close as possible to the mesh ear plane without touching the head.
usage: ear_module.py <head.npz> <outdir> [--panel-gap 0]
"""
import json, os, subprocess, sys
import numpy as np
from scipy import ndimage
from sklearn.cluster import KMeans
sys.path.insert(0, os.path.expanduser("~/bench/tools")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import partlib as PL, conn
import brickify_plus as BP
from snot_ears import pack2d

BLACK, LBG = 0, 71
DV = np.array([3, 4])                    # stud offset between the two turntables (x, z): 5 studs, 53.13 deg

def rot_y_mat(c, s):
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], float)

def place_line(colour, num, M, o):
    return f"1 {colour} {o[0]:.4f} {o[1]:.4f} {o[2]:.4f} " + " ".join(f"{v:.6f}" for v in np.asarray(M).ravel()) + f" {num}.dat"

def axis_place(num, R, target_min):
    """origin of a part rotated by the axis-aligned matrix R so that its body box starts at target_min"""
    P = conn.part(num)
    corners = np.array([[x, y, z] for x in (P["lo"][0], P["hi"][0]) for y in (P["lo"][1], P["hi"][1]) for z in (P["lo"][2], P["hi"][2])]) @ R.T
    return np.array(target_min, float) - corners.min(0)

def main():
    npz, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    d = np.load(npz); G = d["grid"].astype(int); F = d["fine"]; K = int(d["k"]); NX, NY, NZ = G.shape
    fr = F.reshape(NX, K, NY, K, NZ, K).mean(axis=(1, 3, 5)); occ = (G >= 0) & (fr >= 0.5)
    # ---------------- upper ear cells (same segmentation as iteration 06)
    black = occ & (G == BLACK); black[:, :, 17:] = False
    lab, n = ndimage.label(black, structure=np.ones((3, 3, 3))); sz = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    ear_all = np.isin(lab, [k + 1 for k in range(n) if sz[k] >= 8]); cells = np.argwhere(ear_all)
    km = KMeans(2, n_init=10, random_state=0).fit(cells * np.array([8, 3.2, 8]))
    up = int(np.argmax([cells[km.labels_ == k][:, 1].mean() for k in range(2)]))
    ear = np.zeros_like(ear_all); ear[tuple(cells[km.labels_ == up].T)] = True
    # remove the ear skin, its thin black cells and its yellow core from the head grid
    black_any = (G == BLACK); black_any[:, :, 17:] = False
    la, _ = ndimage.label(black_any, structure=np.ones((3, 3, 3)))
    skin = np.isin(la, np.unique(la[ear])) & (la > 0) & ndimage.binary_dilation(ear, iterations=1) & ~(ear_all & ~ear)
    G2 = G.copy(); G2[skin] = -1
    occ2 = (G2 >= 0) & (fr >= 0.5); l3, _ = ndimage.label(occ2)
    keep = {int(v) for v in np.unique(l3[:, 0, :]) if v > 0}
    core = occ2 & ~np.isin(l3, list(keep)); G2[(G2 >= 0) & ~np.isin(l3, list(keep)) & ndimage.binary_dilation(skin, iterations=3)] = -1
    head_npz = os.path.join(out, "head_C_without_upper_ear.npz")
    np.savez_compressed(head_npz, grid=G2, surface=d["surface"], fine=F, k=K, neck=d["neck"], full_shape=d["full_shape"], hoff=d["hoff"])
    rep = dict(ear_skin_cells_removed=int(skin.sum()), ear_core_cells_removed=int(core.sum()))
    # head = prototype C settings on that grid
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "brickify_plus.py"), head_npz, out, "head_C",
                        "--occupancy", "0.5", "--no-shapes", "--drop-floating"], check=True, capture_output=True, text=True)
    rep["head"] = {k: v for k, v in json.loads(r.stdout.strip().splitlines()[-1]).items() if k not in ("settings", "part_numbers")}
    # head occupancy from the parts actually placed (bridges and dropped floaters included)
    H = np.zeros(G.shape, bool)
    for l in open(os.path.join(out, "head_C.ldr")):
        t = l.split()
        if len(t) < 15 or t[0] != "1": continue
        Pt = conn.part(t[14].replace(".dat", "")); Mt = np.array(t[5:14], float).reshape(3, 3); ot = np.array(t[2:5], float)
        cs = np.array([[x, y, z] for x in (Pt["lo"][0], Pt["hi"][0]) for y in (Pt["lo"][1], Pt["hi"][1]) for z in (Pt["lo"][2], Pt["hi"][2])]) @ Mt.T + ot
        H[int(round(cs[:, 0].min() / 20)):int(round(cs[:, 0].max() / 20)), int(round(-cs[:, 1].max() / 8)):int(round(-cs[:, 1].min() / 8)),
          int(round(cs[:, 2].min() / 20)):int(round(cs[:, 2].max() / 20))] = True
    # ---------------- ear plane from the mesh (fine voxels of the ear skin + core)
    region = ndimage.binary_dilation(ear, iterations=1) & ~H        # the ear skin only (the removed yellow core is not ear)
    fv = []
    for (x, y, z) in np.argwhere(region):
        sub = np.argwhere(F[x * K:(x + 1) * K, y * K:(y + 1) * K, z * K:(z + 1) * K])
        if len(sub): fv.append(sub + [x * K, y * K, z * K])
    fv = np.concatenate(fv)
    P_ear = np.c_[(fv[:, 0] + 0.5) * 5, -(fv[:, 1] + 0.5) * 2, (fv[:, 2] + 0.5) * 5]       # LDraw LDU
    c0 = P_ear.mean(0); _, _, vt = np.linalg.svd(P_ear - c0, full_matrices=False); nrm = vt[2]; nrm[1] = 0; nrm /= np.linalg.norm(nrm)
    rep["ear_plane"] = dict(centre_ldu=np.round(c0, 1).tolist(), normal=np.round(nrm, 3).tolist(),
                            in_plane_angle_deg=round(float(np.degrees(np.arctan2(abs(nrm[0]), abs(nrm[2])))), 1),
                            module_angle_deg=round(float(np.degrees(np.arctan2(4, 3))), 2))
    # ---------------- search the turntable pair on the head top (risers of 1x1 plates level uneven cells)
    coltop = np.full((NX, NZ), -1)
    for x in range(NX):
        for z in range(NZ):
            ys = np.nonzero(H[x, :, z])[0]
            if len(ys): coltop[x, z] = ys.max() + 1
    best = None
    sub = P_ear[np.random.default_rng(0).choice(len(P_ear), min(3000, len(P_ear)), replace=False)]
    for sgn in (+1, -1):
        dv = sgn * DV; X_m = np.array([dv[0], 0, dv[1]], float) / 5.0
        for side in (+1, -1):
            Z_m = np.array([-X_m[2], 0, X_m[0]]); R_mod = np.c_[X_m, [0, 1, 0], Z_m]; out_n = -side * Z_m
            for cx in range(1, NX):
                for cz in range(1, NZ):
                    c2x, c2z = cx + dv[0], cz + dv[1]
                    if not (1 <= c2x < NX and 1 <= c2z < NZ): continue
                    t8 = np.r_[coltop[cx - 1:cx + 1, cz - 1:cz + 1].ravel(), coltop[c2x - 1:c2x + 1, c2z - 1:c2z + 1].ravel()]
                    if (t8 <= 0).any(): continue
                    yt = int(t8.max())
                    if yt + 5 > NY or (yt - t8).max() > 10: continue
                    risers = int((yt - t8).sum())
                    O = np.array([20 * cx, -8 * yt, 20 * cz], float)
                    # clearance: plate and bracket tops (module y -24..0) over the plate footprint
                    clear = True
                    for mx in range(-40, 161, 10):
                        for mz in (-22 * side, -18, 0, 18):
                            for my in (-20, -4):
                                p_ = O + R_mod @ np.array([mx, my, mz]); x, z = int(np.floor(p_[0] / 20)), int(np.floor(p_[2] / 20)); y = int(np.floor(-p_[1] / 8))
                                if 0 <= x < NX and 0 <= y < NY and 0 <= z < NZ and H[x, y, z]: clear = False
                    if not clear: continue
                    mid = O + R_mod @ np.array([0, 0, -32 * side])
                    dist = float((c0 - mid) @ out_n)
                    # the bracket studs (module x 0..140, module y -14 and +6) must fall inside the ear silhouette
                    rel_ = (sub - O) @ R_mod
                    if not (rel_[:, 0].min() < -10 and rel_[:, 0].max() > 150 and rel_[:, 1].min() < -34 and rel_[:, 1].max() > 26): continue
                    score = abs(dist) + 4 * risers
                    if best is None or score < best[0]:
                        best = (score, sgn, side, yt, cx, cz, R_mod, out_n, dist, risers)
    _, sgn, side, yt, cx, cz, R_mod, out_n, dist, risers = best
    O = np.array([20 * cx, -8 * yt, 20 * cz], float)
    # riser columns under the turntables are part of the head from now on (panel and brackets must clear them)
    for (ax, az) in ((cx, cz), (cx + sgn * DV[0], cz + sgn * DV[1])):
        for x in (ax - 1, ax):
            for z in (az - 1, az):
                H[x, int(coltop[x, z]):yt, z] = True
    tt_boxes = []
    for mx_ in (0.0, 100.0):
        cpt = O + R_mod @ np.array([mx_, 0, 0]); tt_boxes.append((cpt + [-20, -8, -20], cpt + [20, 0, 20]))
    rep["placement"] = dict(turntable_1_corner=[int(cx), int(cz)], turntable_2_corner=[int(cx + sgn * DV[0]), int(cz + sgn * DV[1])], head_top_layer=int(yt),
                            panel_side=int(side), panel_to_mesh_ear_plane_ldu=round(dist, 1), riser_plates_1x1=risers)
    # ---------------- panel silhouette: mesh ear projected on the panel plane, panel-local (x = along plate, z = up)
    rel = (P_ear - O) @ R_mod                                   # module coordinates
    u = rel[:, 0]; vmod = rel[:, 1]                             # vmod: module y (LDraw y, down)
    # panel cells: x centre 10 + 20 i ; row centre (module y) -14 + 20 j (bracket side-stud height) -> panel-local z = -(module y)
    i_idx = np.floor((u - 0) / 20).astype(int); j_idx = np.floor((vmod - (-24)) / 20).astype(int)
    imin, imax, jmin, jmax = i_idx.min() - 1, i_idx.max() + 1, j_idx.min() - 1, j_idx.max() + 1
    NI, NJ = imax - imin + 1, jmax - jmin + 1
    fine2 = np.zeros((NI * 4, NJ * 4))
    fi = np.floor((u - 20 * imin) / 5).astype(int); fj = np.floor((vmod - (-24 + 20 * jmin)) / 5).astype(int)
    okf = (fi >= 0) & (fi < NI * 4) & (fj >= 0) & (fj < NJ * 4); fine2[fi[okf], fj[okf]] = 1
    fine2 = ndimage.binary_closing(fine2 > 0, iterations=2)
    fine2 = ndimage.binary_fill_holes(fine2)
    cov = fine2.reshape(NI, 4, NJ, 4).mean(axis=(1, 3))
    mask = cov >= float(os.environ.get("EAR_COV", "0.6"))
    lab0, n0 = ndimage.label(mask)
    if n0 > 1: mask = lab0 == (1 + int(np.argmax(ndimage.sum(mask, lab0, range(1, n0 + 1)))))   # main leaf only
    if os.environ.get("DEBUG_MASK"):
        print("silhouette (rows = module y down, cols = along the plate):")
        for j in range(NJ): print("".join("#" if cov[i, j] >= 0.5 else ("+" if cov[i, j] > 0 else ".") for i in range(NI)))
    # cells the panel may not occupy: anything inside the head (sample each cell at both layers)
    def world_of(i, j, zm):
        return O + R_mod @ np.array([20 * (i + imin) + 10, -14 + 20 * (j + jmin), zm])
    def in_head(p):
        x, z = int(np.floor(p[0] / 20)), int(np.floor(p[2] / 20)); y = int(np.floor(-p[1] / 8))
        if 0 <= x < NX and 0 <= y < NY and 0 <= z < NZ and H[x, y, z]: return True
        return any(np.all(p > lo_ - 1) and np.all(p < hi_ + 1) for lo_, hi_ in tt_boxes)
    blocked = np.zeros_like(mask)
    for i in range(NI):
        for j in range(NJ):
            if not mask[i, j]: continue
            for zm in (-25, -28, -31, -34, -37, -39.5):
                for du in (-9.5, -5, 0, 5, 9.5):
                    for dvv in (-9.5, -5, 0, 5, 9.5):
                        p = world_of(i, j, zm * side) + R_mod @ np.array([du, dvv, 0])
                        if in_head(p): blocked[i, j] = True
    # brackets 99781 (1x2 - 1x2 Down: hangs 20 LDU, stays above the head top) on the plate row next to the panel.
    # base plate 2x10 (3832) spans module x -40..160 (turntable studs at -10, 10, 90, 110). Bracket centres on plate
    # stud pairs; a bracket is kept only if its real solid clears the head, the risers and the turntable bases.
    BR, PLATE, PX0, PX1 = "99781", "3832", -40, 160
    PB = conn.part(BR); side_st = [s_ for s_ in PB["studs"] if abs(s_[1][2]) > 0.9]
    Rb = np.eye(3) if side > 0 else PL.rot_y(2)
    def clear_world(pts):
        for p_ in pts:
            x, z = int(np.floor(p_[0] / 20)), int(np.floor(p_[2] / 20)); y = int(np.floor(-p_[1] / 8))
            if 0 <= x < NX and 0 <= y < NY and 0 <= z < NZ and H[x, y, z]: return False
            for lo_, hi_ in tt_boxes:
                if np.all(p_ > lo_ + 0.5) and np.all(p_ < hi_ - 0.5): return False
        return True
    br_cells, valid_b = {}, []
    for bx in range(PX0 + 20, PX1 - 19, 20):
        cells_b = []
        for s_ in side_st:
            sl_ = Rb @ np.array(s_[0]); sx = bx + sl_[0]; sy = -24 + sl_[1]       # bracket origin (top) at module y -24
            cells_b.append((int(np.floor(sx / 20)) - imin, int(np.floor((sy + 24) / 20)) - jmin))
        br_cells[bx] = cells_b
        pts_w = (conn.solid_points(BR) @ Rb.T + np.array([bx, -24.0, -10.0 * side])) @ R_mod.T + O
        if all(0 <= i < NI and 0 <= j < NJ and not blocked[i, j] for i, j in cells_b) and clear_world(pts_w): valid_b.append(bx)
    # one or more "Down" brackets 40 LDU apart, then "Up" brackets (99780) raised by a 1x2 plate (3023) so that their
    # side studs fall one panel row higher (module y -34 = -14 - 20); placed where they do not overlap the others
    chosen = []
    for bx in sorted(valid_b):
        if all(abs(bx - c_) >= 40 for c_ in chosen): chosen.append(bx)
    PU = conn.part("99780"); side_up = [s_ for s_ in PU["studs"] if abs(s_[1][2]) > 0.9]
    chosen_up = []
    for bx in range(PX0 + 20, PX1 - 19, 20):
        if any(abs(bx - c_) < 40 for c_ in chosen + chosen_up): continue
        cells_b = []
        for s_ in side_up:
            sl_ = Rb @ np.array(s_[0]); sx = bx + sl_[0]; sy = -32 + sl_[1]
            cells_b.append((int(np.floor(sx / 20)) - imin, int(np.floor((sy + 24) / 20)) - jmin))
        pts_w = np.r_[conn.solid_points("99780") @ Rb.T + np.array([bx, -32.0, -10.0 * side]),
                      conn.solid_points("3023") + np.array([bx, -24.0, -10.0 * side])] @ R_mod.T + O
        if all(0 <= i < NI and 0 <= j < NJ and not blocked[i, j] for i, j in cells_b) and clear_world(pts_w):
            chosen_up.append(bx); br_cells[("up", bx)] = cells_b
    if len(chosen) + len(chosen_up) < 2: raise SystemExit("fewer than 2 bracket positions: down %s up %s placement %s" % (valid_b, chosen_up, rep.get("placement")))
    anchor_cells = [c_ for bx in chosen for c_ in br_cells[bx]] + [c_ for bx in chosen_up for c_ in br_cells[("up", bx)]]
    # anchors must touch the leaf (a bracket under a lone anchor cell would hold a stub, not the ear)
    near = ndimage.binary_dilation(mask, iterations=1)
    keep_anchor = [c_ for c_ in anchor_cells if near[c_]]
    if len(keep_anchor) < 4: keep_anchor = anchor_cells
    anchor_cells = keep_anchor
    for (i, j) in anchor_cells: mask[i, j] = True
    mask &= ~blocked
    lab2, _ = ndimage.label(mask); mask = np.isin(lab2, np.unique([lab2[i, j] for i, j in anchor_cells]))
    if os.environ.get("DEBUG_MASK"):
        print("final mask (o = removed: touches head, A = anchor):")
        for j in range(NJ): print("".join("A" if (i, j) in anchor_cells else ("#" if mask[i, j] else ("o" if blocked[i, j] else ".")) for i in range(NI)))
    rep["panel"] = dict(cells=int(mask.sum()), cells_removed_touching_head=int(blocked.sum()), brackets_down_99781_at_module_x=[int(b) for b in chosen], brackets_up_99780_at_module_x=[int(b) for b in chosen_up], plate=PLATE, side_studs=len(anchor_cells))
    # ---------------- outer layer: rounded outline pieces fitted to the fine silhouette, then plates
    sil = fine2                                                     # (NI*4, NJ*4)  x right, j down (module y)
    outline_parts = ["30565", "30357", "41769", "41770", "43722", "43723", "24299", "24307"]
    occB = np.zeros((NI, NJ), int) - 1; piecesB = []
    cand = []
    for num in outline_parts:
        if not BP.available(num, BLACK): continue
        for r in range(4):
            Q = PL.placed(num, r); top = Q["solid"].any(axis=1)      # (nx*4, nz*4) in (local x, local z)
            # panel-local z grows upward = -j : flip the mask's z axis to index rows j downward
            topj = top[:, ::-1]
            w, h = Q["nx"], Q["nz"]
            for i0 in range(NI - w + 1):
                for j0 in range(NJ - h + 1):
                    cellblk = mask[i0:i0 + w, j0:j0 + h]
                    if cellblk.sum() < 0.5 * w * h: continue
                    s_ = sil[i0 * 4:(i0 + w) * 4, j0 * 4:(j0 + h) * 4]
                    agree = int((topj & s_).sum()); extra = int((topj & ~s_).sum())
                    # compare with plain plates on the masked cells of the block
                    plain = np.repeat(np.repeat(cellblk, 4, 0), 4, 1)
                    gain = (agree - 2 * extra) - (int((plain & s_).sum()) - 2 * int((plain & ~s_).sum()))
                    if gain > 4 and not blocked[i0:i0 + w, j0:j0 + h].any():
                        cand.append((gain, num, r, i0, j0, w, h))
    cand.sort(key=lambda c: -c[0])
    for gain, num, r, i0, j0, w, h in cand:
        if (occB[i0:i0 + w, j0:j0 + h] >= 0).any(): continue
        occB[i0:i0 + w, j0:j0 + h] = len(piecesB); piecesB.append(("shaped", num, r, i0, j0, w, h))
    sizes = []                                           # (extent along x = axis 0, extent along rows = axis 1, part)
    for (L_, W_), num in BP.PLATES.items():
        if BP.available(num, BLACK):
            sizes.append((L_, W_, num))
            if L_ != W_: sizes.append((W_, L_, num))
    restB = mask & (occB < 0)
    rects, ownR = pack2d(restB, sizes)
    for (i0, j0, ex, ey, num) in rects:                 # ex cells along x, ey along rows
        occB[i0:i0 + ex, j0:j0 + ey] = len(piecesB); piecesB.append(("plate", num, 0 if ex >= ey else 1, i0, j0, ex, ey))
    # ---------------- inner layer: plates on the cells fully covered by the outer layer, staggered against it
    fullB = np.zeros_like(mask)
    for k, pc in enumerate(piecesB):
        if pc[0] == "shaped":
            _, num, r, i0, j0, w, h = pc; top = PL.placed(num, r)["solid"].any(axis=1)[:, ::-1]
            cellcov = top.reshape(w, 4, h, 4).mean(axis=(1, 3))
            fullB[i0:i0 + w, j0:j0 + h] |= cellcov >= 0.99
        else:
            _, num, rr, i0, j0, ex, ey = pc; fullB[i0:i0 + ex, j0:j0 + ey] = True
    for (i, j) in anchor_cells: fullB[i, j] = True
    rectsA, ownA = pack2d(fullB, sizes, seam_below=occB)
    import networkx as nx
    Gp = nx.Graph(); Gp.add_nodes_from([("A", k) for k in range(len(rectsA))] + [("B", k) for k in range(len(piecesB))])
    for (i, j) in zip(*np.nonzero(ownA >= 0)):
        if occB[i, j] >= 0: Gp.add_edge(("A", int(ownA[i, j])), ("B", int(occB[i, j])))
    anch = {("A", int(ownA[i, j])) for (i, j) in anchor_cells if ownA[i, j] >= 0}
    keepn = set().union(*[nx.node_connected_component(Gp, a_) for a_ in anch]) if anch else set()
    dropped = [n_ for n_ in Gp.nodes if n_ not in keepn]
    rectsA = [r_ for k, r_ in enumerate(rectsA) if ("A", k) in keepn]; piecesB = [p_ for k, p_ in enumerate(piecesB) if ("B", k) in keepn]
    rep["panel"].update(outer_pieces=len(piecesB), outer_rounded=sum(1 for p in piecesB if p[0] == "shaped"), inner_plates=len(rectsA), pieces_dropped_unlinked=len(dropped))
    # ---------------- write the module (module frame) and the assembled head (world)
    R_pm = np.c_[[1, 0, 0], [0, 0, side], np.cross([1, 0, 0], [0, 0, side])]   # panel-local -> module
    mod = []   # (colour, num, M_module, o_module, group)
    for (ax, az, tag) in ((0, 0, "1"), (100, 0, "2")):
        pass
    # turntables: centres at module (0,0,0) and (100,0,0); base and top share the origin (top of the 1-plate turntable)
    for k, mx in enumerate((0.0, 100.0)):
        mod.append((BLACK, "3680", np.eye(3), np.array([mx, -8.0, 0.0]), "base"))
        mod.append((LBG, "3679", np.eye(3), np.array([mx, -8.0, 0.0]), "module"))
    # base plate 2x10 along module X, cells x in [-40, 160], z in [-20, 20], top at y = -16
    Pp = conn.part(PLATE); Rp = np.eye(3) if (Pp["hi"][0] - Pp["lo"][0]) > (Pp["hi"][2] - Pp["lo"][2]) else PL.rot_y(1)
    mod.append((BLACK, PLATE, Rp, axis_place(PLATE, Rp, (PX0, -16, -20)), "module"))
    for bx in chosen:
        mod.append((BLACK, BR, Rb, np.array([bx, -24.0, -10.0 * side]), "module"))
    for bx in chosen_up:      # 1x2 riser plate across module X, then the Up bracket on it
        mod.append((BLACK, "3023", np.eye(3) if (conn.part("3023")["hi"][0] - conn.part("3023")["lo"][0]) > 30 else PL.rot_y(1),
                    axis_place("3023", np.eye(3) if (conn.part("3023")["hi"][0] - conn.part("3023")["lo"][0]) > 30 else PL.rot_y(1), (bx - 20, -24, -10.0 * side - 10)), "module"))
        mod.append((BLACK, "99780", Rb, np.array([bx, -32.0, -10.0 * side]), "module"))
    # panel pieces: panel-local frame -> module (R_pm); layer A at panel-local y top -32, layer B at -40 (if side>0)
    def panel_piece(num, r, i0, j0, w, h, layer_top):
        Rl = PL.rot_y(r)
        zmin = 4 - 20 * (j0 + jmin + h - 1)                       # panel-local z min (z_local = -module y)
        tmin = (20 * (i0 + imin), layer_top, zmin)
        o_l = axis_place(num, Rl, tmin)
        return R_pm @ Rl, R_pm @ o_l
    for (i0, j0, ex, ey, num) in rectsA:
        M_, o_ = panel_piece(num, 0 if ex >= ey else 1, i0, j0, ex, ey, -32)
        mod.append((BLACK, num, M_, o_, "panel"))
    for pc in piecesB:
        if pc[0] == "shaped":
            _, num, r, i0, j0, w, h = pc; M_, o_ = panel_piece(num, r, i0, j0, w, h, -40)
        else:
            _, num, rr, i0, j0, ex, ey = pc; M_, o_ = panel_piece(num, rr, i0, j0, ex, ey, -40)
        mod.append((BLACK, num, M_, o_, "panel"))
    # final check on the real geometry: a panel piece touching the head (or a turntable base) is removed
    kept, removed = [], 0
    for item in mod:
        col, num, M_, o_, g = item
        if g == "panel":
            pts = conn.solid_points(num) @ (R_mod @ M_).T + (O + R_mod @ o_)
            if any(in_head(p_) for p_ in pts[::2]): removed += 1; continue
        kept.append(item)
    mod = kept; rep["panel"]["pieces_removed_touching_head"] = removed
    json.dump(dict(rep, R_mod=R_mod.tolist(), O=O.tolist()), open(os.path.join(out, "module_report.json"), "w"), indent=1, default=float)
    # module alone (module frame)
    L = ["0 module_oreille", "0 Name: module_oreille.ldr", "0 Author: brickify V4 demonstrator (parametric ear module, Paco 400 mm)"]
    for grp in ("base", "module", "panel"):
        for (col, num, M_, o_, g) in mod:
            if g == grp: L.append(place_line(col, num, R_mod.T if g == "base" else M_, o_))
        L.append("0 STEP")
    open(os.path.join(out, "module_oreille.ldr"), "w").write("\n".join(L) + "\n")
    # head + module in world coordinates; the panel is built first, then the rest of the module, then attached
    head = [l for l in open(os.path.join(out, "head_C.ldr")).read().splitlines() if l.startswith("1 ") or l.startswith("0 STEP")]
    # supports: replace tiles under the turntables by plates of the same size (tiles have no stud), then riser columns
    TILE2PLATE = {"3070b": "3024", "3069b": "3023", "63864": "3623", "2431": "3710", "6636": "3666", "3068b": "3022"}
    c2x, c2z = cx + sgn * DV[0], cz + sgn * DV[1]
    sup_cells = [(x, z) for (ax, az) in ((cx, cz), (c2x, c2z)) for x in (ax - 1, ax) for z in (az - 1, az)]
    fixed = 0
    for k, l in enumerate(head):
        t = l.split()
        if not l.startswith("1 ") or t[14].replace(".dat", "") not in TILE2PLATE: continue
        Pt = conn.part(t[14].replace(".dat", "")); Mt = np.array(t[5:14], float).reshape(3, 3); ot = np.array(t[2:5], float)
        cs = np.array([[x, y, z] for x in (Pt["lo"][0], Pt["hi"][0]) for y in (Pt["lo"][1], Pt["hi"][1]) for z in (Pt["lo"][2], Pt["hi"][2])]) @ Mt.T + ot
        x0, x1, z0, z1 = int(round(cs[:, 0].min() / 20)), int(round(cs[:, 0].max() / 20)), int(round(cs[:, 2].min() / 20)), int(round(cs[:, 2].max() / 20))
        if any(x0 <= x < x1 and z0 <= z < z1 for (x, z) in sup_cells):
            t[14] = TILE2PLATE[t[14].replace(".dat", "")] + ".dat"; head[k] = " ".join(t); fixed += 1
    rep["placement"]["tiles_replaced_by_plates"] = fixed
    for (x, z) in sup_cells:
        for y in range(int(coltop[x, z]), yt):
            head.append(place_line(BLACK, "3024", np.eye(3), axis_place("3024", np.eye(3), (20 * x, -8 * (y + 1), 20 * z))))   # black: ear root
    W = ["0 tete_C_avec_module", "0 Name: tete_C_avec_module.ldr", "0 Author: brickify V4 demonstrator"] + head + ["0 STEP"]
    for (col, num, M_, o_, g) in mod:
        if g == "base": W.append(place_line(col, num, np.eye(3), O + R_mod @ o_))    # bases sit on the head grid
    W.append("0 STEP")
    W.append("0 BRICKIFY SUBASSEMBLY BEGIN oreille")
    for grp in ("module", "panel"):
        for (col, num, M_, o_, g) in mod:
            if g == grp: W.append(place_line(col, num, R_mod @ M_, O + R_mod @ o_))
    W.append("0 BRICKIFY SUBASSEMBLY END oreille"); W.append("0 STEP")
    open(os.path.join(out, "tete_C_avec_module.ldr"), "w").write("\n".join(W) + "\n")
    print(json.dumps(rep, default=float))

if __name__ == "__main__":
    main()
