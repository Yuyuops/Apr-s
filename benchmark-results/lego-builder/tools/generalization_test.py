#!/usr/bin/env python3
"""C (Sprint V13) : reproducible protocol for an UNSEEN subject from four photos. It runs the one-command pipeline twice (same photos, two output folders), then measures :
  geometry      : occupancy IoU model vs GLB (engine-1 audit_fidelity), per zone
  colour        : mean Delta E (CIE76) against the GLB, palette floor, parasite cells, no-match share
  reproducibility : same photos -> same GLB ? same LDraw (SHA-256) ? (the HF Space may be non-deterministic : the result is REPORTED, not assumed)
  constructibility : independent validator (collisions, disconnected parts, islands, unsupported) + fragility report + reference/piece counts
  time          : wall clock of each run
  notice        : number of steps, pieces per step (min/median/max), PDF produced
Thresholds are declared BEFORE the run (below) and are not changed after seeing the results. A subject already known to the Builder (SHA of the photos / GLB fingerprint) is NOT a generalization proof : the script refuses to
call it one. usage : generalization_test.py OUT_DIR face.png dos.png profil_gauche.png profil_droit.png [--size-mm 400] [--runs 2] [--allow-known]"""
import hashlib, json, os, statistics, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
THRESHOLDS = dict(iou_global_min=0.75, dE_mean_max=20.0, parasite_share_max=0.05, collisions=0, disconnected=0, islands=0, unsupported=0, notice_steps_min=10, runs_identical_ldr="reported")
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def run_one(photos, out, size, env):
    t = time.time(); cmd = [sys.executable, "-m", "lego_builder", "run", "--photos", *photos, "--out", str(out), "--size-mm", str(size), "--notice", "fast", "--pdf"]
    p = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, env=env); return dict(seconds=round(time.time() - t, 1), returncode=p.returncode, log_tail=(p.stdout + p.stderr).splitlines()[-8:])
def measure(proj):
    proj = Path(proj); m = dict(); run = proj / "model" / "run"; ldr = proj / "model" / "diorama.ldr"
    if not ldr.exists(): return dict(error="no diorama.ldr")
    m["ldr_sha256"] = sha(ldr); parts = [l for l in open(ldr, errors="replace") if l.startswith("1 ")]; m["pieces"] = len(parts); m["references"] = len({(l.split()[14].lower(), l.split()[1]) for l in parts})
    g = next(iter((proj / "derived").glob("*couleur.glb")), None); m["glb_sha256"] = sha(g) if g else None
    py = os.environ.get("LEGO_ENGINE_HOME", "") + "/.venv/bin/python"; eng = Path(os.environ.get("LEGO_ENGINE_SRC", HERE.parent / "20_portable_engine"))
    if run.exists() and (eng / "engine" / "audit_fidelity.py").exists():
        out = proj / "audit"; r = subprocess.run([py, str(eng / "engine" / "audit_fidelity.py"), "--glb", str(run / "ref_full_frame.glb"), "--ldr", str(run / "final" / next(f.name for f in (run / "final").glob("*_brut.ldr"))), "--grid", str(run / "grid" / "full400.npz"),
                                                    "--seg", str(run / "seg" / "segmentation.npz"), "--details", str(run / "details.json"), "--exclude", "", "--run", str(run), "--out", str(out), "--tag", "unseen"], capture_output=True, text=True)
        a = next(iter(out.glob("audit_*.json")), None)
        if a: d = json.load(open(a)); c = d["couleurs"]; m["dE_mean"] = c["dE_moyen"]; m["dE_floor_engine"] = c["plancher_palette_moteur_moyen"]; m["parasite_cells"] = c.get("cellules_parasites"); m["audit_raw_keys"] = list(d)[:6]; m["iou_global"] = d.get("placement", {}).get("iou_global", d.get("iou_global"))
    for f in ("independent_validation.json", "model/independent_validation.json"):
        q = proj / f
        if q.exists(): v = json.load(open(q)); m["validator"] = {k: v.get(k) for k in ("all_pass", "collisions", "disconnected_parts", "islands", "unsupported_at_placement")}; break
    fr = proj / "model" / "fragility.json"
    if fr.exists(): d = json.load(open(fr)); m["fragility"] = {k: d.get(k) for k in ("parts_hanging_by_one_stud", "one_stud_and_carrying", "articulation_points_with_loss")}
    ns = sorted((proj / "model").rglob("*notice*.ldr")); m["notice_files"] = [str(n.relative_to(proj)) for n in ns][:3]
    if ns:
        steps = sum(1 for l in open(ns[0], errors="replace") if l.strip() == "0 STEP"); m["notice_steps"] = steps
    m["pdf"] = [str(p.relative_to(proj)) for p in proj.rglob("*.pdf")][:3]; return m
def main():
    a = sys.argv[1:]; out = Path(a[0]); photos = [str(Path(x).resolve()) for x in a[1:5]]; size = float(a[a.index("--size-mm") + 1]) if "--size-mm" in a else 400; n = int(a[a.index("--runs") + 1]) if "--runs" in a else 2
    hashes = {sha(p) for p in photos}; hist = {sha(f) for f in (HERE.parent / "01_inputs_prepared").rglob("*") if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg")}      # historical photos (Paco, Beagle)
    is_known = bool(hashes & hist); out.mkdir(parents=True, exist_ok=True)
    if is_known and "--allow-known" not in a: print("REFUSED : at least one photo is already known to the Builder (historical subject) : this would not prove generalization. Use --allow-known only for a smoke test."); sys.exit(2)
    env = dict(os.environ); res = dict(thresholds=THRESHOLDS, photos=photos, photos_sha256=sorted(hashes), known_subject=is_known, runs=[])
    for i in range(n):
        d = out / ("run%d" % (i + 1)); r = run_one(photos, d, size, env); r["measures"] = measure(d) if r["returncode"] == 0 else {}; res["runs"].append(r)
    for r in res["runs"]:
        try: r["declared_known_subject"] = json.load(open(out / ("run%d" % (res["runs"].index(r) + 1)) / "manifest.json"))["parameters"].get("subject")
        except Exception: r["declared_known_subject"] = None
    ms = [r["measures"] for r in res["runs"] if r["measures"]]
    if len(ms) >= 2: res["reproducibility"] = dict(same_glb=len({m.get("glb_sha256") for m in ms}) == 1, same_ldr=len({m["ldr_sha256"] for m in ms}) == 1, pieces=[m["pieces"] for m in ms], seconds=[r["seconds"] for r in res["runs"]])
    if ms:
        m = ms[0]; v = m.get("validator") or {}; checks = {"validator_pass": bool(v.get("all_pass")), "iou": (m.get("iou_global") or 0) >= THRESHOLDS["iou_global_min"], "dE": (m.get("dE_mean") or 99) <= THRESHOLDS["dE_mean_max"], "notice_steps": (m.get("notice_steps") or 0) >= THRESHOLDS["notice_steps_min"]}
        res["checks"] = checks; res["result"] = "PASS" if all(checks.values()) else "FAIL"
    else: res["result"] = "BLOCKED (no successful run)"
    json.dump(res, open(out / "generalization_result.json", "w"), indent=1); print(json.dumps({k: res.get(k) for k in ("known_subject", "reproducibility", "checks", "result")}))
if __name__ == "__main__":
    main()
