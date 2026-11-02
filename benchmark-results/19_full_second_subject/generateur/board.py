import sys, os
from PIL import Image, ImageDraw
d, out, title = sys.argv[1:4]; names = sys.argv[4:]
rows = []
for n in names:
    A = Image.open(f"{d}/r_ref/{n}.png").convert("RGB").resize((420, 420)); B = Image.open(f"{d}/r_lego/{n}.png").convert("RGB").resize((420, 420)); rows.append((n, A, B))
W = 420 * 2 + 20; H = 420 * len(rows) + 40; img = Image.new("RGB", (W, H), "white"); dr = ImageDraw.Draw(img); dr.text((10, 5), title + "  (gauche : GLB source ; droite : assemblage LDraw)", fill="black")
for k, (n, A, B) in enumerate(rows): img.paste(A, (0, 30 + 420 * k)); img.paste(B, (430, 30 + 420 * k)); dr.text((6, 34 + 420 * k), n, fill="black")
img.save(out)
