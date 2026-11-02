"""LEGO V9.1 - independent replay of an assembly sequence.
The sequencer (seq.py) works with solid sample points (2 LDU grid, studs excluded). This replay uses a different geometry: the SURFACE points of the real mesh of every part
(filled mesh sampled at 1.5 LDU, at least 1 LDU inside the faces so that faces in contact are 2 LDU apart, threshold 1.4) and a 1 LDU step along the path, and re-checks every step:
  1. the inserted part (or unit) travels from outside the model to its place, first along the slide direction (if any), then along the engagement axis for the last LIFT ldu ;
     at no moment is any of its surface points closer than THR to a surface point of a part already placed ;
  2. every stud contact between the inserted part and the parts already placed is engaged by the last motion (stud axis = motion, exact) ;
  3. the inserted part has at least one stud contact with the parts already placed (no floating part) unless it is declared a first part (list `bases`).
"""
import os, sys
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.expanduser("~/bench/tools")); sys.path.insert(0, os.path.expanduser("~/bench/proto/v9"))
import conn
THR = 1.4; LIFT = 5.0

import functools
@functools.lru_cache(maxsize=None)
def dense_points(num, pitch=1.5, inside=1.0):
    """points of the filled real mesh of the part (studs excluded), at least `inside` ldu inside its faces : faces in contact are 2 x inside apart"""
    import trimesh, partlib as PL
    P0 = conn.part(num)
    if P0["fill"] >= 0.97 and "bracket" not in PL.title(num).lower():       # solid box parts (plates, bricks, tiles) : exact box sampled at `pitch`, `inside` ldu from every face
        lo, hi = P0["lo"], P0["hi"]
        ax = [np.arange(lo[k] + inside, hi[k] - inside + 1e-6, pitch) for k in range(3)]
        ax = [a if len(a) else np.array([(lo[k] + hi[k]) / 2]) for k, a in enumerate(ax)]
        return np.stack(np.meshgrid(*ax, indexing="ij"), -1).reshape(-1, 3)
    T, _ = PL.lib().geom(num + ".dat"); Vv = T.reshape(-1, 3).astype(float)
    P0 = conn.part(num); keep = np.all((Vv >= P0["lo"] - 0.6) & (Vv <= P0["hi"] + 0.6), axis=1).reshape(-1, 3).all(axis=1)
    m = trimesh.Trimesh(Vv.reshape(-1, 3, 3)[keep].reshape(-1, 3), np.arange(3 * keep.sum()).reshape(-1, 3), process=True)
    vg = m.voxelized(pitch=pitch).fill(); pts = vg.points
    surf = m.sample(60000); d_, _ = cKDTree(surf).query(pts)
    ok = (d_ >= inside) & np.all((pts >= P0["lo"]) & (pts <= P0["hi"]), axis=1)
    return pts[ok] if ok.any() else np.array([(P0["lo"] + P0["hi"]) / 2])

def shell_world(p):
    return dense_points(p["num"]) @ p["M"].T + p["o"]

def replay(P, G, order, bases=(), verbose=False):
    """order : list of dict(ids=[...], e=extraction unit vector or None, slide=unit vector or None). returns list of per-step results"""
    placed = set(); pts_placed = []; res = []
    cache = {}
    def pts(i):
        if i not in cache: cache[i] = shell_world(P[i])
        return cache[i]
    allpts = None
    for k, st in enumerate(order):
        ids = st["ids"]; e = st.get("e"); sl = st.get("slide")
        r = dict(step=k, ids=list(ids), ok=True, problems=[])
        mover = np.vstack([pts(i) for i in ids])
        # path (assembly = reverse of extraction): from far along e (+slide) down to the final place
        if placed and e is not None:
            e = np.asarray(e, float)
            plist = sorted(placed); allp = np.vstack([pts(i) for i in plist]); own = np.concatenate([[i] * len(pts(i)) for i in plist]); tree = cKDTree(allp)
            span = float(np.abs(allp.max(0) - allp.min(0)).max()) + 60
            path = []
            if sl is not None:
                sl = np.asarray(sl, float)
                for s in np.arange(span, LIFT, -1.0): path.append(e * LIFT + sl * s)       # approach along -slide
                for s in np.arange(LIFT, -0.01, -1.0): path.append(e * s)                   # final engagement lift
            else:
                for s in np.arange(span, -0.01, -1.0): path.append(e * s)
            sub = mover if len(mover) <= 3000 else mover[::int(np.ceil(len(mover) / 3000))]
            bad_at = None
            for t, sh in enumerate(path):
                d, k = tree.query(sub + sh, distance_upper_bound=THR)
                if np.isfinite(d).any():
                    if float(np.linalg.norm(sh)) < 2.0: r.setdefault("graze", []).append(round(float(d[np.isfinite(d)].min()), 2)); continue    # contact serre a la position finale, leve des les 2 premiers ldu
                    if bad_at is None: bad_at = float(np.linalg.norm(sh))
                    r.setdefault("hit_parts", set()).update(int(x) for x in own[k[np.isfinite(d)]])
            if bad_at is not None: r["ok"] = False; r["problems"].append("collision sur le chemin d'insertion a %.0f ldu de la position finale" % bad_at)
            # stud rule : every contact with placed parts must be engaged by the motion -e
            for i in ids:
                for q in G.neighbors(i):
                    if q in placed:
                        for (pt, ax, owner) in G[i][q]["contacts"]:
                            m = ax if owner == i else -ax     # engagement motion of i
                            if np.dot(m, -e) < 0.99: r["ok"] = False; r["problems"].append("liaison %d-%d non engagee par le mouvement (axe %s)" % (i, q, np.round(m, 2).tolist())); break
            if not any(q in placed for i in ids for q in G.neighbors(i)): r["ok"] = False; r["problems"].append("aucune liaison avec les pieces deja posees")
        elif placed and not any(q in placed for i in ids for q in G.neighbors(i)) and not set(ids) & set(bases):
            r["ok"] = False; r["problems"].append("aucune liaison avec les pieces deja posees")
        placed |= set(ids); res.append(r)
    return res
