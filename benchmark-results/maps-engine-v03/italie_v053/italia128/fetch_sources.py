#!/usr/bin/env python3
"""Fetches and caches the two real sources of the Italia 128 model (pinned, licences recorded in fixtures/SOURCES.md):
 - Natural Earth 10m admin-0 countries + populated places (public domain), pinned commit ;
 - AWS Terrain Tiles 'terrarium' z=6 (elevation composite : SRTM, GMTED, EU-DEM... ; open data, attribution required).
Writes fixtures/italy_polygons.json, fixtures/places.json, fixtures/dem_z6.npy (metres) with the geographic window and SHA-256."""
import hashlib, io, json, math, os, urllib.request
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); FX = os.path.join(HERE, "fixtures"); os.makedirs(FX, exist_ok=True)
COMMIT = "ca96624a56bd078437bca8184e78163e5039ad19"; RAW = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/%s/geojson/" % COMMIT
BBOX = (6.15, 35.0, 19.35, 47.65); Z = 6
def get(url): return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "lego-maps-research"}), timeout=60).read()
def main():
    out = {}
    c = json.loads(get(RAW + "ne_10m_admin_0_countries.geojson"))
    ita = [f for f in c["features"] if f["properties"].get("ADM0_A3") == "ITA" or f["properties"].get("ISO_A3") == "ITA" or f["properties"].get("NAME") == "Italy"]
    json.dump(ita[0]["geometry"], open(os.path.join(FX, "italy_polygons.json"), "w"))
    p = json.loads(get(RAW + "ne_10m_populated_places_simple.geojson"))
    places = [dict(name=f["properties"]["name"], lon=f["geometry"]["coordinates"][0], lat=f["geometry"]["coordinates"][1], pop=f["properties"].get("pop_max", 0)) for f in p["features"] if f["properties"].get("adm0_a3") == "ITA"]
    json.dump(sorted(places, key=lambda x: -x["pop"])[:40], open(os.path.join(FX, "places.json"), "w"), indent=0)
    n = 2 ** Z; x0 = int((BBOX[0] + 180) / 360 * n); x1 = int((BBOX[2] + 180) / 360 * n)
    ytile = lambda lat: int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n); y0, y1 = ytile(BBOX[3]), ytile(BBOX[1])
    W, H = (x1 - x0 + 1) * 256, (y1 - y0 + 1) * 256; dem = np.zeros((H, W), np.float32)
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            im = np.asarray(Image.open(io.BytesIO(get("https://s3.amazonaws.com/elevation-tiles-prod/terrarium/%d/%d/%d.png" % (Z, x, y)))).convert("RGB"), np.float32)
            dem[(y - y0) * 256:(y - y0 + 1) * 256, (x - x0) * 256:(x - x0 + 1) * 256] = im[..., 0] * 256 + im[..., 1] + im[..., 2] / 256 - 32768
    np.save(os.path.join(FX, "dem_z6.npy"), dem)
    meta = dict(commit=COMMIT, bbox=BBOX, zoom=Z, tiles_x=[x0, x1], tiles_y=[y0, y1], dem_shape=list(dem.shape), dem_sha256=hashlib.sha256(dem.tobytes()).hexdigest(), dem_min=float(dem.min()), dem_max=float(dem.max()))
    json.dump(meta, open(os.path.join(FX, "sources_meta.json"), "w"), indent=1); print(meta)
if __name__ == "__main__": main()
