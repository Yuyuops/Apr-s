#!/usr/bin/env python3
"""V0.4 art-direction fixture for the REAL LEGO Maps pipeline.

Source coastline: same 10m Natural Earth country geometry as V0.3.
Artistic layers: Alps/Apennines are stylized (NOT geographic elevation).
New decorative features: ITALIA plaque and compass on open sea, rasterized
and then passed through the *actual* image -> LEGO parts engine. No fake
monuments, floating overlay graphics, or claimed LEGO manufacturability.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent / "italie" / "make_italy_source.py"

def source_module():
    spec = importlib.util.spec_from_file_location("italy_geo_fixture", LEGACY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_font(size):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()

def ocean_mask(image, sea_rgb):
    a = np.asarray(image).astype("int16")
    d = np.max(np.abs(a - np.asarray(sea_rgb, dtype="int16")), axis=2)
    return (d <= 4).astype("uint8")

def emptiness(mask, box):
    x0, y0, x1, y1 = box
    crop = mask[y0:y1, x0:x1]
    return float(crop.mean()) if crop.size else 0

def best_position(mask, boxes, min_free=0.96):
    # select an ocean-only location, without manually moving coastlines.
    best = max(boxes, key=lambda b: emptiness(mask, b))
    fraction = emptiness(mask, best)
    if fraction < min_free:
        raise ValueError(f"Not enough empty sea for ornament {best} ({fraction:.2%})")
    return best, fraction

def make(out, ornaments=True):
    geo = source_module()
    target = Path(out)
    target.parent.mkdir(parents=True, exist_ok=True)
    baseline = target.parent / "italie_geographique_style_original.png"
    if not baseline.exists():
        geo.render(baseline, geo.fetch_source())
    image = Image.open(baseline).convert("RGB")
    mask = ocean_mask(image, (36, 99, 158))
    opts = []
    d = ImageDraw.Draw(image)

    if ornaments:
        # Find a label in open sea, not over the real country; the plaque is
        # a simple pixel-art motif. Generated LEGO pixels are NOT a physical
        # engraved or printed part.
        plaque, free = best_position(mask, [
            (307, 448, 495, 494), (310, 18, 498, 64), (8, 448, 196, 494)
        ], min_free=0.96)
        x0,y0,x1,y1 = plaque
        d.rounded_rectangle((x0,y0,x1,y1), radius=6, fill="#e9d5a4",outline="#a17b4e",width=4)
        font=load_font(26)
        bb=d.textbbox((0,0),"ITALIA",font=font)
        tx=x0+(x1-x0-(bb[2]-bb[0]))//2
        ty=y0+(y1-y0-(bb[3]-bb[1]))//2-bb[1]
        d.text((tx,ty),"ITALIA",font=font,fill="#72472d")
        opts.append(dict(kind="title",text="ITALIA",rect=plaque,original_sea_fraction=round(free,4),
                         material="raster colour classes, not a printed element"))
        mask[y0:y1,x0:x1]=0

        compass, free = best_position(mask, [
            (430, 165, 506, 241), (5, 200, 81, 276), (428, 260, 504, 336),
            (425, 78, 501, 154)
        ], min_free=0.92)
        a,b,c,e=compass; cx=(a+c)//2; cy=(b+e)//2; rr=min((c-a)//2,(e-b)//2)-5
        d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline="#ddbf83",width=6)
        d.line((cx,cy-rr,cx,cy+rr),fill="#d7b47e",width=7)
        d.line((cx-rr,cy,cx+rr,cy),fill="#d7b47e",width=7)
        d.polygon([(cx,cy-rr-2),(cx-8,cy+8),(cx+8,cy+8)],fill="#79553e")
        d.polygon([(cx,cy+rr+2),(cx-6,cy-6),(cx+6,cy-6)],fill="#e6cf9e")
        d.ellipse((cx-5,cy-5,cx+5,cy+5),fill="#79553e")
        opts.append(dict(kind="compass",rect=compass,original_sea_fraction=round(free,4),
                         material="raster geometric regions, not physical 3D ornamental pieces"))

    image.save(target)
    original_meta=json.loads(baseline.with_suffix(".source.json").read_text())
    metadata=dict(geographic_source=original_meta, artistic_features=opts,
                  image_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                  source_unchanged_for_country=True, max_grid=64,
                  elevation_data="ARTISTIC_ONLY_NOT_A_DEM",
                  monuments_physically_modelled=False,
                  source_image=str(target.name),
                  targets=["LDraw","BOM","PNG renders","viewer","PDF notice"])
    target.with_suffix(".json").write_text(json.dumps(metadata,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(dict(image=str(target),sha256=metadata["image_sha256"],ornaments=opts),indent=2))
    return metadata

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default=str(HERE/"results/italia_art_v04.png"))
    parser.add_argument("--no-ornaments",action="store_true")
    a=parser.parse_args()
    make(a.out,ornaments=not a.no_ornaments)
