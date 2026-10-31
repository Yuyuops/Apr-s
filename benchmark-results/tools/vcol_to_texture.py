"""Carry per-vertex colours in a texture so the unmodified brickify (which calls visual.to_color()) reads them.
One texel per vertex; each vertex's UV points at the centre of its own texel. Round-trip is checked exactly.
usage: vcol_to_texture.py <in_vertexcolour.glb> <out_textured.glb>"""
import sys, numpy as np, trimesh
from PIL import Image
src, out = sys.argv[1:3]
m = trimesh.load(src, force='mesh', process=False)
c = np.asarray(m.visual.vertex_colors)[:, :3].astype(np.uint8); n = len(c)
W = int(np.ceil(np.sqrt(n))); H = int(np.ceil(n / W))
img = np.zeros((H, W, 3), np.uint8); i = np.arange(n); r, k = i // W, i % W; img[r, k] = c
uv = np.c_[k / (W - 1), 1 - r / (H - 1)]
mat = trimesh.visual.material.SimpleMaterial(image=Image.fromarray(img))
m2 = trimesh.Trimesh(m.vertices, m.faces, process=False)
m2.visual = trimesh.visual.TextureVisuals(uv=uv, image=Image.fromarray(img), material=mat)
m2.export(out)
back = trimesh.load(out, force='mesh', process=False)
bc = np.asarray(back.visual.to_color().vertex_colors)[:, :3]
same = len(bc) == n and np.array_equal(bc, c)
print(f'{out}: {n} vertices, texture {W}x{H}, round-trip exact: {same}' + ('' if same else f' (max diff {np.abs(bc.astype(int)-c).max() if len(bc)==n else "len mismatch"})'))
