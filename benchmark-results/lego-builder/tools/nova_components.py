#!/usr/bin/env python3
"""LDraw Nova connectivity cross-check : optimistic and confirmed contact components of a model, with the isolated parts listed (part, colour, position). Run inside a venv with ldraw-nova.
usage : LDRAW_DIR=<library> python nova_components.py MODEL.ldr OUT.json"""
import json, sys, time
from collections import Counter
from ldraw_tools.common import get_parts
from ldraw_tools.validation import validate_file
from ldraw_tools.geometry import analyze_geometry
ldr, out = sys.argv[1:3]; parts = get_parts(); model, _ = validate_file(ldr, parts, assembly=False, instance_limit=400000); t = time.time()
g = analyze_geometry(model, parts, pair_limit=50, instance_limit=400000, contacts="all"); occ = list(model.iter_occurrences(include_steps=True))
def desc(i): o = occ[i]; return dict(index=i, part=o.part_code, colour=getattr(o.colour, "code", None), position=[round(float(v)) for v in (o.position.x, o.position.y, o.position.z)])
res = dict(file=ldr, seconds=round(time.time() - t, 1), occurrences=len(occ), contacts=g.get("contact_count"), problems=dict(Counter(p["code"] for p in g.get("problems", []))))
for kind in ("confirmed", "optimistic"):
    comps = g.get(kind + "_components") or []; sizes = sorted((len(c) for c in comps), reverse=True)
    res[kind] = dict(count=g.get(kind + "_component_count"), largest=sizes[:5], singletons=sum(1 for s in sizes if s == 1), small_under_10=sum(1 for s in sizes if s < 10))
    res[kind]["small_components"] = [[desc(i) for i in c[:6]] for c in comps if len(c) < 10][:12]
json.dump(res, open(out, "w"), indent=1, default=str); print(json.dumps({k: (v if k != "optimistic" and k != "confirmed" else {kk: vv for kk, vv in v.items() if kk != "small_components"}) for k, v in res.items()}))
