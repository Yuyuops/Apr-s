"""before / after strength report for the ear-edge groups : usage strength_cmp.py <V9 dump> <V9 weak.json> <V9.1 dump> <out.json>   (same strength model, unchanged)"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import sys, json, pickle
import numpy as np
from collections import Counter
D0 = pickle.load(open(sys.argv[1], "rb")); W0 = json.load(open(sys.argv[2]))["groupes"]; D1 = pickle.load(open(sys.argv[3], "rb"))
key = lambda p: (p["num"], p["c"], tuple(np.round(p["o"], 2)), tuple(np.round(p["M"].ravel(), 4)) if "M" in p else None)
P0, P1 = D0["parts"], D1["parts"]
def k_(p): return (p["num"], p["c"], tuple(np.round((p["lo"] + p["hi"]) / 2, 1)))
idx1 = {k_(p): i for i, p in enumerate(P1)}
def ear_cases(D, P):
    ear = {i for i, p in enumerate(P) if p["sub"] and "oreille" in p["sub"].lower()}
    return [c for c in D["cases"] if c["mass_g"] >= 1.0 and c["tip_force_N"] is not None and len(set(c["_comp"]) & ear) >= 0.9 * len(c["_comp"])]
out = {}
for tag, D, P in (("V9", D0, P0), ("V91", D1, P1)):
    ec = ear_cases(D, P); f = [c["tip_force_N"] for c in ec]
    out["cas_oreilles_" + tag] = dict(cas=len(ec), sous_0_5N=sum(1 for v in f if v < 0.5), sous_2N=sum(1 for v in f if v < 2), force_min_N=min(f), masse_max_g=max(c["mass_g"] for c in ec))
rows = []
for g in W0:
    if not list(g["sous_ensemble"])[0].startswith("V7_oreille"): continue
    keys = [k_(P0[i]) for i in g["parts_ids"]]; mapped = [idx1[k] for k in keys if k in idx1]
    ear1 = [c for c in ear_cases(D1, P1) if len(set(c["_comp"]) & set(mapped)) >= max(1, len(mapped) // 2)]
    w = min(ear1, key=lambda c: c["tip_force_N"]) if ear1 else None
    rows.append(dict(groupe_V9=g["id"], pieces=g["parties"], masse_g=g["masse_g"], tenons_avant=g["tenons"], force_avant_N=g["force_N"], pieces_conservees=len(mapped), pieces_remplacees=len(keys) - len(mapped),
                     apres=None if w is None else dict(pieces=w["parts"], masse_g=w["mass_g"], tenons=w["studs"], force_N=w["tip_force_N"]), plus_aucun_cas_sous_0_5N_contenant_le_groupe=(w is None or w["tip_force_N"] >= 0.5)))
out["groupes"] = rows
json.dump(out, open(sys.argv[4], "w"), indent=1, ensure_ascii=False, default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
print(json.dumps(out, indent=1, ensure_ascii=False)[:2500])
