"""Geographic layer shared by the V0.5.5 generators : projection (identical to compose.py), land coverage from Natural Earth, elevation sampling from Terrain Tiles.
Everything is computed on demand from fixtures/ and artistic_scale_config.json (no Italy constant in the code)."""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); CFG = json.load(open(os.path.join(HERE, "artistic_scale_config.json"))); G = CFG["geographic"]
GR, GC = G["grid_studs"]; BB = G["window_lonlat"]; CLON, CLAT = (BB[0] + BB[2]) / 2, (BB[1] + BB[3]) / 2; K_ = math.cos(math.radians(CLAT)); SCALE = G["fill_fraction"] * max(GR, GC) / max((BB[2] - BB[0]) * K_, BB[3] - BB[1])
def to_grid(lon, lat): return GR / 2 - (lat - CLAT) * SCALE, GC / 2 + (lon - CLON) * K_ * SCALE
def to_lonlat(r, c): return CLON + (c - GC / 2) / (K_ * SCALE), CLAT - (r - GR / 2) / SCALE
_dem = None; _meta = None
def dem():
    global _dem, _meta
    if _dem is None: _dem = np.load(os.path.join(HERE, G["dem"]["file"])); _meta = json.load(open(os.path.join(HERE, "fixtures/sources_meta.json")))
    return _dem, _meta
def land_coverage(ss=8):
    geo = json.load(open(os.path.join(HERE, G["source_polygons"]))); img = Image.new("L", (GC * ss, GR * ss), 0); d = ImageDraw.Draw(img)
    for poly in (geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]):
        for i, ring in enumerate(poly): d.polygon([(to_grid(lo, la)[1] * ss, to_grid(lo, la)[0] * ss) for lo, la in ring], fill=255 if i == 0 else 0)
    return np.asarray(img, np.float32).reshape(GR, ss, GC, ss).mean(axis=(1, 3)) / 255.0
def elevation_fine(r0, r1, c0, c1, sub=2):
    """elevation (m) of the window rows r0..r1, cols c0..c1 (studs) at sub x sub samples per stud : array ((r1-r0)*sub, (c1-c0)*sub)"""
    dm, meta = dem(); n = 2 ** meta["zoom"]; x0, y0 = meta["tiles_x"][0], meta["tiles_y"][0]; out = np.zeros(((r1 - r0) * sub, (c1 - c0) * sub), np.float32)
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            lo, la = to_lonlat(r0 + (i + .5) / sub, c0 + (j + .5) / sub); px = ((lo + 180) / 360 * n - x0) * 256; py = ((1 - math.asinh(math.tan(math.radians(la))) / math.pi) / 2 * n - y0) * 256
            out[i, j] = dm[int(min(max(py, 0), dm.shape[0] - 1)), int(min(max(px, 0), dm.shape[1] - 1))]
    return np.maximum(out, 0)
def elevation_stud(r0, r1, c0, c1, sub=4, peak_boost=None):
    """per-stud elevation : mean + peak_boost*(p90-mean) of the sub x sub samples (same rule as compose.py, finer sampling)"""
    pb = G["dem"]["peak_boost"] if peak_boost is None else peak_boost; f = elevation_fine(r0, r1, c0, c1, sub); R, C = r1 - r0, c1 - c0
    blk = f.reshape(R, sub, C, sub).transpose(0, 2, 1, 3).reshape(R, C, sub * sub); return blk.mean(-1) + pb * (np.percentile(blk, 90, axis=-1) - blk.mean(-1)), blk.max(-1)
