"""Generator 2 : 3D sculptures (engine 1 : GLB -> voxel volume -> bricks -> reinforcement -> notice). Reuses lego_run.py as is. A GLB that is a KNOWN subject (sha256 in data/known_subjects.json) uses its validated configuration ;
any other GLB gets a GENERIC configuration (no ears, automatic palette) and the manifest says the segmentation rules (biped/quadruped assumptions) were not validated for it."""
import json, shutil, time
from pathlib import Path
from .. import core
from ..paths import E1_SRC, PY, DATA, BR
from ..manifest import sha256
def pick_subject(glb, name, height_mm, subject=None):
    known = json.load(open(DATA / "known_subjects.json")); h = sha256(glb)
    if subject:
        if subject in known: return E1_SRC / known[subject]["subject_config"], "explicit subject '%s' (validated configuration %s) applied to THIS geometry" % (subject, known[subject]["subject_config"]), False
        return Path(subject), "explicit configuration file %s" % subject, False
    for k, v in known.items():
        if v["sha256"] == h: return E1_SRC / v["subject_config"], "known subject '%s' (validated configuration %s)" % (k, v["subject_config"]), True
    cfg = json.load(open(E1_SRC / "subjects" / "beagle.json")); cfg.update(name=name, description="GENERIC configuration derived from the Beagle one (no ears, automatic palette) : segmentation rules NOT validated for this subject", height_mm=height_mm)
    cfg["ears"] = {"enabled": False}; return cfg, "generic configuration (derived from beagle.json) : segmentation assumptions unvalidated for this GLB", False
def build(out, glb, name, height_mm=400, log=None, with_notice=False, subject=None, notice_timeout=900):
    out = Path(out); out.mkdir(parents=True, exist_ok=True); log = log or out / "build.log"; cfg, why, known = pick_subject(glb, name, height_mm, subject)
    if isinstance(cfg, dict): p = out / "subject.json"; json.dump(cfg, open(p, "w"), indent=1); cfg = p
    run_dir = out / "run"
    if not list((run_dir / "final").glob("*_brut.ldr")): core.run([PY, E1_SRC / "engine" / "lego_run.py", "--glb", glb, "--subject", cfg, "--out", run_dir, "--height-mm", str(height_mm)], log=log)      # an existing complete run is reused (resume)
    sname = json.load(open(cfg))["name"]; fin = run_dir / "final"; brut = next(fin.glob("*_brut.ldr")); shutil.copy(brut, out / "diorama.ldr")
    cat = next(fin.glob("*_catalogue.csv")); n_ref, n_parts = core.parts_csv_from_catalogue(cat, out / "parts_list.csv"); bom = core.verify_catalogue(out)
    notice = dict(mode=with_notice or "off")
    if with_notice in ("fast", "full", True):
        # FAST plan : same stages, but WITHOUT the ear sub-assembly search (`run_ears_v91.py --all` is the step that takes more than 20 minutes) ; FULL plan : with the ears, under a hard timeout.
        mode = "full" if with_notice == "full" else "fast"; cfg_n = cfg; extra = ["--notice-ears", "all" if mode == "full" else "sub"]      # fast : ear sequences only for the tagged ear sub-assemblies
        t0 = time.time()
        try:
            core.run([PY, E1_SRC / "engine" / "lego_run.py", "--glb", glb, "--subject", cfg_n, "--out", run_dir, "--height-mm", str(height_mm), "--from-stage", "notice", "--stop-after", "notice"] + extra, log=log, timeout=notice_timeout)
            notice.update(mode=mode, status="ok", seconds=round(time.time() - t0, 1))
            if mode == "fast": notice["note"] = "fast plan : ear sequences planned for the tagged ear sub-assemblies only (not for the whole model)"
        except TimeoutError as e: notice.update(mode=mode, status="timeout", seconds=notice_timeout, note="notice stage killed after %ss ; the ordered-steps file (final/*_notice.ldr, STEP lines) is the fallback" % notice_timeout)
        except Exception as e: notice.update(mode=mode, status="failed", note=str(e)[:300])
    rc = out / "renders_tmp"; core.run([PY, E1_SRC / "engine" / "render_compare.py", out / "diorama.ldr", run_dir / "ref_full_frame.glb", rc], log=log)
    rend = out / "renders"; rend.mkdir(exist_ok=True)
    for n in ("1_face", "2_dos", "3_profil_gauche", "5_trois_quarts", "6_dessus"):
        for k in ("r_lego", "r_ref"):
            f = next((rc / k).glob(n + "*.png"), None)
            if f: shutil.copy(f, rend / ("%s_%s.png" % ("lego" if k == "r_lego" else "reference_glb", n)))
    shutil.rmtree(rc, ignore_errors=True)
    val = json.load(open(next(fin.glob("*_validation_v2.json")))); weak = json.load(open(next(fin.glob("*_weak.json")))); nd = run_dir / "notice"; plan = next(nd.glob("*_plan.json"), None) if nd.exists() else None
    return dict(pieces=n_parts, references=n_ref, subject_config=why, known_subject=known, catalogue_check=dict(all_dat_exist=bom["all_dat_exist"], all_colours_valid=bom["all_colours_valid"], pairs_not_catalogued=bom["pairs_not_catalogued"]),
                validation=dict(collisions=val.get("collisions"), blocked_studs=val.get("blocked_studs"), single_stud_joints=val.get("single_stud_joints"), weak_cases=weak.get("cas_faibles"), weak_distinct_groups=weak.get("cas_distincts")),
                notice=notice, ordered_steps_ldr=str(next(fin.glob("*_notice.ldr")).relative_to(out)) if list(fin.glob("*_notice.ldr")) else None, notice_plan=str(plan.relative_to(out)) if plan else None, notice_files=sorted(p.name for p in nd.glob("*"))[:12] if nd.exists() else [], renders=sorted(p.name for p in rend.glob("*.png")), ldraw="diorama.ldr", bom="parts_list.csv", run_dir=str(run_dir))
