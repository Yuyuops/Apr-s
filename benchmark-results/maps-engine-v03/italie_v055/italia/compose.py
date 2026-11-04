#!/usr/bin/env python3
"""Italia 128 composition engine : geographic layer (coast, DEM relief levels, cities) + decorative layer (monuments, ITALIA title, compass) placed by rules read from
artistic_scale_config.json (no dimension hard-coded for Italy). Outputs placements.json (decision log), levels_128.npy, composition_preview.png.
usage: compose.py [config.json] [outdir]"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from decor import text_cells, compass_cells
cfg_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "artistic_scale_config.json"); out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "output"); os.makedirs(out, exist_ok=True)
cfg = json.load(open(cfg_path)); G = cfg["geographic"]; GR, GC = G["grid_studs"]; bb = G["window_lonlat"]
def rel(p): return os.path.join(HERE, p)
clon, clat = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2; k = math.cos(math.radians(clat)); scale = G["fill_fraction"] * max(GR, GC) / max((bb[2] - bb[0]) * k, bb[3] - bb[1])
def to_grid(lon, lat): return GR / 2 - (lat - clat) * scale, GC / 2 + (lon - clon) * k * scale          # (row, col) in studs, continuous
def to_lonlat(r, c): return clon + (c - GC / 2) / (k * scale), clat - (r - GR / 2) / scale
# ---- geographic layer
SS = 8; img = Image.new("L", (GC * SS, GR * SS), 0); d = ImageDraw.Draw(img); geo = json.load(open(rel(G["source_polygons"])))
polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
for poly in polys:
    for i, ring in enumerate(poly):
        pts = [((to_grid(lo, la)[1]) * SS, (to_grid(lo, la)[0]) * SS) for lo, la in ring]; d.polygon(pts, fill=255 if i == 0 else 0)
cov = np.asarray(img, np.float32).reshape(GR, SS, GC, SS).mean(axis=(1, 3)) / 255.0; land = cov >= G["land_min_coverage"]
dem = np.load(rel(G["dem"]["file"])); meta = json.load(open(rel("fixtures/sources_meta.json"))); Z = meta["zoom"]; n = 2 ** Z; x0, y0 = meta["tiles_x"][0], meta["tiles_y"][0]
elev = np.zeros((GR, GC), np.float32)
for r in range(GR):
    for c in range(GC):
        vals = []
        for a in (0.2, 0.4, 0.6, 0.8):
            for b in (0.2, 0.4, 0.6, 0.8):
                lo, la = to_lonlat(r + a, c + b); px = ((lo + 180) / 360 * n - x0) * 256; py = ((1 - math.asinh(math.tan(math.radians(la))) / math.pi) / 2 * n - y0) * 256
                vals.append(dem[int(min(max(py, 0), dem.shape[0] - 1)), int(min(max(px, 0), dem.shape[1] - 1))])
        v = np.array(vals); elev[r, c] = max(0.0, v.mean() + G["dem"]["peak_boost"] * (np.percentile(v, 90) - v.mean()))
m = G["dem"]["metres_to_levels"]; lev = np.where(land, np.maximum(m["min_land_level"], np.rint(m["gain"] * (elev / m["unit_m"]) ** m["exponent"])), 0).astype(int); lev = np.minimum(lev, m["max_level"])
places = []
for p in json.load(open(rel(G["places"]))):
    r, c = to_grid(p["lon"], p["lat"])
    if 0 <= r < GR and 0 <= c < GC: places.append(dict(name=p["name"], row=round(r, 1), col=round(c, 1), pop=p["pop"]))
# ---- decorative layer
D = cfg["decorative"]; keep = D["frame_margin_keepout"]; occupied = np.zeros((GR, GC), bool); occupied[:keep] = occupied[-keep:] = True; occupied[:, :keep] = occupied[:, -keep:] = True
log = []; zones = {}
integral = lambda M: np.pad(M.astype(np.int32).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
def rect_sum(I, r, c, h, w): return I[r + h, c + w] - I[r, c + w] - I[r + h, c] + I[r, c]
def corner_score(r, c, h, w, pref):
    cr, cc = r + h / 2, c + w / 2; tgt = {"bottom-left": (GR, 0), "top-left": (0, 0), "bottom-right": (GR, GC), "top-right": (0, GC)}
    return min(math.hypot(cr - tgt[p][0], cc - tgt[p][1]) + 4 * i for i, p in enumerate(pref))
for z in D["reserved_zones"]:
    if z["kind"] == "text": cells, (h, w) = text_cells(z["text"], z["letter_gap"])
    else: h = w = z["diameter"]
    mg = z["margin"]; H, W = h + 2 * mg, w + 2 * mg; Isea = integral(~land & ~occupied); best = None
    for r in range(GR - H + 1):
        for c in range(GC - W + 1):
            if rect_sum(Isea, r, c, H, W) == H * W:
                s = corner_score(r, c, H, W, z["prefer"])
                if best is None or s < best[0]: best = (s, r, c)
    if best is None: log.append(dict(id=z["id"], status="FAIL", reason="no open-sea rectangle %dx%d" % (H, W))); continue
    _, r, c = best; occupied[r:r + H, c:c + W] = True; zones[z["id"]] = dict(row=r + mg, col=c + mg, h=h, w=w, margin=mg); log.append(dict(id=z["id"], status="placed", row=r + mg, col=c + mg, size=[h, w]))
placed = []
for mo in sorted(D["monuments"], key=lambda x: x["priority"]):
    ar, ac = to_grid(*mo["lonlat"]); done = None; steps = []
    for sc in mo["scales"]:
        fh, fw = sc["footprint"]; offs = sorted(((dr, dc) for dr in range(-mo["max_shift_studs"], mo["max_shift_studs"] + 1) for dc in range(-mo["max_shift_studs"], mo["max_shift_studs"] + 1)), key=lambda o: math.hypot(*o))
        Iland = integral(land)
        for dr, dc in offs:
            if math.hypot(dr, dc) > mo["max_shift_studs"]: break
            r = int(round(ar + dr - fh / 2)); c = int(round(ac + dc - fw / 2)); cl = mo["clearance"]
            if r - cl < 0 or c - cl < 0 or r + fh + cl > GR or c + fw + cl > GC: continue
            if rect_sum(Iland, r, c, fh, fw) / (fh * fw) < mo["min_land_fraction"]: continue
            if occupied[max(0, r - cl):r + fh + cl, max(0, c - cl):c + fw + cl].any(): continue
            done = dict(id=mo["id"], name=mo["name"], module=mo["module"], variant=sc["variant"], footprint=[fh, fw], row=r, col=c, shift_studs=round(math.hypot(dr, dc), 1), true_anchor=[round(ar, 1), round(ac, 1)]); break
        steps.append("scale %s: %s" % (sc["footprint"], "OK" if done else "no free spot"))
        if done: break
    if done:
        occupied[done["row"]:done["row"] + done["footprint"][0], done["col"]:done["col"] + done["footprint"][1]] = True; placed.append(done); log.append(dict(status="placed", steps=steps, **done))
    else: log.append(dict(id=mo["id"], status="removed" if mo["allow_remove"] else "FAIL", steps=steps))
json.dump(dict(grid=[GR, GC], projection=dict(centre=[clon, clat], k=k, studs_per_degree_lat=scale), zones=zones, monuments=placed, log=log, land_cells=int(land.sum()), max_level=int(lev.max()), level_histogram={int(a): int(b) for a, b in zip(*np.unique(lev, return_counts=True))}, places=places), open(os.path.join(out, "placements.json"), "w"), indent=1)
np.save(os.path.join(out, "levels_128.npy"), lev)
# ---- preview (8 px per stud, 2-stud frame)
PX = 8; F = cfg["geographic"]["frame_studs"]; W_ = (GC + 2 * F) * PX; H_ = (GR + 2 * F) * PX; im = Image.new("RGB", (W_, H_), (96, 54, 30)); dr_ = ImageDraw.Draw(im)
col = {0: (36, 99, 158), 1: (97, 150, 80), 2: (82, 128, 68), 3: (118, 138, 78), 4: (146, 128, 88), 5: (150, 118, 78), 6: (128, 126, 122), 7: (150, 148, 146), 8: (176, 176, 178), 9: (205, 205, 208), 10: (225, 225, 228), 11: (245, 245, 247)}
gy, gx = np.gradient(lev.astype(float)); shade = np.clip(1 + 0.12 * (gy + gx) * -1, .7, 1.25)
for r in range(GR):
    for c in range(GC):
        b = col[int(lev[r, c])]; s = shade[r, c] if land[r, c] else 1; x, y = (c + F) * PX, (r + F) * PX
        dr_.rectangle([x, y, x + PX - 1, y + PX - 1], fill=tuple(int(min(255, v * s)) for v in b))
try: fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
except Exception: fnt = ImageFont.load_default()
for p in places[:14]:
    x, y = (p["col"] + F) * PX, (p["row"] + F) * PX; dr_.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(180, 40, 30), outline=(255, 255, 255)); dr_.text((x + 5, y - 6), p["name"], fill=(20, 20, 20), font=fnt)
if "title" in zones:
    z = zones["title"]; cells, _ = text_cells(cfg["decorative"]["reserved_zones"][0]["text"], cfg["decorative"]["reserved_zones"][0]["letter_gap"])
    for (r, c) in cells: x, y = (z["col"] + c + F) * PX, (z["row"] + r + F) * PX; dr_.rectangle([x, y, x + PX - 2, y + PX - 2], fill=(245, 245, 245))
if "compass" in zones:
    z = zones["compass"]
    for (r, c), role in compass_cells(z["h"]).items():
        x, y = (z["col"] + c + F) * PX, (z["row"] + r + F) * PX; dr_.rectangle([x, y, x + PX - 2, y + PX - 2], fill={"ring": (149, 138, 115), "blade": (245, 245, 245), "north": (196, 40, 27), "diag": (200, 190, 160), "centre": (149, 138, 115)}[role])
for mo in placed:
    x0_, y0_ = (mo["col"] + F) * PX, (mo["row"] + F) * PX; x1_, y1_ = x0_ + mo["footprint"][1] * PX, y0_ + mo["footprint"][0] * PX
    dr_.rectangle([x0_, y0_, x1_, y1_], fill=(222, 196, 155), outline=(60, 30, 10), width=2); dr_.text((x0_ + 2, y0_ + 2), mo["name"] + (" (simpl.)" if mo["variant"] == "simplified" else ""), fill=(40, 20, 5), font=fnt)
    if mo["shift_studs"] > 0.5: ay, ax = mo["true_anchor"]; dr_.line([(ax + F) * PX, (ay + F) * PX, (mo["col"] + mo["footprint"][1] / 2 + F) * PX, (mo["row"] + mo["footprint"][0] / 2 + F) * PX], fill=(220, 20, 20), width=2); dr_.ellipse([(ax + F) * PX - 4, (ay + F) * PX - 4, (ax + F) * PX + 4, (ay + F) * PX + 4], outline=(220, 20, 20), width=2)
dr_.rectangle([F * PX, F * PX, (F + GC) * PX, (F + GR) * PX], outline=(40, 25, 10), width=2)
im.save(os.path.join(out, "composition_preview.png")); print(json.dumps([{k_: v for k_, v in e.items() if k_ != "steps"} for e in log])); print("land cells", int(land.sum()), "max level", int(lev.max()), "preview", im.size)
