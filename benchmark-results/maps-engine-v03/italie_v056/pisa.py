"""Torre di Pisa module : eight-storey leaning tower from 2x2 round bricks. Each storey is shifted by one stud over the one below on a fixed schedule (visible lean, every joint >= 2 studs) ;
storeys 1-6 are 'round with grille' bricks (arcaded loggias), storey 0 and the belfry are plain round bricks, round tile on top. Footprint 6x6 studs : square plaza + 4x4 stepped base + tower.
Returns info (pieces, lean in studs / degrees at model scale)."""
import random
from tiler import tile, PLATES
WHITE, LGRAY, DTAN, TAN = 15, 71, 28, 19
SHIFT = [0, 0, 0, 1, 1, 1, 2, 2]           # cumulative lateral shift (studs) per storey
def build_pisa(S, r0, c0, rng=None, lean_col=1):
    """(r0, c0) = top-left of the 6x6 footprint. lean_col = +1 leans towards +column, -1 towards -column."""
    rng = rng or random.Random(5); info = dict(storeys=8, lean_studs=max(SHIFT)); cells = {(r0 + i, c0 + j) for i in range(6) for j in range(6)}
    for (r, c, nr, nc, part, rot) in tile(cells, PLATES, rng, 1.4, 16, S.stud_cells(3), 20): S.add(part, DTAN, r, c, 3, rot, "pisa_plaza")
    bc = c0 + 1; S.add("3031", LGRAY, r0 + 1, bc, 4, 0, "pisa_base"); base_y = 5                     # 4x4 plate base
    for f in range(8):
        sh = SHIFT[f] * lean_col; cc = c0 + (2 if lean_col > 0 else 2) + sh - (1 if lean_col < 0 else 0) + (0 if lean_col > 0 else 1) - (0 if lean_col > 0 else 0)
        cc = c0 + 1 + (SHIFT[f] if lean_col > 0 else 2 - SHIFT[f]); part = "92947" if 1 <= f <= 6 else "3941"
        S.add(part, WHITE if f % 2 == 0 else LGRAY if f in (2, 4) else WHITE, r0 + 2, cc, base_y + 3 * f, 0, "pisa_storey_%d" % f)
    cc = c0 + 1 + (SHIFT[7] if lean_col > 0 else 2 - SHIFT[7]); S.add("4150", LGRAY, r0 + 2, cc, base_y + 24, 0, "pisa_cap")
    info["height_plates"] = base_y + 25 - 3; info["pieces"] = sum(1 for p in S.parts if p["region"].startswith("pisa")); return info
