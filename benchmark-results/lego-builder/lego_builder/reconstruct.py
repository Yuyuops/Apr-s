"""Photos -> GLB (connects the EXISTING reconstruction scripts to the builder, nothing is re-implemented) :
  1. tools/hf_gen.py        : shape from the 4 views on a white background, Hunyuan3D-2mv (public Hugging Face Space, api /shape_generation, seed fixed)
  2. tools/colorize_from_views.py : colours projected from the 4 views onto the mesh (ray casting, no generative model)
  3. geometry and colour control of the result (check_glb) : explicit thresholds, every failure is reported.
Needs : `pip install gradio_client` (requirements-reconstruct.txt), Internet access to huggingface.co, RGBA cut-outs of the subject (or a uniform background that can be removed)."""
import json, os, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np
from PIL import Image
from .paths import BR, PY, env
VIEWS = {"face": ("face", "front", "avant"), "dos": ("dos", "back", "arriere"), "profil_gauche": ("profil_gauche", "left", "gauche"), "profil_droit": ("profil_droit", "right", "droit")}
def find_views(files):
    """map 4 files to face / dos / profil_gauche / profil_droit by file name ; returns (views, problems)"""
    views = {}; problems = []
    for f in files:
        n = Path(f).stem.lower()
        for k, keys in VIEWS.items():
            if any(x in n for x in keys) and k not in views: views[k] = Path(f); break
    for k in VIEWS:
        if k not in views: problems.append("missing view '%s' : name a file with one of %s" % (k, "/".join(VIEWS[k])))
    return views, problems
def ensure_rgba(src, dst):
    """RGBA cut-out of the subject. A picture without transparency is cut out ONLY if its background is uniform (border colour distance) ; otherwise the caller is told."""
    im = Image.open(src); report = {"source": str(src), "had_alpha": im.mode in ("RGBA", "LA")}
    if report["had_alpha"] and np.asarray(im.convert("RGBA"))[..., 3].min() < 250: im.convert("RGBA").save(dst); report["cutout"] = "provided"; return report
    a = np.asarray(im.convert("RGB")).astype(float); b = 6; border = np.concatenate([a[:b].reshape(-1, 3), a[-b:].reshape(-1, 3), a[:, :b].reshape(-1, 3), a[:, -b:].reshape(-1, 3)]); bg = np.median(border, axis=0); sd = float(border.std(0).mean())
    report.update(background_rgb=[round(float(x)) for x in bg], border_std=round(sd, 1))
    if sd > 12: report["cutout"] = "failed : background is not uniform (border std %.1f) : provide RGBA cut-outs" % sd; return report
    mask = np.linalg.norm(a - bg, axis=2) > 28; from scipy import ndimage; mask = ndimage.binary_opening(mask, iterations=2); lab, n = ndimage.label(mask)
    if n: mask = lab == (np.argmax(ndimage.sum(mask, lab, range(1, n + 1))) + 1)
    out = np.dstack([a.astype(np.uint8), (ndimage.binary_fill_holes(mask) * 255).astype(np.uint8)]); Image.fromarray(out, "RGBA").save(dst); report["cutout"] = "automatic (uniform background removed)"; return report
def to_white(rgba, dst):
    im = Image.open(rgba).convert("RGBA"); bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im); bg.convert("RGB").save(dst)
def reconstruct(views, outdir, name="subject", steps=30, octree=256, seed=1234, log=None):
    """-> dict(report, glb, problems). `views` : {face, dos, profil_gauche, profil_droit} -> image paths."""
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True); st_rgba = out / "views_rgba"; st_white = out / "views_white"; st_rgba.mkdir(exist_ok=True); st_white.mkdir(exist_ok=True); rep = {"views": {}}; problems = []
    for k, f in views.items():
        r = ensure_rgba(f, st_rgba / ("%s_%s_rgba.png" % (name, k))); rep["views"][k] = r
        if r.get("cutout", "").startswith("failed"): problems.append("%s : %s" % (k, r["cutout"]))
        else: to_white(st_rgba / ("%s_%s_rgba.png" % (name, k)), st_white / ("%s_%s_blanc.png" % (name, k)))
    if problems: return dict(report=rep, glb=None, problems=problems)
    e = env(); e.update(INDIR=str(st_white) + "/", SUF="blanc", EP="/shape_generation", PYTHONPATH=os.pathsep.join(filter(None, [e.get("PYTHONPATH", ""), e.get("LEGO_GRADIO_PATH", "")])))
    shape_dir = out / "shape"; t0 = time.time(); last = ""
    for attempt in range(3):
        r = subprocess.run([PY, str(BR / "tools" / "hf_gen.py"), "tencent/Hunyuan3D-2mv", name, str(shape_dir), str(steps), str(octree)], env=e, capture_output=True, text=True)
        if log: open(log, "a").write("$ hf_gen attempt %d\n%s%s\n" % (attempt + 1, r.stdout, r.stderr))
        glbs = sorted(shape_dir.glob("*.glb")) if shape_dir.exists() else []
        if r.returncode == 0 and glbs: break
        last = (r.stdout + r.stderr)[-600:]; time.sleep(20 * (attempt + 1))
    else: return dict(report=rep, glb=None, problems=["shape generation failed after 3 attempts (Hugging Face Space) : " + last])
    rep["shape"] = dict(space="tencent/Hunyuan3D-2mv", api="/shape_generation", steps=steps, octree_resolution=octree, seed=seed, seconds=round(time.time() - t0, 1), file=str(glbs[0].name))
    coloured = out / ("%s_couleur.glb" % name); report = out / "projection_couleurs.json"; e2 = env(); e2["INPUTS_DIR"] = str(st_rgba) + "/"
    r = subprocess.run([PY, str(BR / "tools" / "colorize_from_views.py"), str(glbs[0]), name, str(coloured), str(report)], env=e2, capture_output=True, text=True)
    if log: open(log, "a").write("$ colorize_from_views\n%s%s\n" % (r.stdout, r.stderr))
    if r.returncode != 0 or not coloured.exists(): return dict(report=rep, glb=None, problems=["colour projection failed : " + (r.stdout + r.stderr)[-500:]])
    rep["projection"] = json.load(open(report)); return dict(report=rep, glb=coloured, problems=[])
def check_glb(glb, projection, min_iou=0.60, max_unseen=0.20):
    """Geometry and colour control of a reconstructed GLB. Returns (ok, checks, warnings) : every threshold is explicit."""
    import trimesh
    sc = trimesh.load(str(glb), force="scene"); g = list(sc.geometry.values()); faces = sum(len(x.faces) for x in g); ext = sc.bounds[1] - sc.bounds[0]; checks = {}; warn = []
    vc = [x.visual.vertex_colors for x in g if getattr(x.visual, "kind", "") == "vertex"]; col = np.concatenate(vc) if vc else np.zeros((0, 4))
    checks["has_vertex_colours"] = bool(len(col)); checks["faces"] = int(faces); checks["extents"] = [round(float(x), 3) for x in ext]; checks["watertight"] = all(x.is_watertight for x in g)
    ious = {k: v["iou_silhouette"] for k, v in projection.items() if isinstance(v, dict) and "iou_silhouette" in v}; checks["view_silhouette_iou"] = ious; checks["views_ok"] = bool(ious) and min(ious.values()) >= min_iou
    unseen = projection.get("vertices_seen_in_no_view", 0) / max(1, projection.get("vertices_total", 1)); checks["unseen_vertex_fraction"] = round(float(unseen), 3); checks["coverage_ok"] = unseen <= max_unseen
    kept = projection.get("faces_kept_largest_component", faces) / max(1, projection.get("faces_in", faces)); checks["largest_component_face_fraction"] = round(float(kept), 3)
    if kept < 0.5: warn.append("only %.0f %% of the faces belong to the main component : the reconstruction contains many fragments" % (100 * kept))
    if not checks["watertight"]: warn.append("mesh not watertight : the volume is filled by the voxeliser")
    if len(col):
        rgb = col[:, :3].astype(float); checks["colour_distinct_8bit"] = int(len({tuple(x) for x in rgb[:: max(1, len(rgb) // 20000)].astype(int)}))
    ok = checks["has_vertex_colours"] and checks["views_ok"] and checks["coverage_ok"]
    if not checks["views_ok"]: warn.append("a view registers badly with the mesh (silhouette IoU < %.2f) : geometry or colours may be wrong on that side" % min_iou)
    if not checks["coverage_ok"]: warn.append("%.0f %% of the vertices are seen in no view : their colour is guessed from neighbours" % (100 * unseen))
    return ok, checks, warn
