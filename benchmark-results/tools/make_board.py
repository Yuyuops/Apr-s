#!/usr/bin/env python3
"""Assemble a labelled comparison board from existing images (no retouching: images are only
auto-cropped to their content and scaled). usage: make_board.py out.png "Title" "row label:img1,img2,..." ..."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageChops

def font(sz):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try: return ImageFont.truetype(f, sz)
        except OSError: pass
    return ImageFont.load_default()

def crop(im):
    im = im.convert("RGB"); bg = Image.new("RGB", im.size, im.getpixel((0, 0)))
    bb = ImageChops.difference(im, bg).getbbox()
    if not bb: return im
    pad = 12; x0, y0, x1, y1 = bb
    return im.crop((max(0, x0-pad), max(0, y0-pad), min(im.width, x1+pad), min(im.height, y1+pad)))

def main():
    out, title, rows = sys.argv[1], sys.argv[2], sys.argv[3:]
    C, LW = 420, 260
    parsed = []
    for r in rows:
        label, files = r.split(":", 1)
        cells = []
        for f in files.split(","):
            cap = ""
            if "=" in f: cap, f = f.split("=", 1)
            cells.append((cap, f))
        parsed.append((label, cells))
    ncol = max(len(c) for _, c in parsed)
    W, H = LW + ncol * C, 70 + len(parsed) * (C + 30)
    board = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(board)
    d.text((16, 18), title, fill="black", font=font(28))
    for i, (label, cells) in enumerate(parsed):
        y = 70 + i * (C + 30)
        for k, line in enumerate(label.split("|")):
            d.text((16, y + C // 2 - 30 + k * 26), line, fill="black", font=font(20 if k == 0 else 15))
        for j, (cap, f) in enumerate(cells):
            if f in ("", "-"): continue
            im = crop(Image.open(f)); im.thumbnail((C - 16, C - 16))
            x = LW + j * C
            board.paste(im, (x + (C - im.width) // 2, y + (C - im.height) // 2))
            if cap: d.text((x + 8, y + C + 2), cap, fill="#444", font=font(15))
    board.save(out); print(out, board.size)

if __name__ == "__main__":
    main()
