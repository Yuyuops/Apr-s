#!/usr/bin/env python3
"""BLOCKING non-regression check : every generated model is compared with its reference sha256 (ci/reference_hashes.json). Exit code 1 on any mismatch, missing model or missing reference.
usage : check_regression.py maps OUTROOT                      (LDraw of each map model : OUTROOT/<name>/diorama.ldr)
        check_regression.py sculpture NAME LDR REFKEY          (one sculpture model against ci/reference_hashes.json -> sculptures -> REFKEY)
        check_regression.py glb                                (the committed GLB inputs : a changed input is a regression too)"""
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; REF = json.load(open(HERE / "ci" / "reference_hashes.json")); BR = HERE.parent
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
def main():
    mode = sys.argv[1]; bad = []
    if mode == "maps":
        root = Path(sys.argv[2])
        for k, ref in REF["maps"].items():
            p = root / k / "diorama.ldr"
            if not p.exists(): bad.append("%s : model missing" % k); continue
            got = sha(p); print("%-20s %s %s" % (k, "IDENTICAL" if got == ref else "DIFFERS", got[:12])); 
            if got != ref: bad.append("%s : sha256 %s != reference %s" % (k, got[:12], ref[:12]))
    elif mode == "sculpture":
        name, ldr, key = sys.argv[2:5]; ref = REF["sculptures"][key]["sha256"]; got = sha(ldr); print("%s %s %s" % (name, "IDENTICAL" if got == ref else "DIFFERS", got[:12]))
        if got != ref: bad.append("%s : sha256 %s != reference %s (%s)" % (name, got[:12], ref[:12], key))
    elif mode == "glb":
        for k, ref in REF["glb"].items():
            got = sha(BR / "02_glb_gratuit_hunyuan2mv" / k); print("%s %s" % (k, "IDENTICAL" if got == ref else "DIFFERS (Git LFS pointer ? a changed file ?)"))
            if got != ref: bad.append("%s input changed or is an LFS pointer" % k)
    if bad: print("REGRESSION :", *bad, sep="\n  "); sys.exit(1)
    print("no regression")
main()
