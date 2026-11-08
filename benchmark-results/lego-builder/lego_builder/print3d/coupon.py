"""B4 (Sprint V13) : tolerance coupon. Generates ONE build plate (3MF + STLs) to find out, on the real printer and filament, which clearances make LEGO-like pieces clutch. Nothing here proves that LEGO tolerances work in FDM :
the printed coupon has to be MEASURED and TRIED (see TOLERANCE_TEST.md). EXPERIMENTAL, no printing was done by this code.
Contents (all dimensions are the variants under test, in mm) :
  A  stud/tube matrix   : 3 base plates 2x2 with studs of diameter 4.7 / 4.8 / 4.9  x  5 caps (2x2 tile, hollow, central tube) with tube outer diameter 6.3 / 6.4 / 6.5 / 6.6 / 6.7 -> 15 combinations to try by hand
  B  module joint       : 4 pairs of 20x20x10 blocks with a dowel socket of radius 2.5 + clearance (0.10 / 0.20 / 0.30 / 0.40) and 4 dowels of diameter 5.0 x 12 mm
  C  curved details     : 1x1 slope (45 deg), 1x1 round tile, 1x1 quarter round, printed from the real LDraw geometry (convex hull), to compare edge sharpness and radius with the nominal shape
  D  wall / skin gauge  : 1.2 mm wall box and a 0.8 / 1.0 / 1.2 mm step wedge to check what the printer reproduces"""
import json, os, sys
from pathlib import Path
import numpy as np
import manifold3d as M
from .common import PARAMS, write_3mf, write_stl
from . import bricks, shapes
STUD_D = (4.7, 4.8, 4.9); TUBE_OD = (6.3, 6.4, 6.5, 6.6, 6.7); SOCKET_CLEAR = (0.10, 0.20, 0.30, 0.40)
def _arr(m): mm = m.to_mesh(); return np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts)
def build(out, bed=250.0):
    out = Path(out); out.mkdir(parents=True, exist_ok=True); items = []; x = 2.0; y = 2.0; meta = []; P0 = dict(PARAMS)
    def add(name, m, colour, xy, label):
        v, f = _arr(m); lo = v.min(0); items.append(dict(name=name, v=v - lo, f=f, colour_hex=colour, offset=(xy[0], xy[1], 0))); write_stl(v - lo, f, out / ("%s.stl" % name)); meta.append(dict(name=name, label=label, bbox_mm=[round(float(q), 2) for q in v.max(0) - v.min(0)], volume_mm3=round(m.volume(), 1)))
    # A : stud/tube matrix
    xx = 2.0
    for sd in STUD_D:
        P = dict(P0, stud_d=sd); add("A_base_stud%.2f" % sd, bricks.brick_mesh("plate", 2, 2, P), "2E7D32", (xx, 2.0), "base 2x2, stud diameter %.2f mm" % sd); xx += 20
    xx = 2.0
    for to in TUBE_OD:
        P = dict(P0, tube_od=to); add("A_cap_tube%.2f" % to, bricks.brick_mesh("tile", 2, 2, P).rotate([180, 0, 0]), "C62828", (xx, 24.0), "cap 2x2 tile PRINTED FLIPPED (smooth face on the bed : no bridging), tube outer diameter %.2f mm" % to); xx += 20
    # B : module joint (blocks with a socket in the top face, dowel separate)
    xx = 2.0; r0 = P0["peg_d"] / 2
    for c in SOCKET_CLEAR:
        blk = M.Manifold.cube([20, 20, 10]); sock = M.Manifold.cylinder(P0["peg_len"] + 0.5, r0 + c, r0 + c, 32).translate([10, 10, 10 - (P0["peg_len"] + 0.5)]); add("B_block_clear%.2f" % c, blk - sock, "1565C0", (xx, 48.0), "block 20x20x10, socket radius %.2f (clearance %.2f)" % (r0 + c, c)); xx += 24
    peg = M.Manifold.cylinder(2 * P0["peg_len"], r0, r0, 32); chamfer = M.Manifold.cylinder(0.6, r0 - 0.5, r0, 32)
    for i in range(4): add("B_dowel_%d" % i, peg, "F9A825", (2.0 + 12 * i, 72.0), "dowel diameter %.1f x %.0f mm" % (2 * r0, 2 * P0["peg_len"]))
    # C : curved details from the real LDraw geometry
    xx = 60.0
    for part, label in (("54200", "1x1 slope 31 deg"), ("3040b", "1x2 slope 45 deg"), ("98138", "1x1 round tile"), ("25269", "1x1 quarter round tile")):
        pts = shapes.part_points(part)
        if len(pts) < 4: continue
        w = np.stack([pts[:, 0] * 0.4, pts[:, 2] * 0.4, -pts[:, 1] * 0.4], 1); h = M.Manifold.hull_points(w.astype(float)); add("C_%s" % part, h, "EF6C00", (xx, 72.0), label + " (convex hull of the LDraw part)"); xx += 24
    # D : wall / skin gauge
    steps = [M.Manifold.cube([30, 8, t]).translate([0, 0, 0]) for t in (0.8,)]
    g = M.Manifold.batch_boolean([M.Manifold.cube([10, 10, t]).translate([12 * i, 0, 0]) for i, t in enumerate((0.8, 1.0, 1.2, 1.6, 2.0))], M.OpType.Add); add("D_skin_gauge", g, "6A1B9A", (2.0, 92.0), "skin thickness steps 0.8 / 1.0 / 1.2 / 1.6 / 2.0 mm")
    wallbox = M.Manifold.cube([20, 20, 8]) - M.Manifold.cube([17.6, 17.6, 8]).translate([1.2, 1.2, 1.0]); add("D_wall_box", wallbox, "6A1B9A", (70.0, 92.0), "hollow box, 1.2 mm walls, 1.0 mm skin")
    write_3mf(items, out / "tolerance_coupon_plate.3mf", title="lego_builder tolerance coupon (EXPERIMENTAL)")
    ext = np.max([[it["offset"][0] + it["v"][:, 0].max(), it["offset"][1] + it["v"][:, 1].max()] for it in items], 0)
    rep = dict(items=len(items), extent_mm=[round(float(q), 1) for q in ext], fits_bed=bool(ext.max() <= bed), parameters=dict(stud_d=STUD_D, tube_od=TUBE_OD, socket_clearance=SOCKET_CLEAR, dowel_d=2 * r0, dowel_len=2 * P0["peg_len"]), pieces=meta,
               warning="Dimensions under test, not proven LEGO-compatible in FDM. Print, MEASURE (calipers), TRY every combination and record the result in TOLERANCE_TEST.md.")
    json.dump(rep, open(out / "coupon.json", "w"), indent=1); return rep
if __name__ == "__main__":
    print(json.dumps(build(sys.argv[1]))[:600])
