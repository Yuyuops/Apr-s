"""Tiny software renderer (numpy + PIL, flat shading, painter's algorithm) for 3MF/STL print exports : used for the before/after proofs of Sprint V13. usage : render_3mf.py OUT.png a.3mf [b.3mf ...] (side by side, 2 views each)"""
import sys, zipfile, xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw
NS = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
def load(f):
    x = ET.fromstring(zipfile.ZipFile(f).read("3D/3dmodel.model")); bases = [b.get("displaycolor")[1:7] for b in x.findall(".//m:base", NS)]; out = []
    for o in x.findall(".//m:object", NS):
        v = np.array([[float(a.get(k)) for k in "xyz"] for a in o.findall(".//m:vertex", NS)]); t = np.array([[int(a.get(k)) for k in ("v1", "v2", "v3")] for a in o.findall(".//m:triangle", NS)])
        rgb = tuple(int(bases[int(o.get("pindex", 0))][i:i + 2], 16) for i in (0, 2, 4)); out.append((v, t, rgb))
    return out
def render(objs, az, el, size=700, ctr=None, scale=None):
    allv = np.vstack([o[0] for o in objs]); ctr = allv.mean(0) if ctr is None else ctr; a, e = np.radians(az), np.radians(el)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]]); Rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]]); R = Rx @ Rz
    tris = []
    for v, t, rgb in objs:
        w = (v - ctr) @ R.T; tri = w[t]; n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
        for k in range(len(t)): tris.append((tri[k, :, 1].mean(), tri[k], n[k], rgb))      # y = depth after rotation (camera looks along +y)
    tris.sort(key=lambda q: -q[0]); ext = max(np.ptp(np.vstack([q[1] for q in tris[::50]])[:, [0, 2]], axis=0)) if scale is None else scale; s = size * 0.9 / ext
    im = Image.new("RGB", (size, size), (255, 255, 255)); d = ImageDraw.Draw(im); L = np.array([-0.4, -0.8, 0.5]); L /= np.linalg.norm(L)
    for _, tri, n, rgb in tris:
        if n[1] > 0.0: continue
        sh = 0.35 + 0.65 * max(0.0, float(n @ L)); col = tuple(int(c * sh) for c in rgb); pts = [(size / 2 + p[0] * s, size / 2 - p[2] * s) for p in tri]; d.polygon(pts, fill=col)
    return im
if __name__ == "__main__":
    out = sys.argv[1]; files = sys.argv[2:]; rows = []
    for f in files:
        o = load(f); rows.append([render(o, az, el) for az, el in ((200, 25), (160, 55))])
    W = Image.new("RGB", (700 * len(rows[0]), 700 * len(rows)), "white")
    for r, row in enumerate(rows):
        for c, im in enumerate(row): W.paste(im, (700 * c, 700 * r))
    W.save(out)
