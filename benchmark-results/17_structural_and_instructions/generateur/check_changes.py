"""V9 - spatial control of one reinforcement run: zones declared from the run log (each group's region box, the base layer for R1), then scope.compare(before, after).
usage: check_changes.py <before.ldr> <after.ldr> <weak.json> <log.json> <out.json>"""
import json, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scope
before, after, weakf, logf, out = sys.argv[1:6]
Pb = scope.read_parts(before); log = json.load(open(logf)); weak = {g["id"]: g for g in json.load(open(weakf))["groupes"]}
zones = []
if log["r1"].get("retirees"):
    zones.append(dict(name="R1 plan d'appui (couche 0)", kind="module", lo=[0, 0, 0], hi=[39, 0, 39]))
for r in log["r2"]:
    if not r.get("cellules"): continue
    g = weak[r["groupe"]]; cells = []
    for i in g["parts_ids"]:
        st, rc, lo, hi = scope.conn.world(Pb[i]["num"], Pb[i]["M"], Pb[i]["o"])
        a = np.round([lo[0] / 20, -hi[1] / 8, lo[2] / 20]).astype(int); b = np.round([hi[0] / 20, -lo[1] / 8, hi[2] / 20]).astype(int)
        cells += [a, b - 1]
    cells += [np.array(c) for c in r["cellules"]]
    zones.append(scope.box_zone(f"R2 groupe {r['groupe']}", cells, margin=1))
A = scope.voxelise(Pb); B = scope.voxelise(scope.read_parts(after))
rep = scope.compare(A, B, zones)
rep["zones"] = zones
json.dump(rep, open(out, "w"), indent=1, default=str)
print({k: rep[k] for k in ("categories", "violations_total", "ignores_tessellation", "pieces_hors_reseau_modifiees")}, "par_zone", rep["par_zone"])
