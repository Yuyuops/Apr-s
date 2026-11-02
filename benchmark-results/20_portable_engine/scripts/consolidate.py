"""One-time consolidation of the engine sources of ~/bench into engine/ (provenance tool, kept for audit).
Takes the REFERENCE version of every module (newest generic one), copies it flat, removes the absolute paths (~/bench, /root/bench) and replaces them by the
helpers of engine/_paths.py. No algorithm is rewritten here."""
import os, re, shutil, sys
B = os.path.expanduser("~/bench"); OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine")
SRC = [  # (source relative to ~/bench, destination name)
 "tools/conn.py", "tools/partlib.py", "tools/studrefs.py", "tools/ldr_expand.py", "tools/reorder_notice.py", "tools/validate_v3.py", "tools/validate_v2.py", "tools/validate_v2_bigcases.py",
 "tools/render_ldr.js", "tools/render_steps.js",
 "proto/brickify_plus.py", "proto/ear10/design_v51.py", "proto/ear11/autogen.py", "proto/ear11/contour.py", "proto/ear12/autogen61.py",
 "proto/v7/fullgrid.py", "proto/v7/segment.py", "proto/v7/integrate.py", "proto/v7/assemble.py", "proto/v7/ref_glb_fullframe.py",
 "proto/v8/detect.py", "proto/v8/microdetails.py", "proto/v8/assemble_v8.py", "proto/v8/assemble_v81.py", "proto/v8/lcm.py", "proto/v82/assemble_v82.py", "proto/v82/lcm82.py",
 "proto/v10/tools/reinforce.py", "proto/v10/tools/weak_groups.py", "proto/v10/tools/classify_weak.py", "proto/v10/tools/final_scope.py", "proto/v10/tools/validate_v4.py",
 "proto/v10/tools/notice_plan.py", "proto/v10/tools/make_notice_pdf.py", "proto/v91/scope91.py:scope.py",
 "proto/v91/seq.py", "proto/v91/verify_seq.py", "proto/v91/ear_plan.py", "proto/v91/stitch.py", "proto/v91/run_ears_v91.py", "proto/v91/fix_steps.py", "proto/v91/annotate_plan.py",
 "proto/v91/suspended_analysis.py", "proto/v91/check_ear_seq.py", "proto/v91/test_scope_v91.py", "proto/v91/checks_v91.py", "proto/v91/strength_cmp.py", "proto/v91/mass_report.py",
 "proto/v91/export_notice.py", "proto/v10/render_compare.py", "proto/v10/board.py", "proto/v9/test_scope.py", "proto/v9/make_notice_pdf.py:make_notice_pdf_v9.py"]
SRC.remove("proto/v9/make_notice_pdf.py:make_notice_pdf_v9.py")
LD = "LDRAW"; 
def repl_expand(m):
    p = m.group(1)
    if p.startswith("brickify/pipeline"): return "BRICKIFY_PIPELINE"
    if p == "data/rb.db": return "RB_DB"
    if p.startswith("ldraw-parts-library/complete/ldraw"): rest = p[len("ldraw-parts-library/complete/ldraw"):]; return "LDRAW" + (' + "%s"' % rest if rest else "")
    if p == "tools/node_modules": return "NODE_MODULES"
    if p == "proto/ear08/run/module_report.json": return "EAR_FRAME_JSON"
    if p == "proto/v7/paco_full400.npz": return 'CTX("full_npz")'
    if p == "proto/v7/segmentation.npz": return 'CTX("seg_npz")'
    if p == "proto/v7/ref_full_frame.glb": return 'CTX("ref_full_frame")'
    if p.startswith("proto/ear0") and p.split("/")[-1] != "": return 'LEGACY_DATA("%s")' % p     # ear-era design data (not used by the V7+ chain; fails loudly if reached)
    base = p.split("/")[-1]
    if "." in base and p.split("/")[0] in ("tools", "proto"): return 'os.path.join(ENGINE_DIR, "%s")' % base
    return "ENGINE_DIR"
def conv(text):
    text = re.sub(r'os\.path\.expanduser\("~/bench/([^"]*)"\)', repl_expand, text)
    text = re.sub(r'"/root/bench/[^"]*"', "ENGINE_DIR", text)
    text = text.replace('"/home/user/Apr-s/benchmark-results/02_glb_gratuit_hunyuan2mv/beagle.glb"', 'CTX("source_glb")')
    text = text.replace("import scope91 as scope", "import scope")
    text = re.sub(r'os\.environ\.get\("LDRAW", [^)]*\)\)?', 'os.environ.get("LDRAW", LDRAW)', text) if "environ.get(\"LDRAW\"" in text else text
    return text
HEAD = "import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))\nfrom _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA\n"
os.makedirs(OUT, exist_ok=True)
for ent in SRC:
    src, _, dst = ent.partition(":"); dst = dst or os.path.basename(src)
    t = open(os.path.join(B, src), encoding="utf-8").read()
    if dst.endswith(".py"):
        t = conv(t)
        m = re.search(r"^(import |from )", t, re.M)
        t = t[:m.start()] + HEAD + t[m.start():]
    else: t = conv(t) if "bench" in t else t
    open(os.path.join(OUT, dst), "w", encoding="utf-8").write(t)
shutil.copytree(os.path.join(B, "proto/ear11/targets"), os.path.join(OUT, "targets"), dirs_exist_ok=True)
print(len(SRC), "modules")
