#!/usr/bin/env python3
"""Background removal (rembg, isnet-general-use) + keep only the main subject (largest connected blob, which drops
fragments of neighbouring figures at the image borders) + square padding on white. No pixel of the subject is altered."""
import sys, os, glob, json
import numpy as np
from PIL import Image
from scipy import ndimage
from rembg import remove, new_session
src, dst = sys.argv[1], sys.argv[2]; os.makedirs(dst, exist_ok=True)
sess = new_session("isnet-general-use"); info = {}
for f in sorted(glob.glob(os.path.join(src, "*.png"))):
    im = Image.open(f).convert("RGB")
    rgba = remove(im, session=sess)
    a = np.array(rgba)[:, :, 3]
    lab, n = ndimage.label(a > 128)
    sizes = ndimage.sum(np.ones_like(a), lab, range(1, n + 1))
    keep = lab == (1 + int(np.argmax(sizes)))
    keep = ndimage.binary_dilation(keep, iterations=3) & (a > 0)
    alpha = np.where(keep, a, 0).astype(np.uint8)
    out = np.array(rgba); out[:, :, 3] = alpha
    ys, xs = np.where(alpha > 128)
    touches = dict(left=bool(xs.min() <= 1), right=bool(xs.max() >= a.shape[1]-2), top=bool(ys.min() <= 1), bottom=bool(ys.max() >= a.shape[0]-2))
    crop = Image.fromarray(out).crop((xs.min(), ys.min(), xs.max()+1, ys.max()+1))
    s = int(max(crop.size) * 1.15); canvas = Image.new("RGBA", (s, s), (255, 255, 255, 0))
    canvas.paste(crop, ((s - crop.width) // 2, (s - crop.height) // 2))
    name = os.path.basename(f)
    canvas.save(os.path.join(dst, name.replace(".png", "_rgba.png")))
    flat = Image.new("RGB", canvas.size, "white"); flat.paste(canvas, mask=canvas.split()[3]); flat.save(os.path.join(dst, name.replace(".png", "_white.png")))
    info[name] = dict(blobs_removed=int(n - 1), subject_bbox_px=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
                      subject_h_over_w=round((ys.max()-ys.min())/(xs.max()-xs.min()), 3), touches_border=touches)
    print(name, info[name])
json.dump(info, open(os.path.join(dst, "prep_info.json"), "w"), indent=1)
