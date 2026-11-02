"""Reading of a subject GLB : vertex colours OR texture, optional internal mirror in X, explicit validation of the input data.
The geometry and the colours of the source are kept exactly (mirror = x -> -x with the winding reversed, the same operation as the former tools/mirror_x.py)."""
import numpy as np, trimesh

class InputError(ValueError): pass

def load(path, mirror_x=False):
    m = trimesh.load(path, force="mesh", process=False)
    if not hasattr(m, "faces") or len(m.faces) == 0: raise InputError("no triangle mesh in %s" % path)
    if not np.isfinite(m.vertices).all(): raise InputError("non-finite vertices in %s" % path)
    if mirror_x:
        v = m.vertices.copy(); v[:, 0] *= -1
        m = trimesh.Trimesh(v, m.faces[:, ::-1], visual=m.visual, process=False)
    m.merge_vertices()
    return m

def vertex_rgb(mesh):
    """(n, 3) uint8 colour of every vertex : texture sampled at the vertices, or the vertex colours themselves"""
    vis = mesh.visual
    if hasattr(vis, "to_color"): c = np.asarray(vis.to_color().vertex_colors)
    elif hasattr(vis, "vertex_colors"): c = np.asarray(vis.vertex_colors)
    else: raise InputError("the GLB has neither vertex colours nor a texture")
    if len(c) != len(mesh.vertices): raise InputError("colour count %d differs from vertex count %d" % (len(c), len(mesh.vertices)))
    return c[:, :3].astype(np.uint8)

def validate(path):
    """explicit report on the input : returns a dict, raises InputError if unusable"""
    m = trimesh.load(path, force="mesh", process=False); c = vertex_rgb(m)
    ext = m.extents
    rep = dict(path=str(path), vertices=int(len(m.vertices)), faces=int(len(m.faces)), kind=type(m.visual).__name__, extents=[float(x) for x in ext],
               colours_distinct=int(len(np.unique(c, axis=0))), watertight=bool(m.is_watertight), components=int(len(m.split(only_watertight=False))))
    if rep["colours_distinct"] < 2: raise InputError("the GLB carries a single colour : the colours of the subject cannot be recovered")
    if min(ext) <= 0: raise InputError("degenerate extents %s" % ext)
    return rep
