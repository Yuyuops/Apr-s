"""V7 adapter: the WHOLE character grid (same voxeliser, colours and fine grid as headgrid.py, no crop).
Paco head + ears grid at 400 mm, built with brickify's own (unmodified) voxeliser and colour functions,
plus a fine occupancy grid (K sub-cells per stud, KY per plate) of the same mesh in the same frame.
usage: headgrid.py <textured_mirrored.glb> <out.npz> [--height-mm 400] [--neck auto|<layer>]"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import argparse, os, sys, json
import numpy as np, trimesh
sys.path.insert(0, BRICKIFY_PIPELINE)
import brickify as B          # original engine, imported, not modified

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("glb"); ap.add_argument("out")
    ap.add_argument("--height-mm", type=float, default=400); ap.add_argument("--neck", default="auto")
    ap.add_argument("--exclude", required=True); ap.add_argument("--palette-passes", type=int, default=4)
    ap.add_argument("--ldconfig", default=LDRAW + "/LDConfig.ldr")
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--mirror-x", action="store_true", help="mirror the source in X (brickify's LDraw export is a reflection)")
    a = ap.parse_args()
    # --- identical to brickify.load_and_voxelize, but we keep the transform to build the fine grid too
    import glb_io
    mesh = glb_io.load(a.glb, mirror_x=a.mirror_x)
    vcol = glb_io.vertex_rgb(mesh)
    geo = mesh.copy(); geo.visual = trimesh.visual.ColorVisuals(); geo.merge_vertices(merge_tex=True, merge_norm=True)
    body = sorted(geo.split(only_watertight=False), key=lambda c: len(c.faces), reverse=True)[0]
    scale = a.height_mm / body.extents[1]
    S = np.diag([scale / B.STUD_MM, scale / B.PLATE_MM, scale / B.STUD_MM, 1.0]); T = np.eye(4); T[:3, 3] = -body.bounds[0]; M = S @ T
    body.apply_transform(M)
    vg = body.voxelized(pitch=1.0).fill()
    mat = np.asarray(vg.matrix, bool); idx = np.argwhere(mat); centers = vg.indices_to_points(idx)
    from scipy.spatial import cKDTree
    tree = cKDTree(trimesh.transform_points(mesh.vertices, M))
    th = dict(blue_s=0.18, pink_s=0.16, white_v=0.84, white_s=0.16, black_v=0.25)  # brickify defaults
    grid, surface, srgb, sidx = B.build_grid(mat, idx, centers, tree, vcol, th)
    B.load_ldconfig(a.ldconfig)
    excl = tuple(int(c) for c in a.exclude.split(",") if c.strip())
    grid, used = B.palette_colours(grid, surface, srgb, sidx, min_frac=0.01, passes=a.palette_passes, contrast_max=32.0, gain=1.0, exclude=excl)
    grid = B.fill_interior(grid, surface, mode="dominant")
    occ_y = np.where((grid >= 0).any(axis=(0, 2)))[0]; occ_x = np.where((grid >= 0).any(axis=(1, 2)))[0]; occ_z = np.where((grid >= 0).any(axis=(0, 1)))[0]
    off = np.array([occ_x.min(), occ_y.min(), occ_z.min()])
    grid = grid[occ_x.min():occ_x.max() + 1, occ_y.min():occ_y.max() + 1, occ_z.min():occ_z.max() + 1]
    surface = surface[occ_x.min():occ_x.max() + 1, occ_y.min():occ_y.max() + 1, occ_z.min():occ_z.max() + 1]
    print("full grid", grid.shape, "cells", int((grid >= 0).sum()))
    # --- neck: the narrowest layer between 55 % and 80 % of the height
    area = (grid >= 0).sum(axis=(0, 2)); ny = grid.shape[1]
    if a.neck == "auto":
        lo, hi = int(0.55 * ny), int(0.80 * ny)
        neck = lo + int(np.argmin(area[lo:hi]))
    else:
        neck = int(a.neck)
    print("layer areas around neck:", {int(y): int(area[y]) for y in range(neck - 4, neck + 5)}, "-> neck layer", neck)
    head = grid[:, neck:, :]
    hx = np.where((head >= 0).any(axis=(1, 2)))[0]; hz = np.where((head >= 0).any(axis=(0, 1)))[0]
    head_in_full = np.array([hx.min(), neck, hz.min()])               # head grid cell (0,0,0) in the full grid
    # --- fine occupancy of the same mesh, whole character
    k = a.k
    vgf = body.voxelized(pitch=1.0 / k).fill()
    pf = vgf.indices_to_points(np.argwhere(vgf.matrix))
    c0 = vg.indices_to_points(np.array([[0, 0, 0]]))[0]
    rel = (pf - (c0 - 0.5)) * k
    fi = np.floor(rel + 1e-6).astype(int) - off * k
    NX, NY, NZ = grid.shape
    ok = (fi[:, 0] >= 0) & (fi[:, 0] < NX * k) & (fi[:, 1] >= 0) & (fi[:, 1] < NY * k) & (fi[:, 2] >= 0) & (fi[:, 2] < NZ * k)
    fine = np.zeros((NX * k, NY * k, NZ * k), bool); fine[tuple(fi[ok].T)] = True
    print("full grid", grid.shape, "cells", int((grid >= 0).sum()), "fine/coarse", round(fine.sum() / k**3 / max((grid >= 0).sum(), 1), 3), "head in full", head_in_full)
    np.savez_compressed(a.out, grid=grid, surface=surface, fine=fine, k=k, neck=neck, full_shape=np.array(grid.shape), hoff=off, head_in_full=head_in_full)

if __name__ == "__main__":
    main()
