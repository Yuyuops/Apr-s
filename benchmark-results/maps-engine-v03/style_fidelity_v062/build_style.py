#!/usr/bin/env python3
"""LEGO Maps V0.6 style engine :  geography -> composition (framing) -> strata/levels -> style (palette, finish, frame, title, decor) -> real-part LDraw.
usage : build_style.py STYLE.json COMPOSITION.json OUTDIR [--grid R C] [--frame N] [--no-title] [--no-decor]
Every rule is read from the style/composition files ; nothing refers to a particular country."""
import json, math, os, random, sys
from collections import Counter
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import geodata, strata, basefit
from scene import Scene, PAIRS, CAT, LOW_DIR
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
        if self.rel.get("smooth_height"): self.smooth_heights(self.rel["smooth_height"], names, codes)
    def smooth_heights(self, cfg, names, codes):
        """V16 (ON ONLY with relief.smooth_height) : relief by progressive 1-plate steps instead of 2-plate strata. The height of every LAND cell (class level x strata thickness, plus the interior gain) is smoothed by a Gaussian
        (normalised over land cells only, so water never pulls the coast up or down) and rounded to plates ; water and the classes listed in `keep` (e.g. craters) keep their height ; land stays at least `coast_min` plates above the water.
        Heights remain an ESTIMATE from the semantic zones (no altitude data)."""
        th0 = self.thick; h = (self.lev * th0).astype(float); land = self.subj.copy(); sig = float(cfg.get("sigma", 1.0)); keep = np.isin(codes, [k for k, nm in names.items() if nm in cfg.get("keep", [])])
        num = ndimage.gaussian_filter(np.where(land, h, 0.0), sig); den = ndimage.gaussian_filter(land.astype(float), sig); hs = np.where(land & (den > 1e-6), num / np.maximum(den, 1e-6), h)
        hs = np.where(keep, h, hs); jt = np.where(land, np.rint(hs).astype(int), h.astype(int)); wl = int(h[~land].max()) if (~land).any() else 0; jt = np.where(land, np.maximum(jt, wl + int(cfg.get("coast_min", 1))), jt)
        if cfg.get("coast_ramp") and (~land).any():                                  # banks : height above the water grows by `coast_ramp` plates per stud inland (gentle beaches instead of a vertical bank)
            dw = ndimage.distance_transform_edt(land); cap = wl + int(cfg.get("coast_min", 1)) + np.floor((dw - 1) * float(cfg["coast_ramp"])).astype(int); jt = np.where(land & ~keep & (dw <= float(cfg.get("coast_width", 4))), np.minimum(jt, cap), jt)          # the ramp only shapes the bank belt (coast_width studs) : inland massifs keep their full height
        mw = int(cfg.get("min_peak_width", 0))
        if mw >= 2:                                                                    # no needle-like spires : every height level must be made of regions at least mw x mw studs wide (a 1-2 stud column of stacked plates is both unnatural and a single point of failure)
            st_el = np.ones((mw, mw), bool)
            for L in range(int(jt.max()), wl + int(cfg.get("coast_min", 1)) + 1, -1):
                m = (jt >= L) & land & ~keep; op = ndimage.binary_opening(np.pad(m, mw, constant_values=False), structure=st_el)[mw:-mw, mw:-mw]; jt = np.where(m & ~op, L - 1, jt)
        self.thick = 1; self.lev = jt.astype(int); self.maxlev = int(jt.max()); self.info["levels_histogram"] = {int(a): int(b) for a, b in zip(*np.unique(jt, return_counts=True))}; self.info["smooth_height"] = dict(sigma=sig, th0=th0, max_plates=self.maxlev)
    def plan_slopes(self):
        """V16 (ON ONLY with surface.cliff_slopes) : at the FOOT of a cliff (a land cell with exactly one land neighbour at least `min_dh` plates higher), the plain top tile is replaced by a cheese slope (part 54200, 31 degrees, 2 plates high) rising toward the cliff,
        in the colour of the cell : a talus instead of a vertical block face. A cell with two or more higher neighbours (concave corner) keeps its tile. Placement is deterministic (no randomness)."""
        self.slopes = {}; cfg = self.sf.get("cliff_slopes")
        if not cfg: return
        jt = self.lev * self.thick; R, C = self.R, self.C; mc = self.sf["min_sets"]; part = cfg.get("part", "54200"); mind = int(cfg.get("min_dh", 2)); top = self.biome["top"]
        for r in range(R):
            for c in range(C):
                if not self.subj[r, c] or self.studded[r, c]: continue
                hi = [(dr, dc, int(jt[r + dr, c + dc] - jt[r, c])) for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)) if 0 <= r + dr < R and 0 <= c + dc < C and self.subj[r + dr, c + dc] and jt[r + dr, c + dc] - jt[r, c] >= mind]
                if len(hi) != 1: continue
                dr, dc, dh = hi[0]; col = int(top[r, c])
                if PAIRS.get(part, {}).get(str(col), 0) < max(1, mc): continue
                rot = next((a for a, d in LOW_DIR.items() if d == (-dr, -dc)), None)
                if rot is not None: self.slopes[(r, c)] = (rot, col)
        self.info["cliff_slopes_planned"] = len(self.slopes)
    def plan_details(self):
        """V16 (ON ONLY with a `details` block in the style) : vegetation placed by RULES, not at random. For every rule {class, part, colours, density, min_dist} the cells of the class become studded plates and a deterministic blue-noise
        sample (seeded, minimum spacing) receives the detail piece on the stud of the surface (round bricks 3062b = trees, round plates 6141 = bushes). Rules read the semantic classes, never the picture."""
        self.details_plan = []; cfg = self.st.get("details")
        if not cfg: return
        rng = random.Random(int(cfg.get("seed", 11))); names = self.biome["names"]; codes = self.biome["codes"]; R, C = self.R, self.C; mc = self.sf["min_sets"]; taken = set()
        for rule in cfg.get("rules", []):
            ks = [k for k, nm in names.items() if nm in rule["classes"]]
            if not ks: continue
            cells = [(r, c) for r in range(R) for c in range(C) if codes[r, c] in ks and not self.taken[r, c]]
            for (r, c) in cells:
                if rule.get("studded_class", True): self.studded[r, c] = True
            md = float(rule.get("min_dist", 2.0)); target = int(rule.get("density", 0.3) * len(cells)); order = cells[:]; rng.shuffle(order); placed = []; cols = rule["colours"]
            for (r, c) in order:
                if len(placed) >= target: break
                if any((r - a) ** 2 + (c - b) ** 2 < md * md for a, b in placed + [q for q in taken]): continue
                if rule.get("interior_only", True) and not all(0 <= r + dr < R and 0 <= c + dc < C and codes[r + dr, c + dc] in ks for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))): continue
                col = cols[len(placed) % len(cols)]
                if PAIRS.get(rule["part"], {}).get(str(col), 0) < max(1, mc): continue
                if not rule.get("studded_class", True):                                    # sparse detail on a tiled surface : the cell and one neighbour of the same class become a studded 1x2 patch (the piece needs a stud and a 2-stud plate under it)
                    nb = next(((r + dr, c + dc) for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)) if 0 <= r + dr < R and 0 <= c + dc < C and codes[r + dr, c + dc] in ks and (r + dr, c + dc) not in taken and not self.studded[r + dr, c + dc]), None)
                    if nb is None or self.studded[r, c]: continue
                    self.studded[r, c] = True; self.studded[nb] = True
                placed.append((r, c)); self.details_plan.append((r, c, rule["part"], int(col), rule.get("region", "detail")))
            taken.update(placed)
        self.info["details_planned"] = len(self.details_plan)
    def place_details(self):
        if not getattr(self, "details_plan", None): return
        S, F = self.S, self.F; jt = self.lev * self.thick; n = 0
        for (r, c, part, col, region) in getattr(self, "details_plan", []):
            y = self.y0 + int(jt[r, c]) + 1
            try: S.add(part, col, r + F, c + F, y, 0, region); n += 1
            except ValueError: self.info["details_skipped"] = self.info.get("details_skipped", 0) + 1
        self.info["details_placed"] = n
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
                if self.sf.get("body_tiler") == "wild" and hid is not None and body_mask.any() and self.body_layer_wild(j, y, body_mask, ~(j <= minnb), wall_col, hid, mc): wc = None
                for col in (sorted({int(x) for x in wc[body_mask]}) if wc is not None else []):
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
    def body_layer_wild(self, j, y, body_mask, visible_mask, wall_col, hid, mc):
        """V16 structural tiler (ON ONLY with surface.body_tiler = "wild"). One layer of strata body : cells whose side faces are visible keep their wall colour (fixed) ; cells hidden by the neighbours' bodies are WILD
        (any colour, never seen) so a one-cell visible strip can be extended into the hidden cells behind it : larger parts, 2+ studs, no lonely 1x1 plates. The engine tiler (maps_engine.tiling : orphan cost, seam stagger,
        local search + merge of small parts) is reused unchanged. Returns True when the layer was tiled, False to let the caller fall back to the legacy tiler."""
        sys.path.insert(0, os.path.join(HERE, "..", "engine"))
        from maps_engine import tiling as TL
        S, F, R, C = self.S, self.F, self.R, self.C; fixed = np.where(body_mask & visible_mask, wall_col, -1).astype(int); wild = body_mask & ~visible_mask
        below = -np.ones((R, C), int)
        if j > 0:
            for r in range(R):
                for c in range(C): below[r, c] = S.occ.get((r + F, c + F, y - 1), -1)
        allowed = lambda part, col: PAIRS.get(part, {}).get(str(int(col)), 0) >= max(1, mc)
        def hidden_colour_of(x, z, w, d, part):
            for col in ([hid] if hid is not None else []) + [72, 71, 0, 15, 70, 7]:
                if allowed(part, col): return col
            for col in sorted(PAIRS.get(part, {}), key=lambda c: -PAIRS[part][c]):      # hidden cells are never seen : any catalogued colour of this part is acceptable (V16 : the 28/hid fallback could pick an uncatalogued pair)
                if allowed(part, col): return int(col)
            for col in sorted(PAIRS.get(part, {}), key=lambda c: -PAIRS[part][c]):      # nothing reaches the min-sets threshold : still never an uncatalogued pair (hidden cell, never seen)
                if PAIRS[part][col] >= 1: return int(col)
            return hid if hid is not None else 72
        catalog = {(max(k), min(k)): v for k, v in PLATES.items() if v in CAT and k[0] * k[1] <= self.sf.get("body_max_area", 64)}
        above_pen = float(self.sf.get("body_above_pen", 0.0)); above = None
        if above_pen:                                              # clusters of cells that stand ABOVE this layer (jtop >= j+1) : see maps_engine.tiling (single-point-of-failure penalty)
            above, _ = ndimage.label(self.lev * self.thick >= j + 1); above = above - 1
        flag = None                                                    # V16 reinforcement pass : cells of parts that were single points of failure in the previous build are re-tiled with SMALL parts (see tools/reinforce_v16.py)
        if self.sf.get("reinforce_file"):
            if not hasattr(self, "_rf"): self._rf = json.load(open(self.sf["reinforce_file"]))
            cells = self._rf.get(str(y))
            if cells:
                flag = np.zeros((R, C), bool)
                for (rr, cc) in cells:
                    if 0 <= rr < R and 0 <= cc < C: flag[rr, cc] = True
        fixed_all, wild_all = fixed, wild
        if flag is not None: fixed = np.where(flag, -1, fixed_all); wild = wild_all & ~flag
        try:
            parts = TL.best_tiling(fixed, wild, below, hidden_colour_of, catalog, tries=self.sf.get("body_tiler_tries", 3), seed=7919 * j + 13, allowed=allowed, orphan_cost=self.sf.get("body_orphan_cost", 60.0), stagger=self.sf.get("body_stagger", 2.0), seam_pen=self.sf.get("body_seam_pen", 4.0), above_label=above, above_pen=above_pen) if (fixed >= 0).any() or wild.any() else []
            if parts: parts = TL.merge_small(parts, catalog, allowed=allowed); parts = TL.local_improve(parts, catalog, below, tries=self.sf.get("body_local_tries", 40), seed=j, allowed=allowed, above_label=above, above_pen=above_pen)
            if flag is not None:
                small = {k: v for k, v in catalog.items() if k[0] * k[1] <= int(self.sf.get("reinforce_max_area", 4))}; fx = np.where(flag, fixed_all, -1); wd = wild_all & flag
                parts += TL.best_tiling(fx, wd, below, hidden_colour_of, small, tries=3, seed=j + 7, allowed=allowed, orphan_cost=self.sf.get("body_orphan_cost", 60.0), stagger=self.sf.get("body_stagger", 2.0) * 3, seam_pen=self.sf.get("body_seam_pen", 4.0) * 2) if (fx >= 0).any() or wd.any() else []
        except RuntimeError: return False
        if any(PAIRS.get(catalog[(max(p["w"], p["d"]), min(p["w"], p["d"]))], {}).get(str(int(p["colour"])), 1) == 0 for p in parts):
            self.info["wild_uncatalogued_fallback"] = self.info.get("wild_uncatalogued_fallback", 0) + 1; return False      # a part/colour pair the catalogue refuses : let the legacy tiler (which respects availability) do this layer
        for p in parts:
            key = (max(p["w"], p["d"]), min(p["w"], p["d"])); part = catalog[key]; rot = 0 if p["d"] >= p["w"] else 90
            S.add(part, p["colour"], p["x"] + F, p["z"] + F, y, rot, "strata_body")
        self.info["wild_layers"] = self.info.get("wild_layers", 0) + 1; return True
    def top_seam_tiles(self, groups, y):
        """V16 (ON ONLY with surface.top_tiler = "seam") : the plain top tiles of this layer are tiled by the engine tiler with the part ids of the layer below, so that tiles bridge the seams of the plates under them (>= 2 supporting parts
        where possible) instead of resting on a single plate. Colours without a 1x1 tile keep the legacy path. Returns the groups that were NOT handled."""
        sys.path.insert(0, os.path.join(HERE, "..", "engine"))
        from maps_engine import tiling as TL
        S, mc = self.S, self.sf["min_sets"]; mn = 0 if self.sf.get("allow_rare", False) else mc; fixed = -np.ones((S.R, S.C), int); rest = {}; handled = False; tcat = {}
        for (col, stud), cells in sorted(groups.items()):
            if stud: rest[(col, stud)] = cells; continue
            try: tbl = avail(TILES, col, mn)
            except ValueError: rest[(col, stud)] = cells; continue
            if (1, 1) not in tbl or self.sf.get("allow_rare", False): rest[(col, stud)] = cells; continue
            for (r, c) in cells: fixed[r, c] = col
            handled = True
        if not handled: return groups
        below = -np.ones((S.R, S.C), int)
        for (r, c) in zip(*np.where(fixed >= 0)): below[r, c] = S.occ.get((int(r), int(c), y - 1), -1)
        catalog = {(max(k), min(k)): v for k, v in TILES.items() if v in CAT}; allowed = lambda part, col: PAIRS.get(part, {}).get(str(int(col)), 0) >= max(1, mn)
        try:
            parts = TL.best_tiling(fixed, np.zeros_like(fixed, bool), below, lambda *a: 72, catalog, tries=self.sf.get("top_tiler_tries", 3), seed=104729 * int(y) + 5, allowed=allowed, orphan_cost=self.sf.get("top_orphan_cost", 60.0), stagger=self.sf.get("top_stagger", 6.0), seam_pen=self.sf.get("top_seam_pen", 6.0))
        except RuntimeError: return groups
        for p in parts:
            key = (max(p["w"], p["d"]), min(p["w"], p["d"])); self.S.add(catalog[key], p["colour"], p["x"], p["z"], y, 0 if p["d"] >= p["w"] else 90, "top_tile")
        self.info["seam_top_layers"] = self.info.get("seam_top_layers", 0) + 1; return rest
    def corner_rot(self, dr, dc):
        """rot (about the vertical) that sends the rounded corner of 25269 (local +x,-z = East,South at rot 0, verified on the LDraw mesh : the underside has no vertex there) to the corner (dr,dc) : dr=+1 south, dc=+1 east"""
        from scene import rot_xz
        for rot in (0, 90, 180, 270):
            x, z = rot_xz(rot, 1, -1)
            if (round(x), round(-z)) == (dc, dr): return rot
    def place_top(self, top, y, colour_top):
        S, F, mc = self.S, self.F, self.sf["min_sets"]; sup = S.stud_cells(y); groups = {}; jt = (y - self.y0); rounded = 0
        if getattr(self, "slopes", None):
            for (r, c) in sorted(top):
                sl = self.slopes.get((r - F, c - F))
                if sl is not None: S.add(self.sf["cliff_slopes"].get("part", "54200"), sl[1], r, c, y, sl[0], "cliff_slope"); self.info["cliff_slopes_placed"] = self.info.get("cliff_slopes_placed", 0) + 1
            top = {k for k in top if (k[0] - F, k[1] - F) not in self.slopes}
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
        if self.sf.get("top_tiler") == "seam": groups = self.top_seam_tiles(groups, y)
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
            placed = set(); import tiler as _t; tb = avail(TILES, col2, 5)
            if (1, 1) in tb: tiles_ = tile(cells, tb, self.rng, 1.8, 8, S.stud_cells(yc), 12); left_ = set()
            else:      # colour without a 1x1 tile (e.g. gold) and an odd-length run : cover what the tiles can, finish single cells with a round 1x1 tile of the same colour (98138) when catalogued
                _t.PARTIAL = True; _t.LEFT.clear(); tiles_ = tile(cells, tb, self.rng, 1.8, 8, S.stud_cells(yc), 12); left_ = set(_t.LEFT); _t.PARTIAL = False; _t.LEFT.clear()
            for (r, c, nr, nc, part, rot) in tiles_:
                p = S.add(part, col2, r, c, yc, rot, "frame_cap"); placed.update((rr, cc2) for rr in range(p["r"], p["r"] + p["nr"]) for cc2 in range(p["c"], p["c"] + p["nc"]))
            for (r, c) in sorted(left_ - placed):
                if PAIRS.get("98138", {}).get(str(col2), 0) >= 1: S.add("98138", col2, r, c, yc, 0, "frame_cap_single"); placed.add((r, c)); self.info["frame_single_round_tiles"] = self.info.get("frame_single_round_tiles", 0) + 1
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
    def plan_objects(self):
        """V17 (ON ONLY with an `objects` block in the style or --objects FILE) : parametric assemblies of real catalogue pieces (objects.py) + terrain edits (river, path) described by a MANIFEST of observed/estimated objects.
        Footprints are flattened and studded here (before slopes/details/layers) ; the pieces are placed by place_objects() once the surface exists. Nothing happens without a manifest."""
        self.obj_plan = []; self.obj_log = dict(items=[], skipped=[]); cfg = self.st.get("objects")
        if not cfg or not hasattr(self, "biome"): return
        import objects as OB
        man = json.load(open(cfg["file"] if os.path.isabs(cfg["file"]) else os.path.join(HERE, cfg["file"]))); o_r, o_c = self.cp.get("origin_rc", [0, 0]); R, C = self.R, self.C; names = self.biome["names"]; inv = {nm: k for k, nm in names.items()}; defs = self.st["biomes"]
        codes, top, wall = self.biome["codes"], self.biome["top"], self.biome["wall"]; ground = man.get("ground_class", "grass")
        def set_cell(r, c, cls, lv=None):
            codes[r, c] = inv[cls]; top[r, c] = defs[cls]["top"]; wall[r, c] = defs[cls]["wall"]; self.lev[r, c] = defs[cls]["level"] if lv is None else lv; self.subj[r, c] = not defs[cls].get("water")
        def line(a, b):
            (r0, c0), (r1, c1) = a, b; n = max(abs(r1 - r0), abs(c1 - c0), 1); return [(int(round(r0 + (r1 - r0) * i / n)), int(round(c0 + (c1 - c0) * i / n))) for i in range(n + 1)]
        inside = lambda r, c: 0 <= r < R and 0 <= c < C
        for it in man["items"]:
            t = it["type"]; prov = it.get("provenance", "estimated"); log = dict(type=t, provenance=prov, source=it.get("source", ""))
            if t == "river":
                pts = [(int(a) - o_r, int(b) - o_c) for a, b in it["points"]]; cls = it.get("class", "water"); cells = set()
                for a, b in zip(pts, pts[1:]): cells.update(line(a, b))
                for k in range(int(it.get("width", 1)) - 1): cells.update({(r + dr, c + dc) for (r, c) in list(cells) for dr, dc in ((0, 1), (1, 0))})
                n = 0
                for (r, c) in sorted(cells):
                    if inside(r, c) and not self.taken[r, c] and codes[r, c] != inv.get("void", -9): set_cell(r, c, cls, it.get("level")); n += 1
                log.update(cells=n); self.obj_log["items"].append(log); continue
            if t == "land":                                                                        # land bridge / causeway : cells become `ground` at a fixed level
                pts = [(int(a) - o_r, int(b) - o_c) for a, b in it["points"]]; cells = set()
                for a, b in zip(pts, pts[1:]): cells.update(line(a, b))
                for k in range(int(it.get("width", 1)) - 1): cells.update({(r + dr, c + dc) for (r, c) in list(cells) for dr, dc in ((0, 1), (1, 0))})
                n = 0
                for (r, c) in sorted(cells):
                    if inside(r, c) and not self.taken[r, c]: set_cell(r, c, it.get("class", ground), int(it.get("level", defs[ground]["level"]))); top[r, c] = it.get("colour", top[r, c]); n += 1
                log.update(cells=n); self.obj_log["items"].append(log); continue
            if t == "path":
                pts = [(int(a) - o_r, int(b) - o_c) for a, b in it["points"]]; cells = set()
                for a, b in zip(pts, pts[1:]): cells.update(line(a, b))
                n = 0
                for (r, c) in sorted(cells):
                    if inside(r, c) and self.subj[r, c] and not self.taken[r, c]: top[r, c] = it.get("colour", 19); n += 1
                log.update(cells=n); self.obj_log["items"].append(log); continue
            if t == "scatter":
                self.plan_scatter(it, OB, o_r, o_c, log); continue
            r0, c0 = int(it["row"]) - o_r, int(it["col"]) - o_c; asm = OB.build(t, it.get("params", {})); br0, bc0, br1, bc1 = asm.bbox(); nr, nc = br1 - br0, bc1 - bc0
            rr, cc = r0 + br0, c0 + bc0
            errs = OB.check_assembly(asm, self.sf["min_sets"])
            if errs or rr < 0 or cc < 0 or rr + nr > R or cc + nc > C or self.taken[rr:rr + nr, cc:cc + nc].any():
                self.obj_log["skipped"].append(dict(log, reason=errs or "outside the grid or on a reserved zone")); continue
            cells = [(rr + a, cc + b) for a in range(nr) for b in range(nc)]
            if t == "bridge":                                                                      # deck rests on the two bank cells (first and last) ; the cells between stay water
                ends = [cells[0], cells[-1]]; L = max(int(self.lev[e]) for e in ends)
                if any(codes[e] == inv.get("void", -9) for e in ends): self.obj_log["skipped"].append(dict(log, reason="bank on the void")); continue
                for e in ends:
                    if not self.subj[e]: set_cell(e[0], e[1], ground, L)
                    else: self.lev[e] = L
                    self.studded[e] = True
                for e in cells: self.taken[e] = True
            else:
                land = [int(self.lev[e]) for e in cells if self.subj[e]]; L = int(it.get("params", {}).get("level", int(np.median(land)) if land else defs[ground]["level"]))
                for e in cells:
                    if not self.subj[e] or it.get("force_ground"): set_cell(e[0], e[1], it.get("ground", ground), L)
                    else: self.lev[e] = L
                    self.studded[e] = True; self.taken[e] = True
            self.obj_plan.append(dict(asm=asm, r=r0, c=c0, level=L, item=dict(log, row=r0 + o_r, col=c0 + o_c, params=it.get("params", {})), cells=cells))
        self.info["objects_planned"] = len(self.obj_plan)
    def plan_scatter(self, it, OB, o_r, o_c, log):
        """deterministic scatter of a small assembly (e.g. trees) on cells of given classes : same blue-noise rule as the V16 details planner ; a 2x2 variant needs 4 free cells of the same level, else it falls back to the 1x1 variant"""
        names = self.biome["names"]; codes = self.biome["codes"]; ks = [k for k, nm in names.items() if nm in it["classes"]]; R, C = self.R, self.C
        cells = [(r, c) for r in range(R) for c in range(C) if codes[r, c] in ks and not self.taken[r, c]]
        pos = OB.scatter_positions(cells, it.get("density", 0.25), float(it.get("min_dist", 2.0)), int(it.get("seed", 5))); rng = random.Random(int(it.get("seed", 5)) + 1); vs = it.get("variants", [["small", 1.0]]); n = 0; used = set()
        for (r, c) in pos:
            v = rng.choices([x[0] for x in vs], [x[1] for x in vs])[0]; asm = OB.build(it["assembly"], dict(it.get("params", {}), variant=v)); br0, bc0, br1, bc1 = asm.bbox()
            cl = [(r + a, c + b) for a in range(br1 - br0) for b in range(bc1 - bc0)]
            if not all(0 <= x < R and 0 <= y < C and codes[x, y] in ks and not self.taken[x, y] and (x, y) not in used and self.lev[x, y] == self.lev[r, c] for x, y in cl):
                asm = OB.build(it["assembly"], dict(it.get("params", {}), variant="small")); cl = [(r, c)]
                if self.taken[r, c] or (r, c) in used: continue
            for e in cl: self.studded[e] = True; self.taken[e] = True; used.add(e)
            self.obj_plan.append(dict(asm=asm, r=r, c=c, level=int(self.lev[r, c]), item=dict(type=it["assembly"], variant=v, provenance=it.get("provenance", "estimated")), cells=cl)); n += 1
        log.update(count=n, scatter=it["assembly"]); self.obj_log["items"].append(log)
    def place_objects(self):
        if not getattr(self, "obj_plan", None): return
        S, F = self.S, self.F; placed = Counter(); failed = []; rows = []
        for o in self.obj_plan:
            asm = o["asm"]; yb = self.y0 + int(o["level"]) * self.thick + 1; items = []
            ok = all(S.free(o["r"] + p["r"] + F, o["c"] + p["c"] + F, yb + p["dy"], p["nr"], p["nc"], p["h"]) for p in asm.pieces)
            if not ok: failed.append(dict(o["item"], reason="volume not free")); continue
            for p in asm.pieces: S.add(p["part"], p["colour"], o["r"] + p["r"] + F, o["c"] + p["c"] + F, yb + p["dy"], p["rot"], "obj_" + asm.kind)
            placed[asm.kind] += 1; rows.append(dict(o["item"], pieces=len(asm.pieces), bom=[[k[0], k[1], q] for k, q in sorted(asm.bom().items())], substitutions=asm.meta.get("substitutions", []), height_plates=asm.height()))
        self.info["objects_placed"] = dict(placed); self.info["objects_failed"] = failed; self.info["object_pieces"] = sum(r["pieces"] for r in rows)
        os.makedirs(self.out, exist_ok=True); json.dump(dict(placed=rows, failed=failed, skipped=self.obj_log["skipped"], terrain_edits=[i for i in self.obj_log["items"]]), open(os.path.join(self.out, "objects_placed.json"), "w"), indent=1, default=int)
    def run(self, with_title=True, with_decor=True, figures_cfg=None):
        self.figures_cfg = figures_cfg or {}
        import tiler; tiler.ORIENT_H = self.sf.get('orient_h', 1.0); tiler.SQUARISH = self.sf.get('squarish', 1.0)
        self.make_levels(); R, C = self.R, self.C; self.taken = np.zeros((R, C), bool); self.studded = np.zeros((R, C), bool)
        import figures.figures as FG
        self._fig_after, self.fig_log = FG.run(self, self.figures_cfg, CAT, PAIRS)
        self.ornaments(); self.decor() if with_decor else None
        if with_title: self.title()
        self.plan_objects(); self.plan_flanks(); self.plan_slopes(); self.plan_details(); self.build_layers(); self.place_flanks(); self.place_details(); self.place_objects(); self.frame(); 
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
    if "--objects" in a: style["objects"] = {"file": os.path.abspath(a[a.index("--objects") + 1])}
    if "--reinforce" in a: style["surface"]["reinforce_file"] = os.path.abspath(a[a.index("--reinforce") + 1])
    fc = json.load(open(a[a.index("--figures") + 1])) if "--figures" in a else {}
    b = Builder(style, comp, out, grid, frame); m = b.run(with_title="--no-title" not in a, with_decor="--no-decor" not in a, figures_cfg=fc); print(json.dumps({k: m[k] for k in ("pieces", "references", "max_height_mm", "physical_size_mm")}), json.dumps(b.info.get("levels_histogram")))
