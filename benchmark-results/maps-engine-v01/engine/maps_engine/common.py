import os, sys, sqlite3
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))                                    # maps-engine-v01
E1 = os.path.normpath(os.path.join(ROOT, "..", "20_portable_engine", "engine"))             # engine 1, READ ONLY
if E1 not in sys.path: sys.path.insert(0, E1)
import numpy as np
STUD = 20.0; PLATE = 8.0                                                                     # LDU
# every part below was checked to exist in the LDraw library (engine-1 conn.part) ; key = (long side, short side) in studs ; origin = centre of the top face
PLATES = {(1, 1): "3024", (2, 1): "3023", (3, 1): "3623", (4, 1): "3710", (6, 1): "3666", (8, 1): "3460", (10, 1): "4477", (12, 1): "60479",
          (2, 2): "3022", (3, 2): "3021", (4, 2): "3020", (6, 2): "3795", (8, 2): "3034", (10, 2): "3832", (12, 2): "2445",
          (4, 4): "3031", (6, 4): "3032", (8, 4): "3035", (10, 4): "3030", (12, 4): "3029", (6, 6): "3958", (8, 6): "3036", (10, 6): "3033", (8, 8): "41539"}
TILES = {(1, 1): "3070b", (2, 1): "3069b", (3, 1): "63864", (4, 1): "2431", (6, 1): "6636", (8, 1): "4162", (2, 2): "3068b", (3, 2): "26603", (4, 2): "87079", (6, 2): "69729"}
BRICKS = {(1, 1): "3005", (2, 1): "3004", (3, 1): "3622", (4, 1): "3010", (6, 1): "3009", (8, 1): "3008", (2, 2): "3003", (3, 2): "3002", (4, 2): "3001", (6, 2): "2456", (8, 2): "3007"}
ROUND_PLATE = "6141"; ROUND_TILE = "98138"; CUT_CORNER_PLATE = "26601"                       # round 1x1 plate with solid stud / round 1x1 tile / 2x2 wedge plate with one cut corner
KINDS = {"plate": (PLATES, 1, True), "tile": (TILES, 1, False), "brick": (BRICKS, 3, True)}   # catalogue, height in plates, has studs
def part_for(kind, w, d):
    cat = KINDS[kind][0]; return cat[(max(w, d), min(w, d))]

_rb = None
def rb_colours():
    """real LEGO colour values (Rebrickable `colors` table of the technical catalogue). V0 used the LDraw LDConfig values, which differ (e.g. Tan #B0A06F vs #E4CD9E)."""
    global _rb
    if _rb is None:
        from _paths import RB_DB
        db = sqlite3.connect(RB_DB); _rb = {r[0]: dict(name=r[1].replace(" ", "_"), rgb=tuple(int(r[2][i:i + 2], 16) for i in (0, 2, 4)), trans=bool(r[3])) for r in db.execute("select id,name,rgb,is_trans from colors")}
    return _rb
def lab(rgb):
    c = np.asarray(rgb, float) / 255.0; c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]); xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)
def dE(a, b): return float(np.linalg.norm(lab(a) - lab(b)))

def dE2000(l1, l2):
    """CIEDE2000 between Lab arrays (broadcasting over the leading dimensions)"""
    l1 = np.asarray(l1, float); l2 = np.asarray(l2, float); L1, a1, b1 = l1[..., 0], l1[..., 1], l1[..., 2]; L2, a2, b2 = l2[..., 0], l2[..., 1], l2[..., 2]
    C1 = np.hypot(a1, b1); C2 = np.hypot(a2, b2); Cb = (C1 + C2) / 2; G = 0.5 * (1 - np.sqrt(Cb ** 7 / (Cb ** 7 + 25.0 ** 7)))
    a1p = (1 + G) * a1; a2p = (1 + G) * a2; C1p = np.hypot(a1p, b1); C2p = np.hypot(a2p, b2)
    h1 = np.degrees(np.arctan2(b1, a1p)) % 360; h2 = np.degrees(np.arctan2(b2, a2p)) % 360
    dL = L2 - L1; dC = C2p - C1p; dh = h2 - h1; dh = np.where(dh > 180, dh - 360, np.where(dh < -180, dh + 360, dh)); dh = np.where(C1p * C2p == 0, 0, dh)
    dH = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dh / 2)); Lb = (L1 + L2) / 2; Cbp = (C1p + C2p) / 2
    hs = h1 + h2; hb = np.where(C1p * C2p == 0, hs, np.where(np.abs(h1 - h2) <= 180, hs / 2, np.where(hs < 360, (hs + 360) / 2, (hs - 360) / 2)))
    T = 1 - 0.17 * np.cos(np.radians(hb - 30)) + 0.24 * np.cos(np.radians(2 * hb)) + 0.32 * np.cos(np.radians(3 * hb + 6)) - 0.20 * np.cos(np.radians(4 * hb - 63))
    Sl = 1 + 0.015 * (Lb - 50) ** 2 / np.sqrt(20 + (Lb - 50) ** 2); Sc = 1 + 0.045 * Cbp; Sh = 1 + 0.015 * Cbp * T
    dth = 30 * np.exp(-((hb - 275) / 25) ** 2); Rc = 2 * np.sqrt(Cbp ** 7 / (Cbp ** 7 + 25.0 ** 7)); Rt = -np.sin(np.radians(2 * dth)) * Rc
    return np.sqrt((dL / Sl) ** 2 + (dC / Sc) ** 2 + (dH / Sh) ** 2 + Rt * (dC / Sc) * (dH / Sh))
def de00(a, b): return float(dE2000(lab(a), lab(b)))
