"""engine 2 CLI.  generate : image -> grid -> relief -> tiling -> backing -> LDraw + BOM (raw, no verification)
                 full     : generate + validation (engine-1 validator, read-only) + renders + viewer + notice PDF + Briquestore check + metrics
usage: python -m maps_engine.run_map {generate|full} --input in.png|svg --out dir [--mode 2.5d|2d] [--style styles/relief_classic.json]"""
import argparse, json, os, shutil, subprocess, sys, time, urllib.request
import numpy as np
from . import classify as C, build as B, export as X, validate as V, render as R, viewer as W, notice as N
from .common import ROOT

def load_input(path, out):
    if path.lower().endswith(".svg"):
        png = os.path.join(out, "input.png"); subprocess.run(["node", os.path.join(ROOT, "engine", "rasterize_svg.js"), path, png, "512"], check=True, env=dict(os.environ, NODE_PATH=R.NODE_MODULES, LEGO_NODE_MODULES=R.NODE_MODULES)); return png
    return path

def generate(inp, out, mode="2.5d", style_path=None, tries=8, with_steps=False):
    style = json.load(open(style_path or os.path.join(ROOT, "styles", "relief_classic.json"))); t = time.time(); os.makedirs(out, exist_ok=True)
    cg = C.classify(inp); model = B.build(cg, style, mode, tries=tries)
    steps = N.steps_of(model, sorted(cg["classes"], key=lambda c: -int((cg["grid"] == cg["classes"].index(c)).sum()))) if with_steps else None
    B.write_ldr(model, os.path.join(out, "map.ldr"), os.path.splitext(os.path.basename(inp))[0] + " (%s)" % mode, steps)
    cnt = X.write_all(cg, model, out, os.path.basename(inp)); P = model["parts"]
    rep = dict(input=os.path.basename(inp), mode=mode, style=style["name"], pieces=len(P), pieces_1x1=sum(1 for p in P if p["name_size"] == "1x1"), references=len(cnt), seconds=round(time.time() - t, 1))
    rep["part_1x1_share"] = round(rep["pieces_1x1"] / rep["pieces"], 4); json.dump(rep, open(os.path.join(out, "generation.json"), "w"), indent=1); return cg, model, rep

def briquestore_check(out):
    """one polite request to the supplier page ; nothing is scraped or bypassed. Prices and stock stay null unless a human verifies them."""
    url = "https://store.bricklink.com/briquestore.fr"; r = dict(url=url, checked_at=time.strftime("%Y-%m-%d"), price_checked=False, stock_checked=False, values="null")
    try:
        q = urllib.request.Request(url, headers={"User-Agent": "lego-maps-research/0.1"}); resp = urllib.request.urlopen(q, timeout=15); r["http_status"] = resp.status; r["note"] = "page reachable but the store inventory is rendered client-side and per-item stock/price are not machine-verified by this engine : left null"
    except Exception as e: r["http_status"] = None; r["error"] = str(e)[:200]; r["note"] = "supplier not reachable / access refused : no workaround attempted, prices and stock left null"
    json.dump(r, open(os.path.join(out, "briquestore_check.json"), "w"), indent=1); return r

def zooms_for(cg):
    z = {}; g = cg["grid"]
    for nm in ("village", "sommet", "lac"):
        if nm in cg["classes"]:
            idx = np.argwhere(g == cg["classes"].index(nm))
            if len(idx): r0, c0 = idx.min(0); r1, c1 = idx.max(0) + 1; cr, cc = (r0 + r1) / 2, (c0 + c1) / 2; half = max(5, (max(r1 - r0, c1 - c0)) / 2 + 3); z[nm] = (max(0, int(cc - half)), max(0, int(cr - half)), min(32, int(cc + half)), min(32, int(cr + half)))
    return z

def full(inp, out, mode="2.5d", style_path=None, tries=8, render=True):
    os.makedirs(out, exist_ok=True); png = load_input(inp, out); t0 = time.time()
    cg, model, rep = generate(png, out, mode, style_path, tries, with_steps=True); name = os.path.splitext(os.path.basename(inp))[0]
    vd = os.path.join(out, "validation"); os.makedirs(vd, exist_ok=True); v1 = V.engine1(os.path.join(out, "map.ldr"), vd, "map"); chk = V.checks(model)
    json.dump(dict(moteur1=dict(parts=v1["parts"], collisions=v1["collisions"]["pairs"], disconnected_parts=v1["disconnected_parts"], islands=v1["islands"], unsupported_at_placement=v1["unsupported_at_placement"], joints=v1["joints"], studs_engaged=v1["studs_engaged"],
                                single_stud_joints=v1["single_stud_joints"], blocked_studs=v1["blocked_studs"], min_tip_force_N=v1["stability"].get("min_tip_force_N") if isinstance(v1["stability"], dict) else None, stabilite_moteur1={k: v for k, v in v1["stability"].items() if k not in ("big_cases", "weakest")}, disclaimer=v1["disclaimer"]), moteur2=chk), open(os.path.join(vd, "validation_resume.json"), "w"), indent=1, default=str)
    renders = {}
    if render:
        R.render_all(os.path.join(out, "map.ldr"), os.path.join(out, "renders"), layers=model["levels"] + 2, zooms=zooms_for(cg))
        renders = {k: os.path.join(out, "renders", k + ".png") for k in ("face", "trois_quarts")}
    W.write_viewer(model, os.path.join(out, "viewer.html"), name + " - " + mode)
    ns = N.build_notice(model, cg, out, name, renders, v1)
    bq = briquestore_check(vd)
    shutil.rmtree(os.path.join(out, "renders", "_scene"), ignore_errors=True)            # intermediate scene (tens of MB), regenerable
    if os.path.exists(os.path.join(out, "notice.pdf")) and os.path.exists(os.path.join(out, "notice.html")): os.remove(os.path.join(out, "notice.html"))
    rep.update(etapes=ns, validation=dict(collisions=v1["collisions"]["pairs"], deconnectees=v1["disconnected_parts"], liaisons=v1["joints"], tenons_engages=v1["studs_engaged"], a_1_tenon=chk["plaques_attachees_par_1_tenon"], points_articulation=chk["points_d_articulation"], coupe_min_tenons=chk["coupe_minimale_tenons"]), briquestore=bq.get("http_status"), seconds_total=round(time.time() - t0, 1))
    json.dump(rep, open(os.path.join(out, "generation.json"), "w"), indent=1); return cg, model, rep

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["generate", "full"]); ap.add_argument("--input", required=True); ap.add_argument("--out", required=True); ap.add_argument("--mode", default="2.5d"); ap.add_argument("--style"); ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    print((generate(a.input, a.out, a.mode, a.style)[2]) if a.cmd == "generate" else full(a.input, a.out, a.mode, a.style, render=not a.no_render)[2])
