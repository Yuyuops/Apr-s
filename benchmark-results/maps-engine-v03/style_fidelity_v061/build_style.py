#!/usr/bin/env python3
"""LEGO Maps V0.6 style engine :  geography -> composition (framing) -> strata/levels -> style (palette, finish, frame, title, decor) -> real-part LDraw.
usage : build_style.py STYLE.json COMPOSITION.json OUTDIR [--grid R C] [--frame N] [--no-title] [--no-decor]
Every rule is read from the style/composition files ; nothing refers to a particular country."""
import json, math, os, random, sys
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import geodata, strata, basefit
from scene import Scene, PAIRS, CAT
from tiler import tile, PLATES, TILES, BRICKS
from decor import text_cells
def avail(table, colour, minsets):
    """catalogue-aware part table : only sizes whose (part, colour) pair is catalogued by Rebrickable in >= minsets sets"""
    minsets = max(1, minsets)      # a pair must be catalogued at least once : never invent a part/colour reference
    t = {k: v for k, v in table.items() if v in CAT and PAIRS.get(v, {}).get(str(colour), 0) >= minsets}
    if (1, 1) not in t:
        for k, v in table.items():
            if k == (1, 1) and PAIRS.get(v, {}).get(str(colour), 0) > 0: t[k] = v
    if not t: raise ValueError("no catalogued part of this family in colour %s" % colour)
    return t
def ceil_div(a, b): return -(-a // b)
class Builder:
    def __init__(self, style, comp, out, grid=None, frame=None):
        self.st, self.cp, self.out = style, comp, out; self.R, self.C = grid or comp["grid_studs"]; self.F = frame if frame is not None else style["frame"]["width_studs"]
        self.rng = random.Random(style["relief"].get("seed", 7)); self.rel = style["relief"]; self.pal = style["palette"]; self.sf = style["surface"]; self.thick = self.rel["strata_thickness_plates"]; self.info = {}
        self.S = Scene(self.R + 2 * self.F, self.C + 2 * self.F); self.S.tops[2] = {(a, b) for a in range(self.R + 2 * self.F) for b in range(self.C + 2 * self.F)}; self.y0 = 2
    # ---------- levels
    def make_levels(self):
        geo = geodata.rasterise(self.cp["window"], (self.R, self.C), self.cp["territory_iso"], self.cp.get("sub", 8)); p = dict(self.rel); p["strata_widths"] = self.rel["sea_strata_widths_studs"]
        if not p["strata_widths"]: p["strata_widths"] = [0.0001]; flat_sea = True
        else: flat_sea = False
        p["foreign_level"] = self.rel["foreign_level"]; lev, cat = strata.levels_from_masks(geo, (self.R, self.C), p, self.cp.get("sub", 8)); lev = strata.smooth_levels(lev, 1)
        if flat_sea:      # no sea strata : the sea is one flat floor ; land base level is 1
            lev = np.where(cat["subject"], 1, np.where(cat["foreign"], self.rel["foreign_level"], 0)).astype(np.int16)
        self.S_sea = len(self.rel["sea_strata_widths_studs"]); self.base_land = self.S_sea + 1; subj, forn = cat["subject"], cat["foreign"]
        inl = self.rel.get("land_inland_widths_studs", [])
        if inl:   # land contours : stacked bands towards the inside of the territory
            d = ndimage.distance_transform_edt(subj)
            for w in sorted(inl): lev = np.where(subj & (d > w), lev + 1, lev)
            lev = np.where(subj, strata.smooth_levels(np.where(subj, lev, 0).astype(np.int16), 1) + 0, lev)
        self.lev, self.subj, self.forn, self.geo = lev.astype(int), subj, forn, geo; self.maxlev = int(self.lev.max())
        self.info["levels_histogram"] = {int(a): int(b) for a, b in zip(*np.unique(self.lev, return_counts=True))}
    def colour_of_level(self, k, kind="wall"):
        pl = self.pal
        if k == 0: return pl.get("floor_wall", pl["floor"]) if kind == "wall" else pl["floor"]
        if kind == "wall" and k <= self.S_sea and str(k) in pl.get("sea_levels_wall", {}): return pl["sea_levels_wall"][str(k)]
        if k <= self.S_sea and str(k) in pl.get("sea_levels", {}): return pl["sea_levels"][str(k)]
        if "land_levels" in pl:
            ll = pl["land_levels"]; kk = k - self.S_sea
            return ll.get(str(kk), ll[str(max(int(x) for x in ll))])
        return pl["subject_land"]
    # ---------- zones (flat, studded) for decor
    def reserve(self, h, w, anchor, margin, must=None):
        R, C = self.R, self.C; rr = {"top": margin, "bottom": R - h - margin, "middle": (R - h) // 2}; cc = {"left": margin, "right": C - w - margin, "centre": (C - w) // 2, "middle": (C - w) // 2}
        v, hh = anchor.split("-"); r0, c0 = rr[v], cc[hh]
        if anchor == "right-middle": r0, c0 = (R - h) // 2, C - w - margin
        if self.taken[r0:r0 + h, c0:c0 + w].any() or (self.subj[r0:r0 + h, c0:c0 + w].any()): return None
        self.taken[r0:r0 + h, c0:c0 + w] = True; blk = self.lev[r0:r0 + h, c0:c0 + w]; L = int(np.bincount(blk.ravel()).argmax()); self.lev[r0:r0 + h, c0:c0 + w] = L; self.studded[r0:r0 + h, c0:c0 + w] = True
        return r0, c0, L
    # ---------- layers
    def build_layers(self):
        S, R, C, F, th = self.S, self.R, self.C, self.F, self.thick; self.maxj = self.maxlev * th; mc = self.sf["min_sets"]
        lev = self.lev; jtop = lev * th; yb = self.y0; mosaic = self.rel.get("sea_mosaic"); self.top_y = {}
        colour_top = np.zeros((R, C), int)
        for r in range(R):
            for c in range(C):
                if self.subj[r, c]: colour_top[r, c] = self.colour_of_level(int(lev[r, c]), "top") if "land_levels" in self.pal else self.pal["subject_land"]
                elif self.forn[r, c]: colour_top[r, c] = self.pal["foreign_land"]
                else: colour_top[r, c] = self.colour_of_level(int(lev[r, c]), "top")
        if mosaic: self.apply_mosaic(colour_top, mosaic)
        if "land_highlight" in self.pal: self.apply_highlights(colour_top)
        self.colour_top = colour_top
        for j in range(0, self.maxj + 1):
            y = yb + j; k = ceil_div(j, th)
            body = {(r + F, c + F) for r, c in zip(*np.where(jtop > j))}; top = {(r + F, c + F) for r, c in zip(*np.where(jtop == j))}
            # body plates : wall colour of this stratum
            if body:
                col = self.colour_of_level(k); tb = avail(PLATES, col, mc); sup = S.stud_cells(y)
                for (r, c, nr, nc, part, rot) in tile(body, tb, self.rng, 2.0, 32, sup, 8): S.add(part, col, r, c, y, rot, "strata_body")
            if top: self.place_top(top, y, colour_top)
    def corner_rot(self, dr, dc):
        """rot (about the vertical) that sends the rounded corner of 25269 (local +x,-z = East,South at rot 0, verified on the LDraw mesh : the underside has no vertex there) to the corner (dr,dc) : dr=+1 south, dc=+1 east"""
        from scene import rot_xz
        for rot in (0, 90, 180, 270):
            x, z = rot_xz(rot, 1, -1)
            if (round(x), round(-z)) == (dc, dr): return rot
    def place_top(self, top, y, colour_top):
        S, F, mc = self.S, self.F, self.sf["min_sets"]; sup = S.stud_cells(y); groups = {}; jt = (y - self.y0); rounded = 0
        allc = set(top)
        # convex corners of the surface of this stratum : exposed on two perpendicular sides (neighbour absent from top+body of this plane)
        solid = self.solid_at(jt)
        corner_cells = {}
        if self.sf.get("round_corners", False):
            for (r, c) in top:
                if not (self.studded[r - F, c - F]):
                    for dr in (-1, 1):
                        for dc in (-1, 1):
                            if (r + dr, c) not in solid and (r, c + dc) not in solid and (r + dr, c + dc) not in solid and (r - dr, c) in solid and (r, c - dc) in solid: corner_cells[(r, c)] = (dr, dc)
        for (r, c), (dr, dc) in corner_cells.items():
            col = int(colour_top[r - F, c - F])
            if PAIRS.get("25269", {}).get(str(col), 0) >= 1 and (r, c) in allc:
                S.add("25269", col, r, c, y, self.corner_rot(dr, dc), "top_corner_round"); allc.discard((r, c)); rounded += 1
        self.info["rounded_corners"] = self.info.get("rounded_corners", 0) + rounded
        for (r, c) in allc:
            cc = colour_top[r - F, c - F]; stud = bool(self.studded[r - F, c - F]) or (self.subj[r - F, c - F] and self.sf["land"] == "plate" and self.rng.random() < self.sf["stud_fraction_land"] * 1.0)
            groups.setdefault((int(cc), stud), set()).add((r, c))
        import tiler
        for (col, stud), cells in sorted(groups.items()):
            mn = 0 if self.sf.get("allow_rare", False) else mc
            fam = PLATES if stud else TILES
            tbl = avail(fam, col, mn)
            if not stud and (1, 1) not in tbl:      # rare colour without a 1x1 tile : cover what it can, finish with the plates of the same colour, then the fallback colour
                tiler.PARTIAL = True; tiler.LEFT.clear()
                for (r, c, nr, nc, part, rot) in tile(cells, tbl, self.rng, self.sf["tile_bias"], self.sf["tile_max_area"], sup, 20): S.add(part, col, r, c, y, rot, "top_tile")
                left = set(tiler.LEFT); tiler.PARTIAL = False; tiler.LEFT.clear()
                if left:
                    try: pt = avail(PLATES, col, 0)
                    except ValueError: pt = {}
                    if pt:
                        tiler.PARTIAL = True; tiler.LEFT.clear()
                        for (r, c, nr, nc, part, rot) in tile(left, pt, self.rng, 1.8, 16, sup, 12): S.add(part, col, r, c, y, rot, "top_plate_rare")
                        left = set(tiler.LEFT); tiler.PARTIAL = False; tiler.LEFT.clear()
                    if left:
                        fb = self.sf.get("fallback_colour", 323); self.info["rare_colour_fallback_cells"] = self.info.get("rare_colour_fallback_cells", 0) + len(left)
                        for (r, c, nr, nc, part, rot) in tile(left, avail(TILES, fb, mc), self.rng, 1.6, 8, sup, 12): S.add(part, fb, r, c, y, rot, "top_tile_fallback")
            elif stud:
                if (1, 1) not in tbl:
                    tiler.PARTIAL = True; tiler.LEFT.clear()
                    for (r, c, nr, nc, part, rot) in tile(cells, tbl, self.rng, 1.8, 16, sup, 12): S.add(part, col, r, c, y, rot, "top_plate_rare")
                    left = set(tiler.LEFT); tiler.PARTIAL = False; tiler.LEFT.clear()
                    if left:
                        fb = self.sf.get("fallback_colour", 323); self.info["rare_colour_fallback_cells"] = self.info.get("rare_colour_fallback_cells", 0) + len(left)
                        for (r, c, nr, nc, part, rot) in tile(left, avail(PLATES, fb, mc), self.rng, 1.8, 8, sup, 12): S.add(part, fb, r, c, y, rot, "top_plate_fallback")
                else:
                    for (r, c, nr, nc, part, rot) in tile(cells, tbl, self.rng, 1.8, 16, sup, 12): S.add(part, col, r, c, y, rot, "top_plate")
            else:
                for (r, c, nr, nc, part, rot) in tile(cells, tbl, self.rng, self.sf["tile_bias"], self.sf["tile_max_area"], sup, 20): S.add(part, col, r, c, y, rot, "top_tile")
    def solid_at(self, j):
        """cells (scene coords) occupied at plane j by body or top : level_j >= j"""
        if not hasattr(self, "_jt"): self._jt = self.lev * self.thick
        F = self.F; return {(r + F, c + F) for r, c in zip(*np.where(self._jt >= j))}
    def apply_mosaic(self, colour_top, m):
        R, C, cs = self.R, self.C, m["cell_studs"]; rg = np.random.RandomState(self.rel.get("seed", 7)); nr, nc = ceil_div(R, cs), ceil_div(C, cs)
        nz = ndimage.gaussian_filter(rg.standard_normal((nr, nc)), m["scale_studs"] / cs); qs = np.cumsum(m["weights"])[:-1]; thr = np.quantile(nz, qs); idx = np.digitize(nz, thr)
        for r in range(R):
            for c in range(C):
                if not self.subj[r, c] and not self.forn[r, c] and self.lev[r, c] == 0: colour_top[r, c] = m["colours"][idx[r // cs, c // cs]]
        dp = m.get("deep_patch")
        if dp:
            h, w = dp["size_studs"]; rr = 0 if "top" in dp["corner"] else R - h; cc = 0 if "left" in dp["corner"] else C - w
            for r in range(rr, rr + h):
                for c in range(cc, cc + w):
                    # ragged edge : the patch boundary follows the mosaic cells
                    if not self.subj[r, c] and not self.forn[r, c] and self.lev[r, c] == 0 and (r - rr) // cs + (c - cc) // cs < (h + w) // (2 * cs) + 1: colour_top[r, c] = dp["colour"]
    def apply_highlights(self, colour_top):
        hi = self.pal["land_highlight"]; rg = np.random.RandomState(5); nz = ndimage.gaussian_filter(rg.standard_normal((self.R, self.C)), 2.2); nz = (nz - nz.mean()) / (nz.std() + 1e-9)
        top = self.lev == self.lev[self.subj].max() if self.subj.any() else None
        for r in range(self.R):
            for c in range(self.C):
                if self.subj[r, c] and self.lev[r, c] >= self.base_land + 1:
                    if nz[r, c] > 1.15: colour_top[r, c] = hi["peak"]
                    elif nz[r, c] > 0.45: colour_top[r, c] = hi["colour"]
    # ---------- frame, title, decor
    def frame(self):
        S, R, C, F = self.S, self.R, self.C, self.F; fr = self.st["frame"]; fr = dict(fr, corner=dict(fr["corner"], size=fr["corner"]["size"] if fr["corner"]["kind"] == "bracket" else F)); ring = {(r, c) for r in range(R + 2 * F) for c in range(C + 2 * F) if r < F or c < F or r >= R + F or c >= C + F}
        topy = self.y0 + self.maxj + 1 + fr["rim_above_top_plates"]; n = ceil_div(topy - self.y0, 3); mc = self.sf["min_sets"]; col = fr["colour"]
        for k in range(n):
            y = self.y0 + 3 * k
            for (r, c, nr, nc, part, rot) in tile(ring, avail(BRICKS, col, mc), self.rng, 1.8, 16, S.stud_cells(y), 14): S.add(part, col, r, c, y, rot, "frame")
        yc = self.y0 + 3 * n; cc = fr["cap_colour"]; gold = fr["corner"]["colour"]; size = fr["corner"]["size"]; g = {}
        for (r, c) in ring:
            near = lambda a, L: min(a, L - 1 - a); cr = near(r, R + 2 * F) < size and near(c, C + 2 * F) < size
            g.setdefault(gold if (cr and fr["corner"]["kind"] in ("bracket", "gold_cap", "gold_cap+scroll")) else cc, set()).add((r, c))
        for col2, cells in g.items():
            for (r, c, nr, nc, part, rot) in tile(cells, avail(TILES, col2, 5), self.rng, 1.8, 8, S.stud_cells(yc), 12): S.add(part, col2, r, c, yc, rot, "frame_cap")
        self.info["frame"] = dict(courses=n, top_plate=yc)
    SCROLL7 = ["..rrr..", ".r...r.", "r..r..r", "r.rrr.r", "r.....r", ".r...r.", "..rrr.."]
    SCROLL5 = ["rrt..", "r...t", "t.r..", "..t.r", "...rr"]
    def ornaments(self):
        S, F = self.S, self.F; fr = self.st["frame"]; k = fr["corner"]["kind"]
        if k not in ("scroll", "gold_cap+scroll"): return
        sz = fr["corner"]["size"]; gold = fr["corner"].get("ornament_colour", fr["corner"]["colour"]); pat = self.SCROLL7 if sz >= 7 else self.SCROLL5
        for (v, h) in (("top", "left"), ("top", "right"), ("bottom", "left"), ("bottom", "right")):
            z = self.reserve(sz, sz, v + "-" + h, 1)
            if not z: continue
            r0, c0, L = z; y = self.y0 + L * self.thick + 1
            for i in range(sz):
                for j in range(sz):
                    ch = pat[i if v == "top" else sz - 1 - i][j if h == "left" else sz - 1 - j]
                    if ch == "r": S.add("6141", gold, r0 + F + i, c0 + F + j, y, 0, "ornament_scroll")
                    elif ch == "t": S.add("3024", gold, r0 + F + i, c0 + F + j, y, 0, "ornament_scroll")
    def title(self):
        t = self.st.get("title")
        if not t: return
        cells, (h, w) = text_cells(t["text"], t["letter_gap"]); sc = t["scale"]; H, W = h * sc, w * sc
        # find a flat sea rectangle (no land, constant level) closest to the requested anchor
        best = None
        for r0 in range(self.R - H - 2, 1, -1):
            for c0 in range(3, self.C - W - 3):
                sl = (slice(r0 - 1, r0 + H + 1), slice(c0 - 1, c0 + W + 1))
                if self.subj[sl].any() or self.taken[r0:r0 + H, c0:c0 + W].any() or (t.get('on_foreign_land', True) is False and self.forn[sl].any()): continue
                a = self.st["title"]["anchor"]; tgt = ((0 if "top" in a else self.R), 0 if "left" in a else self.C / 2 if "centre" in a else self.C); score = math.hypot(r0 + H / 2 - tgt[0], c0 + W / 2 - tgt[1]) + 3 * float(np.ptp(self.lev[sl]))
                if best is None or score < best[0]: best = (score, r0, c0)
        if not best: self.info["title"] = "no flat sea zone found"; return
        _, r0, c0 = best; self.taken[r0:r0 + H, c0:c0 + W] = True; sl = (slice(r0 - 1, r0 + H + 1), slice(c0 - 1, c0 + W + 1)); L = int(np.bincount(self.lev[sl].ravel()).argmax()); self.lev[sl] = L; S, F = self.S, self.F; y = self.y0 + L * self.thick; colour = t["colour"]
        self.title_zone = (r0, c0, H, W, L); self.studded[r0:r0 + H, c0:c0 + W] = True
        self.info["title"] = dict(row=r0, col=c0, size=[H, W], level=L)
    def place_title_letters(self):
        t = self.st.get("title"); z = getattr(self, "title_zone", None)
        if not t or not z: return
        S, F = self.S, self.F; r0, c0, H, W, L = z; sc = t["scale"]; cells, _ = text_cells(t["text"], t["letter_gap"]); y = self.y0 + L * self.thick; colour = t["colour"]; mc = self.sf["min_sets"]
        px = {(r0 + F + r * sc + i, c0 + F + c * sc + j) for (r, c) in cells for i in range(sc) for j in range(sc)}
        for k in range(t["raise_plates"]):
            yy = y + 1 + k; last = k == t["raise_plates"] - 1; table = avail(TILES if last else PLATES, colour, 5)
            for (r, c, nr, nc, part, rot) in tile(px, table, self.rng, 1.8, 8, S.stud_cells(yy), 16): S.add(part, colour, r, c, yy, rot, "title_letters")
    def decor(self):
        S, F = self.S, self.F
        for d in self.st.get("decor", []):
            kind = d["kind"]
            if kind == "tricolour_flag":
                z = self.reserve(4, 6, "top-right", d["margin"] + 8)
                if z: r0, c0, L = z; self.flag = (r0, c0, L)
            if kind == "gold_plaque":
                z = self.reserve(2, 6, "top-right", d["margin"] + 1)
                if z: self.plaque = z
            if kind == "compass_wheel":
                z = self.reserve(7, 7, "top-left", d["margin"])
                if z: self.wheel = z
            if kind == "anchor":
                z = self.reserve(9, 7, "right-middle", d["margin"])
                if z: self.anchor_z = z
    def place_decor(self):
        S, F, th = self.S, self.F, self.thick
        if hasattr(self, "flag"):
            r0, c0, L = self.flag; y = self.y0 + L * th + 1
            for k, col in enumerate((2, 15, 4)):
                for (r, c, nr, nc, part, rot) in tile({(r0 + F + a, c0 + F + 2 * k + b) for a in range(4) for b in range(2)}, avail(TILES, col, 5), self.rng, 2, 8, S.stud_cells(y), 6): S.add(part, col, r, c, y, rot, "decor_flag")
        if hasattr(self, "plaque"):
            r0, c0, L = self.plaque; y = self.y0 + L * th + 1
            for (r, c, nr, nc, part, rot) in tile({(r0 + F + a, c0 + F + b) for a in range(1) for b in range(6)}, avail(TILES, 297, 5), self.rng, 2, 4, S.stud_cells(y), 6): S.add(part, 297, r, c, y, rot, "decor_plaque")
        if hasattr(self, "wheel"):
            r0, c0, L = self.wheel; y = self.y0 + L * th + 1; pat = ["..#.#..", ".#####.", "#.#.#.#", "#######", "#.#.#.#", ".#####.", "..#.#.."]
            for i in range(7):
                for j in range(7):
                    if pat[i][j] == "#": S.add("6141", 297, r0 + F + i, c0 + F + j, y, 0, "decor_wheel")
        if hasattr(self, "anchor_z"):
            r0, c0, L = self.anchor_z; y = self.y0 + L * th + 1; pat = ["...#...", "..###..", "...#...", "#..#..#", "#..#..#", "##.#.##", ".#####.", "..###..", "..#.#.."]
            for i in range(9):
                for j in range(7):
                    if pat[i][j] == "#": S.add("3070b", 0, r0 + F + i, c0 + F + j, y, 0, "decor_anchor")
    # ---------- run
    def run(self, with_title=True, with_decor=True, figures_cfg=None):
        self.figures_cfg = figures_cfg or {}
        import tiler; tiler.ORIENT_H = self.sf.get('orient_h', 1.0); tiler.SQUARISH = self.sf.get('squarish', 1.0)
        self.make_levels(); R, C = self.R, self.C; self.taken = np.zeros((R, C), bool); self.studded = np.zeros((R, C), bool)
        import figures.figures as FG
        self._fig_after, self.fig_log = FG.run(self, self.figures_cfg, CAT, PAIRS)
        self.ornaments(); self.decor() if with_decor else None
        if with_title: self.title()
        self.build_layers(); self.frame(); 
        if with_title: self.place_title_letters()
        if with_decor: self.place_decor()
        if self._fig_after: self._fig_after()
        self.info['figures'] = self.fig_log
        self.info["base_fit"] = [basefit.fit_layer(self.S, 1, 72, "backing", self.R + 2 * self.F, self.C + 2 * self.F, self.rng, 8), basefit.fit_layer(self.S, 0, 72, "backing", self.R + 2 * self.F, self.C + 2 * self.F, self.rng, 8)]
        m = self.S.write(self.out, "LEGO Maps V0.6 " + self.st["name"], dict(style=self.st["name"], composition=self.cp.get("_doc", "")[:60], grid_studs=[self.R, self.C], frame_studs=self.F, **self.info)); return m
if __name__ == "__main__":
    a = sys.argv[1:]; style = json.load(open(a[0])); comp = json.load(open(a[1])); out = a[2]; grid = None; frame = None
    if "--grid" in a: i = a.index("--grid"); grid = (int(a[i + 1]), int(a[i + 2]))
    if "--frame" in a: frame = int(a[a.index("--frame") + 1])
    if "--palette" in a: style["palette"]["sea_levels"] = json.load(open(a[a.index("--palette") + 1]))["sea_levels"]; style["palette"].update({k: v for k, v in json.load(open(a[a.index("--palette") + 1])).items() if k in ("floor", "sea_levels_wall", "floor_wall")}); style["surface"].update(json.load(open(a[a.index("--palette") + 1])).get("surface", {}))
    if "--round" in a: style["surface"]["round_corners"] = a[a.index("--round") + 1] == "1"
    fc = json.load(open(a[a.index("--figures") + 1])) if "--figures" in a else {}
    b = Builder(style, comp, out, grid, frame); m = b.run(with_title="--no-title" not in a, with_decor="--no-decor" not in a, figures_cfg=fc); print(json.dumps({k: m[k] for k in ("pieces", "references", "max_height_mm", "physical_size_mm")}), json.dumps(b.info.get("levels_histogram")))
