"""Pre-mirror a GLB in X (x -> -x, face winding reversed) so that brickify's own X/Z-preserving, Y-flipping
LDraw export (a reflection) yields a model with the same handedness as the reference images.
usage: mirror_x.py in.glb out.glb"""
import sys, numpy as np, trimesh
m = trimesh.load(sys.argv[1], force='mesh', process=False)
v = m.vertices.copy(); v[:, 0] *= -1
m2 = trimesh.Trimesh(v, m.faces[:, ::-1], visual=m.visual, process=False)
m2.export(sys.argv[2])
b = trimesh.load(sys.argv[2], force='mesh', process=False)
print(sys.argv[2], 'colours identical:', np.array_equal(np.asarray(b.visual.to_color().vertex_colors), np.asarray(m.visual.to_color().vertex_colors)))
