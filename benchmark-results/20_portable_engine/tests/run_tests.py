"""Portable tests of the engine (from a fresh clone, after scripts/install.sh) : python tests/run_tests.py [--skip-slow]
 T1  no absolute / developer path in the engine sources
 T2  the historical references are intact (sha256 of refs/references.json)
 T3  the GLB inputs are read DIRECTLY (vertex colours) : the grids of Paco and Beagle equal the archived intermediates
 T4  the input validation refuses a GLB without colours
 T5  audit of the historical Paco V9.1 and Beagle V10 models = archived baseline (colour and placement defects are found again after regeneration)
 T6  the audit detects a colour defect injected on purpose (parasite cells)
 T7  the audit detects a placement defect injected on purpose (ear moved)
"""
import hashlib, json, os, re, subprocess, sys, tempfile, shutil
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ENG = os.path.join(HERE, "..", "engine"); REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ENG)
os.environ.setdefault("LEGO_ENGINE_HOME", os.path.normpath(os.path.join(HERE, "..")))
res = []
def check(name, ok, detail=""):
    res.append(dict(test=name, ok=bool(ok), detail=detail)); print(("PASS " if ok else "FAIL ") + name, detail, flush=True)
SLOW = "--skip-slow" not in sys.argv
CFG = {s: json.load(open(os.path.join(HERE, "..", "subjects", s + ".json"))) for s in ("paco", "beagle")}
INT = {s: os.path.join(HERE, "..", "refs", "intermediates", s) for s in ("paco", "beagle")}
GLB = {s: os.path.join(REPO, CFG[s]["source_glb"].replace("benchmark-results/", "")) for s in CFG}
# T1
bad = []
for f in sorted(os.listdir(ENG)):
    if f.endswith((".py", ".js", ".sh")):
        for n, l in enumerate(open(os.path.join(ENG, f), errors="replace"), 1):
            if re.search(r"~/bench|/root/|/home/user|expanduser\(\"~", l) and not l.lstrip().startswith("#") and "re.search" not in l: bad.append("%s:%d" % (f, n))
check("T1 aucun chemin absolu ni dossier de developpeur dans le moteur", not bad, ", ".join(bad[:5]))
# T2
refs = json.load(open(os.path.join(HERE, "..", "refs", "references.json"))); nb = 0; badref = []
for k, d in refs.items():
    for f, v in d.items():
        if v is None: badref.append(f); continue
        h = hashlib.sha256(open(os.path.join(REPO, f), "rb").read()).hexdigest(); nb += 1
        if h != v["sha256"]: badref.append(f)
check("T2 references historiques intactes (empreintes)", not badref, "%d fichiers verifies ; ecarts : %s" % (nb, badref[:3]))
# T3
if SLOW:
    for s in ("paco", "beagle"):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "g.npz"); c = CFG[s]
            cmd = [sys.executable, os.path.join(ENG, "fullgrid.py"), GLB[s], out, "--height-mm", str(c["height_mm"]), "--neck", "auto", "--exclude", ",".join(map(str, c["palette_exclude"])), "--palette-passes", str(c["palette_passes"]), "--mirror-x"]
            r = subprocess.run(cmd, capture_output=True, text=True); a = np.load(out) if os.path.exists(out) else None
            ref = np.load(os.path.join(INT[s], s + "_full400.npz")); ok = a is not None and all(np.array_equal(a[k], ref[k]) for k in ("grid", "surface", "fine"))
            check("T3 %s : GLB a couleurs par sommets lu directement = grille archivee" % s, ok, "" if ok else r.stderr[-300:])
# T4
import glb_io, trimesh
with tempfile.TemporaryDirectory() as td:
    m = trimesh.creation.box(); p = os.path.join(td, "plain.glb"); m.export(p)
    try: glb_io.validate(p); ok = False
    except glb_io.InputError: ok = True
    check("T4 la validation d'entree refuse un GLB sans couleurs", ok)
# T5-T7 : audit
import audit_fidelity as A
def run_audit(s, ldr, tmp):
    ref = os.path.join(tmp, "ref_full_frame_%s.glb" % s)
    if not os.path.exists(ref): subprocess.run([sys.executable, os.path.join(ENG, "ref_glb_fullframe.py"), GLB[s], os.path.join(INT[s], s + "_full400.npz"), ref], check=True, capture_output=True)
    return A.audit(ref, ldr, os.path.join(INT[s], s + "_full400.npz"), os.path.join(INT[s], "segmentation.npz"), os.path.join(INT[s], "details.json"), CFG[s]["palette_exclude"])
LDR = {"paco": os.path.join(REPO, "18_ear_assembly_final/modeles/paco_V91_brut.ldr"), "beagle": os.path.join(REPO, "19_full_second_subject/modeles/beagle_V10_brut.ldr")}
KEYS = ("cellules_exposees", "cellules_parasites", "cellules_sans_correspondance")
if SLOW:
    base = json.load(open(os.path.join(HERE, "..", "refs", "audit_baseline.json"))); cache = {}
    with tempfile.TemporaryDirectory() as td:
        for s in ("paco", "beagle"):
            os.environ["LEGO_SHAPE"] = "40,130,40" if s == "paco" else "30,126,58"
            r = run_audit(s, LDR[s], td); cache[s] = r; c = r["couleurs"]
            now = dict(cellules_exposees=c["cellules_exposees"], cellules_parasites=c["cellules_parasites"], cellules_sans_correspondance=c["cellules_sans_correspondance"], dE_moyen=c["dE_moyen"], iou_global=r["placement"]["iou_global"])
            ok = all(abs(now[k] - base[s][k]) <= max(1e-6, 0.01 * abs(base[s][k])) for k in now)
            check("T5 audit %s = baseline archivee (defauts retrouves)" % s, ok, json.dumps(now))
        # T6 : inject parasites on Beagle
        os.environ["LEGO_SHAPE"] = "30,126,58"; import scope
        P = scope.read_parts(LDR["beagle"]); V = scope.voxelise(P); lines = open(LDR["beagle"]).read().split("\n")
        part_line = [i for i, l in enumerate(lines) if l.startswith("1 ")]; exposed_pid = sorted({int(p) for p in V["pid"][V["exposed"] & V["occ"]] if p >= 0 and P[int(p)]["c"] == 484 and P[int(p)]["num"] in ("3024", "3023")})[:80]
        for pidx in exposed_pid[:60]:
            t = lines[part_line[pidx]].split(); t[1] = "1"; lines[part_line[pidx]] = " ".join(t)       # Dark Orange -> Blue
        mod = os.path.join(td, "beagle_inject.ldr"); open(mod, "w").write("\n".join(lines))
        r2 = run_audit("beagle", mod, td); gain = r2["couleurs"]["cellules_parasites"] - cache["beagle"]["couleurs"]["cellules_parasites"]
        check("T6 l'audit detecte des briques de couleur parasite injectees (60 plaques Dark Orange -> bleu)", gain >= 40, "+%d cellules parasites" % gain)
        # T7 : move the upper ear of Paco by 4 studs
        os.environ["LEGO_SHAPE"] = "40,130,40"; lines = open(LDR["paco"]).read().split("\n"); inside = False
        for i, l in enumerate(lines):
            if l.startswith("0 BRICKIFY SUBASSEMBLY BEGIN V7_oreille_haute"): inside = True
            elif l.startswith("0 BRICKIFY SUBASSEMBLY END"): inside = False
            elif inside and l.startswith("1 "): t = l.split(); t[2] = "%g" % (float(t[2]) + 80); lines[i] = " ".join(t)
        mod = os.path.join(td, "paco_ear_moved.ldr"); open(mod, "w").write("\n".join(lines)); r3 = run_audit("paco", mod, td)
        e0 = cache["paco"]["placement"]["oreilles"]["V7_oreille_haute"]["ecart_centre_mm"]; e1 = r3["placement"]["oreilles"]["V7_oreille_haute"]["ecart_centre_mm"]
        check("T7 l'audit detecte une oreille deplacee (80 ldu = 32 mm)", e1 - e0 >= 15, "ecart du centre %.1f -> %.1f mm" % (e0, e1))
json.dump(res, open(os.path.join(HERE, "resultats_tests.json"), "w"), indent=1, ensure_ascii=False)
print("%d/%d tests reussis" % (sum(r["ok"] for r in res), len(res))); sys.exit(0 if all(r["ok"] for r in res) else 1)
