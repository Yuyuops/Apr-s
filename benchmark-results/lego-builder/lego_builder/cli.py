"""LEGO Builder orchestrator (command line) : import -> analyse -> propose the type -> prepare data -> choose the generator -> build -> verify -> deliverables.
  python -m lego_builder analyze SRC
  python -m lego_builder prepare SRC --out PROJECT [--type auto|map|sculpture|mosaic] [--size-mm 400] [--title TEXT] [--rules RULES.json] [--corners x1,y1,...,x4,y4]
  python -m lego_builder build PROJECT [--pdf]
  python -m lego_builder run SRC --out PROJECT [...]            (prepare + build)
  python -m lego_builder geo --composition COMP.json --style STYLE.json --out PROJECT      (real geodata composition : the coast/sea variant of the maps generator)
  python -m lego_builder check PROJECT                           (strict manifest validation)"""
import argparse, json, shutil, sys, time
from pathlib import Path
from . import analyze as A, manifest as MF, core, map_ingest
from .paths import MAPS
TYPES = {"map": "map_relief_25d", "sculpture": "sculpture_3d", "mosaic": "mosaic_2d", "auto": None}
GEN = {"map_relief_25d": "maps", "sculpture_3d": "sculpture", "mosaic_2d": "mosaic", "undetermined": "none"}
def _new(proj, src_files, kind, ctype, analysis, args, unc):
    return {"schema_version": 1, "project_id": Path(proj).name, "source": {"kind": kind, "files": [{"path": str(Path("source") / f.name), "sha256": MF.sha256(f)} for f in src_files], "rights_note": "provided by the user ; rights not verified by the builder : never redistribute third-party works"},
            "construction_type": ctype, "generator": GEN[ctype], "geometry_source": {"kind": "none"}, "target": {"size_mm": args.size_mm, "height_mm": args.size_mm}, "palette_mode": "catalogue_lego", "analysis": analysis, "parameters": {}, "uncertainties": list(unc), "status": "analysed"}
def prepare(args):
    proj = Path(args.out); (proj / "source").mkdir(parents=True, exist_ok=True); photos = [Path(p) for p in (getattr(args, "photos", None) or [])]
    src = [Path(s) for s in (([args.src] if getattr(args, "src", None) else []) + (args.more or []) + [str(p) for p in photos])]
    for s in src: shutil.copy(s, proj / "source" / s.name)                                   # the original source is kept untouched, derived data go elsewhere
    is_photos = len(photos) >= 2 or (len(src) >= 2 and all(s.suffix.lower() in A.IMG for s in src))
    if is_photos:
        from . import reconstruct as RC
        views, vprob = RC.find_views([proj / "source" / s.name for s in src]); an = dict(kind="photos", construction_type="sculpture_3d", confidence=0.9 if not vprob else 0.6, evidence=["%d photographs : views found %s" % (len(src), sorted(views))], alternatives=[], uncertainties=list(vprob), sha256=MF.sha256(src[0]), file=src[0].name)
    else: an = A.analyse(src[0])
    ctype = TYPES[args.type] or an["construction_type"]; kind = "glb" if an["kind"] == "glb" else "photos" if is_photos else "image"
    m = _new(proj, [proj / "source" / s.name for s in src], kind, ctype, an, args, an["uncertainties"]); m["source"]["files"] = [{"path": str(Path("source") / s.name), "sha256": MF.sha256(proj / "source" / s.name)} for s in src]
    json.dump(an, open(proj / "analysis.json", "w"), indent=1); d = proj / "derived"; d.mkdir(exist_ok=True)
    if ctype == "map_relief_25d":
        corners = [tuple(map(float, args.corners.split(",")[i:i + 2])) for i in range(0, 8, 2)] if args.corners else None
        r = map_ingest.prepare_map(proj / "source" / src[0].name, d, size_mm=args.size_mm, rules_file=args.rules, corners=corners, title=args.title, aspect=args.aspect)
        m["geometry_source"] = {"kind": "terrain_classes", "files": {"terrain_classes": "derived/terrain_classes.tif", "palette": "derived/palette.json", "composition": "derived/composition.json", "style": "derived/style.json", "preview": "derived/preview.png"}}
        m["parameters"] = dict(grid_studs=r["grid_studs"], size_mm=r["size_mm"], board=r["board"], biome_share=r["biome_share"], corners=r["corners"], relief="estimated from terrain classes (shape heuristic, not altitude)")
        m["uncertainties"] += ["relief is an estimate (no altitude data)"] + (["board proportions assumed square (perspective view)"] if r["board"].get("aspect_source", "").startswith("assumed") else [])
        m["status"] = "ready_for_generation"
    elif ctype == "sculpture_3d":
        if kind == "glb": m["geometry_source"] = {"kind": "glb", "files": {"glb": str(Path("source") / src[0].name)}}; m["status"] = "ready_for_generation"; m["parameters"] = dict(height_mm=args.size_mm, subject=getattr(args, "subject", None))
        elif kind == "photos" and not vprob:
            from . import reconstruct as RC
            r = RC.reconstruct(views, proj / "derived", name=proj.name, log=proj / "reconstruct.log"); m["parameters"] = dict(height_mm=args.size_mm, subject=getattr(args, "subject", None), reconstruction=r["report"])
            if r["problems"]: m["status"] = "needs_input"; m["uncertainties"] += ["reconstruction : " + p for p in r["problems"]]
            else:
                ok, checks, warn = RC.check_glb(r["glb"], r["report"]["projection"]); m["parameters"]["glb_check"] = checks; m["uncertainties"] += warn + ["back and hidden volumes are ESTIMATED by the reconstruction model (4 views only)"]
                m["geometry_source"] = {"kind": "glb", "files": {"glb": str(Path("derived") / r["glb"].name)}}; m["status"] = "ready_for_generation" if ok else "needs_input"
                if not ok: m["uncertainties"].append("GLB control failed (see parameters.glb_check) : generation refused")
        else:
            m["status"] = "needs_input"; m["uncertainties"] += ["NO 3D GEOMETRY : give 4 views (face, dos, profil_gauche, profil_droit) or a GLB"] + (vprob if kind == "photos" else [])
    elif ctype == "mosaic_2d": m["status"] = "needs_input"; m["uncertainties"].append("the 2D mosaic generator is not implemented in this version")
    else: m["status"] = "needs_input"; m["uncertainties"].append("construction type undetermined : choose --type map|sculpture|mosaic")
    MF.write(m, proj); return m
def build(args):
    proj = Path(args.project); m = MF.read(proj); t0 = time.time()
    if m["status"] not in ("ready_for_generation", "generated", "validated"): raise SystemExit("project not ready : status %s ; %s" % (m["status"], "; ".join(m["uncertainties"][-2:])))
    out = proj / "model"; m["validation_strategy"] = core.strategies()[m["construction_type"]]
    try:
        if m["generator"] == "maps":
            from .generators import maps; g = m["geometry_source"]["files"]; res = maps.build(out, (proj / g["style"]).resolve(), (proj / g["composition"]).resolve(), pdf=args.pdf)
        elif m["generator"] == "sculpture":
            from .generators import sculpture; res = sculpture.build(out, (proj / m["geometry_source"]["files"]["glb"]).resolve(), proj.name, m["target"].get("height_mm", 400), with_notice=getattr(args, "notice", False), subject=m["parameters"].get("subject"), notice_timeout=getattr(args, "notice_timeout", 900))
        else: raise SystemExit("no generator for %s" % m["generator"])
        m["results"] = res; ok = res.get("delivery_check", {}).get("all_ok", None) if m["generator"] == "maps" else (res["catalogue_check"]["all_dat_exist"] and res["catalogue_check"]["all_colours_valid"] and not res["catalogue_check"]["pairs_not_catalogued"])
        m["status"] = "validated" if ok else "generated"; m["results"]["seconds"] = round(time.time() - t0, 1)
        m["deliverables"] = {k: str(Path("model") / v) for k, v in (("ldraw", res["ldraw"]), ("bom", res["bom"]))}
    except Exception as e: m["status"] = "failed"; m["uncertainties"].append("generation failed : %s" % str(e)[:300]); MF.write(m, proj); raise
    MF.write(m, proj); return m
def geo(args):
    proj = Path(args.out); (proj / "source").mkdir(parents=True, exist_ok=True); comp, sty = Path(args.composition).resolve(), Path(args.style).resolve()
    for f in (comp, sty): shutil.copy(f, proj / "source" / f.name)
    class _A: size_mm = 0
    m = _new(proj, [proj / "source" / comp.name, proj / "source" / sty.name], "geodata", "map_relief_25d", {"kind": "geodata", "evidence": ["real geodata composition (Natural Earth admin-0, public domain)"], "uncertainties": []}, _A, [])
    m["geometry_source"] = {"kind": "geodata_composition", "files": {"composition": "source/" + comp.name, "style": "source/" + sty.name}}; m["target"] = {}; m["status"] = "ready_for_generation"; MF.write(m, proj); return m
def main(argv=None):
    p = argparse.ArgumentParser(prog="lego_builder"); sp = p.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("analyze"); a.add_argument("src")
    def common(x):
        x.add_argument("--out", required=True); x.add_argument("--type", choices=list(TYPES), default="auto"); x.add_argument("--size-mm", type=float, default=400); x.add_argument("--title"); x.add_argument("--rules"); x.add_argument("--corners"); x.add_argument("--aspect", type=float); x.add_argument("--more", nargs="*"); x.add_argument("--photos", nargs="*", help="four views of a subject (names contain face/dos/profil_gauche/profil_droit or front/back/left/right)"); x.add_argument("--subject", help="sculpture : known validated configuration (paco, beagle) or a JSON path ; default = by GLB fingerprint, else generic"); x.add_argument("--pdf", action="store_true"); x.add_argument("--notice", choices=["off", "fast", "full"], default="fast"); x.add_argument("--notice-timeout", type=int, default=900)
    for n in ("prepare", "run"): x = sp.add_parser(n); x.add_argument("src", nargs="?"); common(x)
    b = sp.add_parser("build"); b.add_argument("project"); b.add_argument("--pdf", action="store_true"); b.add_argument("--notice", choices=["off", "fast", "full"], default="fast", help="sculptures : assembly plan : fast (no ear search, default), full (with ears, hard timeout) or off"); b.add_argument("--notice-timeout", type=int, default=900)
    g = sp.add_parser("geo"); g.add_argument("--composition", required=True); g.add_argument("--style", required=True); g.add_argument("--out", required=True); g.add_argument("--pdf", action="store_true")
    i = sp.add_parser("intent"); i.add_argument("--request"); i.add_argument("--source", action="append", default=[]); i.add_argument("--requirements"); i.add_argument("--out")
    c = sp.add_parser("check"); c.add_argument("project"); ar = p.parse_args(argv)
    if ar.cmd == "analyze": print(json.dumps(A.analyse(ar.src), indent=1, ensure_ascii=False))
    elif ar.cmd == "prepare": m = prepare(ar); print(json.dumps({k: m[k] for k in ("construction_type", "generator", "status", "uncertainties")}, indent=1, ensure_ascii=False))
    elif ar.cmd == "build": m = build(ar); print(json.dumps({k: m["results"].get(k) for k in ("pieces", "references", "seconds")} | {"status": m["status"]}))
    elif ar.cmd == "run": prepare(ar); ar.project = ar.out; m = build(ar); print(json.dumps({k: m["results"].get(k) for k in ("pieces", "references", "seconds")} | {"status": m["status"]}))
    elif ar.cmd == "geo": geo(ar); ar.project = ar.out; m = build(ar); print(json.dumps({k: m["results"].get(k) for k in ("pieces", "references", "seconds")} | {"status": m["status"]}))
    elif ar.cmd == "intent":
        from . import intent as I
        req = json.load(open(ar.requirements)) if ar.requirements else None; plan = I.interpret(ar.request, ar.source, req); txt = json.dumps(plan, indent=1, ensure_ascii=False); print(txt)
        if ar.out: Path(ar.out).write_text(txt)
    elif ar.cmd == "check": print(json.dumps({"errors": MF.validate(json.load(open(Path(ar.project) / "manifest.json")), ar.project)}))
if __name__ == "__main__": main()
