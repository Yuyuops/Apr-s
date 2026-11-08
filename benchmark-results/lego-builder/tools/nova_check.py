#!/usr/bin/env python3
"""Independent validation of an LDraw model with LDraw Nova (AGPL-3.0, used as an EXTERNAL tool : it is not imported by the builder, only run here for comparison).
usage (inside a venv with ldraw-nova installed) : LDRAW_DIR=<library> python nova_check.py MODEL.ldr OUT.json
Runs : validate_file (syntax / structure diagnostics) then analyze_geometry (rectangular body overlaps, connected components, coverage). Reports counts per issue code and timings."""
import json, sys, time
from collections import Counter
from pathlib import Path
from ldraw_tools.common import get_parts
from ldraw_tools.validation import validate_file
from ldraw_tools.geometry import analyze_geometry
ldr, out = sys.argv[1:3]; t0 = time.time(); parts = get_parts(); t_idx = time.time() - t0
t = time.time(); model, diags = validate_file(ldr, parts, assembly=False, instance_limit=300000); t_val = time.time() - t
res = dict(file=ldr, diagnostics=dict(Counter((d["severity"], d["code"]) .__str__() for d in diags)), n_diagnostics=len(diags), validate_seconds=round(t_val, 1), index_seconds=round(t_idx, 1))
res["examples"] = [dict(code=d["code"], severity=d["severity"], message=d["message"][:140]) for d in diags[:6]]
if model is not None:
    t = time.time()
    try:
        g = analyze_geometry(model, parts, pair_limit=50, instance_limit=300000, contacts=__import__("os").environ.get("NOVA_CONTACTS", "none")); res["geometry_seconds"] = round(time.time() - t, 1)
        res["geometry_keys"] = list(g)[:20]
        probs = g.get("problems", []); res["geometry_problems"] = dict(Counter(p["code"] for p in probs)); res["geometry_problem_examples"] = [dict(code=p["code"], message=p["message"][:140]) for p in probs[:6]]
        for k in ("complete", "collision_method", "physical_validity", "connection_coverage", "occurrence_count", "contact_count", "contacts_checked", "confirmed_component_count", "optimistic_component_count", "overlap_candidate_count", "components", "summary", "overlap_count", "coverage"):
            if k in g: res[k] = g[k] if not isinstance(g[k], list) else dict(count=len(g[k]))
    except Exception as e: res["geometry_error"] = "%s: %s" % (type(e).__name__, str(e)[:300])
json.dump(res, open(out, "w"), indent=1, default=str); print(json.dumps({k: v for k, v in res.items() if k not in ("examples", "geometry_problem_examples")}, default=str)[:1500])
