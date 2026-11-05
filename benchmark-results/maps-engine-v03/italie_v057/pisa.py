"""Torre di Pisa v2 : eight architectural storeys on a 6x6 plaza. Ground storey = plain round brick (blind arcade), storeys 1-6 = round bricks with grille (loggias), belfry = narrower look via colour change + round tile cap.
Every storey carries a cornice (2x2 round plate, one plate high, light grey) so the eight levels read as distinct floors ; the lean is 1 stud every two storeys (total 3 studs, ~ 6 degrees at model scale) and
each joint keeps >= 2 studs. Entrance step plates at the foot. Footprint 6x6 studs (unchanged : the monument is not enlarged)."""
import random
from tiler import tile, PLATES
WHITE, LGRAY, DTAN, TAN, DGRAY = 15, 71, 28, 19, 72
SHIFT = [0, 0, 1, 1, 2, 2, 3, 3]
def build_pisa(S, r0, c0, rng=None, lean_col=1):
    rng = rng or random.Random(5); info = dict(storeys=8, lean_studs=max(SHIFT)); cells = {(r0 + i, c0 + j) for i in range(6) for j in range(6)}
    for (r, c, nr, nc, part, rot) in tile(cells, PLATES, rng, 1.4, 16, S.stud_cells(3), 20): S.add(part, DTAN, r, c, 3, rot, "pisa_plaza")
    S.add("3031", LGRAY, r0 + 1, c0 + 1, 4, 0, "pisa_base"); S.add("3023", TAN, r0 + 5, c0 + 2, 4, 0, "pisa_step")          # 4x4 plinth plate + entrance step
    y = 5
    def col(f): return c0 + 1 + (SHIFT[f] if lean_col > 0 else 3 - SHIFT[f])
    for f in range(8):
        part = "3941" if f in (0, 7) else "92947"; cc = col(f)
        S.add(part, WHITE if f % 2 == 0 else LGRAY if f == 7 else WHITE, r0 + 2, cc, y, 0, "pisa_storey_%d" % f); y += 3
        S.add("4032a", LGRAY if f < 7 else DGRAY, r0 + 2, cc, y, 0, "pisa_cornice_%d" % f); y += 1
    S.add("4150", DGRAY, r0 + 2, col(7), y, 0, "pisa_cap")
    info["height_plates"] = y + 1 - 3; info["pieces"] = sum(1 for p in S.parts if p["region"].startswith("pisa")); return info
