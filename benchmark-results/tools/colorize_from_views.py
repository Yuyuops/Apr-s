"""Colour a geometry-only mesh by projecting the 4 reference views onto it (no generative model).

Visibility is tested by ray casting (embree). Each vertex takes its colour from the reference view that faces it most squarely and in which it is visible.
Each view is registered to the mesh by maximising the overlap (IoU) between the projected mesh silhouette and the
alpha mask of the cut-out reference image (isotropic scale + 2D offset). The references are perspective renders,
so the orthographic projection is an approximation; residual misregistration shows up at silhouette edges.
Vertices seen in no view (under the belly, top of the head) take the colour of the nearest coloured vertex.

usage: colorize_from_views.py <mesh.glb> <dog> <out.glb> <report.json>
"""
import sys, json
import numpy as np, trimesh
from PIL import Image
from scipy.spatial import cKDTree
from scipy.ndimage import binary_dilation

src, dog, out, rep = sys.argv[1:5]
D = '/home/user/Apr-s/benchmark-results/01_inputs_prepared/'

g = trimesh.load(src).to_geometry(); g.merge_vertices()
comps = sorted(g.split(only_watertight=False), key=lambda m: -len(m.faces))
m = comps[0]
info = {'source': src, 'faces_in': int(len(g.faces)), 'faces_kept_largest_component': int(len(m.faces)),
        'components_in': len(comps), 'second_component_faces': int(len(comps[1].faces)) if len(comps) > 1 else 0}
V = m.vertices.copy(); N = m.vertex_normals.copy()

# glTF: Y up, subject faces +Z, subject's left = +X. (u right, v up, depth toward camera)
views = {
    'face':          (lambda p: (p[:, 0],  p[:, 1],  p[:, 2]),  np.array([0, 0, 1.0])),
    'dos':           (lambda p: (-p[:, 0], p[:, 1], -p[:, 2]),  np.array([0, 0, -1.0])),
    'profil_gauche': (lambda p: (-p[:, 2], p[:, 1],  p[:, 0]),  np.array([1.0, 0, 0])),
    'profil_droit':  (lambda p: (p[:, 2],  p[:, 1], -p[:, 0]),  np.array([-1.0, 0, 0])),
}

def to_px(u, v, s, ox, oy, S):
    return (u * s + ox) * S, (oy - v * s) * S  # normalised [0,1] image coords * S

best_w = np.zeros(len(V)); col = np.zeros((len(V), 3)); src_view = np.full(len(V), -1)
for vi, (name, (proj, d)) in enumerate(views.items()):
    im = np.asarray(Image.open(D + f'{dog}_{name}_rgba.png').convert('RGBA')).astype(float)
    H = im.shape[0]; alpha = im[:, :, 3] > 127
    u, v, dep = proj(V)
    # coarse registration from vertical extent of the alpha mask
    ys, xs = np.nonzero(alpha)
    s0 = (ys.max() - ys.min()) / H / (v.max() - v.min())
    oy0 = ys.min() / H + v.max() * s0
    ox0 = (xs.min() + xs.max()) / 2 / H - (u.min() + u.max()) / 2 * s0
    S = 192; small = np.asarray(Image.fromarray(alpha).resize((S, S), Image.NEAREST))
    sub = np.random.default_rng(0).choice(len(V), min(len(V), 60000), replace=False)
    def iou(s, ox, oy):
        x, y = to_px(u[sub], v[sub], s, ox, oy, S); x = x.astype(int); y = y.astype(int)
        ok = (x >= 0) & (x < S) & (y >= 0) & (y < S)
        sil = np.zeros((S, S), bool); sil[y[ok], x[ok]] = True; sil = binary_dilation(sil, iterations=1)
        return (sil & small).sum() / max((sil | small).sum(), 1)
    bestp = (s0, ox0, oy0); bi = iou(*bestp)
    for step in (0.06, 0.03, 0.012, 0.005):
        improved = True
        while improved:
            improved = False
            for ds in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        p = (bestp[0] * (1 + ds * step), bestp[1] + dx * step * 0.5, bestp[2] + dy * step * 0.5)
                        val = iou(*p)
                        if val > bi + 1e-5: bi, bestp, improved = val, p, True
    s, ox, oy = bestp
    x, y = to_px(u, v, s, ox, oy, H); xi = np.clip(x.astype(int), 0, H - 1); yi = np.clip(y.astype(int), 0, H - 1)
    # visibility: ray from the vertex (offset along its normal) toward the camera; visible if nothing is hit
    if 'rays' not in globals():
        from trimesh.ray.ray_pyembree import RayMeshIntersector
        rays = RayMeshIntersector(m)
    eps = 0.003 * float(np.ptp(V, axis=0).max())
    org = V + N * eps
    vis = ~rays.intersects_any(org, np.tile(d, (len(V), 1)))
    a_ok = im[yi, xi, 3] > 127
    w = np.clip(N @ d, 0, None) ** 2 * vis * a_ok
    take = w > best_w
    best_w[take] = w[take]; col[take] = im[yi[take], xi[take], :3]; src_view[take] = vi
    info[f'view_{name}'] = {'iou_silhouette': round(float(bi), 3), 'scale': round(float(s), 4),
                            'vertices_coloured_from_this_view': int(take.sum())}

unc = src_view < 0
info['vertices_total'] = int(len(V)); info['vertices_seen_in_no_view'] = int(unc.sum())
if unc.any():
    t = cKDTree(V[~unc]); _, j = t.query(V[unc]); col[unc] = col[~unc][j]
for vi, name in enumerate(views):
    info[f'view_{name}']['vertices_final'] = int((src_view == vi).sum())
m.visual = trimesh.visual.ColorVisuals(m, vertex_colors=np.c_[col.astype(np.uint8), np.full(len(V), 255, np.uint8)])
m.export(out)
json.dump(info, open(rep, 'w'), indent=1)
print(json.dumps(info, indent=1))
