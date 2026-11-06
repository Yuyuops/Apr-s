"""Generator 2 : 3D sculptures (engine 1 : GLB -> voxel volume -> bricks -> reinforcement -> notice). Reuses lego_run.py as is. A GLB that is a KNOWN subject (sha256 in data/known_subjects.json) uses its validated configuration ;
any other GLB gets a GENERIC configuration (no ears, automatic palette) and the manifest says the segmentation rules (biped/quadruped assumptions) were not validated for it."""
import json, shutil
from pathlib import Path
from .. import core
from ..paths import E1_SRC, PY, DATA, BR
from ..manifest import sha256
def pick_subject(glb, name, height_mm):
    known = json.load(open(DATA / "known_subjects.json")); h = sha256(glb)
    for k, v in known.items():
        if v["sha256"] == h: return E1_SRC / v["subject_config"], "known subject '%s' (validated configuration %s)" % (k, v["subject_config"]), True
    cfg = json.load(open(E1_SRC / "subjects" / "beagle.json")); cfg.update(name=name, description="GENERIC configuration derived from the Beagle one (no ears, automatic palette) : segmentation rules NOT validated for this subject", height_mm=height_mm)
    cfg["ears"] = {"enabled": False}; return cfg, "generic configuration (derived from beagle.json) : segmentation assumptions unvalidated for this GLB", False
def build(out, glb, name, height_mm=400, log=None, with_notice=False):
    out = Path(out); out.mkdir(parents=True, exist_ok=True); log = log or out / "build.log"; cfg, why, known = pick_subject(glb, name, height_mm)
    if isinstance(cfg, dict): p = out / "subject.json"; json.dump(cfg, open(p, "w"), indent=1); cfg = p
    run_dir = out / "run"
    if not list((run_dir / "final").glob("*_brut.ldr")): core.run([PY, E1_SRC / "engine" / "lego_run.py", "--glb", glb, "--subject", cfg, "--out", run_dir, "--height-mm", str(height_mm)], log=log)      # an existing complete run is reused (resume)
    sname = json.load(open(cfg))["name"]; fin = run_dir / "final"; brut = next(fin.glob("*_brut.ldr")); shutil.copy(brut, out / "diorama.ldr")
    cat = next(fin.glob("*_catalogue.csv")); n_ref, n_parts = core.parts_csv_from_catalogue(cat, out / "parts_list.csv"); bom = core.verify_catalogue(out)
    if with_notice: core.run([PY, E1_SRC / "engine" / "lego_run.py", "--glb", glb, "--subject", cfg, "--out", run_dir, "--height-mm", str(height_mm), "--from-stage", "notice", "--stop-after", "notice"], log=log)      # hierarchical assembly plan : SLOW (more than 20 minutes on Paco) -> opt-in
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
                notice_plan=str(plan.relative_to(out)) if plan else None, notice_files=sorted(p.name for p in nd.glob("*"))[:12] if nd.exists() else [], renders=sorted(p.name for p in rend.glob("*.png")), ldraw="diorama.ldr", bom="parts_list.csv", run_dir=str(run_dir))
