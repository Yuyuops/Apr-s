#!/usr/bin/env python3
"""Renders the third test map (Scotland, northern England, northern Ireland) from NATURAL EARTH vector data (public domain) as a flat-colour 512 x 512 PNG.
SOURCE / LICENCE : Natural Earth (naturalearthdata.com), https://github.com/nvkelso/natural-earth-vector — "Everything here is public domain ... No permission is needed to use Natural Earth. Crediting the authors is unnecessary" (LICENSE.md of the repository, copied in LICENCE_NATURAL_EARTH.md). Attribution given anyway : "Made with Natural Earth. Free vector and raster map data @ naturalearthdata.com."
Only these layers are used (10 m) : land, admin_1 states / provinces (nations), lakes, rivers_lake_centerlines, roads (major highways), geography_regions_polys (the 'Grampian Mts.' range polygon : a DESCRIPTIVE region of the source, NOT an elevation), populated_places_simple.
There is NO elevation data in this map : any relief built from it is ARTISTIC (declared per class), never real altitude.
usage: python make_ecosse_map.py <dir with the geojson files> <out.png> [--text]"""
import json, math, sys, os
from PIL import Image, ImageDraw, ImageFont
BBOX = (-8.6, 54.0, 0.8, 59.2)          # lon0, lat0, lon1, lat1  (Scotland, northern England, Northern Ireland)
S = 512
COL = dict(sea=(49, 92, 156), scotland=(222, 205, 160), england=(236, 226, 190), ireland=(110, 158, 98), lake=(120, 170, 215), river=(120, 170, 215), road=(176, 128, 84), range=(150, 118, 78), city=(170, 55, 40), text=(240, 240, 240))
def proj(lon, lat):
    lat0 = (BBOX[1] + BBOX[3]) / 2; kx = math.cos(math.radians(lat0)); w = (BBOX[2] - BBOX[0]) * kx; h = (BBOX[3] - BBOX[1]); sc = S / max(w, h)
    return ((lon - BBOX[0]) * kx * sc + (S - w * sc) / 2, (BBOX[3] - lat) * sc + (S - h * sc) / 2)
def load(d, name): return json.load(open(os.path.join(d, name + ".geojson")))["features"]
def polys(geom):
    if geom["type"] == "Polygon": return [geom["coordinates"]]
    if geom["type"] == "MultiPolygon": return geom["coordinates"]
    return []
def lines(geom):
    if geom["type"] == "LineString": return [geom["coordinates"]]
    if geom["type"] == "MultiLineString": return geom["coordinates"]
    return []
def draw_poly(dr, geom, fill):
    for rings in polys(geom):
        dr.polygon([proj(*p[:2]) for p in rings[0]], fill=fill)
        for hole in rings[1:]: dr.polygon([proj(*p[:2]) for p in hole], fill=None)
def inbox(geom, pad=1.0):
    xs = []; ys = []
    def walk(c):
        if not c: return
        if isinstance(c[0], (int, float)): xs.append(c[0]); ys.append(c[1])
        else:
            for x in c: walk(x)
    walk(geom["coordinates"])
    if not xs: return False
    return not (max(xs) < BBOX[0] - pad or min(xs) > BBOX[2] + pad or max(ys) < BBOX[1] - pad or min(ys) > BBOX[3] + pad)
def main(d, out, text=False):
    img = Image.new("RGB", (S, S), COL["sea"]); dr = ImageDraw.Draw(img)
    for f in load(d, "ne_10m_land"):
        if inbox(f["geometry"]): draw_poly(dr, f["geometry"], COL["england"])
    land = Image.new("L", (S, S), 0); ld = ImageDraw.Draw(land)
    for f in load(d, "ne_10m_land"):
        if inbox(f["geometry"]):
            for rings in polys(f["geometry"]): ld.polygon([proj(*p[:2]) for p in rings[0]], fill=255)
    for f in load(d, "ne_10m_admin_0_countries"):
        nm = f["properties"].get("NAME") or f["properties"].get("ADMIN")
        if nm == "Ireland" and inbox(f["geometry"]): draw_poly(dr, f["geometry"], COL["ireland"])
    for f in load(d, "ne_10m_admin_1_states_provinces"):
        p = f["properties"]
        if p.get("adm0_a3") == "GBR" and inbox(f["geometry"], 0.2):
            reg = (p.get("region") or p.get("name") or "").lower()
            draw_poly(dr, f["geometry"], COL["scotland"] if "scotland" in reg else COL["ireland"] if "northern ireland" in reg or "ireland" in reg else COL["england"])
    rng = Image.new("RGB", (S, S), COL["range"]); rm = Image.new("L", (S, S), 0); rd = ImageDraw.Draw(rm)
    for f in load(d, "ne_10m_geography_regions_polys"):
        if f["properties"].get("NAME") == "Grampian Mts.": draw_poly(rd, f["geometry"], 255)
    from PIL import ImageChops
    img.paste(rng, (0, 0), ImageChops.multiply(rm, land)); dr = ImageDraw.Draw(img)
    for f in load(d, "ne_10m_lakes"):
        if inbox(f["geometry"], 0.1): draw_poly(dr, f["geometry"], COL["lake"])
    for f in load(d, "ne_10m_rivers_lake_centerlines"):
        if inbox(f["geometry"], 0.1):
            for l in lines(f["geometry"]): dr.line([proj(*p[:2]) for p in l], fill=COL["river"], width=3)
    for f in load(d, "ne_10m_roads"):
        if inbox(f["geometry"], 0.1) and f["properties"].get("type") == "Major Highway":
            for l in lines(f["geometry"]): dr.line([proj(*p[:2]) for p in l], fill=COL["road"], width=4)
    for f in load(d, "ne_10m_populated_places_simple"):
        p = f["properties"]; lon, lat = f["geometry"]["coordinates"][:2]
        if BBOX[0] < lon < BBOX[2] and BBOX[1] < lat < BBOX[3] and (p.get("pop_max") or 0) > 400000:
            x, y = proj(lon, lat); dr.ellipse((x - 5, y - 5, x + 5, y + 5), fill=COL["city"])
    if text:
        try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
        except Exception: font = ImageFont.load_default()
        dr.text((28, 24), "SCOTLAND", fill=COL["text"], font=font)
    img.save(out)
if __name__ == "__main__": main(sys.argv[1], sys.argv[2], "--text" in sys.argv)
