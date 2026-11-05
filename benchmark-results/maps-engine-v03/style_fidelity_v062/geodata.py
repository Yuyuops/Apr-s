#!/usr/bin/env python3
"""Geography for any territory : Natural Earth 10m admin-0 countries (public domain, pinned commit) cached under fixtures/ ; rasterisation of a framing window at sub-stud resolution.
 territory = ISO_A3 codes of the 'subject' land (e.g. ["ITA"]) ; every other country is 'foreign land'. Nothing here is specific to Italy.
 usage (module) : rasterise(window, grid, sub) -> dict(subject=bool[R*sub,C*sub], foreign=..., studs_per_deg_lat, lonlat_of(r,c))"""
import json, math, os, urllib.request
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); FX = os.path.join(HERE, "fixtures")
COMMIT = "ca96624a56bd078437bca8184e78163e5039ad19"; URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/%s/geojson/ne_10m_admin_0_countries.geojson" % COMMIT
def countries():
    p = os.path.join(FX, "countries_min.json")
    if not os.path.exists(p):
        os.makedirs(FX, exist_ok=True); g = json.loads(urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "lego-maps-research"}), timeout=120).read())
        out = []
        for f in g["features"]:
            pr = f["properties"]; iso = pr.get("ADM0_A3") or pr.get("ISO_A3"); out.append(dict(iso=iso, name=pr.get("NAME"), geom=f["geometry"]))
        json.dump(out, open(p, "w"))
    return json.load(open(p))
def project(window):
    """window : lat_c, lon_c, lat_span (degrees of latitude shown) ; returns (studs_per_deg_lat, k=cos(lat_c))"""
    return math.cos(math.radians(window["lat_c"]))
def rasterise(window, grid, subject_iso, sub=8):
    R, C = grid; k = project(window); spd = R / window["lat_span"]            # studs per degree of latitude (same scale in both axes : no distortion)
    def to_px(lon, lat): return ((C / 2 + (lon - window["lon_c"]) * k * spd) * sub, (R / 2 - (lat - window["lat_c"]) * spd) * sub)
    subj = Image.new("L", (C * sub, R * sub), 0); forn = Image.new("L", (C * sub, R * sub), 0); ds, df = ImageDraw.Draw(subj), ImageDraw.Draw(forn)
    lon0, lon1 = window["lon_c"] - C / (2 * k * spd), window["lon_c"] + C / (2 * k * spd); lat0, lat1 = window["lat_c"] - window["lat_span"] / 2, window["lat_c"] + window["lat_span"] / 2
    for ct in countries():
        g = ct["geom"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]; d = ds if ct["iso"] in subject_iso else df
        for poly in polys:
            xs = [p[0] for p in poly[0]]; ys = [p[1] for p in poly[0]]
            if max(xs) < lon0 - 1 or min(xs) > lon1 + 1 or max(ys) < lat0 - 1 or min(ys) > lat1 + 1: continue
            for i, ring in enumerate(poly): d.polygon([to_px(lo, la) for lo, la in ring], fill=255 if i == 0 else 0)
    S = np.asarray(subj) > 127; Fo = np.asarray(forn) > 127; Fo &= ~S
    return dict(subject=S, foreign=Fo, studs_per_deg_lat=spd, k=k, bbox=[lon0, lat0, lon1, lat1], to_lonlat=lambda r, c: (window["lon_c"] + (c - C / 2) / (k * spd), window["lat_c"] - (r - R / 2) / spd))
