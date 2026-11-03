#!/usr/bin/env python3
"""Reproducible Italy raster from a pinned, public-domain Natural Earth GeoJSON.

The Italian coastline (including Sicily and Sardinia) is geographic. The
surface colour and alpine / Apennine bands are an ORIGINAL ARTISTIC STYLE;
these layers are NOT a digital elevation model. Output: 512x512 RGB PNG.
"""
import argparse
import hashlib
import io
import json
import math
import time
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

NE_COMMIT = "ca96624a56bd078437bca8184e78163e5039ad19"
SOURCE_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
    + NE_COMMIT + "/geojson/ne_10m_admin_0_countries.geojson"
)
LICENCE_URL = "https://www.naturalearthdata.com/about/terms-of-use/"
S = 1024
SIZE = 512
BBOX = (6.15, 35.0, 19.35, 47.65)  # geographic window, lon/lat
SEA = "#24639e"
BEACH = "#dec49b"
GREEN = "#6d995c"
MOUNTAINS = "#aa8051"
ALPS_SNOW = "#f1e2c2"
HILLS = "#b89360"
VILLAGE = "#b34932"
CITIES = {
    "Milano": (9.19, 45.46), "Venezia": (12.33, 45.44),
    "Firenze": (11.25, 43.77), "Roma": (12.50, 41.90),
    "Napoli": (14.25, 40.85), "Bari": (16.87, 41.12),
    "Palermo": (13.36, 38.11), "Cagliari": (9.12, 39.22),
}


def project(lon, lat):
    k = math.cos(math.radians((BBOX[1] + BBOX[3]) / 2))
    w = (BBOX[2] - BBOX[0]) * k
    h = BBOX[3] - BBOX[1]
    scale = 0.94 * S / max(w, h)
    return (S / 2 + (lon - sum([BBOX[0], BBOX[2]]) / 2) * k * scale,
            S / 2 - (lat - sum([BBOX[1], BBOX[3]]) / 2) * scale)


def polygons(geometry):
    if geometry["type"] == "Polygon":
        yield geometry["coordinates"]
    elif geometry["type"] == "MultiPolygon":
        yield from geometry["coordinates"]
    else:
        raise ValueError("Italy geometry was not Polygon/MultiPolygon")


def fetch_source():
    request = urllib.request.Request(
        SOURCE_URL, headers={"User-Agent": "LEGO-Maps-Italy-V0.3/1.0"}
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return response.read()
        except (OSError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def country_feature(data):
    features = json.loads(data)["features"]
    matches = [x for x in features
               if x.get("properties", {}).get("ADMIN") == "Italy"
               or x.get("properties", {}).get("ADM0_A3") == "ITA"
               or x.get("properties", {}).get("NAME_EN") == "Italy"]
    if len(matches) != 1:
        raise RuntimeError("Expected exactly one Italy feature, got " + str(len(matches)))
    return matches[0]


def draw_band(canvas, mask_land, coords, width, color):
    layer = Image.new("RGB", (S, S), color)
    cover = Image.new("L", (S, S), 0)
    pen = ImageDraw.Draw(cover)
    pen.line([project(*p) for p in coords], fill=255, width=width, joint="curve")
    # clip all artistic relief strictly to Natural Earth Italy silhouette
    from PIL import ImageChops
    clipped = ImageChops.multiply(cover, mask_land)
    canvas.paste(layer, (0, 0), clipped)


def render(out, source):
    feature = country_feature(source)
    land = Image.new("L", (S, S), 0)
    pen = ImageDraw.Draw(land)
    polys = list(polygons(feature["geometry"]))
    for rings in polys:
        if not rings:
            continue
        pen.polygon([project(*c[:2]) for c in rings[0]], fill=255)
        for hole in rings[1:]:
            pen.polygon([project(*c[:2]) for c in hole], fill=0)

    if sum(1 for v in land.getdata() if v) < S*S*.12:
        raise RuntimeError("Italy mask is suspiciously small; verify source/projection")
    canvas = Image.new("RGB", (S, S), SEA)
    canvas.paste(Image.new("RGB", (S, S), BEACH), (0, 0), land)
    interior = land.filter(ImageFilter.MinFilter(37))
    canvas.paste(Image.new("RGB", (S, S), GREEN), (0, 0), interior)

    # Alpine region and Apennine chain: artistic approximation only.
    # No claim of physically accurate altitude or DEM-derived relief.
    draw_band(canvas, land,
              [(7.15, 45.9), (8.30, 46.40), (9.50, 46.3),
               (10.70, 46.56), (11.8, 46.38), (12.9, 46.30), (13.65, 46.07)],
              74, MOUNTAINS)
    draw_band(canvas, land,
              [(7.3, 46.25), (8.6, 46.75), (10.1, 46.78),
               (11.8, 46.80), (13.1, 46.56)],
              35, ALPS_SNOW)
    draw_band(canvas, land,
              [(9.4, 44.40), (10.60, 43.65), (11.80, 42.70),
               (13.0, 42.1), (14.1, 41.0), (15.1, 40.0),
               (16.10, 39.0)],
              46, HILLS)
    draw_band(canvas, land,
              [(10.0, 44.10), (11.5, 43.0), (12.6, 42.2),
               (14.0, 41.0), (15.4, 39.5)],
              20, MOUNTAINS)

    draw = ImageDraw.Draw(canvas)
    for name, (lon, lat) in CITIES.items():
        x, y = project(lon, lat)
        ix, iy = int(x), int(y)
        if 0 <= ix < S and 0 <= iy < S and land.getpixel((ix, iy)) > 0:
            r = 10
            draw.ellipse((x-r, y-r, x+r, y+r), fill=VILLAGE)
    target = Path(out)
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas = canvas.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    canvas.save(target)
    metadata = {
        "country": "Italy", "source": "Natural Earth public domain", "source_url": SOURCE_URL,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "source_commit": NE_COMMIT, "license": LICENCE_URL,
        "projection": "equirectangular local with cos(latitude_mid) correction",
        "bounding_box": list(BBOX), "country_polygons": len(polys),
        "source_resolution": "Natural Earth 1:10m", "image_resolution_px": [SIZE, SIZE],
        "includes_islands": "Sicily and Sardinia are drawn from the actual country geometry",
        "relief_is_actual_topography": False,
        "description": "Artistic Alps and Apennines, green interior, beige coast; NOT elevation data",
        "cities_marked": list(CITIES), "image_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "commercial_prices_stock_verified": False,
    }
    target.with_suffix(".source.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    return metadata


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="benchmark-results/maps-engine-v03/italie/source/italie_ne_10m_style.png")
    args = ap.parse_args()
    render(args.out, fetch_source())
