#!/usr/bin/env python3
"""Independent checks + real LDraw renders for a diorama folder (diorama.ldr + parts.json + parts_list.csv).
usage: check_render.py FOLDER [--zooms]  (needs LEGO_ENGINE_HOME pointing at an engine-1 folder with .deps and node_modules)"""
import csv, json, sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))
from maps_engine import validate as V, render as R
root = Path(sys.argv[1]); zooms = None
if "--zooms" in sys.argv: zooms = json.load(open(root / "zooms.json"))
(root / "validation").mkdir(exist_ok=True)
parts = json.loads((root / "parts.json").read_text())
out = V.engine1(str(root / "diorama.ldr"), str(root / "validation"), "map")
res = {k: out[k] for k in ("parts", "disconnected_parts", "islands", "unsupported_at_placement", "blocked_studs")}
res["collisions"] = out["collisions"]["pairs"]
cnt = sum(int(r["quantity"]) for r in csv.DictReader(open(root / "parts_list.csv")))
res["bom_count"] = cnt; res["ldraw_count"] = sum(l.startswith("1 ") for l in (root / "diorama.ldr").read_text().splitlines()); res["source_parts"] = len(parts); res["physical_test"] = False
ok = out["parts"] == len(parts) == cnt == res["ldraw_count"] and not (res["collisions"] or res["disconnected_parts"] or res["islands"] or res["unsupported_at_placement"] or res["blocked_studs"])
res["all_pass"] = bool(ok)
(root / "independent_validation.json").write_text(json.dumps(res, indent=2, default=str)); print(json.dumps(res, default=str))
m = json.load(open(root / "metrics.json")); N = max(m["size_studs"]); 
views, _ = R.render_all(str(root / "diorama.ldr"), str(root / "renders"), N=N, height_plates=m.get("height_plates", 21), w=1350, zooms=zooms)
print(views); sys.exit(0 if ok else 1)
