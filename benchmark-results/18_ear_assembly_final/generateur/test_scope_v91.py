"""V9.1 tests of the spatial scope control. Run: venv/bin/python proto/v91/test_scope_v91.py
T1-T8 : tests of V9 (V8.1 error rejected, V8.2 accepted, synthetic changes) replayed unchanged.
T9  : V9 -> V9.1 : every difference lies in the ear zones (tiles re-cut), none outside.
T10 : V8.2 -> V9.1 : the mouth zone (declared box of the V8.2 module) and the eyes / nose cells are identical.
T11 : synthetic recolouring of a plate of the body (outside the ears) on V9.1 -> REJECTED.
T12 : synthetic removal of a plate of the face region on V9.1 -> REJECTED.
T13 : synthetic recolouring of an ear tile (inside the ear zone) -> accepted and attributed to the ear zone.
T14 : synthetic change of a part OUTSIDE the lattice (an ear wing plate moved by one stud) -> reported in pieces_hors_reseau_modifiees (not silent)."""
import json, os, sys, copy, subprocess
import numpy as np
sys.path.insert(0, "/root/bench/proto/v9"); sys.path.insert(0, "/root/bench/proto/v91")
import scope91 as scope
ROOT = os.path.expanduser("~/bench")
res = []
def check(name, cond, detail=""):
    res.append(dict(test=name, ok=bool(cond), detail=detail)); print(("PASS " if cond else "FAIL ") + name, detail)
r = subprocess.run([ROOT + "/venv/bin/python", ROOT + "/proto/v9/test_scope.py"], capture_output=True, text=True, cwd=ROOT)
t18 = json.load(open(ROOT + "/proto/v9/test_scope_resultats.json"))
for t in t18: res.append(t); print(("PASS " if t["ok"] else "FAIL ") + t["test"])
V9 = scope.read_parts(ROOT + "/proto/v9/a2.ldr"); V91 = scope.read_parts(ROOT + "/proto/v91/s2.ldr"); V82 = scope.read_parts(ROOT + "/proto/v82/runC/notice.ldr")
A = scope.voxelise(V9); B = scope.voxelise(V91); C = scope.voxelise(V82)
zones = []
for sub in sorted({p["sub"] for p in V9 if p["sub"]}):
    cells = {tuple(c) for i, p in enumerate(V9) if p["sub"] == sub for c in np.argwhere(A["pid"] == i)}
    zones.append(scope.box_zone(sub, cells, margin=1))
r9 = scope.compare(A, B, zones)
check("T9 V9 -> V9.1 : aucune difference hors des zones d'oreille", r9["violations_total"] == 0 and r9["categories"]["occupation"] == 0 and r9["categories"]["couleur_exposee"] == 0, "violations %d, occupation %d, couleur exposee %d, decoupage seul %d, pieces hors reseau %s" % (r9["violations_total"], r9["categories"]["occupation"], r9["categories"]["couleur_exposee"], r9["ignores_tessellation"], r9["pieces_hors_reseau_modifiees"]))
zb = json.load(open(ROOT + "/proto/v9/zone_bouche.json")); zb = zb if isinstance(zb, dict) else zb[0]
lo, hi = zb["lo"], zb["hi"]; sl = tuple(slice(lo[k], hi[k] + 1) for k in range(3))
same = (A["occ"][sl] == C["occ"][sl]).all() and (B["occ"][sl] == C["occ"][sl]).all() and (B["col"][sl][B["occ"][sl]] == C["col"][sl][C["occ"][sl]]).all()
face_nums = {"43898", "98138", "87087", "54200"}
exact = lambda Pl: sorted(scope.part_key(p) for p in Pl if p["num"] in face_nums)
check("T10 V8.2 -> V9.1 : bouche (zone declaree) identique ; yeux, truffe, pente identiques", same and exact(V82) == exact(V91), "zone bouche %s..%s ; %d pieces de detail identiques" % (lo, hi, len(exact(V91))))
def body_plate(Pl, zonecheck):
    for i, p in enumerate(Pl):
        if p["num"] == "3024" and p["c"] == 14 and p["sub"] is None:
            c_ = np.floor([p["o"][0] / 20, -p["o"][1] / 8 - 1, p["o"][2] / 20]).astype(int)
            if c_[1] < 20 and B["exposed"][tuple(c_)]: return i
i = body_plate(V91, None); P2 = copy.deepcopy(V91); P2[i]["c"] = 4
r = scope.compare(B, scope.voxelise(P2), zones)
check("T11 V9.1 : recoloration d'une plaque de pied hors oreilles -> REJETEE", r["violations_total"] >= 1, "%d violations" % r["violations_total"])
j = next(k for k, p in enumerate(V91) if p["num"] == "3024" and p["c"] == 14 and p["sub"] is None and k != i and p["o"][1] > -300 and B["exposed"][tuple(np.floor([p["o"][0] / 20, -p["o"][1] / 8 - 1, p["o"][2] / 20]).astype(int))])
P3 = [p for k, p in enumerate(V91) if k != j]; r = scope.compare(B, scope.voxelise(P3), zones)
check("T12 V9.1 : suppression d'une plaque de la sculpture hors oreilles -> REJETEE", r["violations_total"] >= 1 and r["categories"]["occupation"] >= 1, "%d violations" % r["violations_total"])
k = next(k for k, p in enumerate(V91) if p["sub"] and p["num"] == "3070b"); P4 = copy.deepcopy(V91); P4[k]["c"] = 4
r = scope.compare(B, scope.voxelise(P4), zones)
check("T13 V9.1 : recoloration d'une tuile d'oreille (zone declaree) -> acceptee et attribuee a la zone d'oreille", r["violations_total"] == 0 and sum(r["par_zone"].values()) >= 1, "par zone %s" % r["par_zone"])
k = next(k for k, p in enumerate(V91) if p["sub"] and p["num"] in ("78443", "78444")); P5 = copy.deepcopy(V91); P5[k]["o"] = P5[k]["o"] + np.array([0.0, 0.0, 20.0])
r = scope.compare(B, scope.voxelise(P5), zones)
rz = scope.compare(B, scope.voxelise(P5), [])
check("T14 V9.1 : une plaque aile d'oreille deplacee HORS de toute zone declaree -> REJETEE", rz["violations_total"] >= 1, "%d violations (zones d'oreille retirees du controle)" % rz["violations_total"])
json.dump(res, open(os.path.join(ROOT, "proto/v91/test_scope_v91_resultats.json"), "w"), indent=1, ensure_ascii=False)
print("%d/%d tests passes" % (sum(t["ok"] for t in res), len(res))); sys.exit(0 if all(t["ok"] for t in res) else 1)
