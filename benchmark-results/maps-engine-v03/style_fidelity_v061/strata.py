#!/usr/bin/env python3
"""Coastal strata generator (style independent). From the sub-stud land masks it
  1. measures the distance (in studs) from every sea cell to the nearest land (subject + foreign), on the fine raster ;
  2. smooths that distance field (gaussian, sigma_studs) so the offset curves lose the pixel staircase while keeping the silhouette ;
  3. cuts it at the stratum widths -> nested bands (nearest to the coast = highest level) ;
  4. cleans each band : morphological opening/closing at stud scale (no 1-stud slivers, small bays closed, small islands kept above min_island_cells) ;
  5. resolves to the stud grid (coverage >= 0.5), guaranteeing nesting, and assigns levels : floor 0, sea strata 1..N, foreign land `foreign_level`, subject land N+1.
Returns int levels[R, C] and category masks. Nothing is specific to one territory or one style."""
import numpy as np
from scipy import ndimage
def band_clean(mask, sub, min_width_studs, min_area_studs2):
    """remove structures thinner than min_width and areas smaller than min_area (on the fine raster)"""
    r = max(1, int(round(min_width_studs * sub / 2)))
    st = ndimage.generate_binary_structure(2, 1); st = ndimage.iterate_structure(st, r)
    pad = r + 2; mp = np.pad(mask, pad, mode='edge')                          # edge padding : the window border is not a coast
    m = ndimage.binary_opening(mp, structure=st); m = ndimage.binary_closing(m, structure=st); m = m[pad:-pad, pad:-pad]
    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lab, range(1, n + 1)); small = [i + 1 for i, s in enumerate(sizes) if s < min_area_studs2 * sub * sub]; m[np.isin(lab, small)] = False
    return m
def levels_from_masks(geo, grid, p, sub=8):
    R, C = grid; subj, forn = geo["subject"], geo["foreign"]; N = len(p["strata_widths"])
    subj = band_clean(subj, sub, p.get("land_min_width", 0.0), p.get("min_island_studs2", 2.0)) if p.get("clean_land", True) else subj
    land = subj | forn
    d = ndimage.distance_transform_edt(~land) / sub                          # studs from the nearest land
    d = ndimage.gaussian_filter(d, p["smooth_sigma_studs"] * sub)
    if p.get("organic_amp", 0) > 0:        # low-frequency 'bathymetry' : offsets the isolines so they form bays, loops and open bights instead of parallel rings (seeded, reproducible)
        rng = np.random.RandomState(p.get("seed", 7)); nz = ndimage.gaussian_filter(rng.standard_normal(d.shape), p.get("organic_scale_studs", 6.0) * sub); nz /= (nz.std() + 1e-9)
        d = np.maximum(d + p["organic_amp"] * nz * np.clip(d / max(p["strata_widths"]), 0.15, 1.0), 0.0)
    if p.get("smooth_land", 0.0) > 0:                                        # soften the land outline itself (round the corners of the staircase) without moving it more than ~sigma
        sm = ndimage.gaussian_filter(subj.astype(float), p["smooth_land"] * sub) > 0.5; subj = sm | (subj & ~ndimage.binary_erosion(subj, iterations=sub)) if p.get("keep_border", False) else sm
    lev_f = np.zeros(subj.shape, np.int16)
    for k, w in enumerate(sorted(p["strata_widths"])):                       # nearest band gets the highest sea level
        band = band_clean(d <= w, sub, p.get("band_min_width", 1.6), p.get("band_min_area", 6.0))
        lev_f = np.where(band, N - k, lev_f) if k == 0 else np.maximum(lev_f, np.where(band, N - k, 0))
    # nesting is by construction (max of nested sets) ; resolve to the stud grid by coverage
    def cov(m): return m.reshape(R, sub, C, sub).mean(axis=(1, 3))
    levels = np.zeros((R, C), np.int16)
    for L in range(1, N + 1):
        levels[cov(lev_f >= L) >= 0.5] = L
    for L in range(N - 1, 0, -1):                                           # monotone : a higher level implies all lower ones (already true), no stray cells
        pass
    forn_c = cov(forn) >= 0.5; subj_c = cov(subj) >= 0.5
    levels[forn_c] = p["foreign_level"]; levels[subj_c] = N + 1
    return levels, dict(subject=subj_c, foreign=forn_c & ~subj_c, N=N)
def smooth_levels(levels, passes=1):
    """remove 1-cell steps : a cell whose four neighbours all differ from it takes the majority neighbour level (kills 1x1 pieces and stair noise)"""
    L = levels.copy()
    for _ in range(passes):
        P = np.pad(L, 1, mode="edge"); nb = np.stack([P[:-2, 1:-1], P[2:, 1:-1], P[1:-1, :-2], P[1:-1, 2:]])
        same = (nb == L).sum(0); maj = np.array([[np.bincount(nb[:, i, j]).argmax() for j in range(L.shape[1])] for i in range(L.shape[0])])
        L = np.where(same == 0, maj, L)
    return L
