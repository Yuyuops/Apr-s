"""LEGO V8 - phase 2/3: automatic generator of small surface details (eyes + pupils, nose, mouth) for the V7 sculpture.

Input : details.json (detect.py: classes, centre, outward normal, size, bulge, pupils), the whole grid without ears
        (V7 run: paco_full_sans_oreilles.npz) and the V7 ears (ears.pkl, unchanged).
Generic rules (no Paco coordinate, no part number chosen for Paco):
  * catalogue = generic families of real surface parts (round tiles / plates, dishes, tiles 1xN); every property used
    (diameter, footprint, dome rise, top centre stud, receptors) is MEASURED on the LDraw geometry (conn/partlib);
    a part is usable in a colour only if Rebrickable lists it in >= MIN_SETS sets in that colour;
  * mounting direction = the grid axis closest to the outward normal of the detail (+-X, +-Z: SNOT; up: inset tile;
    down: no studded mounting possible -> colour of the volume only, flagged); tilt angle -> confidence;
  * round details (eye, pupil, nose): part = argmin(size error + 0.5 x dome-rise error + pupil penalty + visible-stud
    penalty); pupil = round part on the centre stud of the eye part (an eye part without centre stud loses its pupil:
    penalty 1);
  * side mounting: a 1x1 brick with a stud on one side (catalogue 'snot') inside the volume, turned to the axis; 0..2
    round 1x1 plates as spacers; the detail part on one of its receptors. Searched: SNOT cell (inside the body, body
    cells above and below), receptor, spacers; cost = in-plane distance of the part centre to the GLB detail centre
    + 0.5 x |outer face - (GLB surface + bulge)|. The outer face is thus sunk to the GLB surface (no part glued on top
    of the volume);
  * up-facing details (mouth interior seen from above): flat tile of the detail colour set INTO the top layer (the top
    cell under its footprint is removed, the tile sits on the cell below); tile shape = max IoU with the ellipse of
    the patch;
  * space: every body cell hit by a new part (solid points, +-4.5 LDU), plus the cells in front of the part's
    footprint up to the outside (line of sight), are removed before the single brickify_plus rebuild;
  * the voxel colour of a built detail is cleared: cells of the detail colour within its radius become the skin
    colour (majority colour of their non-detail neighbours) - the real part now carries the detail; the same for an
    eye rejected as generation artefact (oeil_douteux).
usage: microdetails.py <details.json> <run V7 dir> <out dir>
"""
import json, os, pickle, sqlite3, sys
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.expanduser("~/bench/tools")); sys.path.insert(0, os.path.expanduser("~/bench/proto"))
import conn, partlib as PL

MIN_SETS = 20
RB = os.path.expanduser("~/bench/data/rb.db")
ROUND = ["98138", "6141", "85861", "4740", "14769", "18674", "43898", "3960"]        # round tiles, plates, dishes
FLAT = ["3070b", "3069b", "63864", "2431", "98138", "24246"]                        # tiles for inset details
SNOT = ["87087"]                                                                   # 1x1 brick, stud on one side
SPACER = "6141"
LDC = {"blanc": 15, "noir": 0, "rouge": 4, "jaune": 14}

def avail(num, colour, _c={}):
    if "db" not in _c: _c["db"] = sqlite3.connect(RB)
    r = _c["db"].execute("select count(distinct inventory_id) from inventory_parts where part_num=? and color_id=?", (num, colour)).fetchone()
    return int(r[0] or 0)

def measure(num):
    P = conn.part(num); lo, hi = np.array(P["lo"]), np.array(P["hi"])
    T, _ = PL.lib().geom(num + ".dat"); V = T.reshape(-1, 3)
    D = float(min(hi[0] - lo[0], hi[2] - lo[2])); Rr = D / 2
    rad = np.hypot(V[:, 0], V[:, 2])
    top_c = float(V[rad < 0.3 * Rr][:, 1].min()) if (rad < 0.3 * Rr).any() else lo[1]
    top_e = float(V[rad > 0.85 * Rr][:, 1].min())
    cstud = [s for s in P["studs"] if abs(s[0][0]) < 0.5 and abs(s[0][2]) < 0.5 and s[1][1] < -0.9]
    return dict(num=num, title=PL.title(num), D_mm=round(D * 0.4, 1), L_mm=round(float(max(hi[0] - lo[0], hi[2] - lo[2])) * 0.4, 1),
                h_ldu=float(hi[1] - lo[1]), rise_mm=round(max(0.0, top_e - top_c) * 0.4, 2), centre_stud=bool(cstud),
                stud_top=float(cstud[0][0][1]) if cstud else None, visible_studs=len(P["studs"]) > 0,
                receptors=[tuple(map(float, r)) for r, _ in P["receptors"]], rond=("round" in PL.title(num).lower() or "dish" in PL.title(num).lower()))

def frame_for(a):
    """R for a part whose local -y (studs) must point along a (LDraw world); local z kept vertical when a is horizontal"""
    a = np.asarray(a, float); ey = -a
    ez = np.array([0.0, -1.0, 0.0]) if abs(a[1]) < 0.5 else np.array([0.0, 0.0, 1.0])
    ex = np.cross(ey, ez); return np.c_[ex, ey, ez]

def snot_frame(a):
    """R for the 1x1 brick with a stud on one side: local side stud axis (0,0,-1) -> a, local y kept"""
    a = np.asarray(a, float); ey = np.array([0.0, 1.0, 0.0]); ez = -a; ex = np.cross(ey, ez); return np.c_[ex, ey, ez]

def choose_round(Dt, rise_t, colour, need_pupil, prefer_flat_face):
    out = []
    for num in ROUND:
        m = measure(num); n_sets = avail(num, LDC[colour])
        if n_sets < MIN_SETS: continue
        c = abs(m["D_mm"] - Dt) / Dt + 0.5 * abs(m["rise_mm"] / m["D_mm"] - max(rise_t, 0) / Dt)
        if need_pupil and not m["centre_stud"]: c += 1.0
        if prefer_flat_face and m["visible_studs"]: c += 0.2
        out.append((round(c, 3), num, m, n_sets))
    out.sort(key=lambda t: t[0]); return out

def ellipse_iou(L, W, ang, fl, fw, rond):
    xs = np.linspace(-30, 30, 241); X, Y = np.meshgrid(xs, xs)
    ca, sa = np.cos(ang), np.sin(ang); u = X * ca + Y * sa; v = -X * sa + Y * ca
    E = (u / (L / 2)) ** 2 + (v / (W / 2)) ** 2 <= 1
    Pm = (X / (fl / 2)) ** 2 + (Y / (fw / 2)) ** 2 <= 1 if rond else (abs(X) <= fl / 2) & (abs(Y) <= fw / 2)
    return float((E & Pm).sum() / max((E | Pm).sum(), 1))

class Grid:
    def __init__(self, npz):
        d = np.load(npz); self.d = d; self.G = d["grid"].astype(int); F = d["fine"]; K = int(d["k"])
        NX, NY, NZ = self.G.shape; self.shape = (NX, NY, NZ)
        self.occ = (self.G >= 0) & (F.reshape(NX, K, NY, K, NZ, K).mean(axis=(1, 3, 5)) >= 0.5)
    def inside(self, c): return all(0 <= c[i] < self.shape[i] for i in range(3))
    def o(self, c): return self.inside(c) and bool(self.occ[tuple(c)])

def cells_of_points(pts, shape):
    ix = np.floor(pts[:, 0] / 20).astype(int); iy = np.floor(-pts[:, 1] / 8).astype(int); iz = np.floor(pts[:, 2] / 20).astype(int)
    ok = (ix >= 0) & (ix < shape[0]) & (iy >= 0) & (iy < shape[1]) & (iz >= 0) & (iz < shape[2])
    return set(map(tuple, np.c_[ix, iy, iz][ok]))

def part_cells(num, R, o, shape, a=None):
    """cells hit by the part solid, dilated by 4.5 LDU in the plane normal to the mounting axis a (never along a: the
    cells behind a detail carry it)"""
    pts = conn.solid_points(num) @ R.T + o; S = set()
    offs = [np.array(v, float) for v in ((0, 0, 0), (4.5, 0, 0), (-4.5, 0, 0), (0, 4.5, 0), (0, -4.5, 0), (0, 0, 4.5), (0, 0, -4.5))]
    for d in offs:
        if a is not None and abs(np.dot(d, a)) > 1e-6: continue
        S |= cells_of_points(pts + d, shape)
    return S

def to_ldu(p): p = np.asarray(p, float); return np.array([p[0] / 0.4, -p[1] / 0.4, -p[2] / 0.4])
def n_ldu(n): n = np.asarray(n, float); return np.array([n[0], -n[1], -n[2]])

AXES = {"+X": np.array([1.0, 0, 0]), "-X": np.array([-1.0, 0, 0]), "+Z": np.array([0, 0, 1.0]), "-Z": np.array([0, 0, -1.0]),
        "haut": np.array([0, -1.0, 0]), "bas": np.array([0, 1.0, 0])}

def axis_of(n):
    k = max(AXES, key=lambda k: np.dot(AXES[k], n)); return k, float(np.degrees(np.arccos(np.clip(np.dot(AXES[k], n), -1, 1))))

def place_side(g, reserved, target, a_name, stack, prot_t):
    """stack: list of (num, colour) from the SNOT stud outwards (detail part first, then pupil). Returns the best
    placement: parts, cells to carve, cost terms."""
    a = AXES[a_name]; Rs = snot_frame(a); ci = np.floor([target[0] / 20, -target[1] / 8, target[2] / 20]).astype(int)
    surf = float(np.dot(target, a))
    main_num = stack[0][0]; mm = measure(main_num); Rd = frame_for(a)
    cands = []
    rng = range(-4, 5)
    for di in rng:
        for dk in rng:
            for dy in range(-9, 7):
                c0 = ci + np.array([di, dy, dk]) if a_name in ("+X", "-X", "+Z", "-Z") else None
                # depth is along a: keep only cells whose outward face is within 2 cells below the GLB surface
                o = np.array([20 * c0[0] + 10, -8 * (c0[1] + 3), 20 * c0[2] + 10])        # brick top centre (3 layers c0[1]..+2)
                s = o + Rs @ np.array([0.0, 10.0, -10.0])                                 # side stud base on the face
                face = float(np.dot(s, a))
                if not (surf - 45 <= face <= surf + 5): continue
                cells = [tuple(c0 + [0, j, 0]) for j in range(3)]
                if not all(g.o(c) and c not in reserved for c in cells): continue
                below, above = tuple(c0 + [0, -1, 0]), tuple(c0 + [0, 3, 0])
                sup = int(g.o(below) and below not in reserved) + int(g.o(above) and above not in reserved)
                if sup == 0: continue
                for nsp in range(3):
                    s2 = s + a * 8 * nsp
                    for r in mm["receptors"]:
                        od = s2 - Rd @ np.array(r)
                        centre = od                                                       # part axis passes through its local origin
                        top = float(np.dot(od, a)) + 0.0
                        # outer face of the stack
                        outer = float(np.dot(od, a)) - float(conn.part(main_num)["lo"][1])
                        if len(stack) > 1: outer += measure(stack[1][0])["h_ldu"]
                        d_in = centre - target; d_in = d_in - np.dot(d_in, a) * a
                        cost = float(np.linalg.norm(d_in)) + 0.5 * abs(outer - (surf + prot_t)) + 3 * (2 - sup) + 2 * nsp
                        cands.append((cost, dict(c0=c0.tolist(), r=r, nsp=nsp, od=od, s=s, outer=outer, surf=surf, d_in=float(np.linalg.norm(d_in)), support=sup, cost=round(cost, 1))))
    cands.sort(key=lambda t: t[0]); return [b for _, b in cands]

def build_side(b, stack, a_name):
    a = AXES[a_name]; Rs = snot_frame(a); Rd = frame_for(a); main_num = stack[0][0]; b = dict(b); parts = []
    c0 = np.array(b["c0"]); o = np.array([20 * c0[0] + 10, -8 * (c0[1] + 3), 20 * c0[2] + 10])
    parts.append(("snot", SNOT[0], Rs, o))
    s = b["s"]
    for j in range(b["nsp"]):
        osp = s - Rd @ np.array([0.0, 8.0, 0.0]); parts.append(("cale", SPACER, Rd, osp)); s = osp
    od = s - Rd @ np.array(b["r"]); parts.append(("detail", main_num, Rd, od))
    if len(stack) > 1:
        st = measure(main_num)["stud_top"]; sp = od + Rd @ np.array([0.0, st, 0.0])
        op = sp - Rd @ np.array([0.0, 8.0, 0.0]); parts.append(("pupille", stack[1][0], Rd, op))
    b["od"] = od.tolist(); b["s"] = np.asarray(b["s"]).tolist()
    return b, parts

def main():
    det_json, run, out = sys.argv[1:4]; os.makedirs(out, exist_ok=True)
    D = json.load(open(det_json)); P = pickle.load(open(os.path.join(run, "ears.pkl"), "rb"))
    g = Grid(P["npz2"]); shape = g.shape
    # cells already used by the V7 ears (carved in assemble): reserved
    R = np.array(P["R"]); reserved = set()
    for ear, e in P["ears"].items():
        O = np.array(e["O"])
        for c, num, M, o, grp, role in e["mod"]:
            reserved |= cells_of_points(conn.solid_points(num) @ (R @ M).T + (O + R @ o), shape)
            if grp == "base":   # turned fixation plates: the cells that carry their seats (2 cells under every stud on the grid)
                Mw, ow = R @ M, O + R @ o
                bottom = (np.array([[x, y, z] for x in (conn.part(num)["lo"][0], conn.part(num)["hi"][0]) for y in (conn.part(num)["lo"][1], conn.part(num)["hi"][1]) for z in (conn.part(num)["lo"][2], conn.part(num)["hi"][2])]) @ Mw.T + ow)[:, 1].max()
                layer = int(round(-bottom / 8)) - 1
                for pt, _ in conn.part(num)["studs"]:
                    st = Mw @ np.array(pt) + ow; x, z = int(np.floor(st[0] / 20)), int(np.floor(st[2] / 20))
                    for dl in (0, 1, 2, 3): reserved.add((x, layer - dl, z))
    dets = {p["id"]: p for p in D["details"]}
    parts, carve, recolour, report = [], set(), {}, []
    md_solid = set()
    skin = 14
    def clear_colour(p, radius_mm, colours, depth_mm=20.0):
        """voxel cells of the detail colours within radius_mm of the detail centre in its plane and depth_mm along its
        normal (the voxel surface can lie a cell off the GLB surface) take the skin colour"""
        c = to_ldu(p["centre_mm"]); nL = n_ldu(p["normale"])
        idx = np.argwhere(np.isin(g.G, colours))   # also cells under the occupancy threshold: brickify_plus copies their colour onto newly visible cells
        rel = (idx + 0.5) * np.array([20.0, -8.0, 20.0]) * np.array([1, 1, 1]) - c
        rel[:, 1] = -(idx[:, 1] + 0.5) * 8.0 - c[1]
        along = rel @ nL; inpl = np.linalg.norm(rel - np.outer(along, nL), axis=1)
        sel = (inpl <= radius_mm / 0.4) & (np.abs(along) <= depth_mm / 0.4)
        for cell in idx[sel]: recolour[tuple(cell)] = skin
        return int(sel.sum())
    for p in D["details"]:
        cls = p["classe"]
        if cls not in ("oeil", "truffe", "bouche", "oeil_douteux"): continue
        if cls == "bouche" and os.environ.get("MD_SKIP_MOUTH"):      # V8.1: the mouth is handled by the lines-and-cavities module (lcm.py)
            report.append(dict(id=p["id"], classe=cls, decision="traite par lcm.py (V8.1)")); continue
        n = n_ldu(p["normale"]); a_name, tilt = axis_of(n); tgt = to_ldu(p["centre_mm"])
        Dt = float(np.sqrt(p["longueur_mm"] * p["largeur_mm"]))
        if p.get("fusion", 1) > 1: Dt = float(p["largeur_mm"])   # patch wrapped over both sides of a tip: its length follows the curvature
        entry = dict(id=p["id"], classe=cls, couleur=p["couleur"], centre_mm=p["centre_mm"], diametre_cible_mm=round(Dt, 1),
                     axe_fixation=a_name, inclinaison_deg=round(tilt, 1))
        if cls == "oeil_douteux":
            entry.update(decision="non construit : oeil sans partenaire symetrique (artefact de generation probable)",
                         cellules_recolorees=clear_colour(p, Dt / 2 + 8, [15, 0]))
            report.append(entry); continue
        if cls in ("oeil", "truffe"):
            pup = dets[p["pupille"][0]] if p.get("pupille") else None
            rise_t = p.get("bombe_membres", p["bombe_mm"]) if cls == "truffe" else p["bombe_mm"]
            cand = choose_round(Dt, rise_t, p["couleur"], pup is not None, cls == "oeil")
            entry["candidats"] = [dict(piece=num, cout=c, D_mm=m["D_mm"], bombe_mm=m["rise_mm"], tenon_central=m["centre_stud"], sets=ns) for c, num, m, ns in cand[:5]]
            stack = [(cand[0][1], p["couleur"])]
            if pup is not None:
                Dp = float(np.sqrt(pup["longueur_mm"] * pup["largeur_mm"]))
                cp = choose_round(Dp, pup["bombe_mm"], pup["couleur"], False, True)
                cp = [t for t in cp if measure(t[1])["D_mm"] <= 0.6 * measure(stack[0][0])["D_mm"]]
                if cp and measure(stack[0][0])["centre_stud"]:
                    stack.append((cp[0][1], pup["couleur"])); entry["pupille"] = dict(id=pup["id"], piece=cp[0][1], diametre_cible_mm=round(Dp, 1), D_mm=measure(cp[0][1])["D_mm"])
            if a_name in ("haut", "bas"):
                entry["decision"] = "axe vertical : non traite par la pose laterale"; report.append(entry); continue
            prot = max(rise_t, 0.0) / 0.4
            cands = place_side(g, reserved | carve, tgt, a_name, stack, prot)
            chosen = None; rejected = 0
            for b0 in cands[:400]:
                b, pp = build_side(b0, stack, a_name)
                new_cells = set()
                for role, num, Rm, o in pp:
                    if role != "snot": new_cells |= part_cells(num, Rm, o, shape, AXES[a_name])
                # line of sight: footprint columns of the detail part, from its base outwards to the outside
                a = AXES[a_name]; od = np.array(b["od"]); Rr = measure(stack[0][0])["D_mm"] / 0.4 / 2
                u = np.cross(a, [0, 1.0, 0]); v = np.cross(a, u)
                for su in np.linspace(-Rr + 3, Rr - 3, 9):
                    for sv in np.linspace(-Rr + 3, Rr - 3, 9):
                        if su * su + sv * sv > (Rr - 2) ** 2: continue
                        # visible along the mounting axis AND along the GLB normal of the detail (tilted details)
                        base_pt = od + su * u + sv * v + a * (b["outer"] - float(np.dot(od, a)) - 6)
                        for dvec in (a, n):
                            for t in range(0, 80, 4):
                                q = (od + su * u + sv * v + a * (t + 2)) if dvec is a else base_pt + dvec * (t + 2)
                                cc = (int(np.floor(q[0] / 20)), int(np.floor(-q[1] / 8)), int(np.floor(q[2] / 20)))
                                if not g.inside(cc) or not g.occ[cc]:
                                    if t > 24: break
                                    continue
                                new_cells.add(cc)
                snot_cells = {tuple(np.array(b["c0"]) + [0, j, 0]) for j in range(3)}
                c0_ = np.array(b["c0"]); support = {tuple(c0_ + [0, -1, 0]), tuple(c0_ + [0, 3, 0])}
                if (new_cells | snot_cells) & (reserved | md_solid): rejected += 1; continue   # ears, their seats, other details
                if len([c for c in support if g.o(c) and c not in new_cells | carve]) < b["support"]: rejected += 1; continue   # keep the cells that hold the SNOT brick
                chosen = (b, pp, new_cells, snot_cells); break
            if chosen is None:
                entry["decision"] = "aucune position de fixation valide (capacite manquante)"; report.append(entry); continue
            b, pp, new_cells, snot_cells = chosen
            col = {"snot": int(g.G[tuple(np.array(b["c0"]))]) if g.G[tuple(np.array(b["c0"]))] >= 0 else skin, "cale": LDC[p["couleur"]], "detail": LDC[p["couleur"]]}
            for role, num, Rm, o in pp:
                colour = col.get(role, LDC[stack[-1][1]] if role == "pupille" else skin)
                parts.append(dict(detail=p["id"], role=role, colour=colour, num=num, R=Rm.tolist(), o=np.round(o, 4).tolist()))
                md_solid.update(part_cells(num, Rm, o, shape, AXES[a_name]) if role != "snot" else snot_cells)
            carve |= (new_cells | snot_cells)
            entry["positions_rejetees"] = rejected
            entry.update(decision="construit", pieces=[(r_, n_) for r_, n_, _, _ in pp], pose=dict(cellule_snot=b["c0"], cales=b["nsp"], ecart_centre_mm=round(b["d_in"] * 0.4, 1),
                         face_externe_vs_surface_mm=round((b["outer"] - b["surf"]) * 0.4, 1), appuis_snot=b["support"]),
                         cellules_creusees=len(new_cells | snot_cells), confiance=("haute" if tilt < 20 else "moyenne" if tilt < 35 else "faible"))
            if p.get("fusion", 1) > 1:
                # patch wrapped over the sides of a tip: the part covers its front only, the voxel colour keeps the sides
                entry["cellules_recolorees"] = 0; entry["couleur_voxel_conservee"] = "flancs de la tache enveloppante"
            else:
                entry["cellules_recolorees"] = clear_colour(p, Dt / 2 + 6, [LDC[p["couleur"]]] + ([LDC[stack[1][1]]] if len(stack) > 1 else []))
            report.append(entry); continue
        if cls == "bouche":
            if a_name == "haut":
                ang = np.arctan2(n_ldu(p["axe_long"])[2], n_ldu(p["axe_long"])[0])
                best = None
                for num in FLAT:
                    m = measure(num); ns = avail(num, LDC[p["couleur"]])
                    if ns < MIN_SETS: continue
                    for rot in (0, 1):
                        iou = ellipse_iou(p["longueur_mm"], p["largeur_mm"], ang - rot * np.pi / 2, m["L_mm"], m["D_mm"], m["rond"])
                        if best is None or iou > best[0]: best = (iou, num, rot, m, ns)
                iou, num, rot, m, ns = best
                ci = np.floor([tgt[0] / 20, -tgt[1] / 8, tgt[2] / 20]).astype(int)
                nl = int(round(m["L_mm"] / 8))
                bestp = None
                for di in range(-2, 3):
                    for dk in range(-2, 3):
                        cols = [(ci[0] + di + (j if rot == 0 else 0), ci[2] + dk + (j if rot == 1 else 0)) for j in range(nl)]
                        tops = []
                        for (x, z) in cols:
                            ys = [y for y in range(ci[1] - 4, ci[1] + 4) if g.o((x, y, z)) and (x, y, z) not in reserved | carve and not g.o((x, y + 1, z))]
                            tops.append(max(ys) if ys else None)
                        if None in tops or len(set(tops)) != 1 or not all(g.o((x, tops[0] - 1, z)) for x, z in cols): continue
                        cx = np.mean([x for x, z in cols]) * 20 + 10; cz = np.mean([z for x, z in cols]) * 20 + 10
                        dist = np.hypot(cx - tgt[0], cz - tgt[2]) + 0.5 * abs(-8 * tops[0] - tgt[1])
                        if bestp is None or dist < bestp[0]: bestp = (dist, cols, tops[0])
                if bestp is None:
                    entry["decision"] = "aucune surface superieure libre (capacite manquante)"; report.append(entry); continue
                _, cols, ytop = bestp
                Rt = np.eye(3) if rot == 0 else PL.rot_y(1)
                x0 = min(x for x, z in cols); z0 = min(z for x, z in cols)
                corner = np.array([20 * x0, -8 * (ytop + 1), 20 * z0])
                Rm = Rt if (conn.part(num)["hi"][0] - conn.part(num)["lo"][0] >= conn.part(num)["hi"][2] - conn.part(num)["lo"][2]) == (rot == 0) else Rt @ PL.rot_y(1)
                o = corner - (np.array([[x, y, z] for x in (conn.part(num)["lo"][0], conn.part(num)["hi"][0]) for y in (conn.part(num)["lo"][1], conn.part(num)["hi"][1]) for z in (conn.part(num)["lo"][2], conn.part(num)["hi"][2])]) @ Rm.T).min(0)
                parts.append(dict(detail=p["id"], role="incrustation", colour=LDC[p["couleur"]], num=num, R=Rm.tolist(), o=np.round(o, 4).tolist()))
                cells = {(x, ytop, z) for x, z in cols}; carve |= cells
                entry.update(decision="construit (tuile incrustee dans la couche superieure)", pieces=[("incrustation", num)], iou_forme=round(iou, 2), cellules_creusees=len(cells),
                             confiance="moyenne" if tilt < 35 else "faible")
            else:
                # facing down (or sideways): no studded mounting faces down; the volume colour carries it
                c = to_ldu(p["centre_mm"]); cc = np.array([c[0] / 20, -c[1] / 8, c[2] / 20]); r = (p["longueur_mm"] / 2 + 2) / 0.4
                idx = np.argwhere(g.occ); dd = np.linalg.norm((idx + 0.5 - cc) * np.array([20.0, 8.0, 20.0]), axis=1); k = 0
                for cell in idx[dd <= r]:
                    x, y, z = cell
                    if a_name == "bas" and not g.o((x, y - 1, z)): recolour[(x, y, z)] = LDC[p["couleur"]]; k += 1
                entry.update(decision="couleur du volume seulement (face tournee vers le bas : aucune fixation a tenon possible) - capacite manquante",
                             cellules_recolorees=k, confiance="faible")
            report.append(entry)
    for c in list(recolour):
        if c in carve: recolour.pop(c)
    pickle.dump(dict(parts=parts, carve=sorted(carve), recolour=recolour, reserved_count=len(reserved)), open(os.path.join(out, "microdetails.pkl"), "wb"))
    cat = {num: measure(num) for num in sorted(set(ROUND + FLAT + SNOT))}
    json.dump(dict(regles=dict(min_sets=MIN_SETS, catalogue=cat), details=report, n_pieces=len(parts), cellules_creusees=len(carve), cellules_recolorees=len(recolour)),
              open(os.path.join(out, "microdetails.json"), "w"), indent=1, ensure_ascii=False, default=lambda x: x.tolist() if hasattr(x, "tolist") else str(x))
    for e in report: print(e["id"], e.get("axe_fixation"), e.get("inclinaison_deg"), e["decision"][:60], e.get("pieces"), e.get("pose"), e.get("pupille"))

if __name__ == "__main__":
    main()
