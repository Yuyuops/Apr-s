#!/usr/bin/env python3
"""Product V1 (Beagle) : automatic simulation of the CUSTOMER JOURNEY on the delivered ZIP only (no repository access). It tests everything that can be tested by a machine ; the physical steps stay 'HUMAN REQUIRED'.
 1 download (copy + ZIP test + extract)  2 open the guide (every file it names exists)  3 look at the renders (decodable, large, not blank)  4 identify the parts (BOM opens as a spreadsheet, totals, Rebrickable format)
 5 prepare the parts (bags by colour)  6 follow the notice (virtual build step by step : never use a part that is not in stock, sub-assemblies built before being attached)  7 finish (stock exactly consumed, last page present)
usage : simulate_customer_v1.py KIT.zip REPORT.json"""
import csv, json, os, re, shutil, subprocess, sys, tempfile, zipfile
from collections import Counter, defaultdict
from PIL import Image, ImageStat
zp, rep = sys.argv[1:3]; R = {}
def put(k, st, **ev): R[k] = dict(status=st, **ev); print("%-26s %s %s" % (k, st, {a: b for a, b in ev.items() if a == "note"} or ""))
d = tempfile.mkdtemp(); dst = os.path.join(d, "Downloads"); os.makedirs(dst); shutil.copy(zp, dst); z = zipfile.ZipFile(os.path.join(dst, os.path.basename(zp))); t = z.testzip(); z.extractall(os.path.join(d, "unzipped")); root = os.path.join(d, "unzipped", os.listdir(os.path.join(d, "unzipped"))[0]); P = lambda r: os.path.join(root, r)
put("1_download", "PASS" if t is None else "FAIL", zip_mb=round(os.path.getsize(zp) / 1e6, 1), files=len(z.namelist()), testzip=t)
txt = open(P("README.md")).read() + open(P("docs/GUIDE_UTILISATEUR.md")).read(); refs = sorted(set(re.findall(r"`([\w./-]+\.(?:md|pdf|csv|json|ldr|png|gif|txt))`", txt))); missing = [r for r in refs if not any(os.path.exists(os.path.join(root, p, r)) or os.path.exists(P(r)) for p in ("", "bom", "docs", "instructions", "model", "renders", "preview", "validation", "LICENSES"))]
put("2_open_guide", "PASS" if not missing and len(txt) > 2000 else "FAIL", files_named=len(refs), missing=missing, guide_chars=len(txt))
bad = []; dims = {}
for f in sorted(os.listdir(P("renders"))):
    im = Image.open(P("renders/" + f)); im.verify(); im = Image.open(P("renders/" + f)).convert("L"); dims[f] = im.size
    if im.size[0] < 2000 or ImageStat.Stat(im).stddev[0] < 15: bad.append(f)
g = Image.open(P("preview/Beagle_V1_turntable.gif")); put("3_renders", "PASS" if not bad and g.n_frames == 12 else "FAIL", renders=len(dims), size=list(dims.values())[0], too_small_or_blank=bad, gif_frames=g.n_frames)
rows = list(csv.DictReader(open(P("bom/Beagle_V1_BOM.csv")))); tot = sum(int(r["quantity"]) for r in rows); rb = list(csv.reader(open(P("bom/Beagle_V1_rebrickable_import.csv"))))
put("4_identify_parts", "PASS" if tot == 10567 and rb[0] == ["Part", "Color", "Quantity"] and len(rb) - 1 == len(rows) else "FAIL", bom_lines=len(rows), total=tot, rebrickable_header=rb[0], rare_file_lines=len(list(csv.reader(open(P("bom/Beagle_V1_rare_parts.csv"))))) - 1)
bags = defaultdict(lambda: [0, 0])
for r in rows: bags[r["colour_name"]][0] += int(r["quantity"]); bags[r["colour_name"]][1] += 1
put("5_prepare_parts", "PASS" if sum(b[0] for b in bags.values()) == tot else "FAIL", bags={k: dict(pieces=v[0], references=v[1]) for k, v in sorted(bags.items())}, note="one bag per colour; physical sorting HUMAN REQUIRED")
stock = Counter({(r["part_num"], int(r["ldraw_colour_id"])): int(r["quantity"]) for r in rows}); steps = list(csv.DictReader(open(P("instructions/steps.csv")))); errs = []; built_sub = set(); placed = 0; maxp = 0
for r in steps:
    need = Counter()
    for tok in r["references"].split(): qp, c = tok.split("@"); q, p = qp.split("x"); need[(p, int(c))] += int(q)
    if r["type"] == "attach":
        if r["module"] not in built_sub: errs.append((r["etape"], "attach before build-apart"))
        continue
    for k, q in need.items():
        if stock[k] < q: errs.append((r["etape"], "not enough %s" % (k,)))
        stock[k] -= q
    placed += sum(need.values()); maxp = max(maxp, sum(need.values()))
    if r["type"] == "sub": built_sub.add(r["module"])
left = sum(v for v in stock.values())
put("6_follow_notice", "PASS" if not errs else "FAIL", steps=len(steps), max_pieces_in_one_step=maxp, errors=errs[:10], note="virtual build in notice order against the BOM stock; the physical assembly is HUMAN REQUIRED")
txt = subprocess.run(["pdftotext", "-layout", P("instructions/Beagle_V1_Notice.pdf"), "-"], capture_output=True, text=True).stdout; low = txt.lower(); pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", P("instructions/Beagle_V1_Notice.pdf")], capture_output=True, text=True).stdout).group(1))
pg = [re.sub(r"\s+", " ", p) for p in txt.split("\f")]; flags = dict(from_below=sum("par en dessous" in p for p in pg), toward_dog_axis=sum(("avant du chien" in p or "arrière du chien" in p) for p in pg), winding_path=sum("virages" in p for p in pg), build_apart=sum("Construire à part" in p for p in pg))
put("7_finish", "PASS" if left == 0 and placed == 10567 and "Terminé" in pg[-2] + pg[-1] else "FAIL", pieces_placed=placed, stock_left=left, pdf_pages=pages, potentially_ambiguous_pages=flags)
R["human_required"] = ["physical sorting of the parts", "physical assembly of the 554 steps", "reading comfort of the PDF on paper/screen", "fit and strength of the finished model", "part availability and real cost"]
json.dump(R, open(rep, "w"), indent=1, default=str); sys.exit(0 if all(v["status"] == "PASS" for k, v in R.items() if isinstance(v, dict)) else 1)
