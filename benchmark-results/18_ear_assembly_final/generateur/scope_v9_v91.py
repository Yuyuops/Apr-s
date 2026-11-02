"""scope control V9 -> V9.1 : the only authorised zone is the two ears (tiles of the faces re-cut). usage: scope_v9_v91.py <A.ldr> <B.ldr> <out.json>"""
import sys, json
sys.path.insert(0, "/root/bench/proto/v9")
import numpy as np, scope
A_ = scope.read_parts(sys.argv[1]); B_ = scope.read_parts(sys.argv[2])
A = scope.voxelise(A_); B = scope.voxelise(B_)
zones = []
for sub in sorted({p["sub"] for p in A_ if p["sub"]}):
    cells = set()
    for i, p in enumerate(A_):
        if p["sub"] == sub:
            idx = np.argwhere(A["pid"] == i)
            for c in idx: cells.add(tuple(c))
    if cells: zones.append(scope.box_zone(sub, cells, margin=1))
r = scope.compare(A, B, zones)
r["zones"] = zones
json.dump(r, open(sys.argv[3], "w"), indent=1, default=str)
print({k: v for k, v in r.items() if k not in ("violations", "zones", "interieur_hors_zone")})
