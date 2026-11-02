"""LEGO V9.1 - assembly plan of an ear sub-assembly (built apart, then attached): orientation on the table, order of every part, insertion motion, checks.

1. candidate orientations on the table (up vector): the stud axis of the core courses (upright) and the two normals of the faces (lying flat, outer face or inner face down);
2. for each orientation the generic sequencer (seq.py) is run with the extraction direction preferring "up" and the highest parts first: the assembly is the reverse (bottom up,
   each part pushed down onto what is placed whenever the joints allow it);
3. every partial assembly is judged on the table: its centre of gravity must be inside the convex hull of the footprint of its lowest parts ("stable") ; every insertion is
   classified from above / sideways / from below (relative to the table) ;
4. the orientation with the fewest unstable steps (then from-below, then sideways insertions) is kept ; the sequence is replayed with the independent geometry (verify_seq.py).
"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import os, sys, time
import numpy as np, networkx as nx
from scipy.spatial import ConvexHull
sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, ENGINE_DIR)
import seq as S, verify_seq as V, conn
G_PER_LDU3 = 0.10 / (20 * 20 * 8)

def mass(p):
    C = conn.part(p["num"]); return float(np.prod(C["hi"] - C["lo"])) * C["fill"] * G_PER_LDU3

def flatten(items, out=None):
    out = [] if out is None else out
    for x in items:
        if x[0] == "part": out.append(dict(ids=[x[1]], e=x[2], slide=x[3], conn=x[4]))
        else: out.append(dict(ids=list(x[1]), e=x[2], slide=x[3], conn=x[5], unit=x[4]))
    return out

def stable(P, placed, up, tol_ldu=1.0):
    """is the placed set stable when standing on the table with `up` upwards ? returns (bool, margin_ldu) ; margin = distance of the CoG projection to the hull edge (>0 inside)"""
    up = np.asarray(up, float); ids = list(placed)
    m = np.array([mass(P[i]) for i in ids]); ctr = np.array([(P[i]["lo"] + P[i]["hi"]) / 2 for i in ids])
    cog = (m[:, None] * ctr).sum(0) / m.sum()
    low = np.array([ (np.array([[x, y, z] for x in (P[i]["lo"][0], P[i]["hi"][0]) for y in (P[i]["lo"][1], P[i]["hi"][1]) for z in (P[i]["lo"][2], P[i]["hi"][2])]) @ up).min() for i in ids])
    base = low.min(); foot = [i for i, l in zip(ids, low) if l < base + 4.0]
    e1 = np.cross(up, [1, 0, 0]) if abs(up[0]) < 0.9 else np.cross(up, [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(up, e1)
    pts = []
    for i in foot:
        cs = np.array([[x, y, z] for x in (P[i]["lo"][0], P[i]["hi"][0]) for y in (P[i]["lo"][1], P[i]["hi"][1]) for z in (P[i]["lo"][2], P[i]["hi"][2])])
        pts += [(c @ e1, c @ e2) for c in cs]
    pts = np.array(pts); q = np.array([cog @ e1, cog @ e2])
    try: h = ConvexHull(pts)
    except Exception: return False, -1.0
    marg = min(-(eq[:2] @ q + eq[2]) for eq in h.equations)
    return bool(marg > 0), float(marg)

def sense(e, up):
    """insertion motion = -e ; relative to the table"""
    if e is None: return "premiere piece"
    d = -np.asarray(e, float); c = float(d @ up)
    return "par le dessus" if c < -0.9 else "par le dessous" if c > 0.9 else "de cote"

def evaluate(P, order, up):
    placed = set(); uns = 0; below = 0; side = 0; rows = []
    for st in order:
        placed |= set(st["ids"])
        ok, marg = stable(P, placed, up) if len(placed) > 1 else (True, 1.0)
        s = sense(st["e"], up)
        uns += (not ok); below += (s == "par le dessous"); side += (s == "de cote")
        rows.append(dict(ids=st["ids"], sens=s, stable=ok, marge_ldu=round(marg, 1)))
    return dict(instables=uns, par_dessous=below, de_cote=side, rows=rows)

def run_orientation(P, G, comp, up, extra_dirs, sq=None):
    up = np.asarray(up, float)
    dirs = [up] + [d for d in extra_dirs if not np.allclose(d, up, atol=0.03)]
    sq = sq or S.Sequencer(P, G, comp, dirs)
    h = lambda i: float(((P[i]["lo"] + P[i]["hi"]) / 2) @ up)
    items, stuck = S.plan(sq, comp, prefer=lambda i: -h(i))
    return items, stuck, sq

def repair(P, G, comp, up, dirs, sq, items, stuck, max_iter=6, log=None):
    """replay the plan with the independent fine geometry ; every step that collides on its path gets its blockers added to the sweep results of the coarse sequencer, then the
    plan is recomputed ; until the replay is clean (or max_iter)"""
    for it in range(max_iter):
        order = flatten(items); res = V.replay(P, G, [dict(ids=o["ids"], e=o["e"], slide=o["slide"]) for o in order], bases=[order[0]["ids"][0]] if order else [])
        bad = [(o, r) for o, r in zip(order, res) if not r["ok"] and r.get("hit_parts")]
        nb = [r for r in res if not r["ok"]]
        if log is not None: log.append(dict(iteration=it, pas_en_defaut=len(nb), avec_bloqueurs=len(bad)))
        if not nb: break
        if not bad: break
        for o, r in bad:
            if o["e"] is None: continue
            for i in o["ids"]: sq.add_extra(i, np.asarray(o["e"], float), r["hit_parts"] - set(o["ids"]))
        items, stuck = S.plan(sq, comp, prefer=lambda i: -float(((P[i]["lo"] + P[i]["hi"]) / 2) @ np.asarray(up, float)))
    return items, stuck

def ear_dirs(P, G, comp):
    axes = {}
    for u, v, d in G.subgraph(comp).edges(data=True):
        for (pt, a, o) in d["contacts"]: axes[tuple(np.round(a, 2))] = np.array(a)
    dirs = []
    for a in axes.values(): dirs += [a, -a]
    dirs += [np.array(v, float) for v in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1))]
    return dirs

def candidate_ups(P, G, comp):
    """table orientations : the stud axis of the core courses (upright, up = -Y) and the two normals of the faces (lying flat)"""
    ax = {}
    for u, v, d in G.subgraph(comp).edges(data=True):
        for (pt, a, o) in d["contacts"]: ax[tuple(np.round(a, 2))] = np.array(a, float)
    ups = [np.array([0, -1.0, 0])]
    for a in ax.values():
        if abs(a[1]) < 0.05 and not any(np.allclose(a, u, atol=0.03) for u in ups): ups.append(a)
    return ups

def up_name(up):
    if abs(up[1]) > 0.99: return "debout"
    return "a plat, face tournee vers %s" % ("l'exterieur" if up @ np.array([0.8, 0, -0.6]) > 0 else "l'interieur")

_G = {}
def _job(args):
    up, = args; P, G, comp, dirs = _G["P"], _G["G"], _G["comp"], _G["dirs"]
    t = time.time(); items, stuck, sq = run_orientation(P, G, comp, up, dirs)
    order = flatten(items); ev = evaluate(P, order, up)
    return dict(up=[float(x) for x in up], items=items, stuck=[int(i) for i in stuck], eval={k: v for k, v in ev.items() if k != "rows"}, rows=ev["rows"], secondes=round(time.time() - t))

def replay_items(P, G, items, base=None):
    """independent replay of a (nested) plan. returns (list of failed steps, dict part -> check)"""
    order = flatten(items); res = V.replay(P, G, [dict(ids=o["ids"], e=o["e"], slide=o["slide"]) for o in order], bases=[order[0]["ids"][0]] if order else [])
    bad = [r for r in res if not r["ok"]]; checks = {}
    for o, r in zip(order, res):
        for i in o["ids"]: checks[i] = dict(ok=r["ok"], reason="; ".join(r["problems"]), motion=None if o["e"] is None else [float(-v) for v in o["e"]])
        if "unit" in o:
            b2, c2 = replay_items(P, G, o["unit"]); bad += b2
            for i, c in c2.items(): checks[("in", i)] = c
    return bad, checks

def plan_ear(P, G, comp, workers=3, ups=None):
    import multiprocessing as mp
    comp = sorted(comp); dirs = ear_dirs(P, G, comp); ups = ups or candidate_ups(P, G, comp)
    _G.update(P=P, G=G, comp=comp, dirs=dirs)
    ctx = mp.get_context("fork")
    with ctx.Pool(min(workers, len(ups))) as pool: res = pool.map(_job, [(u,) for u in ups])
    for r in res: r["name"] = up_name(np.array(r["up"]))
    best = min(res, key=lambda r: (len(r["stuck"]), r["eval"]["instables"] * 10 + r["eval"]["par_dessous"] * 3 + r["eval"]["de_cote"]))
    # repair loop on the chosen orientation (the coarse sequencer is recomputed once more here, its sweeps are cheap compared with the first run)
    up = np.array(best["up"]); dirs_o = [up] + [d for d in dirs if not np.allclose(d, up, atol=0.03)]
    items, stuck, sq = run_orientation(P, G, comp, up, dirs)
    rlog = []; items, stuck = repair(P, G, comp, up, dirs, sq, items, stuck, log=rlog)
    ev = evaluate(P, flatten(items), up); best = dict(best, items=items, stuck=[int(i) for i in stuck], eval={k: v for k, v in ev.items() if k != "rows"}, rows=ev["rows"], reparation=rlog)
    bad, checks = replay_items(P, G, best["items"])
    return dict(best=best, all=[dict(name=r["name"], up=r["up"], stuck=r["stuck"], eval=r["eval"], secondes=r["secondes"]) for r in res], replay_problems=bad, checks=checks)
