import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))                  # maps-engine-v0
E1 = os.path.normpath(os.path.join(ROOT, "..", "20_portable_engine", "engine"))   # engine 1, read only
if E1 not in sys.path: sys.path.insert(0, E1)
import numpy as np
STUD = 20.0; PLATE = 8.0                           # LDU
# plates that really exist in the LDraw library : (long side, short side) in studs -> part number (all verified with engine-1 conn.part)
PLATES = {(1, 1): "3024", (2, 1): "3023", (3, 1): "3623", (4, 1): "3710", (6, 1): "3666", (8, 1): "3460", (10, 1): "4477", (12, 1): "60479",
          (2, 2): "3022", (3, 2): "3021", (4, 2): "3020", (6, 2): "3795", (8, 2): "3034", (10, 2): "3832", (12, 2): "2445",
          (4, 4): "3031", (6, 4): "3032", (8, 4): "3035", (10, 4): "3030", (12, 4): "3029", (6, 6): "3958", (8, 6): "3036", (10, 6): "3033", (8, 8): "41539"}
def lab(rgb):
    """CIE Lab from sRGB 0-255, array (...,3)"""
    c = np.asarray(rgb, float) / 255.0; c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]); xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)
def dE(a, b): return float(np.linalg.norm(lab(a) - lab(b)))
