"""Catalog-driven LEGO scene (V0.5.1). Coordinates: r = row (LDraw -Z), c = column (LDraw +X), y = plate level (0 = underside of the board), 1 plate = 8 LDU = 3.2 mm, 1 stud = 20 LDU = 8 mm.
A part is placed by the footprint of its BODY (studs excluded) read from part_catalog.json, which is derived from the official LDraw geometry: no hand-written offsets, any part/rotation."""
import json, math, os, csv, hashlib
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
CAT = json.load(open(os.path.join(HERE, "part_catalog.json")))
PAIRS = json.load(open(os.path.join(HERE, "pair_sets.json")))
FALLBACK = {28: [19, 71, 72], 288: [2, 72], 2: [288], 378: [2, 288, 19], 70: [28, 72], 19: [28], 71: [72], 72: [71], 15: [71], 272: [72]}
MAT = {0: ((1, 0, 0, 0, 1, 0, 0, 0, 1)), 90: (0, 0, 1, 0, 1, 0, -1, 0, 0), 180: (-1, 0, 0, 0, 1, 0, 0, 0, -1), 270: (0, 0, -1, 0, 1, 0, 1, 0, 0)}
LOW_DIR = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}      # (dr, dc) direction in which the front (low end, local -Z) of a slope points, per rotation
def rot_xz(a, lx, lz):
    m = MAT[a]; return m[0] * lx + m[2] * lz, m[6] * lx + m[8] * lz
def footprint(part, rot):
    """(nr, nc, h) of the body of `part` rotated by `rot` : rows (LDraw z extent), columns (LDraw x extent), plates"""
    p = CAT[part]; lo, hi = p["lo"], p["hi"]
    xs = [rot_xz(rot, x, z) for x in (lo[0], hi[0]) for z in (lo[2], hi[2])]
    nc = (max(a for a, b in xs) - min(a for a, b in xs)) / 20.0; nr = (max(b for a, b in xs) - min(b for a, b in xs)) / 20.0
    h = math.ceil((hi[1] - lo[1]) / 8.0 - 0.15)
    return int(round(nr)), int(round(nc)), h
class Scene:
    def __init__(self, rows, cols):
        self.R, self.C = rows, cols; self.parts = []; self.occ = {}
    substitutions = None
    def add(self, part, colour, r, c, y, rot=0, region="", nr=None, nc=None, h=None):
        """footprint rows r..r+nr-1, columns c..c+nc-1 (computed from the catalogue when not given), bottom plane at plate y"""
        colour = int(colour)
        if PAIRS.get(part, {}).get(str(colour), 1) == 0:       # pair never catalogued by Rebrickable : keep the part, swap to the closest catalogued colour
            alt = [x for x in FALLBACK.get(colour, []) if PAIRS[part].get(str(x), 0) > 0]
            if not alt: raise ValueError("no catalogued colour for part %s colour %s" % (part, colour))
            if self.substitutions is None: self.substitutions = Counter()
            self.substitutions[(part, colour, alt[0])] += 1; colour = alt[0]
        r, c, y, rot = int(r), int(c), int(y), int(rot); fr, fc, fh = footprint(part, rot); nr = nr or fr; nc = nc or fc; h = h or fh
        if not (0 <= r and r + nr <= self.R and 0 <= c and c + nc <= self.C and y >= 0): raise ValueError("out of board %s %s" % (part, (r, c, nr, nc, y)))
        cells = [(rr, cc, yy) for rr in range(r, r + nr) for cc in range(c, c + nc) for yy in range(y, y + h)]
        for k in cells:
            if k in self.occ: raise ValueError("collision %s at %s with part %d" % (part, k, self.occ[k]))
        p = dict(id=len(self.parts) + 1, part=part, colour=colour, r=r, c=c, nr=nr, nc=nc, y=y, h=h, rot=rot, region=region)
        for k in cells: self.occ[k] = p["id"]
        self.parts.append(p); return p
    def free(self, r, c, y, nr, nc, h):
        return all((rr, cc, yy) not in self.occ and 0 <= rr < self.R and 0 <= cc < self.C for rr in range(r, r + nr) for cc in range(c, c + nc) for yy in range(y, y + h))
    def ldline(self, p):
        cat = CAT[p["part"]]; lo, hi = cat["lo"], cat["hi"]; a = p["rot"] % 360
        xs = [rot_xz(a, x, z) for x in (lo[0], hi[0]) for z in (lo[2], hi[2])]
        minx = min(v[0] for v in xs); minz = min(v[1] for v in xs)
        tx = p["c"] * 20 - minx; tz = -(p["r"] + p["nr"]) * 20 - minz; ty = -p["y"] * 8 - hi[1]
        m = MAT[a]
        return "1 %d %g %g %g %s %s.dat" % (p["colour"], tx, ty, tz, " ".join("%d" % v for v in m), p["part"])
    def ldr(self, title):
        out = ["0 " + title, "0 Name: diorama.ldr", "0 Author: procedural generator", "0 !LICENSE Original generated test"]
        for y in sorted({p["y"] for p in self.parts}):
            out.append("0 // layer at plate %d" % y); out += [self.ldline(p) for p in self.parts if p["y"] == y]; out.append("0 STEP")
        return "\n".join(out) + "\n"
    def top_support_ok(self, p):
        """own conservative pre-check : some stud-bearing part ends exactly at p.y under its footprint (engine-1 validation stays the judge)"""
        if p["y"] == 0: return True
        for rr in range(p["r"], p["r"] + p["nr"]):
            for cc in range(p["c"], p["c"] + p["nc"]):
                q = self.occ.get((rr, cc, p["y"] - 1))
                if q and CAT[self.parts[q - 1]["part"]]["studs"] > 0: return True
        return False
    def write(self, folder, title, extra=None):
        os.makedirs(folder, exist_ok=True)
        bad = [p["id"] for p in self.parts if not self.top_support_ok(p)]
        if bad: raise ValueError("parts without any support under them: %s" % bad[:20])
        json.dump(self.parts, open(os.path.join(folder, "parts.json"), "w"))
        text = self.ldr(title); open(os.path.join(folder, "diorama.ldr"), "w").write(text)
        cnt = Counter((p["part"], p["colour"]) for p in self.parts)
        with open(os.path.join(folder, "parts_list.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["part_num", "part_name", "color_id", "quantity", "stock_verified", "unit_price"])
            for (pn, col), q in sorted(cnt.items()): w.writerow([pn, CAT[pn]["title"], col, q, "false", ""])
        m = dict(height_plates=max(p["y"] + p["h"] for p in self.parts), pieces=len(self.parts), references=len(cnt), size_studs=[self.C, self.R], physical_size_mm=[self.C * 8, self.R * 8], max_height_mm=round(max(p["y"] + p["h"] for p in self.parts) * 3.2, 1),
                 colour_substitutions=[[k[0], k[1], k[2], v] for k, v in sorted((self.substitutions or {}).items())], physical_test=False, stock_verified=False, ldraw_sha256=hashlib.sha256(text.encode()).hexdigest()); m.update(extra or {})
        json.dump(m, open(os.path.join(folder, "metrics.json"), "w"), indent=1, default=int); return m
