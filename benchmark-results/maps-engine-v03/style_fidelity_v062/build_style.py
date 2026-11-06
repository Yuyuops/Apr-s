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
    def make_levels_biomes(self):
        """BIOME MODE (V1.0) : the composition gives a class raster (codes -> biome names), the style gives for every biome a top colour, a wall colour, a base level and an optional interior relief gain.
        Relief rule (generic, documented) : cells of a biome with a gain rise by one level every `step` studs of distance from the biome edge, up to `max` extra levels. Nothing here depends on a country or a map."""
        bm = self.cp["biome_map"]; geo = geodata.rasterise_classes(os.path.join(HERE, bm["file"]) if not os.path.isabs(bm["file"]) else bm["file"], (self.R, self.C), self.cp.get("sub", 8)); codes = geo["codes"]
        names = {int(k): v for k, v in bm["classes"].items()}; defs = self.st["biomes"]; R, C = self.R, self.C
        for _ in range(bm.get("majority_passes", 1)):
            cnt = np.stack([ndimage.uniform_filter((codes == k).astype(float), 3) for k in sorted(names)], axis=-1); codes = np.array(sorted(names))[cnt.argmax(axis=-1)]
        lev = np.zeros((R, C), int); top = np.zeros((R, C), int); wall = np.zeros((R, C), int)
        for k, nm in names.items():
            d = defs[nm]; m = codes == k; lv = np.full((R, C), d["level"], int)
            g = d.get("gain")
            if g:
                dist = ndimage.distance_transform_edt(np.pad(m, 1, constant_values=True))[1:-1, 1:-1]; lv = lv + np.minimum(g["max"], (dist // g["step"]).astype(int))
            lev = np.where(m, lv, lev); top = np.where(m, d["top"], top); wall = np.where(m, d["wall"], wall)
        water = [k for k, nm in names.items() if defs[nm].get("water")]; subj = ~np.isin(codes, water)
        self.S_sea = 1; self.base_land = 2; self.lev, self.subj, self.forn = lev, subj, np.zeros((R, C), bool); self.geo = geo; self.maxlev = int(lev.max()); self.biome = dict(top=top, wall=wall, codes=codes, names=names)
        self.info["levels_histogram"] = {int(a): int(b) for a, b in zip(*np.unique(lev, return_counts=True))}
        self.info["biomes"] = {names[k]: int((codes == k).sum()) for k in names}; self.info["biome_mode"] = True
    def make_levels(self):
        if self.cp.get("biome_map"): return self.make_levels_biomes()
        geo = (geodata.rasterise_mask(os.path.join(HERE, self.cp["mask_png"]) if not os.path.isabs(self.cp["mask_png"]) else self.cp["mask_png"], (self.R, self.C), self.cp.get("sub", 8)) if self.cp.get("mask_png") else geodata.rasterise(self.cp["window"], (self.R, self.C), self.cp["territory_iso"], self.cp.get("sub", 8))); p = dict(self.rel); p["strata_widths"] = self.rel["sea_strata_widths_studs"]
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
        sub = self.cp.get("sub", 8); src = np.asarray(geo["subject"]).astype(bool); lab, n = ndimage.label(src, structure=np.ones((3, 3)))
        if n:
            idx = np.arange(1, n + 1); area = ndimage.sum(src, lab, idx); up = np.kron(subj.astype(np.uint8), np.ones((sub, sub), np.uint8)); kept = ndimage.maximum(up, lab, idx) > 0; big = area >= 16
            lost_idx = [int(i) for i in idx[big & ~kept]]; forced = []
            if self.rel.get("keep_islets") and lost_idx:      # cartographic generalisation : every source islet >= 0.25 stud2 is kept as ONE exaggerated stud (the stud it covers most)
                R, C = subj.shape
                for i in lost_idx:
                    cov = (lab == i).reshape(R, sub, C, sub).mean(axis=(1, 3)); r, c = np.unravel_index(int(cov.argmax()), cov.shape); subj[r, c] = True; forn[r, c] = False; self.lev[r, c] = self.base_land; forced.append([int(r), int(c)])
                self.subj, self.forn = subj, forn; self.info["levels_histogram"] = {int(a): int(b) for a, b in zip(*np.unique(self.lev, return_counts=True))}
            self.info["islets_forced_to_one_stud"] = forced
            self.info["island_audit"] = dict(source_components_ge_quarter_stud2=int(big.sum()), represented=int((big & kept).sum()), not_representable_lost=int((big & ~kept).sum()) - len(forced), lost_areas_stud2=[round(float(a) / (sub * sub), 2) for a in area[big & ~kept]][:40],
                                           note="source raster (Natural Earth or user-supplied mask) at %d px/stud ; a component is represented if at least one stud of the subject land covers it" % sub)
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
        if hasattr(self, "biome"):
            colour_top = self.biome["top"].copy(); tz = getattr(self, "title_zone", None); bd = (self.st.get("title") or {}).get("backdrop_colour")
            if tz and bd is not None: colour_top[tz[0]:tz[0] + tz[2], tz[1]:tz[1] + tz[3]] = bd           # plain backdrop under the title letters
            self.colour_top = colour_top; wall_col = self.biome["wall"]; hid = self.st.get("hidden_wall")
            big = int(jtop.max()) + 99; pj = np.pad(jtop, 1, constant_values=big); minnb = np.minimum.reduce([pj[:-2, 1:-1], pj[2:, 1:-1], pj[1:-1, :-2], pj[1:-1, 2:]])      # lowest top among the 4 neighbours (the frame counts as high)
            for j in range(0, self.maxj + 1):
                y = yb + j; body_mask = jtop > j; top_mask = jtop == j; sup = S.stud_cells(y)
                wc = np.where(body_mask & (j <= minnb), hid, wall_col) if hid is not None else wall_col      # planes hidden by the neighbours' bodies are never seen : one neutral colour -> larger plates, better overlap, fewer parts
                for col in sorted({int(x) for x in wc[body_mask]}):
                    body = {(r + F, c + F) for r, c in zip(*np.where(body_mask & (wc == col)))}; tb = avail(PLATES, col, mc)
                    for (r, c, nr, nc, part, rot) in tile(body, tb, self.rng, 2.0, 32, sup, 8): S.add(part, col, r, c, y, rot, "strata_body")
                top = {(r + F, c + F) for r, c in zip(*np.where(top_mask))}
                if top: self.place_top(top, y, colour_top)
            return
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
        fin = fr.get("finish") or {}; W2, H2 = C + 2 * F, R + 2 * F; rounds = []
        def band(r, c):   # (distance from the outer edge, position along the side) for a non-corner ring cell
            if r < F: return r, c
            if r >= H2 - F: return H2 - 1 - r, c
            return (c, r) if c < F else (W2 - 1 - c, r)
        if fin:
            near = lambda a, L: min(a, L - 1 - a)
            for (r, c) in list(ring):
                if near(r, H2) < size and near(c, W2) < size:
                    if fin.get("medallion"):
                        lr, lc = near(r, H2), near(c, W2)
                        for k in g: g[k].discard((r, c))
                        if 0 < lr < size - 1 and 0 < lc < size - 1: g.setdefault(cc, set()).add((r, c))
                        else: rounds.append((r, c, fin["medallion"]["colour"]))
                    continue
                d, pos = band(r, c)
                if "filet" in fin and d == fin["filet"]["index"]:
                    for k in g: g[k].discard((r, c))
                    g.setdefault((fin["filet"]["colour"], "filet", band(r, c)[0], r < F or r >= H2 - F), set()).add((r, c))
                elif "dots" in fin and d == fin["dots"]["index"] and pos % fin["dots"]["period"] == 0:
                    for k in g: g[k].discard((r, c))
                    rounds.append((r, c, fin["dots"]["colour"]))
        for col2, cells in g.items():
            if not cells: continue
            if isinstance(col2, tuple): col2 = col2[0]
            placed = set()
            for (r, c, nr, nc, part, rot) in tile(cells, avail(TILES, col2, 5), self.rng, 1.8, 8, S.stud_cells(yc), 12):
                p = S.add(part, col2, r, c, yc, rot, "frame_cap"); placed.update((rr, cc2) for rr in range(p["r"], p["r"] + p["nr"]) for cc2 in range(p["c"], p["c"] + p["nc"]))
            missing = cells - placed
            if missing: raise ValueError("frame cap cells left uncovered %s (colour %s)" % (sorted(missing)[:6], col2))
        for (r, c, col2) in rounds: S.add("98138", col2, r, c, yc, 0, "frame_ornament")
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
                if t.get("allow_subject_land"):      # no free flat zone on small maps : letters may stand on the subject land (zone must be entirely land, nothing else is touched)
                    if (not self.subj[sl].all()) or self.taken[r0:r0 + H, c0:c0 + W].any(): continue
                elif self.subj[sl].any() or self.taken[r0:r0 + H, c0:c0 + W].any() or (t.get('on_foreign_land', True) is False and self.forn[sl].any()): continue
                a = self.st["title"]["anchor"]; tgt = ((0 if "top" in a else self.R), 0 if "left" in a else self.C / 2 if "centre" in a else self.C); score = math.hypot(r0 + H / 2 - tgt[0], c0 + W / 2 - tgt[1]) + 3 * float(np.ptp(self.lev[sl]))
                if best is None or score < best[0]: best = (score, r0, c0)
        if not best: self.info["title"] = "no flat sea zone found"; return
        _, r0, c0 = best; self.taken[r0:r0 + H, c0:c0 + W] = True; sl = (slice(r0 - 1, r0 + H + 1), slice(c0 - 1, c0 + W + 1)); L = int(np.bincount(self.lev[sl].ravel()).argmax()); self.lev[sl] = L; S, F = self.S, self.F; y = self.y0 + L * self.thick; colour = t["colour"]
        self.title_zone = (r0, c0, H, W, L); sc0 = t["scale"]
        for (rr, cc) in cells:
            for i in range(sc0):
                for j in range(sc0): self.studded[r0 + rr * sc0 + i, c0 + cc * sc0 + j] = True   # studs only under letter cells : counters stay smooth (no stray studs)
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
    # ---------- flanks (V0.6.2) : curved slopes / progressive plates at the foot of a 3-plate wall
    ROT_TO_WALL = {(-1, 0): 0, (0, 1): 90, (1, 0): 180, (0, -1): 270}      # rotation that sends the high end (+z local) of 11477/15068 to the wall direction (dr, dc) ; verified on the mesh : high end at local +z, rot_xz(0,0,1) = north
    def plan_flanks(self):
        mode = self.rel.get("flank", "vertical"); self.skirts = []; self.flank_stats = dict(mode=mode, candidates=0, concave_skipped=0, colour_not_catalogued=0, blocked=0)
        if mode == "vertical": return
        lev, R, C = self.lev, self.R, self.C; used = set(); dirs = ((-1, 0), (0, 1), (1, 0), (0, -1))
        def ok_cell(r, c): return 0 <= r < R and 0 <= c < C and not self.subj[r, c] and not self.forn[r, c] and not self.taken[r, c] and (r, c) not in used
        def higher_nb(r, c): return [(dr, dc) for dr, dc in dirs if 0 <= r + dr < R and 0 <= c + dc < C and lev[r + dr, c + dc] > lev[r, c]]
        units = {d: [] for d in dirs}
        for r in range(R):
            for c in range(C):
                for dr, dc in dirs:
                    wr, wc = r + dr, c + dc; p2 = (r - dr, c - dc)
                    if not (0 <= wr < R and 0 <= wc < C): continue
                    if lev[wr, wc] != lev[r, c] + 1 or not ok_cell(r, c) or not ok_cell(*p2) or lev[p2] != lev[r, c]: continue
                    self.flank_stats["candidates"] += 1
                    hn = higher_nb(r, c)
                    if len(hn) > 1: self.flank_stats["two_wall_cells"] = self.flank_stats.get("two_wall_cells", 0) + 1
                    if self.rel.get("flank_strict", False) and (len(hn) != 1 or higher_nb(*p2)): self.flank_stats["concave_skipped"] += 1; continue
                    col = self.colour_of_level(int(lev[r, c]) + 1, "wall")
                    if PAIRS.get("11477", {}).get(str(col), 0) < 1 and mode == "curved": self.flank_stats["colour_not_catalogued"] += 1; continue
                    units[(dr, dc)].append(((r, c), p2, col))
        # one cell may be a skirt cell of one unit only ; two skirts may not overlap
        for d, lst in units.items():
            for (p1, p2, col) in lst:
                if p1 in used or p2 in used: self.flank_stats["blocked"] += 1; continue
                used.update((p1, p2)); self.skirts.append(dict(p1=p1, p2=p2, dir=d, colour=col, L=int(lev[p1])))
        for s in self.skirts:
            for cell in (s["p1"], s["p2"]): self.studded[cell] = True            # studded plates at the foot : the skirt clips onto them
        self.flank_stats["units"] = len(self.skirts)
        tot = sum(1 for r in range(R) for c in range(C) for dr, dc in dirs if 0 <= r + dr < R and 0 <= c + dc < C and lev[r + dr, c + dc] == lev[r, c] + 1 and not self.subj[r, c] and not self.forn[r, c])
        self.flank_stats["wall_edges_total"] = tot; self.flank_stats["wall_edges_covered"] = len(self.skirts)
    def place_flanks(self):
        if not getattr(self, "skirts", None): return
        S, F, th = self.S, self.F, self.thick; mode = self.rel["flank"]; placed = dict(p11477=0, p15068=0, plates=0)
        byrow = {}
        for s in self.skirts: byrow.setdefault((s["dir"], s["colour"], s["L"]), []).append(s)
        for (d, col, L), lst in byrow.items():
            y_top = self.y0 + L * th; yb = y_top + 1; dr, dc = d
            if mode == "curved":
                lst.sort(key=lambda s: s["p1"]); done = set(); idx = {s["p1"]: s for s in lst}
                for s in lst:
                    if s["p1"] in done: continue
                    r, c = s["p1"]; nb = (r, c + 1) if dr != 0 else (r + 1, c); t = idx.get(nb)
                    if t is not None and nb not in done and PAIRS.get("15068", {}).get(str(col), 0) >= 1:
                        cells = [s["p1"], s["p2"], t["p1"], t["p2"]]; r0 = min(x[0] for x in cells) + F; c0 = min(x[1] for x in cells) + F
                        S.add("15068", col, r0, c0, yb, self.ROT_TO_WALL[d], "flank_curved_2x2"); placed["p15068"] += 1; done.update((s["p1"], t["p1"]))
                    else:
                        cells = [s["p1"], s["p2"]]; r0 = min(x[0] for x in cells) + F; c0 = min(x[1] for x in cells) + F
                        S.add("11477", col, r0, c0, yb, self.ROT_TO_WALL[d], "flank_curved_1x2"); placed["p11477"] += 1; done.add(s["p1"])
            else:                          # progressive plates : 2 plates at the wall, 1 plate one stud further
                A = {(s["p1"][0] + F, s["p1"][1] + F) for s in lst}; B = {(s["p2"][0] + F, s["p2"][1] + F) for s in lst}
                from tiler import tile as _t
                try:
                    for (r, c, nr, nc, part, rot) in _t(A, avail(PLATES, col, 1), self.rng, 1.8, 8, S.stud_cells(yb), 8): S.add(part, col, r, c, yb, rot, "flank_plate_a1"); placed["plates"] += 1
                    for (r, c, nr, nc, part, rot) in _t(B, avail(TILES, col, 1), self.rng, 1.8, 8, S.stud_cells(yb), 8): S.add(part, col, r, c, yb, rot, "flank_tile_b")
                    for (r, c, nr, nc, part, rot) in _t(A, avail(TILES, col, 1), self.rng, 1.8, 8, S.stud_cells(yb + 1), 8): S.add(part, col, r, c, yb + 1, rot, "flank_tile_a2")
                except ValueError: self.flank_stats["colour_not_catalogued"] += 1
        self.flank_stats["placed"] = placed; self.info["flanks"] = self.flank_stats
    # ---------- run
    def run(self, with_title=True, with_decor=True, figures_cfg=None):
        self.figures_cfg = figures_cfg or {}
        import tiler; tiler.ORIENT_H = self.sf.get('orient_h', 1.0); tiler.SQUARISH = self.sf.get('squarish', 1.0)
        self.make_levels(); R, C = self.R, self.C; self.taken = np.zeros((R, C), bool); self.studded = np.zeros((R, C), bool)
        import figures.figures as FG
        self._fig_after, self.fig_log = FG.run(self, self.figures_cfg, CAT, PAIRS)
        self.ornaments(); self.decor() if with_decor else None
        if with_title: self.title()
        self.plan_flanks(); self.build_layers(); self.place_flanks(); self.frame(); 
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
    if "--flank" in a: style["relief"]["flank"] = a[a.index("--flank") + 1]
    if "--round" in a: style["surface"]["round_corners"] = a[a.index("--round") + 1] == "1"
    fc = json.load(open(a[a.index("--figures") + 1])) if "--figures" in a else {}
    b = Builder(style, comp, out, grid, frame); m = b.run(with_title="--no-title" not in a, with_decor="--no-decor" not in a, figures_cfg=fc); print(json.dumps({k: m[k] for k in ("pieces", "references", "max_height_mm", "physical_size_mm")}), json.dumps(b.info.get("levels_histogram")))
