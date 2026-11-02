"""LEGO V9.1 - assembly sequencing of a rigid-part model by directional blocking (group extraction), replacing the unit search of notice_plan.plan_units.

Principle (reverse of assembly): the remaining set R is disassembled by repeatedly removing a GROUP C that can leave as a rigid body along one direction e:
  * stud rule : every stud contact between a part of C and a part outside C must be released by e (the member of C that owns the stud leaves along -axis, the member that
                receives it leaves along +axis; exact axis, the studs have no lateral play);
  * path rule : the swept volume of C along e, from its place to outside the model, meets no part outside C (solid points of the parts, studs excluded, like validate_v3).
A part that fails the stud or the path rule drags the part responsible into the group (closure), so the smallest valid group is found for every seed; a group is never larger than
needed. The reverse order is the assembly order; a group of several parts is a sub-assembly that is itself sequenced the same way.
Optional second phase : "lift then slide" (disengage along the stud axis for LIFT ldu, then translate along any other axis).
Everything is generic: only the part geometry, the stud graph and the candidate directions (axes of the stud joints + global axes) are used.
"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import os, sys, functools
import numpy as np, networkx as nx
from scipy.spatial import cKDTree
sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, ENGINE_DIR)
import conn, partlib as PL
import verify_seq as V

THRESH = 1.5; STEP = 2.0; LIFT = 5.0

@functools.lru_cache(maxsize=None)
def local_points(num):
    P = conn.part(num); t = PL.title(num).lower()
    if P["fill"] >= 0.97 and "bracket" not in t:
        lo, hi = P["lo"], P["hi"]
        ax = [np.arange(lo[k] + 1, hi[k] - 0.99, 2.0) for k in range(3)]
        ax = [a if len(a) else np.array([(lo[k] + hi[k]) / 2]) for k, a in enumerate(ax)]
        return np.stack(np.meshgrid(*ax, indexing="ij"), -1).reshape(-1, 3)
    return conn.solid_points(num)

def world_points(p): return local_points(p["num"]) @ p["M"].T + p["o"]

class Model:
    def __init__(self, P, ids, G):
        self.P, self.G = P, G; self.ids = sorted(ids); self.set = set(ids)
        self.pts = {i: world_points(P[i]) for i in self.ids}
        allp = np.vstack([self.pts[i] for i in self.ids]); self.owner = np.concatenate([[i] * len(self.pts[i]) for i in self.ids])
        self.tree = cKDTree(allp)
        self.lo = allp.min(0) - 10; self.hi = allp.max(0) + 10
        self.hits_cache = {}; self.computed = set()
    def hits(self, i, e, lift_only=False):
        """parts (other than i) met by sweeping part i along unit vector e from its place until it leaves the bounding box of the model"""
        key = (i, tuple(np.round(e, 3)), lift_only)
        if key in self.hits_cache and key in self.computed: return self.hits_cache[key]
        pts = self.pts[i]; L = (LIFT if lift_only else float(np.abs(self.hi - self.lo).max()) + 40)
        n = int(L / STEP) + 1; ss = np.arange(1, n + 1) * STEP
        # sub-sample the points of long parts to keep the cost bounded
        Q = (pts[None, :, :] + ss[:, None, None] * e[None, None, :]).reshape(-1, 3)
        d, k = self.tree.query(Q, distance_upper_bound=THRESH, workers=2)
        ok = np.isfinite(d); out = set(int(x) for x in self.owner[k[ok]]) - {i}
        out |= self.hits_cache.get(key, set()); self.hits_cache[key] = out; self.computed.add(key); return out

def disengage_dir(G, P, x, y):
    """motion of x (member of the moving group) needed to release its stud contacts with y : list of unit vectors (one per distinct contact axis)"""
    ds = []
    for (pt, ax, owner) in G[x][y]["contacts"]:
        d = -ax if owner == x else ax
        if not any(np.allclose(d, o, atol=0.05) for o in ds): ds.append(np.asarray(d, float))
    return ds

class Sequencer:
    def __init__(self, P, G, ids, dirs, lift_slide=True):
        self.P, self.G = P, G
        self.M = Model(P, ids, G)
        self.dirs = []
        for d in dirs:
            d = np.asarray(d, float); d = d / np.linalg.norm(d)
            if not any(np.allclose(d, e, atol=0.03) for e in self.dirs): self.dirs.append(d)
        self.lift_slide = lift_slide; self.fine = False
    def add_extra(self, i, e, owners):
        """blockers found by the independent fine replay : merged into the sweep results of part i along e"""
        key = (int(i), tuple(np.round(e, 3)), False)
        self.M.hits_cache.setdefault(key, set()).update(int(o) for o in owners)
    def bind_closure(self, seed, e, R):
        """parts that must move WITH the seed because of the stud rule only (a stud contact that the motion e does not release) : the rigid group"""
        C = {seed}; todo = [seed]
        while todo:
            x = todo.pop()
            for y in self.G.neighbors(x):
                if y in R and y not in C:
                    ds = disengage_dir(self.G, self.P, x, y)
                    if any(np.dot(d, e) < 0.99 for d in ds):
                        C.add(y); todo.append(y)
                        if len(C) >= len(R): return None
        return C
    def blockers(self, C, e, R, slide=None):
        """parts of R outside C that are in the way of the group C leaving along e (or lifting along e then sliding along `slide`) : they must be extracted BEFORE C"""
        out = set()
        for x in C:
            if slide is None: out |= self.M.hits(x, e) & R
            else: out |= (self.M.hits(x, e, lift_only=True) & R) | (self.hits_from(x, e * LIFT, slide) & R)
        return out - C
    def closure(self, seed, e, R, slide=None):
        """(fallback for mutually blocking groups) smallest group containing the seed that can leave along e: stud rule + path rule, blockers dragged into the group.
        valid only if the group is one connected stud assembly (a rigid body) ; None otherwise"""
        C = {seed}; todo = [seed]
        while todo:
            x = todo.pop(); need = set()
            for y in self.G.neighbors(x):
                if y in R and y not in C:
                    ds = disengage_dir(self.G, self.P, x, y)
                    if any(np.dot(d, e) < 0.99 for d in ds): need.add(y)
            need |= self.blockers({x}, e, R, slide)
            for y in need:
                if y not in C:
                    C.add(y); todo.append(y)
                    if len(C) >= len(R): return None
        if not nx.is_connected(self.G.subgraph(C)): return None
        return C
    def hits_from(self, i, shift, e):
        key = (i, tuple(np.round(shift, 2)), tuple(np.round(e, 3)))
        if key in self.M.hits_cache: return self.M.hits_cache[key]
        pts = self.M.pts[i] + shift; L = float(np.abs(self.M.hi - self.M.lo).max()) + 40
        n = int(L / STEP) + 1; ss = np.arange(0, n + 1) * STEP
        Q = (pts[None, :, :] + ss[:, None, None] * e[None, None, :]).reshape(-1, 3)
        d, k = self.M.tree.query(Q, distance_upper_bound=THRESH, workers=2)
        ok = np.isfinite(d); out = set(int(x) for x in self.M.owner[k[ok]]) - {i}
        self.M.hits_cache[key] = out; return out
    def fine_hits(self, C, e, sl, R):
        """parts of R outside C met by the group C on its way out, with the dense real-mesh points (1.5 ldu) at 1 ldu steps ; the first 2 ldu of the path are ignored (the model has
        grazes of < 1 ldu between parts in contact : lifting the part takes it away)"""
        rest = [i for i in R if i not in C]
        if not rest: return set()
        pts = np.vstack([V.shell_world(self.P[i]) for i in rest]); own = np.concatenate([[i] * len(V.shell_world(self.P[i])) for i in rest]); tree = cKDTree(pts)
        mov = np.vstack([V.shell_world(self.P[i]) for i in C])
        L = float(np.abs(self.M.hi - self.M.lo).max()) + 40
        shifts = [e * s_ for s_ in np.arange(2.0, (LIFT if sl is not None else L) + 0.01, 1.0)]
        if sl is not None: shifts += [e * LIFT + sl * t for t in np.arange(1.0, L + 0.01, 1.0)]
        out = set()
        for sh in shifts:
            d, k = tree.query(mov + sh, distance_upper_bound=V.THR)
            ok = np.isfinite(d)
            if ok.any(): out |= set(int(x) for x in own[k[ok]])
        return out
    def refine(self, C, e, sl, R):
        """grow C with the parts the fine geometry says are in its way (their own closure included) until nothing is hit ; None if the group swallows R"""
        C = set(C)
        for _ in range(8):
            hit = self.fine_hits(C, e, sl, R) - C
            if not hit: return C
            for h in sorted(hit):
                if h in C: continue
                cl = self.closure(h, e, R, sl)
                if cl is None: return None
                C |= cl
                if len(C) >= len(R): return None
        return None
    def connected_without(self, R, C):
        rest = R - C
        if len(rest) <= 1: return True
        return nx.is_connected(self.G.subgraph(rest))
    def extract(self, R, prefer=None):
        """one extraction step. 1) a group bound by the stud rule alone, with nothing in its way (so it can leave now) : prefer a remainder that stays one connected assembly, then the
        earliest seed of `prefer` ; 2) only if no such group exists in any direction : a mutually blocking group, accepted only when it is one connected stud assembly.
        returns (C, e, slide, connected) or None"""
        order = sorted(R, key=prefer) if prefer else sorted(R)
        for slide_mode in ((False, True) if self.lift_slide else (False,)):
            best = None
            for e in self.dirs:
                for s in order:
                    sls = [None] if not slide_mode else [sl for sl in self.dirs if abs(np.dot(sl, e)) < 0.99]
                    for sl in sls:
                        C = self.bind_closure(s, e, R)
                        if C is None or self.blockers(C, e, R, sl): continue
                        conn_ok = self.connected_without(R, C)
                        if conn_ok and len(C) == 1: return (C, e, sl, True)          # one part, free to leave, the remainder stays connected
                        key = (not conn_ok, len(C))
                        if best is None or key < best[0]: best = (key, (C, e, sl, conn_ok))
            if best is not None: return best[1]
        # no group free to leave : mutually blocking groups
        best = None
        for e in self.dirs:
            for s in order:
                C = self.closure(s, e, R)
                if C is not None and (best is None or len(C) < len(best[0])): best = (C, e, None, self.connected_without(R, C))
            if best is not None: return best
        return None

def plan(seq, ids, depth=0, max_depth=4, prefer=None, log=None):
    """full sequencing of `ids`. returns (items, stuck) ; items = assembly order, each ('part', i, e, slide) or ('unit', [ids], e, slide, items_inside)
    where e is the EXTRACTION direction (the insertion motion is -e). stuck = parts that no translation (with optional lift-and-slide) can free."""
    R = set(ids); rev = []; stuck = []
    while R:
        if len(R) == 1:
            (i,) = R; rev.append(("part", i, None, None, True)); R = set(); break
        res = seq.extract(R, prefer)
        if res is None:
            stuck = sorted(R); break
        C, e, sl, cok = res
        if len(C) == 1: rev.append(("part", next(iter(C)), e, sl, cok))
        else: rev.append(("unit", sorted(C), e, sl, None, cok))
        R -= C
    items = []
    for it in reversed(rev):
        if it[0] == "unit":
            sub, st2 = plan(seq, it[1], depth + 1, max_depth, prefer, log) if depth < max_depth else ([("part", i, None, None, True) for i in it[1]], [])
            stuck += st2; items.append(("unit", it[1], it[2], it[3], sub, it[5]))
        else: items.append(it)
    return items, stuck
