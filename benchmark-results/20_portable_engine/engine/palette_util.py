"""Subject palette helpers : the colours of a subject are DATA (the colours its grid uses), never names of a demonstration character.
roles(palette)   : the darkest, lightest and reddest colour of the palette (what the detail modules call "dark", "light", "red")
class_codes(...) : LDraw code that stands for each appearance class of the GLB patches (noir / blanc / rouge / jaune = skin), chosen by the smallest Lab distance between the colour
                   OBSERVED on the GLB (mean of the patch faces) and the colours of the subject palette ; the skin colour is the majority colour of the head surface of the grid."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import LDRAW
import json, re
import numpy as np

_CODES = {}
def codes():
    if not _CODES:
        for l in open(_os.path.join(LDRAW, "LDConfig.ldr"), errors="replace"):
            m = re.search(r"!COLOUR\s+(\S+)\s+CODE\s+(\d+)\s+VALUE\s+#([0-9A-Fa-f]{6})", l)
            if m: _CODES[int(m.group(2))] = (m.group(1), tuple(int(m.group(3)[i:i + 2], 16) for i in (0, 2, 4)))
    return _CODES

def lab(rgb):
    c = np.asarray(rgb, float) / 255.0; c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]); xyz = (c @ M.T) / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)

def subject_palette(full_npz):
    g = np.load(full_npz)["grid"]; return sorted(int(c) for c in np.unique(g) if c >= 0)

def code_for_rgb(rgb, pal):
    c = codes(); L = lab([c[p][1] for p in pal]); d = np.linalg.norm(L - lab(rgb), axis=1); return pal[int(d.argmin())]

def roles(pal):
    c = codes(); L = lab([c[p][1] for p in pal])
    red = [p for p, l in zip(pal, L) if l[1] > 30 and l[2] > 10 and l[0] < 60]
    return dict(dark=pal[int(L[:, 0].argmin())], light=pal[int(L[:, 0].argmax())], red=(red[int(np.argmax([L[pal.index(p)][1] for p in red]))] if red else None))

def dark_neutral(pal, l_max=62.0, chroma_max=25.0):
    """palette colours that can stand for the dark skin of a part of the model (black, dark greys, dark tan...) : the quantiser may use any of them for the same dark GLB tones"""
    c = codes(); L = lab([c[p][1] for p in pal])
    return [p for p, l in zip(pal, L) if l[0] <= l_max and float(np.hypot(l[1], l[2])) <= chroma_max]

def class_codes(details_json, full_npz):
    D = json.load(open(details_json)); pal = subject_palette(full_npz); cc = D["repere"].get("couleurs_classes", {}); r = roles(pal)
    g = np.load(full_npz); G = g["grid"]; neck = int(g["neck"]); head = G[:, neck:, :]; vals, cnt = np.unique(head[head >= 0], return_counts=True)
    out = {"jaune": int(vals[int(cnt.argmax())]) if len(vals) else r["light"]}
    out["noir"] = code_for_rgb(cc["noir"], pal) if "noir" in cc else r["dark"]
    out["blanc"] = code_for_rgb(cc["blanc"], pal) if "blanc" in cc else r["light"]
    out["rouge"] = code_for_rgb(cc["rouge"], pal) if "rouge" in cc else (r["red"] if r["red"] is not None else r["dark"])
    return out
