"""Column fill : solid volumes from a per-cell height (plates) and a colour function, bricks first then plates, nested layers so that every piece stands on the one below."""
import random
from tiler import tile, BRICKS, PLATES
def column_fill(S, heights, colour, y0, rng, region, brick_bias=1.0, brick_max=8, plate_max=8, skip=None):
    """heights {(r,c): plates}; colour(r,c,y,kind)->colour id ; pieces never leave a cell group of the same colour"""
    nb = {k: h // 3 for k, h in heights.items()}; rem = {k: h % 3 for k, h in heights.items()}
    for k in range(max(nb.values(), default=0)):
        y = y0 + 3 * k; groups = {}
        for cell, n in nb.items():
            if n > k: groups.setdefault(colour(cell[0], cell[1], y, "brick"), set()).add(cell)
        for col, cells in groups.items():
            for (r, c, nr, nc, part, rot) in tile(cells, BRICKS, rng, brick_bias, brick_max, S.stud_cells(y)): S.add(part, col, r, c, y, rot, region)
    for j in (0, 1):
        groups = {}
        for cell, n in rem.items():
            if rem[cell] > j: groups.setdefault((y0 + 3 * nb[cell] + j, colour(cell[0], cell[1], y0 + 3 * nb[cell] + j, "plate")), set()).add(cell)
        for (y, col), cells in groups.items():
            for (r, c, nr, nc, part, rot) in tile(cells, PLATES, rng, 1.2, plate_max, S.stud_cells(y)): S.add(part, col, r, c, y, rot, region)
