#!/usr/bin/env python3
"""Land/sea mask from a user-supplied oblique render of a LEGO model of a fictional map (colour segmentation + perspective rectification). NO geography is created :
the only operations are (1) a perspective rectification from 4 board-corner points measured on the picture, (2) a colour threshold : blue-water pixels = sea, every other pixel inside the board = land.
usage : hyrule_mask_from_render.py SRC.jpg OUT_mask.png OUT_check.png  [--grid R C] [--px-per-stud N]   (corner points : edit CORNERS, pixel coordinates measured on the 1920x1080 picture)"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
CORNERS = [(322, 48), (1615, 48), (1668, 812), (163, 812)]       # board interior : top-left, top-right, bottom-right, bottom-left (measured on a pixel grid overlay)
src, out, chk = sys.argv[1:4]; a = sys.argv; R, C = (int(a[a.index("--grid") + 1]), int(a[a.index("--grid") + 2])) if "--grid" in a else (80, 80); K = int(a[a.index("--px-per-stud") + 1]) if "--px-per-stud" in a else 12
W, H = C * K, R * K; im = Image.open(src).convert("RGB")
# homography mapping output rectangle -> source picture (PIL PERSPECTIVE wants the inverse : output pixel -> source pixel)
dst = [(0, 0), (W, 0), (W, H), (0, H)]; A = []; B = []
for (x, y), (u, v) in zip(dst, CORNERS):
    A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u); A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
coef = np.linalg.solve(np.array(A, float), np.array(B, float)); rect = im.transform((W, H), Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)
hsv = np.asarray(rect.convert("HSV")).astype(float); h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
blue = ((h > 190) & (h < 245) & (s > 0.30) & (v > 0.28)).astype(float)         # blue water plates ; snow / grey stone / green are excluded by hue or saturation
sea = ndimage.gaussian_filter(blue, K * 0.7) > 0.45                          # plates are textured (studs, joints) : smooth before thresholding
lab, n = ndimage.label(sea); sz = ndimage.sum(sea, lab, range(1, n + 1)); sea = np.isin(lab, [i + 1 for i, z in enumerate(sz) if z >= 1.5 * K * K])   # drop water specks under 1.5 stud2
lab, n = ndimage.label(~sea); sz = ndimage.sum(~sea, lab, range(1, n + 1)); sea |= np.isin(lab, [i + 1 for i, z in enumerate(sz) if z < 1.5 * K * K])     # fill land specks under 1.5 stud2
sand = ((h > 28) & (h < 62) & (s > 0.10) & (s < 0.60) & (v > 0.66)).astype(float)       # pale sand-coloured plates (desert) : second class, rendered as the style's flat sand land
sand = ndimage.gaussian_filter(sand, K * 1.2) > 0.5; sand &= ~sea; lab, n = ndimage.label(sand); sz = ndimage.sum(sand, lab, range(1, n + 1)); sand = np.isin(lab, [i + 1 for i, z in enumerate(sz) if z >= 40 * K * K])   # keep only regions of >= 40 stud2
sand = ndimage.binary_fill_holes(sand) & ~sea                              # structures standing in the desert (temples, towers) are part of the desert plain
land = ~sea; grey = np.where(sea, 0, np.where(sand, 128, 255)).astype(np.uint8); Image.fromarray(grey).save(out)
Image.fromarray(np.hstack([np.asarray(rect), np.repeat(grey[..., None], 3, axis=2)])).resize((W, H // 2)) if False else Image.fromarray(np.hstack([np.asarray(rect), np.repeat(grey[..., None], 3, axis=2)])).save(chk)
print("desert fraction %.3f" % sand.mean(), "grid", R, C, "sea fraction %.3f" % sea.mean(), "components of sea >= 1 stud2:", int(ndimage.label(sea)[1]))
