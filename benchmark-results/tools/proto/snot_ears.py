"""Variant E: Paco's ears as sideways (SNOT) sub-assemblies on the variant-D head.

Each ear (black cells behind the head) is rebuilt as two layers of black plates whose stud axis is horizontal
(normal to the nearest grid axis, X), with visible studs facing outward like the reference ears. The ear hangs on
the side studs of "Brick 1 x 1 with Stud on 1 Side" (87087) anchors built into the head; anchors are spaced by a
multiple of 5 plates vertically so that their studs fall on the 20-LDU grid of the ear (5 plates = 40 LDU = 2 studs).
The head cells the ear passes through are cut away (slot). The ear outline is the projection of the mesh ear along X,
sampled on the 20 x 20 LDU grid of the ear. Everything is written as LDraw; checks are done by validate_v2.py.
usage: snot_ears.py <head.npz> <outdir> <name> [brickify_plus options for the head]
"""
import json, os, subprocess, sys
import numpy as np
from scipy import ndimage
from sklearn.cluster import KMeans
sys.path.insert(0, os.path.expanduser("~/bench/tools")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import partlib as PL, conn
import brickify_plus as BP

BLACK, YELLOW = 0, 14

def rot_for(stud_dir, long_dir):
    """rotation matrix: local -Y (studs) -> stud_dir, local +X -> long_dir"""
    c2 = -np.array(stud_dir, float); c1 = np.array(long_dir, float); c3 = np.cross(c1, c2)
    return np.c_[c1, c2, c3]

def line(colour, num, R, target_min):
    P = conn.part(num)
    corners = np.array([[x, y, z] for x in (P["lo"][0], P["hi"][0]) for y in (P["lo"][1], P["hi"][1]) for z in (P["lo"][2], P["hi"][2])]) @ R.T
    o = np.array(target_min, float) - corners.min(0)
    return f"1 {colour} {o[0]:g} {o[1]:g} {o[2]:g} " + " ".join(f"{v:g}" for v in R.ravel()) + f" {num}.dat"

def pack2d(mask, sizes, seam_below=None):
    """greedy rectangle packing of a 2D mask (rows, cols), largest first, + seams of the other layer under the part"""
    free = mask.copy(); out = []; NR, NC = mask.shape
    owner = -np.ones(mask.shape, int)
    while free.any():
        best = None
        for (h, w, num) in sizes:
            if h > NR or w > NC: continue
            for r in range(NR - h + 1):
                for c in range(NC - w + 1):
                    if not free[r:r + h, c:c + w].all(): continue
                    seam = 0
                    if seam_below is not None:
                        blk = seam_below[r:r + h, c:c + w]
                        ids = set(blk[blk >= 0].tolist()); seam = len(ids)   # distinct parts of the other layer bridged
                        if seam == 1 and h * w > 1 and (blk == next(iter(ids))).all() and (seam_below == next(iter(ids))).sum() == h * w:
                            continue                                            # exact copy of a plate below: no bond
                    sc = h * w + (4.0 * (seam - 1) if seam_below is not None else 0)
                    if best is None or sc > best[0]: best = (sc, r, c, h, w, num)
        _, r, c, h, w, num = best
        free[r:r + h, c:c + w] = False; owner[r:r + h, c:c + w] = len(out); out.append((r, c, h, w, num))
    return out, owner

def main():
    npz, outdir, name = sys.argv[1:4]; head_opts = sys.argv[4:]
    os.makedirs(outdir, exist_ok=True)
    d = np.load(npz); G = d["grid"].astype(int); F = d["fine"]; K = int(d["k"])
    NX, NY, NZ = G.shape
    fr = F.reshape(NX, K, NY, K, NZ, K).mean(axis=(1, 3, 5)); occ = (G >= 0) & (fr >= 0.5)
    black = occ & (G == BLACK); black[:, :, 17:] = False                      # ears are behind the head (nose/pupils excluded)
    lab, n = ndimage.label(black, structure=np.ones((3, 3, 3))); sz = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    ear_all = np.isin(lab, [k + 1 for k in range(n) if sz[k] >= 8])
    cells = np.argwhere(ear_all)
    n_ears = int(os.environ.get("EARS_PANELS", "1"))          # 1: both ears in one sideways panel (load path cranium <-> lower head)
    km = KMeans(n_ears, n_init=10, random_state=0).fit(cells * np.array([8, 3.2, 8]))
    head = occ & ~ear_all
    # also remove the thin black ear cells that the 50 % occupancy dropped but that are still in the brickify grid
    # (otherwise they serve as colour reference and paint the head black where the ear used to be)
    black_any = (G == BLACK); black_any[:, :, 17:] = False
    lab_a, _ = ndimage.label(black_any, structure=np.ones((3, 3, 3)))
    ear_any = np.isin(lab_a, np.unique(lab_a[ear_all])) & (lab_a > 0) & ndimage.binary_dilation(ear_all, iterations=1)
    G2 = G.copy(); G2[ear_any] = -1
    # the ear interior (filled with the dominant colour, yellow) is left floating once its black skin is removed:
    # drop every occupied piece that is no longer attached to the head (largest 6-connected piece touching the cut)
    occ2 = (G2 >= 0) & (fr >= 0.5)
    lab3, n3 = ndimage.label(occ2)
    keep3 = {int(l) for l in np.unique(lab3[:, 0, :]) if l > 0}
    core = occ2 & ~np.isin(lab3, list(keep3))
    G2[(G2 >= 0) & ~np.isin(lab3, list(keep3)) & ndimage.binary_dilation(ear_any, iterations=3)] = -1
    ear_core_cells = int(core.sum())
    head = (G2 >= 0) & (fr >= 0.5)                                   # head cells available for anchors
    anchors, ears, report = [], [], dict(ear_cells_removed=int(ear_any.sum()), ear_core_cells_removed=ear_core_cells)
    for k in range(n_ears):
        e = np.zeros_like(ear_all); e[tuple(cells[km.labels_ == k].T)] = True
        proj = e.any(axis=0); meanx = np.argwhere(e)[:, 0].mean()
        best = None
        for side in (+1, -1):                                   # side studs facing +X (ear at c+1) or -X (ear at c-1)
            for c in range(1, NX - 1):
                ce = c + side
                anc = [(y, z) for y in range(NY - 2) for z in range(NZ) if head[c, y:y + 3, z].all() and proj[y:y + 3, z].any()]
                carve = int((head[ce] & proj).sum())
                # head cells beyond the ear (on its outer side) would be cut off from the head by the slot
                beyond = int(sum((head[x] & proj).sum() for x in (range(ce + 1, NX) if side > 0 else range(0, ce))))
                for res in range(5):
                    sel = sorted({(y, z) for (y, z) in anc if y % 5 == res})
                    score = len(sel) - 0.15 * carve - 1.0 * beyond - float(os.environ.get("EAR_DISP_W", "1.5")) * abs(ce - meanx)
                    if len(sel) >= int(os.environ.get("EAR_MIN_ANCHORS", "6")) and (best is None or score > best[0]): best = (score, side, c, ce, res, sel, carve)
        _, side, c, ce, res, sel, carve = best
        beyond = int(sum((head[x] & proj).sum() for x in (range(ce + 1, NX) if side > 0 else range(0, ce))))
        # keep anchors that do not share cells (3 plates tall, so same z needs >= 5 plates apart: already by residue)
        r_anchor = 3 if side > 0 else 1
        for (y, z) in sel:
            anchors.append(dict(num="87087", r=r_anchor, x0=int(c), y0=int(y), z0=int(z), w=1, d=1, h=3, colour=YELLOW, anchor=True))
        ears.append(dict(k=k, side=side, c=c, ce=ce, res=res, sel=sel, e=e, proj=proj))
        report[f"ear{k}"] = dict(cells=int(e.sum()), mean_x=round(float(meanx), 1), anchor_column=int(c), ear_column=int(ce), studs_facing="+X" if side > 0 else "-X",
                                 anchors=len(sel), slot_cells=carve, head_cells_beyond_ear=beyond)
    for ear in ears:
        side, c, sel = ear["side"], ear["c"], ear["sel"]
        y0a, z0a = sel[0]
        ystud0 = -(y0a + 3) * 8 + 10                               # LDraw y of the first anchor's side stud centre
        # ear rows (20 LDU) covering the projected ear; row r centre = ystud0 + 20 r
        e = ear["e"]; region = ndimage.binary_dilation(e, iterations=1) & ~head
        fine = np.zeros(F.shape, bool)
        for (x, y, z) in np.argwhere(region): fine[x * K:(x + 1) * K, y * K:(y + 1) * K, z * K:(z + 1) * K] = F[x * K:(x + 1) * K, y * K:(y + 1) * K, z * K:(z + 1) * K]
        pf = fine.any(axis=0)                                      # (y_fine up, z_fine): projection along X
        yf_ld = -(np.arange(pf.shape[0]) + 0.5) * 2                # LDraw y of each fine row
        ylo, yhi = yf_ld[pf.any(axis=1)].min(), yf_ld[pf.any(axis=1)].max()
        r0 = int(np.floor((ylo - ystud0) / 20)) - 1; r1 = int(np.ceil((yhi - ystud0) / 20)) + 1
        rows = [r for r in range(r0, r1 + 1) if ystud0 + 20 * r + 10 <= 0]      # stay above the support plane (neck cut)
        mask = np.zeros((len(rows), NZ), bool)
        for i, r in enumerate(rows):
            yc = ystud0 + 20 * r
            sel_rows = np.abs(yf_ld - yc) < 10
            for z in range(NZ):
                blk = pf[sel_rows][:, z * K:(z + 1) * K]
                if blk.size and blk.mean() >= 0.5: mask[i, z] = True
        anchor_cells = []; valid = []
        for (y, z) in sel:                                          # every anchor stud must be under the ear
            i = int(round(((-(y + 3) * 8 + 10) - ystud0) / 20)) - r0
            if not (0 <= i < len(rows)): continue                   # stud below the support plane: anchor unusable
            mask[i, z] = True; anchor_cells.append((i, z)); valid.append((y, z))
        dropped_anchor = [q for q in anchors if q["x0"] == c and (q["y0"], q["z0"]) in set(sel) - set(valid)]
        for q in dropped_anchor: anchors.remove(q)
        sel = valid; ear["sel"] = sel; report[f"ear{ear['k']}"]["anchors"] = len(sel)
        lab2, n2 = ndimage.label(mask)
        keep = np.unique([lab2[i, z] for (i, z) in anchor_cells])
        mask = np.isin(lab2, keep[keep > 0])                       # only the part of the ear tied to anchors
        # slot: every head cell of the ear column overlapped by an ear plate row
        ce = ear["ce"]; carved = 0
        for i, r in enumerate(rows):
            yc = ystud0 + 20 * r
            for y in range(NY):
                if -(y + 1) * 8 < yc + 10 and -y * 8 > yc - 10:
                    for z in np.nonzero(mask[i])[0]:
                        if G2[ce, y, z] >= 0: G2[ce, y, z] = -1; carved += 1
        ear.update(mask=mask, rows=rows, ystud0=ystud0, anchor_cells=anchor_cells); report[f"ear{ear['k']}"]["slot_cells"] = carved
    # ---- head (variant D settings) with anchors pre-placed and ears/slots removed
    mod = os.path.join(outdir, "head_without_ears.npz")
    np.savez_compressed(mod, grid=G2, surface=d["surface"], fine=F, k=K, neck=d["neck"], full_shape=d["full_shape"], hoff=d["hoff"])
    pre = os.path.join(outdir, "anchors.json"); json.dump(anchors, open(pre, "w"))
    cmd = [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "brickify_plus.py"), mod, outdir, name + "_head",
           "--preplaced", pre] + head_opts
    rep_head = json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip().splitlines()[-1])
    head_ldr = open(os.path.join(outdir, name + "_head.ldr")).read().splitlines()
    # ---- ears: two black plate layers on the side studs
    sizes = []
    for (L, W), num in BP.PLATES.items():
        if not BP.available(num, BLACK): continue
        sizes.append((W, L, num))
        if L != W: sizes.append((L, W, num))
    out_lines = []
    for ear in ears:
        side, c, sel = ear["side"], ear["c"], ear["sel"]; mask, rows, ystud0 = ear["mask"], ear["rows"], ear["ystud0"]; anchor_cells = ear["anchor_cells"]
        X0 = 20 * (c + 1) if side > 0 else 20 * c                  # anchor face
        stud_dir = (side, 0, 0)
        layerA, ownA = pack2d(mask, sizes)
        layerB, ownB = pack2d(mask, sizes, seam_below=ownA)
        # keep only plates linked to an anchored plate (inner plates on anchor studs; inner <-> outer by overlap)
        import networkx as nx
        Gg = nx.Graph(); Gg.add_nodes_from([("A", i) for i in range(len(layerA))] + [("B", j) for j in range(len(layerB))])
        for (r_, c_) in zip(*np.nonzero(mask)):
            Gg.add_edge(("A", int(ownA[r_, c_])), ("B", int(ownB[r_, c_])))
        anch = {("A", int(ownA[i, z])) for (i, z) in anchor_cells}
        keep_nodes = set().union(*[nx.node_connected_component(Gg, a_) for a_ in anch]) if anch else set()
        dropped = [n_ for n_ in Gg.nodes if n_ not in keep_nodes]
        dropped_cells = int(sum(layerA[i][2] * layerA[i][3] for (L_, i) in dropped if L_ == "A"))
        layerA = [pl for i, pl in enumerate(layerA) if ("A", i) in keep_nodes]
        layerB = [pl for j, pl in enumerate(layerB) if ("B", j) in keep_nodes]
        out_lines.append(f"0 BRICKIFY SUBASSEMBLY BEGIN ear{ear['k']}")
        for li, layer in enumerate((layerA, layerB)):
            xmin = X0 + 8 * li if side > 0 else X0 - 8 * (li + 1)
            for (r, zc, h, w, num) in layer:
                L, W = max(h, w), min(h, w)
                long_dir = (0, 0, 1) if w >= h else (0, 1, 0)       # long side along Z, or along Y (rows)
                R = rot_for(stud_dir, long_dir)
                ytop = ystud0 + 20 * rows[r] - 10                   # LDraw y of the top edge of row r
                out_lines.append(line(BLACK, num, R, (xmin, ytop, 20 * zc)))
            out_lines.append("0 STEP")
        out_lines.append(f"0 BRICKIFY SUBASSEMBLY END ear{ear['k']}")
        report[f"ear{ear['k']}"].update(ear_cells_20ldu=int(mask.sum()), plates_layer_inner=len(layerA), plates_layer_outer=len(layerB), ear_cells_dropped_unattached=dropped_cells)
    body = [l for l in head_ldr if l.strip()]
    res = body + ["0 STEP"] + out_lines
    open(os.path.join(outdir, name + ".ldr"), "w").write("\n".join([f"0 {name}", f"0 Name: {name}.ldr", "0 Author: brickify_plus prototype, variant E (SNOT ears)"] + res[3:]) + "\n")
    report["head"] = {k: v for k, v in rep_head.items() if k != "settings"}
    json.dump(report, open(os.path.join(outdir, name + "_report.json"), "w"), indent=1, default=int)
    print(json.dumps(report, default=int))

if __name__ == "__main__":
    main()
