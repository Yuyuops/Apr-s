"""mass of an assembled LDraw model from its bill of materials, with the mass model of validate_v3 (box volume x fill x 0.10 g per 20x20x8 ldu cell) ; compares several models.
usage: mass_report.py <out.json> <label=model.ldr> ..."""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import sys, json
sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, ENGINE_DIR)
import numpy as np, conn, notice_plan as N
from collections import Counter
G3 = 0.10 / (20 * 20 * 8)
out = {}
for a in sys.argv[2:]:
    label, path = a.split("=", 1); P = N.parse(path); per = Counter(); n = Counter(); cells = 0.0; ear = 0.0
    for p in P:
        C = conn.part(p["num"]); v = float(np.prod(C["hi"] - C["lo"])); m = v * C["fill"] * G3
        per[(p["num"], p["c"])] += m; n[(p["num"], p["c"])] += 1; cells += v * C["fill"] / (20 * 20 * 8)
        if p["sub"]: ear += m
    out[label] = dict(pieces=len(P), types=len({k[0] for k in n}), masse_modele_g=round(sum(per.values()), 2), masse_oreilles_g=round(ear, 2), cellules_plein_equivalent=round(cells, 2),
                      par_reference={"%s/%d" % k: dict(qte=n[k], masse_g=round(v, 2)) for k, v in sorted(per.items(), key=lambda kv: -kv[1])})
    print(label, out[label]["pieces"], "pieces", out[label]["masse_modele_g"], "g (oreilles", out[label]["masse_oreilles_g"], "g)")
json.dump(out, open(sys.argv[1], "w"), indent=1)
