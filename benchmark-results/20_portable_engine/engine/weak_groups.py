"""V9 - diagnosis of the fragile sub-assemblies of a model (all cases dumped by validate_v4, no change of the stability model).
A case is fragile when its mass is >= 1 g and its indicative tip force < 0.5 N (same criterion as validate_v3). Nested cases are merged into groups (a case contained
in another one belongs to the larger group's chain; the group is represented by its weakest case)."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import json, pickle, sys, os
import numpy as np
from collections import Counter, defaultdict
dump, seg, out = sys.argv[1:4]
D = pickle.load(open(dump, "rb")); P = D["parts"]; cases = D["cases"]
s = np.load(seg); lab = s["labels"]; names = {int(k): v for k, v in json.loads(str(s["names"])).items()}
weak = [c for c in cases if c["mass_g"] >= 1.0 and c["tip_force_N"] is not None and c["tip_force_N"] < 0.5]
# deduplicate identical part sets, then chains
uniq = {}
for c in weak:
    k = tuple(c["_comp"]); 
    if k not in uniq or c["tip_force_N"] < uniq[k]["tip_force_N"]: uniq[k] = c
items = sorted(uniq.items(), key=lambda kv: len(kv[0]))
groups = []
for k, c in items:
    S = set(k); placed = False
    for g in groups:
        if S <= set(g["maxset"]) or set(g["maxset"]) <= S:   # nested: same location chain
            g["members"].append(c); 
            if len(S) > len(g["maxset"]): g["maxset"] = k
            if c["tip_force_N"] < g["weakest"]["tip_force_N"]: g["weakest"] = c
            placed = True; break
    if not placed: groups.append(dict(maxset=k, members=[c], weakest=c))
def zone_of(lo, hi):
    ctr = (np.array(lo) + np.array(hi)) / 2; cell = np.floor([ctr[0] / 20, -ctr[1] / 8, ctr[2] / 20]).astype(int)
    best = None
    pts = np.argwhere(lab > 0)
    lo_c = np.floor([lo[0] / 20, -hi[1] / 8, lo[2] / 20]).astype(int); hi_c = np.floor([hi[0] / 20, -lo[1] / 8, hi[2] / 20]).astype(int)
    cnt = Counter()
    sub = lab[max(lo_c[0], 0):hi_c[0] + 1, max(lo_c[1], 0):hi_c[1] + 1, max(lo_c[2], 0):hi_c[2] + 1]
    for v in sub.ravel():
        if v > 0: cnt[names[int(v)]] += 1
    return cnt.most_common(2) if cnt else [("hors segmentation", 0)]
rows = []
for gi, g in enumerate(groups):
    w = g["weakest"]; ids = list(g["maxset"]); sub = Counter(P[i]["sub"] or "corps" for i in ids)
    lo = np.min([P[i]["lo"] for i in ids], 0); hi = np.max([P[i]["hi"] for i in ids], 0)
    mass = sum(P[i]["mass"] for i in ids)
    rows.append(dict(id=gi + 1, parties=len(ids), masse_g=round(mass, 1), tenons=w["studs"], force_N=w["tip_force_N"], cas_emboites=len(g["members"]), couleurs=w["colours"], sous_ensemble=dict(sub),
                     bbox_ldu=[np.round(lo).tolist(), np.round(hi).tolist()], zone=zone_of(lo, hi), centre_mm=np.round((lo + hi) / 2 * 0.4 * np.array([1, -1, -1]), 0).tolist(), parts_ids=ids,
                     types=dict(Counter(P[i]["num"] for i in ids).most_common(4))))
rows.sort(key=lambda r: r["force_N"])
json.dump(dict(cas_faibles=len(weak), cas_distincts=len(uniq), groupes=rows), open(out, "w"), indent=1, ensure_ascii=False, default=str)
print("cas faibles", len(weak), "distincts", len(uniq), "groupes", len(rows))
for r in rows: print(r["id"], r["parties"], "p", r["masse_g"], "g", r["tenons"], "tenons", r["force_N"], "N", r["zone"][:2], r["sous_ensemble"], r["couleurs"], "centre", r["centre_mm"])
