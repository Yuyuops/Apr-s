"""engine 2 CLI : generate  (image -> grid -> relief -> tiling -> backing -> LDraw + BOM).   usage: python -m maps_engine.run_map generate --input in.png|svg --out dir [--mode 2.5d|2d] [--style styles/relief_classic.json]"""
import argparse, json, os, sys, time
from . import classify as C, build as B, export as X
from .common import ROOT

def generate(inp, out, mode="2.5d", style_path=None, tries=8):
    style = json.load(open(style_path or os.path.join(ROOT, "styles", "relief_classic.json"))); t = time.time()
    cg = C.classify(inp); model = B.build(cg, style, mode, tries=tries); os.makedirs(out, exist_ok=True)
    B.write_ldr(model, os.path.join(out, "map.ldr"), os.path.splitext(os.path.basename(inp))[0] + " (%s)" % mode)
    cnt = X.write_all(cg, model, out, os.path.basename(inp)); P = model["parts"]
    rep = dict(input=os.path.basename(inp), mode=mode, style=style["name"], pieces=len(P), pieces_1x1=sum(1 for p in P if p["name_size"] == "1x1"), references=len(cnt), seconds=round(time.time() - t, 1))
    rep["part_1x1_share"] = round(rep["pieces_1x1"] / rep["pieces"], 4); json.dump(rep, open(os.path.join(out, "generation.json"), "w"), indent=1); return cg, model, rep

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["generate"]); ap.add_argument("--input", required=True); ap.add_argument("--out", required=True); ap.add_argument("--mode", default="2.5d"); ap.add_argument("--style")
    a = ap.parse_args(); print(generate(a.input, a.out, a.mode, a.style)[2])
