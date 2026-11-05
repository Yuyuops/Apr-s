"""Altitude -> relief field for the LEGO sculptor. Real DEM levels (Terrain Tiles, per-stud elevation) are turned into a plate-height field that keeps the
real ranges (positions, relative heights, coast) and adds controlled, range-aligned irregularity : ridge lines (positive topographic position), valleys (negative),
sub-stud ridged noise scaled by the local relief, concave 'horn' sharpening of the high ground. The vertical exaggeration is declared (VE).
Neighbouring land is kept only as a hinterland band beyond the Italian border, tapered, so the Alps do not end on a sea cliff."""
import os, sys
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "italia"))
import geo
from sculpt import fbm
OUT = os.path.join(HERE, "italia", "output")
def make_field(r0, c0, R, C, seed=5, VE=1.45, band=6, sharpen=1.18, detail=6.0, ridge_gain=2.6, valley_depth=2.6):
    e128 = np.load(os.path.join(OUT, "elev_stud_128.npy")); ita128 = np.load(os.path.join(OUT, "land_128.npy")); all128 = np.load(os.path.join(OUT, "land_all_128.npy"))
    dist = ndimage.distance_transform_edt(~ita128); sl = (slice(r0, r0 + R), slice(c0, c0 + C))
    e = e128[sl].copy(); ita = ita128[sl]; hint = all128[sl] & (dist[sl] <= band) & ~ita; land = ita | hint
    t = np.clip(dist[sl] / band, 0, 1); smooth = t * t * (3 - 2 * t); fac = np.where(hint, 1 - 0.85 * smooth, 1.0); e_eff = e * fac
    m = geo.G["dem"]["metres_to_levels"]; level = np.where(land, m["gain"] * (np.maximum(e_eff, 0) / m["unit_m"]) ** m["exponent"] * VE, 0.0); h = 3.0 * level
    rng = np.random.RandomState(seed); tpi = e_eff - ndimage.gaussian_filter(e_eff, 3.0); rs = ndimage.gaussian_filter(np.abs(tpi), 3.0) + 60.0
    ridge = np.clip(tpi / rs, 0, 2.0); vall = np.clip(-tpi / rs, 0, 1.5) / 1.5
    n = fbm((R, C), [2.0, 1.0], [1, .8], rng); rn = 1 - np.abs(np.tanh(n * 1.4)); amp = detail * np.clip(rs / 380.0, 0, 1.5) * np.clip(level / 2.0, 0, 1)
    h = h + ridge_gain * ridge * np.clip(level / 2.5, 0, 1) - valley_depth * vall * np.clip(level / 2.5, 0, 1) + (rn - 0.55) * amp
    Hm = max(h.max(), 1.0); h = Hm * (np.clip(h, 0, None) / Hm) ** sharpen; h = np.where(land, np.maximum(h, 3.0), 0.0)
    return dict(h=h, land=land, elev=np.where(land, e, 0.0), valley=vall, beach_ok=ita, hinterland=hint, ridge=ridge, info=dict(VE=VE, band=band, max_level=float(h.max() / 3), land_cells=int(land.sum()), italy_cells=int(ita.sum()), hinterland_cells=int(hint.sum())))
