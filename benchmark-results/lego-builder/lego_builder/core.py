"""LEGO Core facade : the shared services, called on a model folder, whatever the generator. It does not re-implement anything : it drives the existing validated scripts
(engine-1 validator validate_v4, ldr_expand, three.js renderers, Rebrickable/LDraw catalogue checks, fragility graph). Validation STRATEGIES differ per family (see strategies())."""
import csv, json, os, subprocess, sys
from pathlib import Path
from .paths import MAPS, E1_SRC, PY, env
def run(cmd, cwd=None, log=None, check=True, timeout=None, extra_env=None):
    """Runs a command in its own process group ; on timeout the WHOLE group is killed (worker processes included) and TimeoutError is raised : no stage can block a run for ever."""
    import signal
    e_ = env(); e_.update(extra_env or {}); p = subprocess.Popen([str(c) for c in cmd], cwd=cwd, env=e_, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    try: out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL); out, err = p.communicate()
        if log: open(log, "a").write("$ %s\nTIMEOUT after %ss (process group killed)\n" % (" ".join(map(str, cmd)), timeout))
        raise TimeoutError("timeout after %ss : %s" % (timeout, " ".join(map(str, cmd))[:200]))
    r = subprocess.CompletedProcess(p.args, p.returncode, out, err)
    if log:
        with open(log, "a") as f: f.write("$ %s\n%s%s\n" % (" ".join(map(str, cmd)), r.stdout, r.stderr))
    if check and r.returncode != 0: raise RuntimeError("command failed (%d): %s\n%s" % (r.returncode, " ".join(map(str, cmd)), (r.stdout + r.stderr)[-1800:]))
    return r
def strategies():
    """What each family is checked for, and what is NOT claimed. A single generic validator must not pretend to cover every mechanical constraint."""
    return {
     "map_relief_25d": dict(support="board fixed in a frame, base plates fitted on the seams", checks=["engine-1 joint graph : 0 collision, 0 disconnected part, 0 island, 0 unsupported part at placement", "catalogue : every part/colour pair exists in Rebrickable and LDraw",
                            "fragility graph : single-stud parts, articulation points, cascade mass (indicative)", "assembly plan ids == model ids, BOM == model"], not_claimed=["physical strength", "stock or price", "behaviour when hung or carried by the frame"]),
     "sculpture_3d": dict(support="free-standing : the contact surface with the ground and the centre of gravity matter", checks=["engine-1 validator (collisions, connectivity, clutch stability per sub-assembly)", "weak groups and reinforcement passes", "scope control (parts outside the network)",
                            "catalogue : every part/colour pair exists"], not_claimed=["physical stability of the standing pose (no real test)", "stock or price"]),
     "mosaic_2d": dict(support="flat plate on a baseplate", checks=["not implemented in this version"], not_claimed=["everything"])}
def verify_catalogue(model_dir):
    """BOM check of <dir>/parts_list.csv (part_num,color_id,quantity) : .dat exists, colour valid, pair catalogued. Writes bom_verification.json."""
    run([PY, MAPS / "verify_bom.py", model_dir]); return json.load(open(Path(model_dir) / "bom_verification.json"))
def render_ldr(model_dir, views, out=None):
    """Real renders of <dir>/diorama.ldr (three.js on the LDraw part meshes). views = {name: {az, el, w, h, zoom, frameBox}} in render_ldr.js format."""
    d = Path(model_dir); out = Path(out or d / "renders"); tmp = out / "_scene"; tmp.mkdir(parents=True, exist_ok=True)
    run([PY, E1_SRC / "engine" / "ldr_expand.py", "--ldr", d / "diorama.ldr", "--ldraw", env()["LEGO_ENGINE_HOME"] + "/.deps/ldraw-parts-library/complete/ldraw", "--json", tmp / "s.json", "--glb", tmp / "g.glb"])
    json.dump(views, open(tmp / "views.json", "w")); run(["node", E1_SRC / "engine" / "render_ldr.js", tmp / "s.json", tmp / "views.json", out])
    import shutil; shutil.rmtree(tmp, ignore_errors=True); return sorted(p.name for p in out.glob("*.png"))
def parts_csv_from_catalogue(catalogue_csv, out_csv):
    """sculpture catalogue (part, ..., rebrickable_colour_id, qty) -> parts_list.csv"""
    rows = list(csv.DictReader(open(catalogue_csv)))
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["part_num", "part_name", "color_id", "quantity", "stock_verified", "unit_price"])
        for r in rows: w.writerow([r["part"], r.get("name", ""), r["rebrickable_colour_id"], r["qty"], "false", ""])
    return len(rows), sum(int(r["qty"]) for r in rows)
