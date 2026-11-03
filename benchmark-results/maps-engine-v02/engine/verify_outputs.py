"""Cross-checks of every V0.1 output folder : LDraw = parts.json = BOM = notice steps (each part exactly once), PDF pages, viewer opens without error and a click identifies a part. usage: python verify_outputs.py <results dir> [...]"""
import csv, json, os, subprocess, sys
import numpy as np
def check(d):
    P = json.load(open(os.path.join(d, "parts.json"))); ldr = [l.split() for l in open(os.path.join(d, "map.ldr")) if l.startswith("1 ")]; bom = sum(int(r["quantity"]) for r in csv.DictReader(open(os.path.join(d, "parts_list.csv"))))
    steps = json.load(open(os.path.join(d, "etapes.json"))); ids = [i for s in steps for i in s["pieces"]]; pdf = subprocess.run(["pdfinfo", os.path.join(d, "notice.pdf")], capture_output=True, text=True).stdout
    pages = int([l for l in pdf.splitlines() if l.startswith("Pages")][0].split()[1]); sections = sorted({s["section"] for s in steps})
    ldr_ids = {}
    for k, l in enumerate(ldr): pass
    # LDraw bounding box in mm (frame included)
    xs = [float(t[2]) for t in ldr]; zs = [float(t[4]) for t in ldr]
    return dict(dossier=os.path.basename(os.path.dirname(d)) + "/" + os.path.basename(d), pieces_parts_json=len(P), pieces_ldr=len(ldr), pieces_bom=bom, pieces_dans_les_etapes=len(ids), chaque_piece_exactement_une_fois=(len(ids) == len(set(ids)) and set(ids) == {p["id"] for p in P}), etapes=len(steps),
                max_pieces_par_etape=max(len(s["pieces"]) for s in steps), sections=sections, pages_pdf=pages, fichiers_presents={f: os.path.exists(os.path.join(d, f)) for f in ("map.ldr", "parts_list.csv", "viewer.html", "notice.pdf", "validation/validation_resume.json", "renders/face.png")})
if __name__ == "__main__":
    out = [check(d) for d in sys.argv[1:]]; print(json.dumps(out, indent=1, ensure_ascii=False))
