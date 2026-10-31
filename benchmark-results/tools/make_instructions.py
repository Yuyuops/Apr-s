#!/usr/bin/env python3
"""Layer-by-layer building instructions (PDF) from a brick .ldr: one page per plate layer, rendered from the
real part geometry (previous layers ghosted, new layer in full colour) + the list of parts to add on that layer.
usage: make_instructions.py --scene scene.json --out dir --name x [--az 220 --el 35]"""
import argparse, json, os, subprocess, sys
from collections import Counter
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
def font(sz):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", sz)
    except OSError: return ImageFont.load_default()
NAMES = {"3005":"Brick 1x1","3004":"Brick 1x2","3622":"Brick 1x3","3010":"Brick 1x4","3009":"Brick 1x6","3008":"Brick 1x8","3003":"Brick 2x2",
 "3002":"Brick 2x3","3001":"Brick 2x4","2456":"Brick 2x6","3007":"Brick 2x8","3024":"Plate 1x1","3023":"Plate 1x2","3623":"Plate 1x3",
 "3710":"Plate 1x4","3666":"Plate 1x6","3460":"Plate 1x8","3022":"Plate 2x2","3021":"Plate 2x3","3020":"Plate 2x4","3795":"Plate 2x6",
 "3034":"Plate 2x8","3031":"Plate 4x4","3032":"Plate 4x6","3035":"Plate 4x8","3958":"Plate 6x6","3036":"Plate 6x8","41539":"Plate 8x8"}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--scene", required=True); ap.add_argument("--out", required=True); ap.add_argument("--name", required=True)
    ap.add_argument("--az", type=float, default=215); ap.add_argument("--el", type=float, default=38)
    a = ap.parse_args()
    S = json.load(open(a.scene)); cols = S["colours"]
    layers = sorted({p["y0"] for p in S["parts"]})
    tmp = os.path.join(a.out, "_instr_png"); os.makedirs(tmp, exist_ok=True)
    full = [{"name": "full", "az": a.az, "el": a.el, "w": 900, "h": 900}]
    json.dump(full, open(os.path.join(tmp, "v0.json"), "w"))
    subprocess.run(["node", os.path.join(HERE, "render_ldr.js"), a.scene, os.path.join(tmp, "v0.json"), tmp], check=True)
    bb = json.load(open(os.path.join(tmp, "render_meta.json")))["views"]["full"]["bbox_mm"]
    views = [{"name": f"L{L:03d}", "az": a.az, "el": a.el, "w": 900, "h": 900, "maxLayer": L, "ghostOld": True, "frameBox": bb} for L in layers]
    json.dump(views, open(os.path.join(tmp, "v.json"), "w"))
    subprocess.run(["node", os.path.join(HERE, "render_ldr.js"), a.scene, os.path.join(tmp, "v.json"), tmp], check=True)
    pages = []
    cover = Image.new("RGB", (1240, 1754), "white"); d = ImageDraw.Draw(cover)
    d.text((60, 60), f"{a.name} - building instructions (layer by layer)", fill="black", font=font(40))
    d.text((60, 120), f"{len(S['parts'])} parts, {len(layers)} layers. Rendered from the LDraw file and the official LDraw part shapes.", fill="#333", font=font(22))
    d.text((60, 155), "Pale = already built; full colour = the parts to add on this page. Build from the bottom.", fill="#333", font=font(22))
    im = Image.open(os.path.join(tmp, "full.png")); im.thumbnail((1100, 1100)); cover.paste(im, (70, 260)); pages.append(cover)
    for k, L in enumerate(layers):
        new = [p for p in S["parts"] if p["y0"] == L]
        cnt = Counter((p["p"].replace(".dat", ""), p["c"]) for p in new)
        pg = Image.new("RGB", (1240, 1754), "white"); d = ImageDraw.Draw(pg)
        d.text((60, 40), f"Page {k+1}/{len(layers)} - layer {L} (height {L*3.2:.1f} mm) - {len(new)} parts", fill="black", font=font(34))
        im = Image.open(os.path.join(tmp, f"L{L:03d}.png")); im.thumbnail((1120, 1120)); pg.paste(im, (60, 100))
        y = 1240; x = 60
        for (part, c), n in sorted(cnt.items(), key=lambda kv: -kv[1]):
            ci = cols.get(str(c), {"hex": "#888888", "name": str(c)})
            d.rectangle([x, y + 4, x + 26, y + 30], fill=ci["hex"], outline="black")
            d.text((x + 36, y + 2), f"{n} x {NAMES.get(part, part)} ({part}) {ci['name'].replace('_', ' ')}", fill="black", font=font(21))
            y += 36
            if y > 1700: y = 1240; x += 590
        pages.append(pg)
    pdf = os.path.join(a.out, f"{a.name}_instructions.pdf")
    pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=150)
    print(pdf, len(pages), "pages")
if __name__ == "__main__":
    main()
