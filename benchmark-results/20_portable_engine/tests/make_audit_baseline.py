"""Archive the audit of the historical references as the diagnostic baseline (refs/audit_baseline.json) + full audit reports in audit/ : python tests/make_audit_baseline.py"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "engine")); os.environ.setdefault("LEGO_ENGINE_HOME", os.path.normpath(os.path.join(HERE, "..")))
import hashlib
import audit_fidelity as A, tempfile
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
CFG = {s: json.load(open(os.path.join(HERE, "..", "subjects", s + "_fixed_v11.json"))) for s in ("paco", "beagle")}
INT = {s: os.path.join(HERE, "..", "refs", "intermediates", s) for s in CFG}; GLB = {s: os.path.join(REPO, CFG[s]["source_glb"].replace("benchmark-results/", "")) for s in CFG}
LDR = {"paco": os.path.join(REPO, "18_ear_assembly_final/modeles/paco_V91_brut.ldr"), "beagle": os.path.join(REPO, "19_full_second_subject/modeles/beagle_V10_brut.ldr")}
out = {}; os.makedirs(os.path.join(HERE, "..", "audit"), exist_ok=True)
for s in CFG:
    os.environ["LEGO_SHAPE"] = "40,130,40" if s == "paco" else "30,126,58"
    with tempfile.TemporaryDirectory() as td:
        ref = os.path.join(td, "ref.glb"); subprocess.run([sys.executable, os.path.join(HERE, "..", "engine", "ref_glb_fullframe.py"), GLB[s], os.path.join(INT[s], s + "_full400.npz"), ref], check=True, capture_output=True)
        r = A.audit(ref, LDR[s], os.path.join(INT[s], s + "_full400.npz"), os.path.join(INT[s], "segmentation.npz"), os.path.join(INT[s], "details.json"), CFG[s]["palette"]["exclude"])
        A.heatmaps(r, os.path.join(HERE, "..", "audit"), s); r.pop("_arrays"); json.dump(r, open(os.path.join(HERE, "..", "audit", "audit_%s_references_historiques.json" % s), "w"), indent=1, ensure_ascii=False)
    c = r["couleurs"]; out[s] = dict(cellules_exposees=c["cellules_exposees"], cellules_parasites=c["cellules_parasites"], cellules_sans_correspondance=c["cellules_sans_correspondance"], dE_moyen=c["dE_moyen"], iou_global=r["placement"]["iou_global"])
json.dump(out, open(os.path.join(HERE, "..", "refs", "audit_baseline.json"), "w"), indent=1); print(out)
