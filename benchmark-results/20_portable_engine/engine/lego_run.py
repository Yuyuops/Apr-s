"""LEGO engine 1 : standard command, from a GLB to a validated LDraw model.

    python engine/lego_run.py --glb <source.glb> --out <folder> [--height-mm 400] [--subject subjects/beagle.json] [--palette-exclude 4,1,...] [--stop-after STAGE]

Stages (each one is an existing validated script, run as a subprocess ; nothing is re-implemented here) :
  input     validation of the GLB (vertex colours or texture)
  grid      fullgrid.py     : voxelisation, colours, fine grid                       (V7)
  segment   segment.py      : zones by rules on the grid                              (V7)
  frame     ref_glb_fullframe.py : the GLB in the render frame of the LDraw model     (V7)
  ears      integrate.py    : ear modules + fixation  [only if the subject config has ears]  (V6.1 / V7)
  details   detect.py + microdetails.py : eyes / nose / mouth details                 (V8)
  assemble  assemble_v82.py : body volume + details + mouth module                    (V8.2)
  validate  reorder_notice.py + validate_v4.py + weak_groups.py                       (V9)
  reinforce reinforce.py x passes (+ validation between passes)                       (V9)
  stitch    stitch.py       : ear seam stitching [only with ears]                     (V9.1)
  final     reorder + validation of the final model + scope control
The run folder receives every intermediate file and `ctx.json` (the files of the run) ; `manifest.json` lists the output files with sha256.
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _paths import ROOT, LDRAW, RB_DB, ENGINE_DIR
STAGES = ["input", "palette", "grid", "segment", "frame", "ears", "details", "assemble", "validate", "reinforce", "stitch", "repair", "final"]

def sh(cmd, env=None, log=None, cwd=None):
    e = dict(os.environ); e.update(env or {})
    t = time.time(); r = subprocess.run(cmd, env=e, cwd=cwd, capture_output=True, text=True)
    if log:
        with open(log, "a") as f: f.write("$ %s\n%s%s\n" % (" ".join(map(str, cmd)), r.stdout, r.stderr))
    if r.returncode != 0:
        sys.stderr.write("STAGE FAILED : %s\n%s\n%s\n" % (" ".join(map(str, cmd)), r.stdout[-1500:], r.stderr[-2500:])); raise SystemExit(2)
    return r.stdout

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--glb", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--subject", help="subject config JSON (palette, passes, ears...) ; defaults are used if absent")
    ap.add_argument("--height-mm", type=float); ap.add_argument("--palette-exclude", help="comma separated LDraw colour codes to exclude")
    ap.add_argument("--stop-after", choices=STAGES, default="final"); ap.add_argument("--from-stage", choices=STAGES, default="input", help="resume : stages before this one are skipped (their files must exist in --out)")
    a = ap.parse_args()
    cfg = json.load(open(a.subject)) if a.subject else {}
    name = cfg.get("name", "subject"); height = a.height_mm or cfg.get("height_mm", 400)
    pal_cfg = cfg.get("palette", {"mode": "fixed", "exclude": cfg.get("palette_exclude", [])})
    excl = a.palette_exclude or ",".join(str(c) for c in pal_cfg.get("exclude", []))
    if not excl and pal_cfg.get("mode") != "auto": sys.exit("no palette : give --palette-exclude, a fixed palette in the subject config, or palette.mode = auto (selection from the GLB)")
    out = os.path.abspath(a.out); os.makedirs(out, exist_ok=True); log = os.path.join(out, "run.log"); py = sys.executable
    E = lambda f: os.path.join(ENGINE_DIR, f)
    for p, what in ((LDRAW, "LDraw library"), (RB_DB, "Rebrickable database")):
        if not os.path.exists(p): sys.exit("missing dependency : %s (%s). Run scripts/fetch_deps.sh" % (what, p))
    ctx = dict(source_glb=os.path.abspath(a.glb), full_npz=os.path.join(out, "grid", "full400.npz"), seg_npz=os.path.join(out, "seg", "segmentation.npz"),
               ref_full_frame=os.path.join(out, "ref_full_frame.glb"))
    json.dump(ctx, open(os.path.join(out, "ctx.json"), "w"), indent=1)
    env = {"LEGO_CTX": os.path.join(out, "ctx.json"), "LEGO_TARGETS": os.path.join(out, "targets"), "GLB_REF": ctx["ref_full_frame"], "LDRAW": LDRAW}
    ears = cfg.get("ears", {}).get("enabled", False)
    if ears: env["LEGO_EAR_FRAME"] = os.path.join(ROOT, cfg["ears"]["frame_json"])
    shutil.copytree(os.path.join(ENGINE_DIR, "targets"), env["LEGO_TARGETS"], dirs_exist_ok=True)
    done = lambda s: STAGES.index(a.from_stage) <= STAGES.index(s) <= STAGES.index(a.stop_after)
    t0 = time.time(); steps = []
    def stage(s, f):
        if done(s): t = time.time(); f(); steps.append((s, round(time.time() - t, 1))); print("stage %-9s %6.1fs" % (s, steps[-1][1]), flush=True)
    # ---- input
    def s_input():
        import glb_io
        rep = glb_io.validate(a.glb); json.dump(rep, open(os.path.join(out, "input_report.json"), "w"), indent=1); json.dump(rep, sys.stdout); print()
    def s_palette():
        nonlocal excl
        if pal_cfg.get("mode") != "auto" or a.palette_exclude: return
        pj = os.path.join(out, "palette.json")
        sh([py, E("palette_select.py"), a.glb, pj, "--required", ",".join(map(str, pal_cfg.get("required", []))), "--forbidden", ",".join(map(str, pal_cfg.get("forbidden", []))), "--max-colours", str(pal_cfg.get("max_colours", 8))], env, log)
        rep = json.load(open(pj)); excl = ",".join(str(c) for c in rep["exclude"]); print("  palette :", [c["nom"] for c in rep["choisies"]])
    # ---- grid
    def s_grid():
        nonlocal excl
        if pal_cfg.get("mode") == "auto" and not a.palette_exclude and os.path.exists(os.path.join(out, "palette.json")): excl = ",".join(str(c) for c in json.load(open(os.path.join(out, "palette.json")))["exclude"])
        os.makedirs(os.path.join(out, "grid"), exist_ok=True)
        cmd = [py, E("fullgrid.py"), a.glb, ctx["full_npz"], "--height-mm", str(height), "--neck", str(cfg.get("neck", "auto")), "--exclude", excl, "--palette-passes", str(cfg.get("palette_passes", 4))]
        if cfg.get("mirror_x", True): cmd.append("--mirror-x")
        sh(cmd, env, log)
    def s_segment():
        os.makedirs(os.path.join(out, "seg"), exist_ok=True)
        sh([py, E("segment.py"), ctx["full_npz"], os.path.join(out, "seg", "segmentation.json"), ctx["seg_npz"]], env, log)
    def s_frame():
        sh([py, E("ref_glb_fullframe.py"), a.glb, ctx["full_npz"], ctx["ref_full_frame"]], env, log)
    run7 = os.path.join(out, "run7")
    def s_ears():
        os.makedirs(run7, exist_ok=True)
        if ears: sh([py, E("integrate.py"), run7], env, log)
        else:
            import numpy as np, pickle
            d = dict(np.load(ctx["full_npz"])); s = np.load(ctx["seg_npz"]); lab = s["labels"]; names = {int(k): v for k, v in json.loads(str(s["names"])).items()}; idx = {v: k for k, v in names.items()}
            d["protect"] = np.isin(lab, [idx[n] for n in ("yeux", "bouche", "truffe") if n in idx]); d["head_in_full"] = np.array([0, int(d["neck"]), 0])
            np.savez_compressed(os.path.join(run7, "full_sans_oreilles.npz"), **d)
            pickle.dump(dict(ears={}, npz2=os.path.join(run7, "full_sans_oreilles.npz"), delta=[0.0, 0.0, 0.0], prep={}, R=np.eye(3).tolist(), lower_shift_ldu=0), open(os.path.join(run7, "ears.pkl"), "wb"))
    md = os.path.join(out, "md")
    def s_details():
        os.makedirs(md, exist_ok=True)
        sh([py, E("detect.py"), ctx["ref_full_frame"], ctx["full_npz"], ctx["seg_npz"], os.path.join(out, "seg", "segmentation.json"), os.path.join(out, "details.json")], env, log)
        sh([py, E("microdetails.py"), os.path.join(out, "details.json"), run7, md], dict(env, MD_SKIP_MOUTH="1"), log)
    v82 = os.path.join(out, "v82")
    def s_assemble():
        os.makedirs(v82, exist_ok=True)
        sh([py, E("assemble_v82.py"), run7, os.path.join(md, "microdetails.pkl"), v82, os.path.join(out, "details.json"), cfg.get("mouth_module", "C")], env, log)
    shape = None
    def shape_env():
        import numpy as np
        g = cfg.get("grid_shape", "auto")
        return {"LEGO_SHAPE": ",".join(map(str, np.load(ctx["full_npz"])["grid"].shape)) if g == "auto" else g}
    def validate(ldr, tag, outdir, reorder):
        e = dict(env, **shape_env()); os.makedirs(outdir, exist_ok=True)
        src = ldr
        if reorder:
            src = os.path.join(outdir, tag + "_notice.ldr"); sh([py, E("reorder_notice.py"), ldr, src], dict(e, DROP_UNATTACHED="1"), log)
        sh([py, E("validate_v4.py"), "--ldr", src, "--ldraw", LDRAW, "--rbdb", RB_DB, "--out", outdir, "--name", tag, "--dump", os.path.join(outdir, tag + "_dump.pkl")], e, log)
        sh([py, E("weak_groups.py"), os.path.join(outdir, tag + "_dump.pkl"), ctx["seg_npz"], os.path.join(outdir, tag + "_weak.json")], e, log)
        return src
    def s_validate(): validate(os.path.join(v82, "paco_V82.ldr"), "v82", v82, True)
    rf = os.path.join(out, "reinforce"); last = {}
    def s_reinforce():
        os.makedirs(rf, exist_ok=True); e = dict(env, **shape_env())
        cur, weak = os.path.join(v82, "v82_notice.ldr"), os.path.join(v82, "v82_weak.json")
        for k, p in enumerate(cfg.get("reinforce_passes", [{"per_layer": 1, "skip_r1": 0}, {"per_layer": 1, "skip_r1": 1}])):
            nxt = os.path.join(rf, "pass%d.ldr" % (k + 1)); log_j = os.path.join(rf, "pass%d_log.json" % (k + 1))
            sh([py, E("reinforce.py"), cur, weak, nxt, log_j, str(p["per_layer"]), str(p["skip_r1"])], e, log)
            validate(nxt, "pass%d" % (k + 1), rf, False); last.update(ldr=nxt, weak=os.path.join(rf, "pass%d_weak.json" % (k + 1)))
            cur, weak = nxt, last["weak"]
        json.dump(last, open(os.path.join(rf, "last.json"), "w"))
    def s_stitch():
        if not (ears and cfg.get("ear_stitch")): return
        l = json.load(open(os.path.join(rf, "last.json"))); out_ldr = os.path.join(rf, "stitched.ldr")
        sh([py, E("stitch.py"), l["ldr"], l["weak"], out_ldr, os.path.join(rf, "stitch_log.json"), "3"], dict(env, **shape_env()), log); l["ldr"] = out_ldr; json.dump(l, open(os.path.join(rf, "last.json"), "w"))
    def s_repair():
        if not cfg.get("colour_repair", False): return
        l = json.load(open(os.path.join(rf, "last.json"))); out_ldr = os.path.join(rf, "repaired.ldr")
        sh([py, E("colour_repair.py"), "--ldr", l["ldr"], "--glb", ctx["ref_full_frame"], "--grid", ctx["full_npz"], "--out", out_ldr, "--report", os.path.join(out, "colour_repair.json")], dict(env, **shape_env()), log)
        l["ldr_avant_reparation"] = l["ldr"]; l["ldr"] = out_ldr; json.dump(l, open(os.path.join(rf, "last.json"), "w"))
    def s_final():
        l = json.load(open(os.path.join(rf, "last.json"))); fin = os.path.join(out, "final"); os.makedirs(fin, exist_ok=True)
        shutil.copy(l["ldr"], os.path.join(fin, "%s_brut.ldr" % name))
        src = validate(l["ldr"], name, fin, True)
        sh([py, E("final_scope.py"), os.path.join(v82, "v82_notice.ldr"), src, os.path.join(fin, "scope.json")] + [os.path.join(v82, "v82_notice.ldr") + ":" + os.path.join(v82, "v82_weak.json") + ":" + os.path.join(rf, "pass1_log.json")]
           + ([os.path.join(rf, "pass1.ldr") + ":" + os.path.join(rf, "pass1_weak.json") + ":" + os.path.join(rf, "pass2_log.json")] if len(cfg.get("reinforce_passes", [0, 0])) > 1 else []), dict(env, **shape_env()), log)
    for s, f in (("input", s_input), ("palette", s_palette), ("grid", s_grid), ("segment", s_segment), ("frame", s_frame), ("ears", s_ears), ("details", s_details), ("assemble", s_assemble), ("validate", s_validate), ("reinforce", s_reinforce), ("stitch", s_stitch), ("repair", s_repair), ("final", s_final)):
        stage(s, f)
    man = {}
    for dp, dn, fn in os.walk(out):
        for f in sorted(fn):
            if f.endswith((".ldr", ".npz", ".glb", ".json")) and "pkl" not in f: man[os.path.relpath(os.path.join(dp, f), out)] = sha(os.path.join(dp, f))
    json.dump(dict(subject=name, glb=os.path.basename(a.glb), height_mm=height, stages=steps, seconds=round(time.time() - t0, 1), files=man), open(os.path.join(out, "manifest.json"), "w"), indent=1)
    print("done in %.0fs ; %d files in manifest.json" % (time.time() - t0, len(man)))

if __name__ == "__main__":
    main()
