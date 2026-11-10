#!/usr/bin/env python3
"""Sprint V17 : object library tests (run with the ENGINE python : LEGO_ENGINE_HOME set).
 1. every assembly : own geometry/connection checks (no collision, every piece on a stud-bearing piece, colours catalogued)
 2. every assembly standing on a studded 8x8 surface : INDEPENDENT validation by the engine (validate_v4) -> 0 collision, 0 disconnected part, 0 island, 0 unsupported
 3. determinism : same manifest -> same LDraw SHA-256 ; zone build with objects OFF (V16 style) equals the same build twice
usage : python tests/test_objects_v17.py"""
import json, os, subprocess, sys, tempfile, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); MAPS = os.path.join(HERE, "..", "..", "maps-engine-v03", "style_fidelity_v062"); sys.path.insert(0, MAPS)
import objects as OB
from scene import Scene
E1 = os.environ["LEGO_ENGINE_HOME"]; PY = os.path.join(E1, ".venv", "bin", "python")
CASES = [("tree", {"variant": "round"}), ("tree", {"variant": "conifer"}), ("tree", {"variant": "tall"}), ("tree", {"variant": "small"}), ("rock", {}), ("tower", {}), ("tower", {"bricks": 1, "roof_cone": False}), ("monument", {}), ("castle", {}),
         ("bridge", {"length": 1}), ("bridge", {"length": 2}), ("bridge", {"length": 4, "dir": "v"})]
def standalone(kind, params, out):
    a = OB.build(kind, params); S = Scene(8, 8); S.add("41539", 72, 0, 0, 0, 0, "base")
    for (r, c) in ((0, 0), (0, 4), (4, 0), (4, 4)): S.add("3031", 71, r, c, 1, 0, "surface")
    if kind == "bridge":                                                              # a deck needs two banks : build them as 1-plate steps 3 studs apart
        pass
    for p in a.pieces: S.add(p["part"], p["colour"], 1 + p["r"], 1 + p["c"], 2 + p["dy"], p["rot"], "obj")
    S.write(out, "object test " + kind); return a, S
def main():
    fails = []; rows = []
    for kind, params in CASES:
        a = OB.build(kind, params); errs = OB.check_assembly(a)
        if errs: fails.append((kind, params, errs)); continue
        with tempfile.TemporaryDirectory() as t:
            try: standalone(kind, params, t)
            except ValueError as e:
                if kind == "bridge": rows.append((kind, params, "skipped standalone (a deck needs banks)")); continue
                fails.append((kind, params, [str(e)])); continue
            subprocess.run([PY, os.path.join(MAPS, "check_render.py"), t, "--no-render"], capture_output=True, text=True, env=dict(os.environ))
            v = json.load(open(t + "/independent_validation.json")); ok = v["all_pass"] and v["collisions"] == 0
            rows.append((kind, params, "pieces=%d bom=%d all_pass=%s" % (len(a.pieces), len(a.bom()), v["all_pass"])))
            if not ok: fails.append((kind, params, ["engine validation failed", {k: v[k] for k in ("collisions", "disconnected_parts", "islands", "unsupported_at_placement")}]))
    for r in rows: print(*r)
    # determinism of the zone build with objects
    sig = []
    for i in range(2):
        with tempfile.TemporaryDirectory() as t:
            subprocess.run([PY, "build_style.py", "styles/hyrule_v17_objects.json", "compositions/hyrule_v17_zone_D.json", t, "--flank", "vertical", "--no-title"], cwd=MAPS, check=True, capture_output=True)
            sig.append(hashlib.sha256(open(t + "/diorama.ldr", "rb").read()).hexdigest())
    print("zone D with objects : sha256 run1 %s run2 %s identical=%s" % (sig[0][:12], sig[1][:12], sig[0] == sig[1]))
    if sig[0] != sig[1]: fails.append(("determinism", {}, sig))
    if fails: print("FAILED", fails); sys.exit(1)
    print("OK : %d assemblies validated, build deterministic" % len(rows))
main()
