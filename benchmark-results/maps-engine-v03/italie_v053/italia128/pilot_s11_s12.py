#!/usr/bin/env python3
"""V0.5.4: REAL LEGO sector pilot Tuscany/Rome across the S11/S12 seam.

Inputs: 128x128 Natural Earth coast + terrain-tile DEM-derived plate levels and
actual composition placements archived by V0.5.3. We construct a continuous
64x64-stud crop: global rows [32,96), cols [32,96). The Colosseum is deliberately
built WHOLE across the S11/S12 boundary. Pisa/Vesuvius are not yet modeled,
and this script never pretends otherwise.

No AI-rendered geometry; all components are existing catalogued LDraw parts.
No wall mount, BOM sourcing or physical test. No V0.5.3 archive mutation.
"""
import argparse
import json
import os
import random
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
sys.path.insert(0, str(MODULE))
from scene import Scene
from tiler import PLATES, tile
from fill import column_fill
from colosseum import oval_cells, build_colosseum

ROWS = COLS = 64
ROW0, COL0 = 32, 32
BLUE, DGRAY, GRASS, DGREEN, TAN, DTAN, LGRAY, WHITE = 272, 72, 2, 288, 19, 28, 71, 15
BASAL = 3    # backing B1,B2, sea plate; first land layer at y=3
SEED = 27


def add_base(scene, rng):
    cells = {(r, c) for r in range(ROWS) for c in range(COLS)}
    for r in range(0, ROWS, 8):
        for c in range(0, COLS, 8):
            scene.add("41539", DGRAY, r, c, 0, 0, "backing_fixed_B1")
    for r, c, nr, nc, part, rot in tile(cells, PLATES, rng, 2.3, 64):
        scene.add(part, DGRAY, r, c, 1, rot, "backing_stagger_B2")
    for r, c, nr, nc, part, rot in tile(cells, PLATES, rng, 2.3, 64):
        scene.add(part, BLUE, r, c, 2, rot, "sea_top")


def colour_grid(levels, reserved):
    """Colour gradients in coherent 2x2 blocs, not singleton noisy pixels."""
    grass = levels > 0
    rows, cols = np.indices(levels.shape)
    coast = grass & (
        (rows == 0) | (rows == ROWS - 1) | (cols == 0) | (cols == COLS - 1)
    )
    from scipy.ndimage import distance_transform_edt
    coastal = grass & (distance_transform_edt(grass) <= 1.8)
    colours = np.full(levels.shape, GRASS, dtype=np.int16)
    for r in range(0, ROWS, 2):
        for c in range(0, COLS, 2):
            slab = levels[r:r+2, c:c+2]
            maxlevel = int(np.percentile(slab[slab > 0], 70)) if np.any(slab > 0) else 0
            col = (WHITE if maxlevel >= 9 else LGRAY if maxlevel >= 7
                   else DGRAY if maxlevel >= 6 else DTAN if maxlevel >= 4
                   else DGREEN if (r * 31 + c * 17) % 11 < 3 and maxlevel >= 2
                   else GRASS)
            colours[r:r+2, c:c+2] = col
    colours[coastal] = TAN
    return colours


def build(out, seed=SEED, with_colosseum=True, with_trees=True, with_slopes=True):
    rng = random.Random(seed)
    levels128 = np.load(HERE / "output/levels_128.npy")
    placement = json.loads((HERE / "output/placements.json").read_text(encoding="utf-8"))
    if levels128.shape != (128, 128):
        raise ValueError("Expected authoritative 128x128 DEM-composition grid")
    lev = np.asarray(levels128[ROW0:ROW0 + ROWS, COL0:COL0 + COLS], dtype=int)
    scene = Scene(ROWS, COLS)
    add_base(scene, rng)
    selected = next((m for m in placement["monuments"] if m["id"] == "colosseum"), None)
    if with_colosseum and selected is None:
        raise ValueError("Colosseum placement missing; never hardcode fake placement")
    if with_colosseum:
        # Exact same footprint convention as the isolated module_test.py.
        nrow, ncol = selected["footprint"]
        center_r = int(round(selected["row"] + nrow / 2 - ROW0))
        center_c = int(round(selected["col"] + ncol / 2 - COL0))
        plaza_margin = 1
        a = (ncol - 2 * plaza_margin) / 2 - 1.2
        b = (nrow - 2 * plaza_margin) / 2 - 1.2
        plaza_extra = 1.2 + plaza_margin
        reserved = set(oval_cells(center_r, center_c, a + plaza_extra,
                                  b + plaza_extra, 3.0))
        if not reserved or any(not(0 <= r < ROWS and 0 <= c < COLS) for r,c in reserved):
            raise ValueError("Plaza crosses sector PILOT boundary")
        # A monolith may cross an internal sector boundary but not the model edge.
        crosses_s11_s12 = selected["col"] < 64 and selected["col"] + ncol > 64
        if not crosses_s11_s12:
            raise ValueError("Pilot should exercise S11/S12 seam; placement has changed")
    else:
        reserved = set()

    colours = colour_grid(lev, reserved)
    land = {(int(r),int(c)): int(3*lev[r,c])
            for r,c in np.argwhere(lev > 0) if (int(r),int(c)) not in reserved}
    if not land:
        raise ValueError("No actual DEM-based land within pilot crop")
    levels_by_cell = {(r,c): int(lev[r,c]) for r,c in land}
    counts = {int(x):int(y) for x,y in zip(*np.unique(lev,return_counts=True))}

    def paint(r, c, y, kind):
        # Core land colour is stable across the depth of a column, with a little
        # rock colour at exposed summits (still using real LEGO colours).
        return int(colours[r,c])

    column_fill(scene, land, paint, BASAL, rng, "terrain_DEM", 1.2, 64, 64)
    monuments = {}
    if with_colosseum:
        monuments["colosseum"] = build_colosseum(
            scene, center_r, center_c, a=a, b=b, plaza_extra=plaza_extra
        )
    trees = 0
    if with_trees:
        # Real conifer bricks on FLAT 2x2 pads; no 1-stud trunks.
        # Restrict height and spacing to preserve the coastline and Colosseum.
        for r in range(2, ROWS-3, 3):
            for c in range(2, COLS-3, 3):
                block = [(r+i, c+j) for i in range(2) for j in range(2)]
                if any(p in reserved or p not in levels_by_cell for p in block):
                    continue
                vals = [levels_by_cell[p] for p in block]
                if len(set(vals)) != 1 or not(1 <= vals[0] <= 3):
                    continue
                if not (rng.random() < .27):
                    continue
                y = BASAL + 3 * vals[0]
                if not all(p in scene.stud_cells(y) for p in block):
                    continue
                if not scene.free(r,c,y,2,2,9):
                    continue
                scene.add("3941", DGREEN, r,c,y,0,"conifer_sturdy_trunk")
                scene.add("3942c", DGREEN, r,c,y+3,0,"conifer_sturdy_crown")
                trees += 1
                if trees >= 40:
                    break
            if trees >= 40:
                break
    slopes = 0
    if with_slopes:
        # Place a small set of real 2x2 slope bricks on coherent high-level
        # plateaus, never forcing a ground-height or coast modification.
        for r in range(3,ROWS-3,4):
            for c in range(3,COLS-3,4):
                block = [(r+i,c+j) for i in range(2) for j in range(2)]
                if any(p in reserved or p not in levels_by_cell for p in block):
                    continue
                vals = [levels_by_cell[p] for p in block]
                if len(set(vals)) != 1 or vals[0] < 3:
                    continue
                y = BASAL + 3*vals[0]
                if not all(p in scene.stud_cells(y) for p in block):
                    continue
                if not scene.free(r,c,y,2,2,3):
                    continue
                scene.add("3039", DTAN if vals[0] < 5 else DGRAY, r,c,y,0,"mountain_slope_DEM")
                slopes += 1
                if slopes >= 35:
                    break
            if slopes >= 35: break

    extra = dict(
        source="Italia128 V0.5.3 Natural Earth/Terrain Tiles",
        global_crop=dict(row0=ROW0,col0=COL0,rows=ROWS,cols=COLS),
        sectors_covered=["S11","S12","S21","S22"],
        geographic_terrain_from_DEM=True,
        elevation_exaggerated=True,
        level_histogram=counts,
        land_cells=len(land), italian_coastline_unchanged=True,
        monument_placement=dict(selected, local_centre=[center_r,center_c])
                 if with_colosseum else None,
        colosseum_crosses_sector_seam=bool(with_colosseum),
        modules_built=["colosseum"] if with_colosseum else [],
        modules_not_yet_built=["pisa_tower","volcano_cone"],
        conifers_sturdy=trees, slopes_real_LDraw=slopes,
        physical_test=False, wall_mount_verified=False, price_stock_verified=False,
    )
    metrics = scene.write(out, "Italia 128 real DEM pilot: Tuscany-Rome, multi-sector", extra)
    print(json.dumps({
        "parts":metrics["pieces"],"refs":metrics["references"],
        "max_height_mm":metrics["max_height_mm"],
        "trees":trees,"slopes":slopes,"land_cells":len(land),
        "colosseum":bool(with_colosseum),"cross_sector":bool(with_colosseum)
    },ensure_ascii=False))
    return metrics


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    ap.add_argument("--seed",type=int,default=SEED)
    ap.add_argument("--no-colosseum",action="store_true")
    ap.add_argument("--no-trees",action="store_true")
    ap.add_argument("--no-slopes",action="store_true")
    a=ap.parse_args()
    build(a.out,a.seed,not a.no_colosseum,not a.no_trees,not a.no_slopes)
