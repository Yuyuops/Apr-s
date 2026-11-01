"""V9 - cumulative spatial control V8.2 -> V9 : the zones declared by every reinforcement pass (from its log and its weak-group file), then scope.compare."""
import json, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scope
base, final, out = sys.argv[1:4]; passes = sys.argv[4:]          # passes: before.ldr:weak.json:log.json ...
zones = []
for ps in passes:
    before, weakf, logf = ps.split(":"); Pb = scope.read_parts(before); log = json.load(open(logf)); weak = {g["id"]: g for g in json.load(open(weakf))["groupes"]}
    if log["r1"] and log["r1"].get("retirees"): zones.append(dict(name="R1 plan d'appui (couche 0)", kind="module", lo=[0, 0, 0], hi=[39, 0, 39]))
    for r in log["r2"]:
        if r.get("decision") != "applique": continue
        g = weak[r["groupe"]]; cells = []
        for i in g["parts_ids"]:
            st, rc, lo, hi = scope.conn.world(Pb[i]["num"], Pb[i]["M"], Pb[i]["o"])
            cells += [np.round([lo[0] / 20, -hi[1] / 8, lo[2] / 20]).astype(int), np.round([hi[0] / 20, -lo[1] / 8, hi[2] / 20]).astype(int) - 1]
        cells += [np.array(c) for c in r["cellules"]]
        zones.append(scope.box_zone(f"R2 {os.path.basename(os.path.dirname(logf))} groupe {r['groupe']}", cells, margin=1))
A = scope.voxelise(scope.read_parts(base)); B = scope.voxelise(scope.read_parts(final))
rep = scope.compare(A, B, zones); rep["zones"] = zones
json.dump(rep, open(out, "w"), indent=1, default=str)
print({k: rep[k] for k in ("categories", "violations_total", "ignores_tessellation", "pieces_hors_reseau_modifiees", "interieur_hors_zone_total") if k in rep})
