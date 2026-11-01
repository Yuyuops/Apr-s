"""V7 adapter (whole character). Reference 3D for the comparisons: the coloured GLB (mirror-corrected like the LEGO input) placed in the head's
render frame (mm, glTF axes) with exactly the transform used by headgrid.py, so that the same frame boxes, angles and
lights apply to the mesh and to the LEGO models. The mesh is not modified, only moved and scaled.
usage: ref_glb_headframe.py <mirrored_textured.glb used for the grid> <vertex_coloured.glb> <head.npz> <out.glb>"""
import sys, numpy as np, trimesh
src_tex, src_col, npz, out = sys.argv[1:5]
d = np.load(npz); hoff = d["hoff"]
mesh = trimesh.load(src_tex, force="mesh")
geo = mesh.copy(); geo.visual = trimesh.visual.ColorVisuals(); geo.merge_vertices(merge_tex=True, merge_norm=True)
body = sorted(geo.split(only_watertight=False), key=lambda c: len(c.faces), reverse=True)[0]
scale = 400.0 / body.extents[1]
S = np.diag([scale / 8.0, scale / 3.2, scale / 8.0, 1.0]); T = np.eye(4); T[:3, 3] = -body.bounds[0]; M = S @ T
b2 = body.copy(); b2.apply_transform(M); vg = b2.voxelized(pitch=1.0)
c0 = vg.indices_to_points(np.array([[0, 0, 0]]))[0]
col = trimesh.load(src_col, force="mesh", process=False)
v = col.vertices.copy(); v[:, 0] *= -1                      # same mirror as mirror_x.py
q = trimesh.transform_points(v, M) - (c0 - 0.5) - hoff      # continuous head-cell coordinates
mm = np.c_[8.0 * q[:, 0], 3.2 * q[:, 1], -8.0 * q[:, 2]]
keepf = np.ones(len(col.faces), bool)                          # V7: whole character
out_m = trimesh.Trimesh(mm, col.faces[keepf][:, ::-1], vertex_colors=col.visual.vertex_colors, process=False)
out_m.remove_unreferenced_vertices()
out_m.export(out); print(out, "bounds mm", np.round(out_m.bounds, 1).tolist())
