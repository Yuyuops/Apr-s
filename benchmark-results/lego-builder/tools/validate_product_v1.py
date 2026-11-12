#!/usr/bin/env python3
"""Product V1 (Beagle) automatic package validator. Works on the delivered ZIP (extracted to a temp dir), never on the repository.
Checks (each one PASS / FAIL / BLOCKED with evidence in the JSON report) :
 1 required files present                       2 ZIP + file integrity (testzip, SHA256SUMS, MANIFEST)         3 BOM == model (CSV, JSON, LDraw part lines, Rebrickable import)
 4 notice == parts (steps vs BOM, PDF pages vs steps, part numbers on every step page)   5 part references recognised (.dat exists in LDraw, colour + pair in the Rebrickable snapshot)
 6 no critical collision   7 no disconnected part / island   (independent engine validator re-run on the shipped LDraw with --deep ; else stored report is only cited and marked 'cited')
 8 reproducible generation (--rebuild : GLB -> LEGO again, SHA-256 equal)   9 SHA-256 of every deliverable
10 no regression of other engines : done by product_regression_v1.sh (reported separately)
usage : validate_product_v1.py KIT.zip REPORT.json [--deep] [--rebuild GLB]   (env LEGO_ENGINE_HOME)"""
import csv, hashlib, json, os, re, sqlite3, subprocess, sys, tempfile, zipfile
from collections import Counter
zp, rep = sys.argv[1:3]; deep = "--deep" in sys.argv; E1 = os.environ.get("LEGO_ENGINE_HOME", ""); R = {}
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
def put(k, status, **ev): R[k] = dict(status=status, **ev); print("%-34s %s" % (k, status), {a: b for a, b in ev.items() if a in ("note", "detail")} or "")
REQUIRED = ["README.md", "MANIFEST.json", "SHA256SUMS.txt", "docs/GUIDE_UTILISATEUR.md", "docs/LIMITES_CONNUES.md", "model/Beagle_V1.ldr", "model/Beagle_V1_steps.ldr", "instructions/Beagle_V1_Notice.pdf", "instructions/steps.csv",
            "bom/Beagle_V1_BOM.csv", "bom/Beagle_V1_BOM.json", "bom/Beagle_V1_ldraw_parts.csv", "bom/Beagle_V1_rebrickable_import.csv", "bom/Beagle_V1_rare_parts.csv", "renders/Beagle_V1_face.png", "renders/Beagle_V1_dos.png",
            "renders/Beagle_V1_profil_gauche.png", "renders/Beagle_V1_profil_droit.png", "renders/Beagle_V1_trois_quarts.png", "renders/Beagle_V1_trois_quarts_arriere.png", "preview/Beagle_V1_turntable.gif", "LICENSES/LICENSES.md"]
t = tempfile.mkdtemp(); z = zipfile.ZipFile(zp); bad = z.testzip(); z.extractall(t); root = os.path.join(t, os.listdir(t)[0]); P = lambda r: os.path.join(root, r)
missing = [f for f in REQUIRED if not os.path.exists(P(f))]; put("1_required_files", "PASS" if not missing else "FAIL", missing=missing, files=len(z.namelist()))
sums = {l.split()[1]: l.split()[0] for l in open(P("SHA256SUMS.txt")) if l.strip()}; man = json.load(open(P("MANIFEST.json"))); mism = [f for f, h in sums.items() if not os.path.exists(P(f)) or sha(P(f)) != h]
unl = [n[len(os.path.basename(root)) + 1:] for n in z.namelist() if not n.endswith("/") and n[len(os.path.basename(root)) + 1:] not in sums and not n.endswith("SHA256SUMS.txt")]
put("2_integrity", "PASS" if bad is None and not mism and not unl else "FAIL", zip_testzip=bad, hash_mismatch=mism, files_not_in_sha_list=unl, manifest_files=len(man.get("files", [])))
ldr = P("model/Beagle_V1.ldr"); cnt = Counter()
for l in open(ldr):
    s = l.split()
    if s and s[0] == "1": cnt[(s[-1][:-4], int(s[1]))] += 1
bomcsv = {(r["part_num"], int(r["ldraw_colour_id"])): int(r["quantity"]) for r in csv.DictReader(open(P("bom/Beagle_V1_BOM.csv")))}; bj = json.load(open(P("bom/Beagle_V1_BOM.json")))
bjj = {(l["part_num"], l["ldraw_colour_id"]): l["quantity"] for l in bj["lines"]}; rb = {(r["Part"], int(r["Color"])): int(r["Quantity"]) for r in csv.DictReader(open(P("bom/Beagle_V1_rebrickable_import.csv")))}
lp = {(r["ldraw_file"][:-4], int(r["ldraw_colour_id"])): int(r["quantity"]) for r in csv.DictReader(open(P("bom/Beagle_V1_ldraw_parts.csv")))}
cnt2 = Counter()
for l in open(P("model/Beagle_V1_steps.ldr")):
    q = l.split()
    if q and q[0] == "1": cnt2[(q[-1][:-4], int(q[1]))] += 1
ok = cnt2 == cnt and bomcsv == dict(cnt) == bjj == lp and rb == dict(cnt) and bj["total_pieces"] == sum(cnt.values()) == sum(bomcsv.values()) and sha(ldr) == bj["ldraw_sha256"]
put("3_bom_equals_model", "PASS" if ok else "FAIL", total=sum(cnt.values()), lines=len(cnt), part_numbers=len({k[0] for k in cnt}), model_sha256=sha(ldr))
steps = list(csv.DictReader(open(P("instructions/steps.csv")))); cn = {l["ldraw_colour_id"]: l["colour_name"] for l in bj["lines"]}; stepsum = Counter(); per = {}
for r in steps:
    d = {}
    for tok in r["references"].split(): qp, c = tok.split("@"); q, p = qp.split("x"); d[(p, int(c))] = int(q)
    per[int(r["etape"])] = (r["type"], d)
    if r["type"] != "attach":
        for k, q in d.items(): stepsum[k] += q
pdfi = subprocess.run(["pdfinfo", P("instructions/Beagle_V1_Notice.pdf")], capture_output=True, text=True).stdout; pages = int(re.search(r"Pages:\s+(\d+)", pdfi).group(1)); front = man["notice"]["front_matter_pages"]
ok4 = stepsum == cnt and pages == front + len(steps) + 1 and sum(int(r["pieces"]) for r in steps if r["type"] != "attach") == sum(cnt.values()) and [int(r["etape"]) for r in steps] == list(range(1, len(steps) + 1))
txt = subprocess.run(["pdftotext", "-layout", P("instructions/Beagle_V1_Notice.pdf"), "-"], capture_output=True, text=True).stdout.split("\f"); miss = []
for n, (typ, d) in per.items():
    pg = re.sub(r"\s+", " ", txt[front + n - 1]) if front + n - 1 < len(txt) else ""
    if ("Étape %d / %d" % (n, len(steps))) not in pg: miss.append((n, "header")); continue
    for (p, c), q in d.items():
        if not re.search(r"\b%d × .*? \(%s\) %s\b" % (q, p, re.escape(cn[c])), pg): miss.append((n, "%dx%s %s" % (q, p, cn[c]))); break
put("4_notice_equals_parts", "PASS" if ok4 and not miss else "FAIL", steps=len(steps), pdf_pages=pages, front_matter_pages=front, pieces_summed_over_steps=sum(stepsum.values()), step_pages_with_missing_or_wrong_lines=miss[:10], note="parts x colour summed over the non-attach steps == BOM ; every step page prints its header and each (qty, part number, colour) line")
db = sqlite3.connect(os.path.join(E1, ".deps/rb.db")) if E1 else None; ld = os.path.join(E1, ".deps/ldraw-parts-library/complete/ldraw/parts") if E1 else ""
if db:
    nodat = [p for p in {k[0] for k in cnt} if not os.path.exists(os.path.join(ld, p + ".dat"))]; nopart = [p for p in {k[0] for k in cnt} if not db.execute("select 1 from parts where part_num=?", (p,)).fetchone()]
    nocol = [c for c in {k[1] for k in cnt} if not db.execute("select 1 from colors where id=?", (c,)).fetchone()]; nopair = [k for k in cnt if not db.execute("select 1 from pcs_mat where part_num=? and color_id=?", k).fetchone()]
    put("5_references_recognised", "PASS" if not (nodat or nopart or nocol or nopair) else "FAIL", no_dat=nodat, not_in_rebrickable_parts=nopart, unknown_colours=nocol, pairs_not_catalogued=nopair)
else: put("5_references_recognised", "BLOCKED", note="LEGO_ENGINE_HOME not set")
if deep and E1:
    V = {}
    for name in ("Beagle_V1_steps.ldr", "Beagle_V1.ldr"):                                             # the build-order file is the one whose support-at-placement is meaningful ; the reference model file is in arbitrary order
        d = tempfile.mkdtemp(); subprocess.run([os.path.join(E1, ".venv/bin/python"), os.path.join(E1, "engine/validate_v4.py"), "--ldr", P("model/" + name), "--ldraw", os.path.join(E1, ".deps/ldraw-parts-library/complete/ldraw"), "--rbdb", os.path.join(E1, ".deps/rb.db"), "--out", d, "--name", "beagle"], capture_output=True, text=True)
        V[name] = json.load(open(os.path.join(d, "beagle_validation_v2.json")))
    a, b = V["Beagle_V1_steps.ldr"], V["Beagle_V1.ldr"]
    put("6_no_critical_collision", "PASS" if a["collisions"]["pairs"] == 0 and b["collisions"]["pairs"] == 0 and a["blocked_studs"] == 0 else "FAIL", mode="engine validate_v4 re-run on both shipped LDraw files", pairs_steps_file=a["collisions"]["pairs"], pairs_model_file=b["collisions"]["pairs"], blocked_studs=a["blocked_studs"])
    put("7_no_disconnected_part", "PASS" if a["disconnected_parts"] == 0 and a["islands"] == 0 and a["unsupported_at_placement"] == 0 and b["disconnected_parts"] == 0 and b["islands"] == 0 else "FAIL", mode="re-run", steps_file=dict(parts=a["parts"], steps=a["steps"], disconnected=a["disconnected_parts"], islands=a["islands"], unsupported_at_placement=a["unsupported_at_placement"]),
        model_file=dict(disconnected=b["disconnected_parts"], islands=b["islands"], unsupported_at_placement=b["unsupported_at_placement"]), note="unsupported_at_placement is judged on the build-order file ; the model file is in arbitrary file order (its count is an ordering artefact, documented)")
else: put("6_no_critical_collision", "BLOCKED", note="run with --deep to re-validate the shipped LDraw"); put("7_no_disconnected_part", "BLOCKED", note="run with --deep")
if "--rebuild" in sys.argv:
    glb = sys.argv[sys.argv.index("--rebuild") + 1]; out = tempfile.mkdtemp(); env = dict(os.environ, PYTHONPATH=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    r = subprocess.run([os.path.join(E1, ".venv/bin/python"), "-m", "lego_builder", "run", glb, "--out", out, "--size-mm", "400", "--notice", "off"], capture_output=True, text=True, env=env)
    s2 = sha(os.path.join(out, "model/diorama.ldr")) if os.path.exists(os.path.join(out, "model/diorama.ldr")) else None; put("8_reproducible_generation", "PASS" if s2 == sha(ldr) else "FAIL", rebuilt_sha256=s2, shipped_sha256=sha(ldr))
else: put("8_reproducible_generation", "BLOCKED", note="run with --rebuild GLB")
put("9_sha256_of_deliverables", "PASS" if not mism else "FAIL", files_hashed=len(sums))
put("10_no_regression_other_engines", "BLOCKED", note="verified separately by tools/product_regression_v1.sh (Maps, Paco, Beagle, unified Builder)")
json.dump(R, open(rep, "w"), indent=1, default=str); sys.exit(0 if all(v["status"] in ("PASS", "BLOCKED") for v in R.values()) else 1)
