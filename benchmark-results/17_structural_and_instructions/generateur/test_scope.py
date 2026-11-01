"""V9 - tests of the spatial scope control (scope.py). Run: venv/bin/python proto/v9/test_scope.py
T1-T3 reproduce the V8.1 error: the mouth module of V8.1 recoloured cells over the whole body; the control must REJECT it and ACCEPT V8.2.
T4-T7 are synthetic: tessellation-only change is not a violation; a far recolouring, a far removal and a far finish change are."""
import json, os, pickle, sys, copy
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scope
ROOT = os.path.expanduser("~/bench")
res = []
def check(name, cond, detail=""):
    res.append(dict(test=name, ok=bool(cond), detail=detail)); print(("PASS " if cond else "FAIL ") + name, detail)

# the mouth module declares the zone of its cavity (cells of the 3D cavity component + 2 cells of margin): ix 12-27, iy 78-91, iz 10-28
ZONE = dict(name="bouche", kind="module", lo=[12, 78, 10], hi=[27, 91, 28])
b = pickle.load(open(f"{ROOT}/proto/v81/runB/lcm_B.pkl", "rb")); c = pickle.load(open(f"{ROOT}/proto/v82/runC/lcm_C.pkl", "rb"))
cells_b = scope.check_module_output(b["recolour"], b["carve"], [], ZONE); cells_c = scope.check_module_output(c["recolour"], c["carve"], [], ZONE)
check("T1 module V8.1 (lcm B) : modifications hors de sa zone -> REJETE", len(cells_b) > 0, f"{len(cells_b)} cellules hors zone sur {len(b['recolour']) + len(b['carve'])}")
check("T2 module V8.2 (lcm C) : toutes les modifications dans sa zone -> ACCEPTE", len(cells_c) == 0, f"{len(cells_c)} cellules hors zone sur {len(c['recolour']) + len(c['carve'])}")
A = scope.voxelise(scope.read_parts(f"{ROOT}/proto/v8/run/notice.ldr")); B1 = scope.voxelise(scope.read_parts(f"{ROOT}/proto/v81/runB/notice.ldr")); B2 = scope.voxelise(scope.read_parts(f"{ROOT}/proto/v82/runC/notice.ldr"))
r1 = scope.compare(A, B1, [ZONE]); r2 = scope.compare(A, B2, [ZONE])
check("T3a modele V8 -> V8.1 : modifications de surface hors zone -> REJETE", r1["violations_total"] > 0, f"{r1['violations_total']} violations (dont occupation : {sum(1 for v in r1['violations'] if v['type'] == 'occupation')} listees)")
# V8.2 : the mouth module itself is clean (T2); the whole-model diff still shows the drift of the volume engine (rebuilt from a modified grid): it is reported, not hidden
a = np.load(f"{ROOT}/proto/v8/run/corps_V8.npz")["grid"]; bb = np.load(f"{ROOT}/proto/v82/runC/corps_V82.npz")["grid"]
d = np.argwhere(a != bb); out_of_zone = [x for x in d if not all(ZONE["lo"][k] <= x[k] <= ZONE["hi"][k] for k in range(3))]
check("T3b entrees du moteur de volume V8 -> V8.2 : identiques hors zone", len(out_of_zone) == 0, f"{len(d)} cellules differentes, {len(out_of_zone)} hors zone")
check("T3c modele V8 -> V8.2 : la derive de reconstruction hors zone est DETECTEE (pas silencieuse) et attribuee au moteur (T3b)", r2["violations_total"] > 0 and len(out_of_zone) == 0, f"{r2['violations_total']} cellules de surface hors zone dans le modele construit, alors que les entrees du moteur sont identiques hors zone : derive du moteur, a ne pas confondre avec une erreur du module")
# synthetic modifications on the V8.2 model
P = scope.read_parts(f"{ROOT}/proto/v82/runC/notice.ldr")
def far_yellow_plate():
    for i, p in enumerate(P):
        if p["num"] == "3024" and p["c"] == 14 and p["sub"] is None:
            c_ = np.floor([p["o"][0] / 20, -p["o"][1] / 8 - 1, p["o"][2] / 20]).astype(int)
            if c_[1] < 20 and B2["exposed"][tuple(c_)]: return i
i = far_yellow_plate(); P2 = copy.deepcopy(P); P2[i]["c"] = 4
r = scope.compare(B2, scope.voxelise(P2), [ZONE])
check("T4 recoloration d'une plaque lointaine (pied/jambe) -> REJETEE", r["violations_total"] >= 1 and r["categories"]["couleur_exposee"] >= 1, f"{r['violations_total']} violations")
P3 = [p for k, p in enumerate(P) if k != i]
r = scope.compare(B2, scope.voxelise(P3), [ZONE])
check("T5 suppression d'une plaque lointaine -> REJETEE (occupation)", r["categories"]["occupation"] >= 1 and r["violations_total"] >= 1, f"{r['violations_total']} violations")
# tessellation only: replace two adjacent 1x1 plates of the same colour in the same row by one 1x2 plate
pair = None
for i, p in enumerate(P):
    if p["num"] != "3024" or p["sub"] is not None or not np.allclose(p["M"], np.eye(3)): continue
    for j, q in enumerate(P):
        if j > i and q["num"] == "3024" and q["sub"] is None and q["c"] == p["c"] and np.allclose(q["M"], np.eye(3)) and abs(q["o"][1] - p["o"][1]) < 1e-6 and abs(q["o"][2] - p["o"][2]) < 1e-6 and abs(q["o"][0] - p["o"][0] - 20) < 1e-6:
            pair = (i, j); break
    if pair: break
i, j = pair; P4 = [p for k, p in enumerate(P) if k not in (i, j)]
P4.append(dict(c=P[i]["c"], o=(P[i]["o"] + P[j]["o"]) / 2, M=np.eye(3), num="3023", sub=None))
r = scope.compare(B2, scope.voxelise(P4), [ZONE])
check("T6 changement de decoupage seul (deux 1x1 -> une 1x2, memes cellules, meme couleur) -> NON une violation", r["violations_total"] == 0 and r["categories"]["occupation"] == 0 and r["categories"]["couleur_exposee"] == 0 and r["ignores_tessellation"] > 0, f"{r['ignores_tessellation']} cellules de decoupage differentes, {r['violations_total']} violations")
inz = None
for k, p in enumerate(P):
    cc = np.floor([p["o"][0] / 20, -p["o"][1] / 8 - 1, p["o"][2] / 20]).astype(int)
    if p["sub"] is None and all(ZONE["lo"][t] <= cc[t] <= ZONE["hi"][t] for t in range(3)) and B2["exposed"][tuple(cc)] and p["c"] == 14: inz = k; break
P5 = copy.deepcopy(P); P5[inz]["c"] = 0
r = scope.compare(B2, scope.voxelise(P5), [ZONE])
check("T7 recoloration d'une plaque DANS la zone declaree -> acceptee et attribuee au module", r["violations_total"] == 0 and r["par_zone"].get("bouche", 0) >= 1, f"par zone {r['par_zone']}")
# V9: reinforcement of V8.2 leaves ears / eyes / nose parts identical (exact lines)
def exact(Pl): return sorted(scope.part_key(p) for p in Pl if p["sub"] is not None or p["num"] in ("43898", "98138", "87087", "54200"))
V9 = scope.read_parts(f"{ROOT}/proto/v9/a2.ldr")
check("T8 V8.2 -> V9 : oreilles, yeux, truffe, pente rouge identiques (pieces, positions, matrices)", exact(P) == exact(V9), f"{len(exact(P))} pieces")
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_scope_resultats.json"), "w"), indent=1, ensure_ascii=False)
print("%d/%d tests passes" % (sum(r["ok"] for r in res), len(res))); sys.exit(0 if all(r["ok"] for r in res) else 1)
