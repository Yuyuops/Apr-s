"""engine 2 V0.1 CLI.  generate : image -> grid -> relief -> colours -> tiling -> backing -> frame -> LDraw + BOM.   full : generate + validation + renders + viewer + notice + supplier check + metrics.
usage: python -m maps_engine.run_map {generate|full} --input in.png|svg --out dir [--finish A|B] [--mode 2.5d|2d] [--n 32] [--frame W] [--style styles/relief_classic.json] [--no-render]"""
import argparse, json, os, shutil, subprocess, sys, time, urllib.request
import numpy as np
from . import classify as C, build as B, export as X, validate as V, render as R, viewer as W, notice as N
from .common import ROOT

def load_input(path, out, size=512):
    if path.lower().endswith(".svg"):
        png = os.path.join(out, "input.png"); subprocess.run(["node", os.path.join(ROOT, "engine", "rasterize_svg.js"), path, png, str(size)], check=True, env=dict(os.environ, NODE_PATH=R.NODE_MODULES, LEGO_NODE_MODULES=R.NODE_MODULES)); return png
    return path

def generate(inp, out, finish="A", mode="2.5d", n=32, frame=None, style_path=None, tries=8, cut=None, smooth=None, cap=None, improve=True, mat=None):
    style = json.load(open(style_path or os.path.join(ROOT, "styles", "relief_classic.json"))); t = time.time(); os.makedirs(out, exist_ok=True)
    cg = C.classify(inp, n=n, size=n * (512 // n) if 512 % n == 0 else n * 10); model = B.build(cg, style, finish, mode, frame_width=frame, tries=tries, contour_cut=cut, smooth_set=smooth, frame_cap=(True if cap is None else cap), improve=improve, mat=mat)
    order = sorted(cg["classes"], key=lambda c: -int((cg["grid"] == cg["classes"].index(c)).sum())); steps = N.steps_of(model, order)
    B.write_ldr(model, os.path.join(out, "map.ldr"), "%s finish %s" % (os.path.splitext(os.path.basename(inp))[0], finish), steps); cnt = X.write_all(cg, model, out); P = model["parts"]
    rep = dict(input=os.path.basename(inp), finish=finish, lisse=model["finish_options"]["smooth"], chape_cadre=model["finish_options"]["frame_cap"], ameliore=improve, coins_coupes=sum(1 for p in P if p.get("wedge")), mode=mode, n=n, frame=model["m"], style=style["name"], pieces=len(P), pieces_1x1=sum(1 for p in P if p["size"] == "1x1"), references=len(cnt), etapes=len(steps), seconds=round(time.time() - t, 1))
    rep["part_1x1_share"] = round(rep["pieces_1x1"] / rep["pieces"], 4); json.dump(rep, open(os.path.join(out, "generation.json"), "w"), indent=1); return cg, model, rep

def briquestore_check(out):
    url = "https://store.bricklink.com/briquestore.fr"; r = dict(url=url, checked_at=time.strftime("%Y-%m-%d"), price_checked=False, stock_checked=False, values="null")
    try:
        q = urllib.request.Request(url, headers={"User-Agent": "lego-maps-research/0.1"}); resp = urllib.request.urlopen(q, timeout=15); r["http_status"] = resp.status; r["note"] = "page answered but per-item price / stock are not machine-verifiable by this engine (client-side inventory) : left null ; no workaround attempted"
    except Exception as e: r["http_status"] = None; r["error"] = str(e)[:200]; r["note"] = "supplier not reachable : prices and stock left null, no workaround attempted"
    json.dump(r, open(os.path.join(out, "briquestore_check.json"), "w"), indent=1); return r

def zooms_for(cg, m):
    z = {}; g = cg["grid"]; n = g.shape[0]
    for nm in ("village", "sommet", "lac"):
        if nm in cg["classes"]:
            idx = np.argwhere(g == cg["classes"].index(nm))
            if len(idx): r0, c0 = idx.min(0); r1, c1 = idx.max(0) + 1; cr, cc = (r0 + r1) / 2, (c0 + c1) / 2; half = max(5, (max(r1 - r0, c1 - c0)) / 2 + 3); z[nm] = (int(max(0, cc - half)) + m, int(max(0, cr - half)) + m, int(min(n, cc + half)) + m, int(min(n, cr + half)) + m)
    return z

def full(inp, out, finish="A", mode="2.5d", n=32, frame=None, style_path=None, tries=8, render=True, cut=None, smooth=None, cap=None, improve=True, mat=None):
    os.makedirs(out, exist_ok=True); png = load_input(inp, out, 512 if 512 % n == 0 else n * 10); t0 = time.time(); cg, model, rep = generate(png, out, finish, mode, n, frame, style_path, tries, cut, smooth, cap, improve, mat); name = os.path.splitext(os.path.basename(inp))[0]
    vd = os.path.join(out, "validation"); os.makedirs(vd, exist_ok=True); v1 = V.engine1(os.path.join(out, "map.ldr"), vd, "map"); chk = V.checks(model)
    json.dump(dict(moteur1=dict(parts=v1["parts"], collisions=v1["collisions"]["pairs"], disconnected_parts=v1["disconnected_parts"], islands=v1["islands"], unsupported_at_placement=v1["unsupported_at_placement"], joints=v1["joints"], studs_engaged=v1["studs_engaged"], single_stud_joints=v1["single_stud_joints"],
                                blocked_studs=v1["blocked_studs"], stabilite_moteur1={k: v for k, v in v1["stability"].items() if k not in ("big_cases", "weakest")}, disclaimer=v1["disclaimer"]), moteur2=chk), open(os.path.join(vd, "validation_resume.json"), "w"), indent=1, default=str)
    renders = {}; hp = max(p["zbot"] + p["h"] for p in model["parts"])
    if render:
        R.render_all(os.path.join(out, "map.ldr"), os.path.join(out, "renders"), N=model["N"], height_plates=hp, zooms=zooms_for(cg, model["m"])); renders = {k: os.path.join(out, "renders", k + ".png") for k in ("face", "trois_quarts")}
    W.write_viewer(model, os.path.join(out, "viewer.html"), "%s - finition %s" % (name, finish))
    steps = N.build_notice(model, cg, out, name, renders, dict(masse=chk["masse_estimee_g"]))
    bq = briquestore_check(vd); shutil.rmtree(os.path.join(out, "renders", "_scene"), ignore_errors=True)
    rep.update(etapes=len(steps), pieces_sur_un_seul_tenon=chk["pieces_sur_un_seul_tenon"], points_articulation=chk["points_d_articulation"], collisions=v1["collisions"]["pairs"], deconnectees=v1["disconnected_parts"], masse_g=chk["masse_estimee_g"], epaisseur_mm=chk["dimensions_mm"]["epaisseur"], briquestore=bq.get("http_status"), seconds_total=round(time.time() - t0, 1))
    json.dump(rep, open(os.path.join(out, "generation.json"), "w"), indent=1); return cg, model, rep

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["generate", "full"]); ap.add_argument("--input", required=True); ap.add_argument("--out", required=True); ap.add_argument("--finish", default="A"); ap.add_argument("--mode", default="2.5d"); ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--frame", type=int); ap.add_argument("--style"); ap.add_argument("--no-render", action="store_true"); ap.add_argument("--no-cut", action="store_true"); ap.add_argument("--smooth", default=""); ap.add_argument("--no-cap", action="store_true"); ap.add_argument("--mat", type=int); ap.add_argument("--no-improve", action="store_true"); a = ap.parse_args(); cut = False if a.no_cut else None; sm = [s for s in a.smooth.split(",") if s] or None; cap = False if a.no_cap else None
    print(generate(a.input, a.out, a.finish, a.mode, a.n, a.frame, a.style, cut=cut, smooth=sm, cap=cap, improve=not a.no_improve, mat=a.mat)[2] if a.cmd == "generate" else full(a.input, a.out, a.finish, a.mode, a.n, a.frame, a.style, render=not a.no_render, cut=cut, smooth=sm, cap=cap, improve=not a.no_improve, mat=a.mat)[2])
