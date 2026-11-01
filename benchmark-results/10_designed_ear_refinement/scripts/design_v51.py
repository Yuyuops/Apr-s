"""LEGO V5.1: the hand-designed ear of V5, made thick, rooted in the skull and fixed without turntables.

Designer choices (explicit below; nothing is searched for the outline):
  * outer outline = the V5 outline (same shaped pieces), one plate layer + tiles, studs facing out (-z);
  * inner face = mirror of the outer face (same outline, studs facing the head (+z), tiles): both faces are clean;
  * core = a one-stud brick wall in the ear plane, built studs-up in the module frame: courses of bricks with studs
    on both sides (52107, 47905) every 40 LDU (side studs hold both faces), two 1xN plates between them;
    ear thickness 52 LDU = 20.8 mm (reference ~20 mm), the tiles stop short of the bevelled wing edges (thinner rim);
  * root: the ear goes into the skull at its head-side end (as the reference ear does); no visible foot;
  * fixation: a 4x6 plate turned 53.13 deg buried in the skull. With a 3-4-5 rotation one stud position in five of
    the turned plate falls exactly on a stud of the skull grid: real stud connections on 1x1 plates of the skull
    (the other skull cells under the plate are tiles). A second turned plate, one wall course higher, does the same.
    No turntable.
Rule-based (not designer) parts, stated as such: wall course filling (bricks/plates along each course, from the
outline), mirror of the inner face, tiles on studs, seat of 1x1 plates/tiles under the turned plates, head rebuild.
usage: design_v51.py <outdir>
"""
import json, os, subprocess, sys
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.expanduser("~/bench/tools")); sys.path.insert(0, os.path.expanduser("~/bench/proto"))
import conn, partlib as PL

BLACK, LBG = 0, 71
HERE = os.path.dirname(os.path.abspath(__file__))
REP = json.load(open(os.path.expanduser("~/bench/proto/ear08/run/module_report.json")))
R_MOD, O = np.array(REP["R_mod"]), np.array(REP["O"])
HEAD_NPZ = os.path.expanduser("~/bench/proto/ear08/run/head_C_without_upper_ear.npz")
V0 = 12                                           # bottom of panel row k = 0 (wall side studs at v = 22 + 40 n)
R_PM = np.c_[[1, 0, 0], [0, 0, 1], [0, -1, 0]]    # panel-local (x=u, y=module z, z=v) -> module
Z_WALL = (-20.0, 0.0)                             # core wall (module z); outer plates -28..-20, tiles -36..-28
OUT_TOP = {"P": -28, "T": -36}                    # inner plates 0..8 (studs +z), tiles 8..16
MIRROR = {"41769": "41770", "41770": "41769", "24299": "24307", "24307": "24299"}

def place_line(colour, num, M, o):
    return f"1 {colour} {o[0]:.4f} {o[1]:.4f} {o[2]:.4f} " + " ".join(f"{v:.6f}" for v in np.asarray(M).ravel()) + f" {num}.dat"

def box_corners(num):
    P = conn.part(num)
    return np.array([[x, y, z] for x in (P["lo"][0], P["hi"][0]) for y in (P["lo"][1], P["hi"][1]) for z in (P["lo"][2], P["hi"][2])])

def axis_place(num, R, target_min):
    return np.array(target_min, float) - (box_corners(num) @ R.T).min(0)

def studs_dir(num, M, o, zdir):
    return [(M @ np.array(p) + o) for (p, a) in conn.part(num)["studs"] if (M @ np.array(a))[2] * zdir > 0.9]

def snap(num, M, o, zdir):
    st = studs_dir(num, M, o, zdir)
    if st:
        a, b = st[0][0], -st[0][1]
        du = (a - 10) - 20 * round((a - 10) / 20); dv = (b - V0 - 10) - 20 * round((b - V0 - 10) / 20)
        o = o - np.array([du, -dv, 0.0])
    return o

def outer_piece(num, r, i0, k0, layer):
    Rl = PL.rot_y(r); M = R_PM @ Rl
    o = R_PM @ axis_place(num, Rl, (20 * i0, OUT_TOP[layer], V0 + 20 * k0))
    return M, snap(num, M, o, -1)

def footprint(num, M, o, res=5.0):
    p = conn.solid_points(num) @ M.T + o
    return {(int(np.floor(q[0] / res)), int(np.floor(-q[1] / res))) for q in p}

def snap_recv(num, M, o):
    """tiles have no studs: put their first anti-stud on the stud grid"""
    rc = conn.part(num)["receptors"]
    if not rc: return o
    w = M @ np.array(rc[0][0]) + o; a, b = w[0], -w[1]
    du = (a - 10) - 20 * round((a - 10) / 20); dv = (b - V0 - 10) - 20 * round((b - V0 - 10) / 20)
    return o - np.array([du, -dv, 0.0])

def mirror_piece(num, M_out, o_out, z_lo):
    """inner-face twin of an outer piece: same outline, studs towards +z, body from module z = z_lo (rule-based)"""
    F = np.diag([1.0, -1.0, -1.0]); target = footprint(num, M_out, o_out)
    cb = box_corners(num) @ M_out.T + o_out; tmin = np.array([cb[:, 0].min(), -cb[:, 1].max()])
    best = None
    for cand in {num, MIRROR.get(num, num)}:
        for r in range(4):
            Rl = PL.rot_y(r); M = F @ R_PM @ Rl
            c = box_corners(cand) @ M.T
            cmin = np.array([c[:, 0].min(), -c[:, 1].max()])
            sh = tmin - cmin
            o2 = np.array([sh[0], -sh[1], z_lo - c[:, 2].min()])
            o2 = snap(cand, M, o2, +1) if studs_dir(cand, M, o2, +1) else snap_recv(cand, M, o2)
            f2 = footprint(cand, M, o2); sc = len(f2 & target) - 2 * len(f2 ^ target)
            if best is None or sc > best[0]: best = (sc, cand, M, o2)
    return best[1], best[2], best[3]

# ---------------------------------------------------------------- outer face (designer layout; V5 outline, rows +2)
# (part, quarter turns, i0, k0, role)   rows: k = v 12+20k .. 32+20k
OUTER = [
    ("22888", 1, -9, 3, "S1 bout arrondi : demi-disque 4x8"),
    ("24307", 0, -5, 2, "S2 bord inferieur gauche : aile 2x2"),
    ("41770", 3, -1, 9, "S3 bord superieur : aile 2x4"),
    ("24299", 3, 3, 8, "S4 bord superieur : aile 2x2"),
    ("24299", 3, 5, 7, "S5 bord superieur : aile 2x2"),
    ("24299", 3, 7, 6, "S6 bord superieur cote crane : aile 2x2"),
    ("3020", 0, -5, 9, "P1 2x4"),
    ("3031", 0, -5, 5, "P2 4x4"),
    ("3023", 0, -5, 4, "P3 1x2"),
    ("3021", 1, -3, 2, "P4 2x3"),
    ("3031", 0, -1, 5, "P5 4x4"),
    ("3020", 0, -1, 3, "P6 2x4"),
    ("3710", 0, -1, 2, "P7 1x4"),
    ("3795", 1, 3, 2, "P8 2x6"),
    ("3020", 1, 5, 3, "P9 2x4"),
    ("3710", 0, 5, 2, "R1 racine 1x4 (bord inferieur, contre le crane)"),
    ("3021", 1, 7, 3, "R2 racine 2x3 (entre dans le crane)"),
]
TILE_SAME = {"3020": "87079", "3031": "1751", "3023": "3069b", "3021": "26603", "3710": "2431", "3795": "69729", "3022": "3068b"}
NO_TILE = set()            # root pieces inside the skull: no tiles (hidden)

def outer_tiles(pieces):
    T = []
    for num, r, i0, k0, role in pieces:
        tag = role.split()[0]
        if tag in NO_TILE: continue
        if num == "22888":
            T += [("1126", 1, i0, k0 + 3, "tuile 1x2 bouts arrondis"), ("25269", 1, i0 + 1, k0 + 1, "tuile 1x1 quart de rond"),
                  ("2431", 1, i0 + 1, k0 + 2, "tuile 1x4"), ("25269", 2, i0 + 1, k0 + 6, "tuile 1x1 quart de rond"),
                  ("69729", 1, i0 + 2, k0 + 1, "tuile 2x6"), ("25269", 1, i0 + 3, k0, "tuile 1x1 quart de rond"),
                  ("25269", 2, i0 + 3, k0 + 7, "tuile 1x1 quart de rond")]
        elif num in TILE_SAME: T.append((TILE_SAME[num], r, i0, k0, f"tuile sur {tag}"))
    return T

def wing_tiles(num, M, o, role):
    s = studs_dir(num, M, o, -1); us = sorted({round(p[0]) for p in s}); vs = sorted({round(-p[1]) for p in s})
    i0 = int((us[0] - 10) // 20); k0 = int((vs[0] - 10 - V0) // 20)
    if len(us) == 1: n = len(vs); tile = {1: "3070b", 2: "3069b", 4: "2431"}[n]; rr = 1 if n > 1 else 0
    else: n = len(us); tile = {1: "3070b", 2: "3069b", 3: "63864", 4: "2431"}[n]; rr = 0
    return (tile, rr, i0, k0, f"tuile sur {role.split()[0]}")

# ---------------------------------------------------------------- core wall (rule from the outline) and fixation
V_PLATE = 48               # top of the turned plate (v); wall side studs at V_PLATE + 14 = 62 = 22 mod 40
BASE = [("3032", (200, -V_PLATE, -80), "plaque 4x6 tournee a 53,13 deg, noyee dans le crane")]
SEAT_PLATES = {"3032"}
# root block hidden in the skull, on the turned plate (module frame, x 200..320, z -80..0; the skull is on the -z side): it spreads the load of
# the wall over the whole turned plate (36 vertical studs) instead of the single wall row
BLOCK = [("2456", (200, -72, -80), "bloc de racine : brique 2x6"), ("3009", (200, -72, -40), "bloc de racine : brique 1x6"),
         ("3032", (200, -80, -80), "bloc de racine : plaque 4x6 (relie l'ame et le bloc)")]
BLOCK_X = (200, 320)
SPARSE = True     # turned plates that get a seat of 1x1 plates/tiles in the skull below them

def wall_courses(cells_ok):
    """courses from v = 8: [SNOT bricks 24][plate 8][plate 8] ... ; cells_ok(i, v0, v1) says if a wall cell may exist"""
    parts = []; v = V_PLATE; n = 0
    while v < 232:
        for kind, h in (("snot", 24), ("plate", 8), ("plate", 8)):
            if v + h > 232: break
            row = [i for i in range(-10, 12) if cells_ok(i, v, v + h)]
            runs = []
            for i in row:
                if runs and runs[-1][1] == i - 1: runs[-1][1] = i
                else: runs.append([i, i])
            for a, b in runs:
                L = b - a + 1; i = a
                if kind == "snot":
                    seq = [2] * (L // 2) + ([1] if L % 2 else [])
                    if n % 2 and L >= 3: seq = [1] + [2] * ((L - 1) // 2) + ([1] if (L - 1) % 2 else [])
                    for k_, w in enumerate(seq):
                        # hollow core: inside long runs, every other 1x2 brick is left out (the plate courses bridge it);
                        # the run ends stay closed (rim) and every brick under a panel joint row is kept by the checks
                        if SPARSE and 0 < k_ < len(seq) - 1 and k_ % 2 == 1 and w == 2 and not (BLOCK_X[0] - 40 <= 20 * i): i += w; continue
                        parts.append(("52107" if w == 2 else "47905", i, w, v, h)); i += w
                else:
                    off = (n + (1 if v % 16 else 0)) % 3
                    seq = []; rem = L
                    first = min(rem, [2, 3, 1][off]); seq.append(first); rem -= first
                    while rem > 0:
                        w = 8 if rem >= 8 else (6 if rem >= 6 else (4 if rem >= 4 else rem)); seq.append(w); rem -= w
                    for w in seq:
                        parts.append(({1: "3024", 2: "3023", 3: "3623", 4: "3710", 5: "3710", 6: "3666", 8: "3460"}[w] if w != 5 else "3710", i, w if w != 5 else 4, v, h)); i += (w if w != 5 else 4)
                        if w == 5: parts.append(("3024", i, 1, v, h)); i += 1
            v += h
        n += 1
    return parts

def wall_piece(num, i, w, v, h):
    P = conn.part(num); R = np.eye(3) if (P["hi"][0] - P["lo"][0]) >= (P["hi"][2] - P["lo"][2]) else PL.rot_y(1)
    return R, axis_place(num, R, (20 * i, -(v + h), Z_WALL[0]))

def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    mod = []        # (colour, num, M, o, group, role)  module frame
    # outer face
    for num, r, i0, k0, role in OUTER:
        M, o = outer_piece(num, r, i0, k0, "P"); mod.append((BLACK, num, M, o, "outer", role))
    for num, r, i0, k0, role in outer_tiles(OUTER):
        M, o = outer_piece(num, r, i0, k0, "T"); mod.append((BLACK, num, M, o, "outer_t", role))
    for c, num, M, o, g, role in list(mod):
        if g == "outer" and num in ("41770", "24299", "24307"):
            t = wing_tiles(num, M, o, role); M2, o2 = outer_piece(t[0], t[1], t[2], t[3], "T"); mod.append((BLACK, t[0], M2, o2, "outer_t", t[4]))
    # inner face = mirror
    for c, num, M, o, g, role in list(mod):
        if g in ("outer", "outer_t"):
            n2, M2, o2 = mirror_piece(num, M, o, 0.0 if g == "outer" else 8.0)
            mod.append((BLACK, n2, M2, o2, "inner" if g == "outer" else "inner_t", "face interieure : " + role))
    # wall: a cell exists where the outer plates cover it fully (5 LDU raster) or inside the root zone (u >= 120)
    fp = set().union(*[footprint(num, M, o) for c, num, M, o, g, r in mod if g == "outer"])
    d0 = np.load(HEAD_NPZ); G0 = d0["grid"]; F0 = d0["fine"]; K0 = int(d0["k"]); NX0, NY0, NZ0 = G0.shape
    occ0 = (G0 >= 0) & (F0.reshape(NX0, K0, NY0, K0, NZ0, K0).mean(axis=(1, 3, 5)) >= 0.5)
    base_x = [(lo[0], lo[0] + 20 * 6) for num, lo, note in BASE]
    def in_skull(i, v0, v1):
        for xm in (20 * i + 1, 20 * i + 19):
            for zm in (Z_WALL[0] + 1, Z_WALL[1] - 1):
                for v in (v0 + 1, v1 - 1):
                    w = O + R_MOD @ np.array([xm, -v, zm]); x, y, z = int(np.floor(w[0] / 20)), int(np.floor(-w[1] / 8)), int(np.floor(w[2] / 20))
                    if not (0 <= x < NX0 and 0 <= y < NY0 and 0 <= z < NZ0 and occ0[x, y, z]): return False
        return True
    def cells_ok(i, v0, v1):
        if BLOCK_X[0] <= 20 * i < BLOCK_X[1] and v0 >= 72 and v1 <= 80: return False     # taken by the block plate
        if 180 <= 20 * i < BLOCK_X[1] and v0 >= V_PLATE and v1 <= 88: return True         # root of the wall (designer zone)
        if v0 == V_PLATE and not any(a <= 20 * i and 20 * i + 20 <= b for a, b in base_x):
            lobe = all((a, b) in fp for a in range(4 * i, 4 * i + 4) for b in range(64 // 5, (v1 + 7) // 5 + 1))
            return lobe
        top = v1 - 16 if (v1 >= 232 or v1 - v0 == 24) else v1 + 7   # side-stud courses: no headroom (their top studs stay between the faces)
        lobe = all((a, b) in fp for a in range(4 * i, 4 * i + 4) for b in range(max(v0, 52) // 5, top // 5 + 1))
        return lobe or in_skull(i, v0, v1)
    for num, i, w, v, h in wall_courses(cells_ok):
        M, o = wall_piece(num, i, w, v, h); mod.append((BLACK, num, M, o, "wall", "ame : " + PL.title(num)))
    for num, lo, note in BLOCK:
        P = conn.part(num); R = np.eye(3) if (P["hi"][0] - P["lo"][0]) >= (P["hi"][2] - P["lo"][2]) else PL.rot_y(1)
        mod.append((BLACK, num, R, axis_place(num, R, lo), "wall", note))
    REC_ALL = [M @ np.array(rc[0]) + o for c, num, M, o, g, role in mod for rc in conn.part(num)["receptors"]]
    REC_ALL = np.array(REC_ALL)
    caps = []
    for c, num, M, o, g, role in list(mod):
        if g != "wall" or "bloc" in role: continue
        for (p, a) in conn.part(num)["studs"]:
            w = M @ np.array(p) + o; ax = M @ np.array(a)
            if ax[1] < -0.9 and np.linalg.norm(REC_ALL - w, axis=1).min() > 2 and w[0] < BLOCK_X[0]:
                caps.append((round(w[0] - 10), round(-w[1])))
    coltop = {}
    for (x0, vtop) in caps: coltop[x0] = max(coltop.get(x0, -1e9), vtop)
    caps = [(x0, vt) for (x0, vt) in caps if vt == coltop[x0]]       # only the top of each column (the inside stays hollow)
    caps = [(x0, vt) for (x0, vt) in caps                             # and only where the outline hides the tile
            if all((a, b) in fp for a in range(int(x0) // 5, int(x0) // 5 + 4) for b in range(int(vt) // 5, (int(vt) + 7) // 5 + 1))]
    for (x0, vtop) in sorted(set(caps)):
        Mt = np.eye(3); ot = axis_place("3070b", Mt, (x0, -(vtop + 8), Z_WALL[0]))
        mod.append((BLACK, "3070b", Mt, ot, "wall", "ame : tuile de fermeture du dessus"))
    for num, lo, note in BASE:
        P = conn.part(num); R = np.eye(3) if (P["hi"][0] - P["lo"][0]) >= (P["hi"][2] - P["lo"][2]) else PL.rot_y(1)
        mod.append((BLACK, num, R, axis_place(num, R, lo), "base", note))
    # ---------------------------------------------------------------- world, carving, head rebuild, seats
    def world(M, o): return R_MOD @ M, O + R_MOD @ o
    d = np.load(HEAD_NPZ); G = d["grid"].astype(int); F = d["fine"]; K = int(d["k"]); NX, NY, NZ = G.shape
    fr = F.reshape(NX, K, NY, K, NZ, K).mean(axis=(1, 3, 5)); occ = (G >= 0) & (fr >= 0.5)
    eyes = (G == 15) | (G == 4)
    carve = np.zeros(G.shape, bool); hit_eye = 0
    for c, num, M, o, g, role in mod:
        Mw, ow = world(M, o); pts = conn.solid_points(num) @ Mw.T + ow
        for dy in (-4.5, 0.0, 4.5):        # studs above, studs of the head below
            q = pts + np.array([0, dy, 0])
            ix = np.floor(q[:, 0] / 20).astype(int); iy = np.floor(-q[:, 1] / 8).astype(int); iz = np.floor(q[:, 2] / 20).astype(int)
            ok = (ix >= 0) & (ix < NX) & (iy >= 0) & (iy < NY) & (iz >= 0) & (iz < NZ)
            carve[ix[ok], iy[ok], iz[ok]] = True
    carve &= occ
    hit_eye = int((carve & eyes).sum())
    G3 = G.copy(); G3[carve] = -1
    head_npz = os.path.join(out, "head_C_V51.npz")
    np.savez_compressed(head_npz, grid=G3, surface=d["surface"], fine=F, k=K, neck=d["neck"], full_shape=d["full_shape"], hoff=d["hoff"])
    r = subprocess.run([sys.executable, os.path.expanduser("~/bench/proto/brickify_plus.py"), head_npz, out, "head_C",
                        "--occupancy", "0.5", "--no-shapes", "--drop-floating"], check=True, capture_output=True, text=True)
    head_rep = {k: v for k, v in json.loads(r.stdout.strip().splitlines()[-1]).items() if k not in ("settings", "part_numbers")}
    head = [l for l in open(os.path.join(out, "head_C.ldr")).read().splitlines() if l.startswith("1 ")]
    Hocc = np.zeros(G.shape, bool)
    for l in head:
        t = l.split(); Pt = conn.part(t[14][:-4]); Mt = np.array(t[5:14], float).reshape(3, 3); ot = np.array(t[2:5], float)
        cs = np.array([[x, y, z] for x in (Pt["lo"][0], Pt["hi"][0]) for y in (Pt["lo"][1], Pt["hi"][1]) for z in (Pt["lo"][2], Pt["hi"][2])]) @ Mt.T + ot
        Hocc[int(round(cs[:, 0].min() / 20)):int(round(cs[:, 0].max() / 20)), int(round(-cs[:, 1].max() / 8)):int(round(-cs[:, 1].min() / 8)),
             int(round(cs[:, 2].min() / 20)):int(round(cs[:, 2].max() / 20))] = True
    # seats under the turned plates: every skull cell whose top touches the plate bottom; a 1x1 plate where a stud of
    # the turned plate is exactly above the cell centre, a 1x1 tile elsewhere; only on a supported, empty cell
    seats = []; coincident = 0; seat_missing = 0; seat_cells = []
    for c, num, M, o, g, role in mod:
        if num not in SEAT_PLATES or g != "base": continue
        Mw, ow = world(M, o); P = conn.part(num)
        bottom_y = (box_corners(num) @ Mw.T + ow)[:, 1].max(); layer = int(round(-bottom_y / 8)) - 1
        st = [Mw @ np.array(p) + ow for p, a in P["studs"]]
        pts = conn.solid_points(num) @ Mw.T + ow
        cells = {(int(np.floor(q[0] / 20)), int(np.floor(q[2] / 20))) for q in pts}
        cells |= {(int(np.floor((q[0] + dx) / 20)), int(np.floor((q[2] + dz) / 20))) for q in pts for dx in (-6, 6) for dz in (-6, 6)}
        for (x, z) in sorted(cells):
            if Hocc[x, layer, z]: continue
            ctr = np.array([20 * x + 10, 20 * z + 10])
            hit = any(abs(s[0] - ctr[0]) < 0.5 and abs(s[2] - ctr[1]) < 0.5 for s in st)
            if hit and not Hocc[x, layer - 1, z]: seat_missing += 1; continue     # coincident stud without skull below
            if not hit: continue          # no spacer where no stud is needed: the plate rests on its stud joints
            coincident += 1
            seats.append(place_line(BLACK, "3024", np.eye(3), axis_place("3024", np.eye(3), (20 * x, -8 * (layer + 1), 20 * z))))
            seat_cells.append((x, layer - 1, z)); Hocc[x, layer, z] = True
    TILE2PLATE = {"3070b": "3024", "3069b": "3023", "63864": "3623", "2431": "3710", "6636": "3666", "3068b": "3022", "87079": "3020"}
    swapped = 0
    for k, l in enumerate(head):
        t = l.split(); n_ = t[14][:-4]
        if n_ not in TILE2PLATE: continue
        Pt = conn.part(n_); Mt = np.array(t[5:14], float).reshape(3, 3); ot = np.array(t[2:5], float)
        cs = box_corners(n_) @ Mt.T + ot
        x0, x1 = int(round(cs[:, 0].min() / 20)), int(round(cs[:, 0].max() / 20)); z0, z1 = int(round(cs[:, 2].min() / 20)), int(round(cs[:, 2].max() / 20))
        yl = int(round(-cs[:, 1].max() / 8))
        if any(x0 <= x < x1 and z0 <= z < z1 and y == yl for (x, y, z) in seat_cells):
            t[14] = TILE2PLATE[n_] + ".dat"; head[k] = " ".join(t); swapped += 1
    # ---------------------------------------------------------------- files
    order = [("base", "plaque tournee"), ("wall", "ame"), ("outer", "face exterieure"), ("outer_t", "tuiles exterieures"),
             ("inner", "face interieure"), ("inner_t", "tuiles interieures")]
    L = ["0 module_oreille_V51", "0 Name: module_oreille_V51.ldr", "0 Author: oreille V5.1 (conception directe), repere de la tete"]
    for g, _ in order:
        for c, num, M, o, gg, role in mod:
            if gg == g: Mw, ow = world(M, o); L.append(place_line(c, num, Mw, ow))
        L.append("0 STEP")
    open(os.path.join(out, "module_oreille_V51.ldr"), "w").write("\n".join(L) + "\n")
    W = ["0 tete_C_avec_oreille_V51", "0 Name: tete_C_avec_oreille_V51.ldr", "0 Author: tete C reconstruite autour de l'oreille V5.1"]
    W += head + seats + ["0 STEP"]
    for c, num, M, o, gg, role in mod:
        if gg == "base": Mw, ow = world(M, o); W.append(place_line(c, num, Mw, ow))
    W += ["0 STEP", "0 BRICKIFY SUBASSEMBLY BEGIN oreille"]
    for g, _ in order[1:]:
        for c, num, M, o, gg, role in mod:
            if gg == g: Mw, ow = world(M, o); W.append(place_line(c, num, Mw, ow))
    W += ["0 BRICKIFY SUBASSEMBLY END oreille", "0 STEP"]
    open(os.path.join(out, "tete_C_avec_oreille_V51.ldr"), "w").write("\n".join(W) + "\n")
    # checks: overlaps per layer, visible studs on the faces, outline
    rep = dict(head=head_rep, carved_cells=int(carve.sum()), carved_eye_or_mouth_cells=hit_eye, seat_pieces=len(seats),
               seat_coincident_studs=coincident, coincident_studs_without_skull_below=seat_missing, head_tiles_turned_to_plates_under_seats=swapped)
    allp = [(num, M, o, g) for c, num, M, o, g, role in mod]
    REC = np.array([M @ np.array(rc[0]) + o for num, M, o, g in allp for rc in conn.part(num)["receptors"]])
    vis = {}
    for num, M, o, g in allp:
        for (p, a) in conn.part(num)["studs"]:
            w = M @ np.array(p) + o
            if np.linalg.norm(REC - w, axis=1).min() > 2: vis[g] = vis.get(g, 0) + 1
    rep["studs_without_receptor_by_group"] = vis
    rep["parts_by_group"] = {g: sum(1 for x in mod if x[4] == g) for g, _ in order}
    json.dump(dict(rep, parts=[dict(part=num, colour=c, group=g, role=role) for c, num, M, o, g, role in mod]),
              open(os.path.join(out, "design_report.json"), "w"), indent=1, default=float)
    print(json.dumps(rep, default=float))

if __name__ == "__main__":
    main()
