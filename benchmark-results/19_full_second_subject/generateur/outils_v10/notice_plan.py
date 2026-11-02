"""LEGO V9 - hierarchical building plan (notice) of the assembled sculpture, with physical checks of every step.

Modules (derived from the model itself, not from Paco coordinates):
  Corps      : main line, built in place from the support plane, layer by layer (feet, legs, hips, torso, shoulders, neck, head) in steps of at most STEP_MAX parts
  Bras G/D   : the arm columns (cells of the torso layers that are not the central torso, between the crotch and the shoulder layers where they merge), built apart from the
               hand up (hand = lowest quarter), then pushed up into the shoulder plates already placed
  Oreilles   : each sub-assembly block of the model (BRICKIFY SUBASSEMBLY), built apart in small groups (<= EAR_STEP parts, joint order), then attached
  Details    : eyes, nose, tongue slope (parts of the face-detail catalogue), attached last
A part is placed when it is joined by real stud joints (validate_v3 rule) to the parts already placed of its module, or when it rests on the support plane / the table
(first layer of a module). For every part and every sub-assembly the insertion is checked as a motion: the part is backed off by 4 LDU along the stud axis (engagement
clearance) and must not collide with any placed body, then it must be able to leave along one of the six axes (it may slide laterally once the studs are free).
Anything that fails is listed. Collisions, joints, order and accessibility are therefore checked as a physical sequence, not as a connected graph.
usage: notice_plan.py <model.ldr> <out_prefix>
"""
import json, os, sys
import numpy as np, networkx as nx
from collections import defaultdict, Counter
sys.path.insert(0, os.path.expanduser("~/bench/tools")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/bench/proto/v10/tools"))
sys.path.insert(0, os.path.expanduser("~/bench/proto/v9"))
import conn, partlib as PL
import scope
sys.path.insert(0, os.path.expanduser("~/bench/proto/v91"))

STEP_MAX = 20; EAR_STEP = 8
DETAIL_NUMS = {"43898", "3960", "4740", "14769", "18674", "98138", "54200", "85861", "6141"}
AXES = [np.array(v, float) for v in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]

def parse(path):
    P, sub = [], None
    for l in open(path, encoding="utf-8", errors="replace"):
        t = l.split()
        if len(t) > 4 and t[0] == "0" and t[1] == "BRICKIFY" and t[2] == "SUBASSEMBLY": sub = t[4] if t[3] == "BEGIN" else None; continue
        if t and t[0] == "1" and len(t) >= 15:
            o = np.array(t[2:5], float); M = np.array(t[5:14], float).reshape(3, 3); num = t[14].lower().replace(".dat", "")
            st, rc, lo, hi = conn.world(num, M, o)
            P.append(dict(i=len(P), line=l, c=int(t[1]), o=o, M=M, num=num, sub=sub, studs=st, recv=rc, lo=lo, hi=hi))
    return P

def build_graph(P):
    rindex = defaultdict(list)
    for p in P:
        for (pt, n) in p["recv"]: rindex[tuple(np.round(pt).astype(int))].append((p["i"], n))
    G = nx.Graph(); G.add_nodes_from(p["i"] for p in P)
    for p in P:
        for (pt, ax) in p["studs"]:
            k = np.round(pt).astype(int)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        for (q, n) in rindex.get((k[0] + dx, k[1] + dy, k[2] + dz), []):
                            if q != p["i"] and np.dot(n, ax) < -0.9:
                                if G.has_edge(p["i"], q): G[p["i"]][q]["contacts"].append((np.array(pt), np.array(ax), p["i"]))
                                else: G.add_edge(p["i"], q, contacts=[(np.array(pt), np.array(ax), p["i"])])
    return G

class Occ:
    """collision state of the placed bodies (studs excluded).
    right-angle parts on the 4-LDU lattice : occupancy grid (exact, their faces lie on multiples of 4 LDU);
    other parts (rotated ear parts, curved plates) : their solid points (>= 1 LDU inside their faces), compared by distance (< 1.5 LDU = overlap, like validate_v3)"""
    def __init__(self, P, pad=160):
        lo = np.min([p["lo"] for p in P], 0); hi = np.max([p["hi"] for p in P], 0)
        self.o = np.floor(lo / 4) * 4 - pad * 4 / 4; self.shape = (np.ceil((hi - self.o) / 4).astype(int) + pad)
        self.g = np.zeros(self.shape, np.int16); self.cache = {}; self.pcache = {}; self.pts = {}; self.tree = None; self.owner = []
    def aligned(self, p):
        if "al" not in p:
            p["al"] = bool(np.all(np.isclose(np.abs(p["M"]), 0, atol=1e-4) | np.isclose(np.abs(p["M"]), 1, atol=1e-4))) and conn.part(p["num"])["fill"] >= 0.97 and "bracket" not in PL.title(p["num"]).lower() \
                and all(abs(v / 4 - round(v / 4)) < 0.05 for v in list(p["lo"]) + list(p["hi"]))
        return p["al"]
    def cells(self, p):
        if p["i"] in self.cache: return self.cache[p["i"]]
        a = np.round((p["lo"] - self.o) / 4).astype(int); b = np.round((p["hi"] - self.o) / 4).astype(int)
        c = np.array(np.meshgrid(*[np.arange(a[k], b[k]) for k in range(3)], indexing="ij")).reshape(3, -1).T
        self.cache[p["i"]] = c; return c
    def points(self, p):
        if p["i"] not in self.pcache: self.pcache[p["i"]] = conn.solid_points(p["num"]) @ p["M"].T + p["o"]
        return self.pcache[p["i"]]
    def add(self, p):
        if self.aligned(p): self.g[tuple(self.cells(p).T)] += 1
        else: self.pts[p["i"]] = self.points(p); self.tree = None
    def remove(self, p):
        if self.aligned(p): self.g[tuple(self.cells(p).T)] -= 1
        elif p["i"] in self.pts: del self.pts[p["i"]]; self.tree = None
    def blocked(self, p, shift_ldu, d=None, own=None):
        sh = np.asarray(shift_ldu, float)
        if self.aligned(p):
            c = self.cells(p) + np.round(sh / 4).astype(int)
            ok = (c >= 0).all(1) & (c < np.array(self.shape)).all(1)
            if ok.any() and (self.g[tuple(c[ok].T)] > 0).any(): return True
            if not self.pts: return False
            q = self.points(p) + sh
        else:
            q = self.points(p) + sh
            c = np.floor((q - self.o) / 4).astype(int); ok = (c >= 0).all(1) & (c < np.array(self.shape)).all(1)
            if ok.any() and (self.g[tuple(c[ok].T)] > 0).any(): return True
            if not self.pts: return False
        if self.tree is None:
            from scipy.spatial import cKDTree
            self.tree = cKDTree(np.vstack(list(self.pts.values())))
        d_, _ = self.tree.query(q, distance_upper_bound=1.5)
        return bool(np.isfinite(d_).any())
    def model_lo(self):
        idx = np.argwhere(self.g > 0)
        return (idx.min(0) * 4 + self.o) if len(idx) else self.o
    def model_hi(self):
        idx = np.argwhere(self.g > 0)
        return ((idx.max(0) + 1) * 4 + self.o) if len(idx) else self.o
    def free_exit(self, p, start_shift, dirs, limit=600):
        """can p, starting from start_shift, translate along one of dirs to leave the model ? returns the first free direction or None"""
        for d in dirs:
            k = 0; free = True; step = 4 if self.aligned(p) else 6
            while k * step <= limit:
                if self.blocked(p, start_shift + d * step * (k + 1)): free = False; break
                k += 1
            if free: return d
        return None

def escape_bfs(occ, p, start, model_lo, model_hi, max_states=120000):
    """path search for a small part: from the engagement clearance position, axis moves of 4 LDU through free space (corners allowed) until the part is outside the model's bounding box"""
    from collections import deque
    step = 4; s0 = tuple(np.round(np.asarray(start) / step).astype(int)); seen = {s0}; dq = deque([s0]); lo, hi = p["lo"], p["hi"]
    while dq and len(seen) < max_states:
        c = dq.popleft(); sh = np.array(c, float) * step
        if (hi + sh < model_lo).any() or (lo + sh > model_hi).any(): return True
        for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            n = (c[0] + d[0], c[1] + d[1], c[2] + d[2])
            if n in seen: continue
            seen.add(n)
            if not occ.blocked(p, np.array(n, float) * step): dq.append(n)
    return False

def motions(p, G, placed):
    """engagement motions (unit vectors) of part p against the placed set: owner of the stud moves along +ax, receiver along -ax_owner"""
    out = []
    for q in G.neighbors(p["i"]):
        if q not in placed: continue
        for (pt, ax, owner) in G[p["i"]][q]["contacts"]:
            m = ax if owner == p["i"] else -ax
            if not any(np.allclose(m, o, atol=0.2) for o in out): out.append(m)
    return out

def check_part(p, G, placed, occ, frame_dirs):
    """insertion test of one part. returns dict(ok, joints, reason, exit)"""
    ms = motions(p, G, placed)
    if not ms: return dict(ok=True, joints=0, reason="repose sur le plan d'appui / la table", exit=None, motion=None)
    if len(ms) > 1:
        # several engagement directions: acceptable only when one motion is shared by every contact (opposite directions = part imprisoned)
        reason = "pieces emprisonnee : emboitements dans des directions differentes (%s)" % ", ".join(str(np.round(m, 1).tolist()) for m in ms)
        # a part pressed between two layers can still be slid when the two directions are opposite and one neighbour is only touching; report it
        return dict(ok=False, joints=len(ms), reason=reason, exit=None, motion=ms[0].tolist())
    m = ms[0]; back = -m * 4.0
    if occ.blocked(p, back): return dict(ok=False, joints=1, reason="emboitement bloque : une piece deja posee gene les 4 LDU d'approche", exit=None, motion=m.tolist())
    dirs = [-m] + [d for d in frame_dirs if not np.allclose(d, -m) and not np.allclose(d, m)]
    e = occ.free_exit(p, back, dirs)
    if e is None:
        if occ.aligned(p) and escape_bfs(occ, p, back, occ.model_lo(), occ.model_hi()):
            return dict(ok=True, joints=1, reason="degagement par un chemin avec virages (pas de ligne droite libre)", exit=[0, 0, 0], motion=m.tolist())
        return dict(ok=False, joints=1, reason="aucune direction de degagement libre : la piece ne peut plus etre inseree", exit=None, motion=m.tolist())
    return dict(ok=True, joints=1, reason="", exit=e.tolist(), motion=m.tolist())

def check_block(idx, P, G, placed, occ, frame_dirs):
    """rigid sub-assembly attaching to the placed set"""
    S = set(idx); ms = []
    for i in idx:
        for q in G.neighbors(i):
            if q in placed and q not in S:
                for (pt, ax, owner) in G[i][q]["contacts"]:
                    m = ax if owner in S else -ax
                    if not any(np.allclose(m, o, atol=0.2) for o in ms): ms.append(m)
    if not ms: return dict(ok=False, reason="le sous-ensemble n'a aucun tenon en commun avec la structure deja posee", motion=None, exit=None, directions=0)
    best = None
    for m in ms:
        back = -m * 4.0
        if any(occ.blocked(P[i], back) for i in idx): continue
        e = None
        for d in [-m] + [d for d in frame_dirs if not np.allclose(d, -m) and not np.allclose(d, m)]:
            ok = True; k = 0
            while k * 6 <= 600:
                if any(occ.blocked(P[i], back + d * 6 * (k + 1)) for i in idx): ok = False; break
                k += 1
            if ok: e = d; break
        if e is not None: best = (m, e); break
    if best is None: return dict(ok=False, reason="le sous-ensemble ne peut pas etre approche sans collision (emboitement ou degagement bloque)", motion=ms[0].tolist(), exit=None, directions=len(ms))
    return dict(ok=True, reason="", motion=best[0].tolist(), exit=best[1].tolist(), directions=len(ms))

def modules_of(P, G):
    """module assignment of every part"""
    mod = {}; lattice = {}
    for p in P:
        cs = None
        if p["sub"] is None and p["num"] not in DETAIL_NUMS:
            if np.all(np.isclose(np.abs(p["M"]), 0, atol=1e-4) | np.isclose(np.abs(p["M"]), 1, atol=1e-4)):
                a = np.round([p["lo"][0] / 20, -p["hi"][1] / 8, p["lo"][2] / 20]).astype(int); b = np.round([p["hi"][0] / 20, -p["lo"][1] / 8, p["hi"][2] / 20]).astype(int)
                cs = (a, b)
        lattice[p["i"]] = cs
    for p in P:
        if p["sub"] is not None: mod[p["i"]] = ("oreille", p["sub"])
        elif p["num"] in DETAIL_NUMS: mod[p["i"]] = ("detail", None)
        else: mod[p["i"]] = ("corps", None)
    # arms: per-layer connected components of the body cells (right-angle body parts only)
    NX, NY, NZ = scope.SHAPE; occ = np.zeros((NX, NY, NZ), bool); who = -np.ones((NX, NY, NZ), np.int32)
    for p in P:
        if mod[p["i"]][0] != "corps" or lattice[p["i"]] is None: continue
        a, b = lattice[p["i"]]; sl = tuple(slice(max(a[k], 0), min(b[k], (NX, NY, NZ)[k])) for k in range(3)); occ[sl] = True; who[sl] = p["i"]
    from scipy import ndimage
    ncomp = {}
    for y in range(NY):
        lab, n = ndimage.label(occ[:, y, :], structure=np.ones((3, 3))); ncomp[y] = n
    ys = [y for y in range(NY) if occ[:, y, :].any()]
    crotch = next((y for y in ys if y > 4 and ncomp[y] != 2 and ncomp[y - 1] == 2), None)         # first layer above the two leg columns
    merge = next((y for y in range(crotch + 1, NY) if occ[:, y, :].any() and ncomp[y] == 1 and ncomp[y - 1] > 1), None) if crotch is not None else None
    info = dict(crotch_layer=crotch, merge_layer=merge)
    arm_parts = {"G": [], "D": []}
    if crotch is not None and merge is not None:
        # the layers in which the two arms are separate from the torso: the highest end layer e giving a torso and two arm components of >= 60 cells in the layers [crotch, e)
        best = None
        for e in range(merge, crotch + 4, -1):
            sub = np.zeros_like(occ); sub[:, crotch:e, :] = occ[:, crotch:e, :]
            lab, n = ndimage.label(sub); sizes = np.bincount(lab.ravel())[1:]
            big = [k for k in range(1, n + 1) if sizes[k - 1] >= 60]
            if len(big) >= 3: best = (e, lab, n, sizes, big); break
        if best is None: info["bras"] = "non detectes : morphologie non bipede, tout le corps sur la ligne principale (V10)"; return mod, info, lattice
        e, lab, n, sizes, big = best; main = max(big, key=lambda k: sizes[k - 1])
        arms = [k for k in big if k != main]
        info["couche_fin_bras"] = int(e); info["composantes_3D"] = int(n); info["bras_tailles"] = [int(sizes[k - 1]) for k in arms]
        for k in arms:
            cx = np.argwhere(lab == k)[:, 0].mean(); side = "G" if cx < np.argwhere(lab == main)[:, 0].mean() else "D"
            for i in np.unique(who[lab == k]):
                if i >= 0 and mod[int(i)][0] == "corps": arm_parts[side].append(int(i))
        moved = 0
        for side, ids in arm_parts.items():
            S_ = set(ids)
            for i in ids:
                if any(q in S_ for q in G.neighbors(i)): mod[i] = ("bras", side)
                else: moved += 1                                     # joined to nothing inside the arm (held only by the shoulder plates): belongs to the main line
        info["bras"] = {k: sum(1 for i in v if mod[i][0] == "bras") for k, v in arm_parts.items()}; info["pieces_de_bras_reaffectees_au_corps"] = moved
    return mod, info, lattice


def order_layers(ids, P, G, occ, base_level, chunk, placed0=(), up=(0.0, -1.0, 0.0)):
    """bottom-up order of a module. Returns a list of batches, each batch = list of (part, flag) with flag in {'joint','pose','pose_sur_appui','suspendue'}.
    A part is placed in its layer when it rests on the support plane or on an already placed body (joined by studs or simply resting on a tile);
    a part with nothing under it (overhang) waits until a neighbour that holds it is placed and is then pushed on from below."""
    ids = set(ids); placed = set(placed0); steps = []; waiting = set(); up = np.asarray(up, float)
    def t0(i):                                  # lowest projection of the part along the building axis
        C = conn.part(P[i]["num"]); cs = np.array([[x, y, z] for x in (C["lo"][0], C["hi"][0]) for y in (C["lo"][1], C["hi"][1]) for z in (C["lo"][2], C["hi"][2])]) @ P[i]["M"].T + P[i]["o"]
        return float((cs @ up).min())
    lay = defaultdict(list)
    for i in ids: lay[int(round(t0(i) / 8))].append(i)
    def holds(i):                      # a neighbour already placed that holds i by studs
        return any(q in placed for q in G.neighbors(i))
    tmin = min(t0(i) for i in ids) if ids else 0.0
    def rests(i):
        if not placed0 and abs(t0(i) - tmin) < 0.6: return True                       # first layer of a module built apart: rests on the table
        if placed0 and abs(P[i]["hi"][1] - base_level) < 0.5 and np.allclose(up, (0, -1, 0)): return True    # support plane of the main line
        return occ.blocked(P[i], -up * 4.0)
    cur = []
    def push(i, f):
        nonlocal cur
        cur.append((i, f)); placed.add(i); occ.add(P[i])
        if len(cur) >= chunk: steps.append(cur); cur = []
    def flush():
        moved = True
        while moved:
            moved = False
            for i in sorted(waiting):
                if holds(i): waiting.discard(i); push(i, "suspendue"); moved = True
    for L in sorted(lay):
        for i in sorted(lay[L], key=lambda i: (P[i]["lo"][0], P[i]["lo"][2])):
            if rests(i) or holds(i): push(i, "joint" if holds(i) else "pose")
            else: waiting.add(i)
        flush()
    flush()
    if cur: steps.append(cur); cur = []
    if waiting: steps.append([(i, "orpheline") for i in sorted(waiting)]); [placed.add(i) for i in waiting]
    return steps


def plan_units(ids, P, G, frame_dirs, depth=0, max_depth=3):
    """assembly by rigid sub-units, found by disassembly : repeatedly remove a unit that can leave along one direction d, where a unit is a connected component of the
    contacts that are NOT along d (those contacts bind its parts) and all its boundary contacts are along d on the same side. The reverse order is the assembly order;
    each unit with several parts is planned the same way inside itself. Returns items: ('parts', [(i, flag)]) or ('unit', ids, items)."""
    ids = list(ids)
    if len(ids) <= 1: return [("parts", [(ids[0], "faisable")])] if ids else []
    S = set(ids); occ = Occ([P[i] for i in ids]); [occ.add(P[i]) for i in ids]
    dirs = []
    for d in list(frame_dirs):
        d = np.asarray(d, float); d = d / np.linalg.norm(d)
        if not any(np.allclose(d, e, atol=0.05) for e in dirs): dirs.append(d)
    rem = set(ids); rev = []
    while rem:
        found = None
        for d in dirs:
            H = nx.Graph(); H.add_nodes_from(rem)
            for u, v, data in G.subgraph(rem).edges(data=True):
                if any(abs(np.dot(ax, d)) < 0.9 for (pt, ax, owner) in data["contacts"]): H.add_edge(u, v)
            for C in sorted(nx.connected_components(H), key=len):
                moves = []
                for u in C:
                    for q in G.neighbors(u):
                        if q in rem and q not in C:
                            for (pt, ax, owner) in G[u][q]["contacts"]:
                                m = -ax if owner in C else ax                      # motion that disengages C
                                if not any(np.allclose(m, o, atol=0.2) for o in moves): moves.append(m)
                if len(moves) != 1 or abs(abs(np.dot(moves[0], d)) - 1) > 0.1: continue
                e = moves[0]; free = True; k = 0
                for i in C: occ.remove(P[i])
                step = 6
                while k * step <= 600:
                    if any(occ.blocked(P[i], e * step * (k + 1)) for i in C): free = False; break
                    k += 1
                if free: found = (set(C), e); break
                for i in C: occ.add(P[i])
            if found: break
        if not found:
            rev.append((set(rem), None, True)); break
        rev.append((found[0], found[1], False)); rem -= found[0]
    items = []
    for C, e, stuck in reversed(rev):
        C = sorted(C)
        if stuck: items.append(("parts", [(i, "orpheline") for i in C])); continue
        if len(C) == 1 or depth >= max_depth: items.append(("parts", [(i, "faisable") for i in C]))
        else: items.append(("unit", C, plan_units(C, P, G, frame_dirs, depth + 1, max_depth)))
    return items

EAR_CHECK = {}; EAR_INFO = {}; ORI = {}

def items_from_json(order):
    out = []
    for x in order:
        if x["kind"] == "part": out.append(("parts", [(x["ids"][0], "faisable")]))
        else: out.append(("unit", x["ids"], items_from_json(x["inside"])))
    return out

def main():
    src, prefix = sys.argv[1:3]
    EARS = json.load(open(sys.argv[sys.argv.index("--ears") + 1])) if "--ears" in sys.argv else None
    P = parse(src); G = build_graph(P); occ = Occ(P)
    mod, info, lattice = modules_of(P, G)
    n = len(P); layer = {p["i"]: int(round(-p["hi"][1] / 8)) for p in P}              # layer index of the bottom of the part
    base_y = max(p["hi"][1] for p in P)
    # ----- module part lists
    groups = defaultdict(list)
    for i in range(n): groups[mod[i]].append(i)
    # hands = lowest quarter of an arm
    hand = {}
    plan = []; issues = []; frame_default = AXES; outplan = []
    body_ids = groups[("corps", None)]
    main_placed = set()
    FLAGTXT = {"joint": "", "pose": "pose sur un appui sans emboitement : verrouillee par la couche suivante", "suspendue": "piece suspendue : emboitee par-dessous apres la piece qui la tient",
               "orpheline": "piece sans appui ni voisin pose", "faisable": ""}
    def run_steps(steps, label, header, occ_real, placed_set, kind, frame_dirs, out):
        for batch in steps:
            res = []
            for i, f in batch:
                if i in EAR_CHECK: r = dict(ok=EAR_CHECK[i]["ok"], joints=1, reason=EAR_CHECK[i]["reason"], exit=None, motion=EAR_CHECK[i]["motion"], sens=EAR_INFO.get(i, {}).get("sens"), stable=EAR_INFO.get(i, {}).get("stable"))
                else: r = check_part(P[i], G, placed_set, occ_real, frame_dirs) if placed_set else dict(ok=True, joints=0, reason="plan d'appui / table", exit=None, motion=None)
                if r["joints"] == 0 and r["ok"]: r["reason"] = FLAGTXT.get(f, "") or r["reason"]
                if f == "orpheline": r = dict(ok=False, joints=0, reason=FLAGTXT["orpheline"], exit=None, motion=None)
                r["flag"] = f; res.append(r); placed_set.add(i); occ_real.add(P[i])
            out.append(dict(module=label, section=header, parts=[i for i, f in batch], checks=res, kind=kind))
    def plan_by_feasibility(ids, occ_m, frame_dirs, chunk, up):
        """assembly sequencing by feasibility : the next part is a part joined to the placed ones whose insertion motion is free (lowest along the building axis first)"""
        ids = set(ids); placed = set(); order = []
        def t0(i):
            C = conn.part(P[i]["num"]); cs = np.array([[x, y, z] for x in (C["lo"][0], C["hi"][0]) for y in (C["lo"][1], C["hi"][1]) for z in (C["lo"][2], C["hi"][2])]) @ P[i]["M"].T + P[i]["o"]
            return float((cs @ up).min())
        rem = set(ids); T = {i: t0(i) for i in ids}; tmin = min(T.values())
        scratch = Occ([P[i] for i in ids])
        while rem:
            cands = [i for i in rem if any(q in placed for q in G.neighbors(i))] if placed else [i for i in rem if abs(T[i] - tmin) < 0.6]
            ok_c = []
            for i in sorted(cands, key=lambda i: (T[i], i)):
                r = check_part(P[i], G, placed, scratch, frame_dirs) if placed else dict(ok=True)
                if r["ok"]: ok_c.append(i)
                if len(ok_c) >= 6: break
            if ok_c: i = min(ok_c, key=lambda i: (T[i], -sum(1 for q in G.neighbors(i) if q in placed))); flag = "faisable"
            else:
                rest = sorted(rem, key=lambda i: (T[i], i)); i = (sorted(cands, key=lambda i: (T[i], i)) or rest)[0]; flag = "joint" if cands else "orpheline"
            order.append((i, flag)); placed.add(i); scratch.add(P[i]); rem.discard(i)
        return [order[k:k + chunk] for k in range(0, len(order), chunk)]
    # ---- arm parts that cannot be sequenced inside their arm (held only by the shoulder plates, through other hanging parts) belong to the main line
    for side in ("G", "D"):
        ids = groups.get(("bras", side), [])
        if not ids: continue
        lowest = max(P[i]["hi"][1] for i in ids); st0 = order_layers(ids, P, G, Occ([P[i] for i in ids]), lowest, STEP_MAX)
        orph = [i for b in st0 for i, f in b if f == "orpheline"]
        if orph:
            groups[("bras", side)] = [i for i in ids if i not in set(orph)]
            for i in orph: mod[i] = ("corps", None)
            groups[("corps", None)] = groups[("corps", None)] + orph
            info.setdefault("pieces_de_bras_sans_sequence_reaffectees", 0); info["pieces_de_bras_sans_sequence_reaffectees"] += len(orph)
    body_ids = groups[("corps", None)]
    # main-line parts that are held only by a module attached later (e.g. the last plates on top of an arm) go with that module
    st_m = order_layers(body_ids, P, G, Occ(P), base_y, STEP_MAX); orph = [i for b in st_m for i, f in b if f == "orpheline"]
    for i in orph:
        kinds = Counter(mod[q] for q in G.neighbors(i) if mod[q][0] in ("bras", "oreille", "detail"))
        if kinds:
            tgt = kinds.most_common(1)[0][0]; groups[tgt] = groups[tgt] + [i]; groups[("corps", None)].remove(i); mod[i] = tgt
            info.setdefault("pieces_du_corps_rattachees_a_un_module", 0); info["pieces_du_corps_rattachees_a_un_module"] += 1
    body_ids = groups[("corps", None)]
    # ---- main steps (strict bottom-up with resting / suspended parts)
    scratch = Occ(P); main_steps = order_layers(body_ids, P, G, scratch, base_y, STEP_MAX)
    # ---- modules
    modules = []     # dicts: label, ids, steps (internal), kind
    for side, label in (("G", "Bras gauche"), ("D", "Bras droit")):
        ids = groups.get(("bras", side), [])
        if not ids: continue
        lowest = max(P[i]["hi"][1] for i in ids); sc = Occ([P[i] for i in ids]); st = order_layers(ids, P, G, sc, lowest, STEP_MAX)
        lays = sorted(int(round(-P[i]["hi"][1] / 8)) for i in ids); cut = lays[int(len(lays) * 0.25)]; hand_set = {i for i in ids if int(round(-P[i]["hi"][1] / 8)) <= cut}
        modules.append(dict(label=label, ids=ids, steps=st, hand=hand_set, kind="bras"))
    for (k, sub), ids in sorted(groups.items(), key=lambda kv: str(kv[0])):
        if k != "oreille": continue
        H = G.subgraph(ids); comps = sorted(nx.connected_components(H), key=lambda c: -len(c)); base_label = "Oreille " + ("haute" if "haute" in sub else "basse") + (" (attache 2)" if sub.endswith("_1") else "")
        for ci, comp in enumerate(comps):
            comp = sorted(comp); name = base_label + (" - piece %d" % (ci + 1) if len(comps) > 1 else "")
            ups = Counter(tuple(np.round(P[i]["M"] @ np.array([0, -1.0, 0]), 2)) for i in comp); upv = np.array(ups.most_common(1)[0][0], float)
            fr = [P[comp[0]]["M"][:, k_] for k_ in range(3)] + [-P[comp[0]]["M"][:, k_] for k_ in range(3)] + list(AXES)
            key = next((k for k, v in EARS.items() if set(v["ids"]) == set(comp)), None) if EARS else None
            if key is None: raise SystemExit("plan d'oreille absent pour %s (%d pieces) : lancer run_ears_v91.py" % (name, len(comp)))
            e = EARS[key]; items = items_from_json(e["best"]["order"])
            for ck, cv in e["checks"].items(): EAR_CHECK[int(ck)] = cv
            for row in e["best"]["rows"]:
                for i in row["ids"]: EAR_INFO[i] = dict(sens=row["sens"], stable=row["stable"], marge=row["marge_ldu"])
            ORI[name] = e["best"]["name"]
            modules.append(dict(label=name, ids=comp, items=items, kind="oreille", frame=fr, orientation=e["best"]["name"]))
    dids = groups.get(("detail", None), [])
    if dids:
        H = G.subgraph(dids)
        for ci, comp in enumerate(sorted(nx.connected_components(H), key=lambda c: min(c))):
            comp = sorted(comp, key=lambda i: -P[i]["hi"][1]); nums = Counter(P[i]["num"] for i in comp)
            modules.append(dict(label="Detail du visage %d (%s)" % (ci + 1, ", ".join(f"{v}x {k}" for k, v in nums.items())), ids=comp, steps=[[(i, "faisable") for i in comp]], kind="detail"))
    # ---- interleaved simulation: main steps in order; after each step, every pending module whose main-line neighbours are all placed is built apart and attached if its motion is free
    def build_items(items, label, frame, occ_level, placed_level, counter):
        batch = []
        def flush():
            top = label.split(" > ")[0]; hdr = "Construction" + (" - oreille posee " + ORI[top] if top in ORI else "")
            for k in range(0, len(batch), EAR_STEP): run_steps([batch[k:k + EAR_STEP]], label, hdr, occ_level, placed_level, "sub", frame, outplan)
            batch.clear()
        for it in items:
            if it[0] == "parts": batch.extend(it[1])
            else:
                flush(); C, sub_items = it[1], it[2]; counter[0] += 1; ulabel = "%s > unite %d" % (label.split(" > ")[0], counter[0])
                occ_u = Occ([P[i] for i in C]); placed_u = set()
                build_items(sub_items, ulabel, frame, occ_u, placed_u, counter)
                att = check_block(C, P, G, placed_level, occ_level, frame) if placed_level else dict(ok=True, reason="", motion=None, exit=None, directions=0)
                outplan.append(dict(module=ulabel, section="Assemblage de l'unite", parts=list(C), checks=[att], kind="attach", attach=att))
                for i in C: placed_level.add(i); occ_level.add(P[i])
        flush()
    pending = list(modules); body_set = set(body_ids)
    def try_attach():
        for m in list(pending):
            nb = {q for i in m["ids"] for q in G.neighbors(i) if q not in m["ids"]}
            if m["kind"] == "bras": needed = {q for q in nb if q in body_set}
            else: needed = {q for q in nb if q in body_set or q in {j for mm in modules if mm["kind"] != m["kind"] and mm is not m for j in mm["ids"]}}
            if not nb: continue
            if m["kind"] == "oreille":
                if not (nb & main_placed): continue                       # an ear is attached as soon as it can be, before the head closes over its root
            elif not (needed <= main_placed): continue
            fr = m.get("frame", frame_default)
            att = check_block(m["ids"], P, G, main_placed, occ, fr)
            if not att["ok"] and not m.get("retry_ok"): m["last"] = att; continue
            # build the module apart, then attach it
            occ_m = Occ([P[i] for i in m["ids"]]); m_placed = set(); n0 = len(outplan)
            if "items" in m: build_items(m["items"], m["label"], fr, occ_m, m_placed, [0])
            else: run_steps(m["steps"], m["label"], "Construction", occ_m, m_placed, "sub", fr, outplan)
            if m["kind"] == "bras":
                for st in outplan[n0:]: st["section"] = "Main" if all(i in m["hand"] for i in st["parts"]) else "Avant-bras et bras"
            outplan.append(dict(module=m["label"], section="Fixation", parts=list(m["ids"]), checks=[att], kind="attach", attach=att))
            for i in m["ids"]: main_placed.add(i); occ.add(P[i])
            pending.remove(m)
    for batch in main_steps:
        run_steps([batch], "Corps", "Pieds, jambes, bassin, torse, cou et tete", occ, main_placed, "main", frame_default, outplan)
        try_attach()
    try_attach()
    for m in pending:      # never attachable: placed at the end and reported
        att = check_block(m["ids"], P, G, main_placed, occ, m.get("frame", frame_default)); att["ok"] = False; att["reason"] = att.get("reason") or "aucun moment d'accrochage libre"
        occ_m = Occ([P[i] for i in m["ids"]]); m_placed = set(); n0 = len(outplan)
        if "items" in m: build_items(m["items"], m["label"], m.get("frame", frame_default), occ_m, m_placed, [0])
        else: run_steps(m["steps"], m["label"], "Construction", occ_m, m_placed, "sub", m.get("frame", frame_default), outplan)
        outplan.append(dict(module=m["label"], section="Fixation", parts=list(m["ids"]), checks=[att], kind="attach", attach=att))
        for i in m["ids"]: main_placed.add(i); occ.add(P[i])
    plan = outplan
    # ----- orphans (parts of no module step)
    placed_all = {i for s in plan for i in s["parts"]}
    missing = sorted(set(range(n)) - placed_all)
    if missing: issues.append(dict(type="pieces absentes du plan", n=len(missing)))
    # ----- summary
    bad = [(k, j, r) for k, s in enumerate(plan) for j, r in enumerate(s["checks"]) if not r["ok"]]
    out = dict(info=info, pieces=n, etapes=len(plan), modules=dict(Counter(s["module"] for s in plan)), problemes_insertion=[dict(etape=k + 1, module=plan[k]["module"], piece=int(plan[k]["parts"][j]) if plan[k]["kind"] != "attach" else None, **{kk: vv for kk, vv in r.items() if kk in ("reason", "motion")}) for k, j, r in bad],
               autres=issues, manquantes=len(missing))
    json.dump(dict(plan=[dict(module=s["module"], section=s["section"], kind=s["kind"], parts=[int(i) for i in s["parts"]], checks=s["checks"], attach=s.get("attach")) for s in plan], resume=out), open(prefix + "_plan.json", "w"), indent=1, default=float)
    # ordered LDraw : one block per top-level module (arm, ear, face detail), the hierarchy (units) is kept in the plan file ; a part line is written once
    lines = ["0 paco_V9_notice", "0 Name: paco_V9_notice.ldr", "0 Author: moteur 1 V9 : plan hierarchique controle (accessibilite, joints, ordre)"]
    cur = None; pos = {}; npart = [0]
    def put(i):
        lines.append(P[i]["line"]); pos[int(i)] = npart[0]; npart[0] += 1
    for s_ in plan:
        top = s_["module"].split(" > ")[0].replace(" ", "_"); is_unit = " > " in s_["module"]
        if s_["kind"] == "main":
            if cur: lines.append(f"0 BRICKIFY SUBASSEMBLY END {cur}"); cur = None
            for i in s_["parts"]: put(i)
            lines.append("0 STEP")
        elif s_["kind"] == "sub":
            if cur != top:
                if cur: lines.append(f"0 BRICKIFY SUBASSEMBLY END {cur}")
                lines.append(f"0 BRICKIFY SUBASSEMBLY BEGIN {top}"); cur = top
            for i in s_["parts"]: put(i)
            lines.append("0 STEP")
        else:   # attach
            if is_unit: lines.append("0 STEP"); continue
            if cur == top: lines.append(f"0 BRICKIFY SUBASSEMBLY END {cur}"); cur = None
            lines.append("0 STEP")
    if cur: lines.append(f"0 BRICKIFY SUBASSEMBLY END {cur}")
    assert npart[0] == n, (npart[0], n)
    open(prefix + "_notice.ldr", "w").write("\n".join(lines) + "\n")
    json.dump(pos, open(prefix + "_map.json", "w"))
    print(json.dumps(out, indent=1, default=float)[:3000])

if __name__ == "__main__":
    main()
