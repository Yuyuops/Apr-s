"""LEGO V9.1 - the parts that must be pushed in FROM BELOW (flag "suspendue" in the plan): where they are, what holds the model while they are pushed, whether the model tips.
For every such part, at the moment it is inserted :
  * the placed set of its module (main line, or the sub-assembly being built apart) must stand on the table : centre of gravity inside the hull of its lowest parts ;
  * the insertion force is F = (number of studs engaged) x 1 N (same assumed clutch as the strength model, used here as the force to overcome) applied upwards at the part ;
    for every edge of the support hull the overturning moment F x (distance of the part outside the edge) is compared with the restoring moment W x (distance of the CoG inside the edge)
    -> safety factor ; < 1 : the model must be held by a hand while the part is pushed ;
  * the free height under the part (distance to the table) tells whether a finger can reach it.
usage: suspended_analysis.py <model.ldr> <plan.json> <segmentation.npz> <out.json>"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import sys, json, os
import numpy as np
from collections import Counter, defaultdict
from scipy.spatial import ConvexHull
sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, ENGINE_DIR)
import notice_plan as N, ear_plan as E, conn
model, planf, segf, outf = sys.argv[1:5]
P = N.parse(model); D = json.load(open(planf)); plan = D["plan"]
s = np.load(segf); lab = s["labels"]; names = {int(k): v for k, v in json.loads(str(s["names"])).items()}
def zone(i):
    c = np.floor([(P[i]["lo"][0] + P[i]["hi"][0]) / 40, -(P[i]["lo"][1] + P[i]["hi"][1]) / 16, (P[i]["lo"][2] + P[i]["hi"][2]) / 40]).astype(int)
    c = np.clip(c, 0, np.array(lab.shape) - 1); v = int(lab[tuple(c)])
    return names.get(v, "hors segmentation") if v > 0 else "hors segmentation"
mass = {p["i"]: E.mass(p) for p in P}
up = np.array([0, -1.0, 0]); e1 = np.array([1.0, 0, 0]); e2 = np.cross(up, e1)
def hull_of(placed):
    ids = list(placed)
    low = np.array([P[i]["hi"][1] for i in ids]); base = low.max()                 # LDraw +Y is down : the lowest part has the largest y
    foot = [i for i, l in zip(ids, low) if l > base - 4.0]
    pts = []
    for i in foot:
        for x in (P[i]["lo"][0], P[i]["hi"][0]):
            for z in (P[i]["lo"][2], P[i]["hi"][2]): pts.append((x, z))
    try: return ConvexHull(np.array(pts)), base
    except Exception: return None, base
def tip_sf(placed, part, F_N):
    hull, base = hull_of(placed)
    if hull is None: return None, None, None
    ids = list(placed); m = np.array([mass[i] for i in ids]); ctr = np.array([(P[i]["lo"][[0, 2]] + P[i]["hi"][[0, 2]]) / 2 for i in ids]); cog = (m[:, None] * ctr).sum(0) / m.sum()
    W = m.sum() / 1000 * 9.81; pc = (P[part]["lo"][[0, 2]] + P[part]["hi"][[0, 2]]) / 2
    sf = np.inf; marg = np.inf
    for eq in hull.equations:
        inside_cog = -(eq[:2] @ cog + eq[2]) * 0.4            # mm inside the edge
        out_part = (eq[:2] @ pc + eq[2]) * 0.4                 # mm outside the edge (>0 : beyond)
        marg = min(marg, inside_cog)
        if out_part > 0 and F_N > 0: sf = min(sf, W * inside_cog / (F_N * out_part)) if inside_cog > 0 else 0.0
    return (None if np.isinf(sf) else float(sf)), float(marg), float(W)
rows = []; placed_main = set(); mods = defaultdict(set)
for st in plan:
    top = st["module"].split(" > ")[0]
    for j, i in enumerate(st["parts"]):
        ch = st["checks"][j] if j < len(st["checks"]) and st["kind"] != "attach" else {}
        if st["kind"] == "attach": continue
        S = placed_main if st["kind"] == "main" else mods[top]
        flag = ch.get("flag")
        if flag == "suspendue":
            ns = sum(len(N.G_cache[(i, q)]) for q in []) if False else None
            F = float(max(ch.get("joints", 1), 1))
            sf, marg, W = tip_sf(S | {i} if S else {i}, i, F) if S else (None, None, None)
            free_h = -P[i]["hi"][1] * 0.4          # LDraw y is negative upwards: height of the underside above the table (mm)
            rows.append(dict(etape=plan.index(st) + 1, module=top, piece=i, ref=P[i]["num"], zone=zone(i), masse_placee_g=round(sum(mass[k] for k in S), 1), force_insertion_N=F, marge_cdg_mm=None if marg is None else round(marg, 1),
                             coeff_securite_basculement=None if sf is None else round(sf, 1), a_tenir=(sf is not None and sf < 1.0) or (marg is not None and marg <= 0), hauteur_libre_sous_la_piece_mm=round(free_h, 1)))
        S.add(i)
    if st["kind"] == "attach": placed_main |= set(st["parts"])
r = dict(total=len(rows), par_module=dict(Counter(x["module"] for x in rows)), par_zone=dict(Counter(x["zone"] for x in rows)), a_tenir=sum(1 for x in rows if x["a_tenir"]),
         sf_min=min([x["coeff_securite_basculement"] for x in rows if x["coeff_securite_basculement"] is not None], default=None),
         marge_cdg_min_mm=min([x["marge_cdg_mm"] for x in rows if x["marge_cdg_mm"] is not None], default=None), lignes=rows)
json.dump(r, open(outf, "w"), indent=1, ensure_ascii=False)
print({k: v for k, v in r.items() if k != "lignes"})
