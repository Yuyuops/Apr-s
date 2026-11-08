#!/usr/bin/env python3
"""Sprint V14 : slicing benchmark on the REAL V13 exports (Paco, Hyrule). Three processes : 1 individual bricks, 2 multicolour modules, 3 monochrome pieces (connected components of each colour body) assembled afterwards.
Slicer = PrusaSlicer 2.7.2 CLI under PROXY machine profiles (bed / acceleration / flow from vendor spec pages) : NO vendor slicer profile (Bambu Studio, Creality Print, Snapmaker Orca) was available, so times are proxy-profile estimates, NOT vendor-slicer results.
usage : benchmark_v14.py WORKDIR OUTJSON"""
import json, math, os, subprocess, sys, re, collections, itertools, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / "tools"))
import render_3mf as R
from lego_builder.print3d import bricks, modules, common
from lego_builder.print3d.common import PARAMS, write_3mf
W = Path(sys.argv[1]); OUT = sys.argv[2]; W.mkdir(parents=True, exist_ok=True)
E1 = Path(os.environ["LEGO_ENGINE_HOME"]); CAT = json.load(open(HERE.parent / "maps-engine-v03/style_fidelity_v062/part_catalog.json")); RB = str(E1 / ".deps/rb.db")
MODELS = {"paco": HERE / "tests/data/paco_sample.ldr", "hyrule": HERE.parent / "maps-engine-v03/style_fidelity_v062/livraison_v10/hyrule_biomes/diorama.ldr"}
BED = 250.0                                           # common usable bed (A1 256, Hi 260, U1 270 minus margin) : conservative for the two larger machines
PROFILES = {"A1": dict(accel=10000, flow=21), "Hi": dict(accel=12000, flow=21), "U1": dict(accel=20000, flow=21)}
def slice_(f, tag, prof, supports=False, extra=()):
    d = W / "slices"; d.mkdir(exist_ok=True); g = d / ("%s.%s.%s.gcode" % (tag, prof, "sup" if supports else "nosup")); P = PROFILES[prof]
    cmd = ["prusa-slicer", "--bed-shape", "0x0,256x0,256x256,0x256", "--layer-height", "0.2", "--first-layer-height", "0.2", "--nozzle-diameter", "0.4", "--filament-diameter", "1.75", "--temperature", "215", "--bed-temperature", "60",
           "--filament-density", "1.24", "--perimeters", "3", "--top-solid-layers", "5", "--bottom-solid-layers", "4", "--fill-density", "15%", "--max-print-height", "256", "--dont-arrange",
           "--max-volumetric-speed", str(P["flow"]), "--perimeter-speed", "200", "--external-perimeter-speed", "120", "--infill-speed", "250", "--solid-infill-speed", "200", "--top-solid-infill-speed", "120", "--travel-speed", "400", "--first-layer-speed", "50",
           "--default-acceleration", str(P["accel"]), "--perimeter-acceleration", str(P["accel"] // 2), "--infill-acceleration", str(P["accel"]), "--external-perimeter-acceleration", str(P["accel"] // 2), "--travel-acceleration", str(P["accel"]),
           "--machine-max-acceleration-extruding", str(P["accel"]), "--machine-max-acceleration-x", str(P["accel"]), "--machine-max-acceleration-y", str(P["accel"]), "--machine-max-feedrate-x", "500", "--machine-max-feedrate-y", "500"]
    if supports: cmd += ["--support-material", "--support-material-auto", "--support-material-threshold", "45"]
    cmd += list(extra) + ["-g", "-o", str(g), str(f)]; p = subprocess.run(cmd, capture_output=True, text=True); txt = p.stdout + p.stderr
    r = dict(tag=tag, profile=prof, supports=supports, rc=p.returncode, warn=sorted({l.strip() for l in txt.splitlines() if re.search(r"stabil|Floating|Long bridging|conflict", l)})[:3])
    if g.exists():
        t = g.read_text(errors="replace")
        def grab(rx): m = re.findall(rx, t); return m[-1] if m else None
        tm = grab(r"estimated printing time \(normal mode\) = ([^\n]+)"); s = 0
        for q, u in re.findall(r"(\d+)([dhms])", tm or ""): s += int(q) * dict(d=86400, h=3600, m=60, s=1)[u]
        r.update(seconds=s, filament_g=float(grab(r"filament used \[g\] = ([\d.]+)") or 0), layers=len(re.findall(r"^;LAYER_CHANGE", t, re.M)), support_lines=len(re.findall(r"^;TYPE:Support material", t, re.M))); g.unlink()
    return r
def components(v, t):
    p = np.arange(len(v))
    def find(a):
        while p[a] != a: p[a] = p[p[a]]; a = p[a]
        return a
    for a, b, c in t: ra = find(a); p[find(b)] = ra; p[find(c)] = find(a)
    lab = np.array([find(i) for i in range(len(v))]); ids = {k: i for i, k in enumerate(sorted(set(lab)))}; fl = np.array([ids[lab[a]] for a, _, _ in t]); out = []
    for k in range(len(ids)):
        tri = t[fl == k]; used = np.unique(tri); mp = {o: i for i, o in enumerate(used)}; out.append((v[used], np.vectorize(mp.get)(tri)))
    return out
def pack(items, bed=BED, gap=3.0):
    """shelf packing of (w, d, payload) -> list of plates [(x, y, payload)]"""
    plates = []; cur = []; x = y = rowh = 0.0
    for w, d, pl in sorted(items, key=lambda i: -i[1]):
        w += gap; d += gap
        if x + w > bed: x = 0.0; y += rowh; rowh = 0.0
        if y + d > bed: plates.append(cur); cur = []; x = y = rowh = 0.0
        cur.append((x + gap / 2, y + gap / 2, pl)); x += w; rowh = max(rowh, d)
    if cur: plates.append(cur)
    return plates
def hexcol(rgb): return "%02X%02X%02X" % rgb
res = {"proxy_profiles": PROFILES, "bed_used_mm": BED, "models": {}}; jobs = []
for name, ldr in MODELS.items():
    m = res["models"][name] = {}; od = W / name; od.mkdir(exist_ok=True)
    # ---- process 1 : bricks (all plates written)
    P = dict(PARAMS, write_plates=9999); b = bricks.export(ldr, CAT, RB, od / "bricks", bed=(BED, BED), P=P); pl = sorted((od / "bricks" / "plates").glob("*.3mf"))
    m["bricks"] = dict(parts=b["parts_total"], supported=b["parts_supported"], unsupported_types=b["unsupported_types"], plates=len(pl), colours=b["colours"], volume_cm3=b["material_volume_cm3"], plates_files=[str(p) for p in pl])
    # ---- process 2 / 3 : shape-aware modules
    md = od / "modules"; r = modules.build(ldr, CAT, RB, md, shape_aware=True); mods = sorted((md / "modules").glob("*.3mf")); m["modules"] = dict(count=len(mods), colour_bodies=r["colour_bodies"], dowel_pairs=r["dowel_pairs"], files=[str(p) for p in mods], module_list=[])
    allc = collections.defaultdict(list)
    for f in mods:
        objs = R.load(f); comps = []
        for v, t, rgb in objs:
            for cv, ct in components(v, t): comps.append(dict(rgb=rgb, v=cv, f=ct, zmin=float(cv[:, 2].min()), zmax=float(cv[:, 2].max()), w=float(np.ptp(cv[:, 0])), d=float(np.ptp(cv[:, 1]))))
        # layer analysis (0.2 mm layers) : colours present per layer, Belady-optimal manual spool loads for a 4-slot machine
        zmax = max(c["zmax"] for c in comps); nl = int(math.ceil(zmax / 0.2)); present = [set() for _ in range(nl)]
        for c in comps:
            for L in range(int(c["zmin"] // 0.2), min(nl, int(math.ceil(c["zmax"] / 0.2)))): present[L].add(c["rgb"])
        changes = sum(max(0, len(s) - 1) for s in present); maxc = max(len(s) for s in present); ncol = len({c["rgb"] for c in comps})
        def loads(slots):
            if maxc > slots: return None
            have = set(); n = 0
            for L, s in enumerate(present):
                for col in s:
                    if col in have: continue
                    n += 1
                    if len(have) >= slots:
                        fut = {x: next((k for k in range(L + 1, nl) if x in present[k]), 10 ** 9) for x in have if x not in s}; have.remove(max(fut, key=fut.get))
                    have.add(col)
            return n
        info = dict(file=f.name, colours=ncol, max_colours_in_layer=maxc, layers=nl, colour_changes=changes, spool_loads_4slots=loads(4), spool_loads_16slots=loads(16), components=len(comps), height_mm=round(zmax, 1))
        m["modules"]["module_list"].append(info)
        for c in comps: allc[c["rgb"]].append(dict(module=f.name, c=c))
        # whole module slices (process 2) : with and without supports under A1, no supports under the others
        for prof in PROFILES: jobs.append(("mod2", name, f.name, dict(f=f, tag="%s_%s" % (name, f.stem), prof=prof, sup=False)))
        jobs.append(("mod2", name, f.name, dict(f=f, tag="%s_%s" % (name, f.stem), prof="A1", sup=True)))
    # ---- process 3 : pack the monochrome components per colour, one plate set per colour
    p3 = []; k = 0
    for rgb, lst in allc.items():
        items = [(x["c"]["w"], x["c"]["d"], x) for x in lst]
        for plate in pack(items):
            objs = [dict(name="c%d" % i, v=x["c"]["v"] - np.array([x["c"]["v"][:, 0].min(), x["c"]["v"][:, 1].min(), x["c"]["zmin"]]), f=x["c"]["f"], colour_hex=hexcol(rgb), offset=(px, py, 0)) for i, (px, py, x) in enumerate(plate)]
            fp = od / "mono" / ("mono_%03d_%s.3mf" % (k, hexcol(rgb))); fp.parent.mkdir(exist_ok=True); write_3mf(objs, fp); p3.append(dict(file=str(fp), colour=hexcol(rgb), pieces=len(objs))); k += 1
            for prof in PROFILES:
                if prof == "A1" or k % 4 == 0: jobs.append(("mono3", name, fp.name, dict(f=fp, tag="%s_%s" % (name, fp.stem), prof=prof, sup=False)))
            jobs.append(("mono3", name, fp.name, dict(f=fp, tag="%s_%s" % (name, fp.stem), prof="A1", sup=True)))
    m["mono"] = dict(plates=len(p3), pieces=sum(p["pieces"] for p in p3), colours=len(allc), plate_list=p3)
    for i, f in enumerate(pl):
        for prof in PROFILES:
            if (prof == "A1" and i % 4 == 0) or (prof != "A1" and i % 8 == 0): jobs.append(("bricks1", name, f.name, dict(f=f, tag="%s_%s" % (name, f.stem), prof=prof, sup=False)))
print("jobs", len(jobs), flush=True); t0 = time.time(); done = []
def run(j): kind, name, fn, a = j; r = slice_(a["f"], a["tag"], a["prof"], a["sup"]); r.update(kind=kind, model=name, file=fn); return r
with ThreadPoolExecutor(3) as ex:
    for i, r in enumerate(ex.map(run, jobs)):
        done.append(r)
        if i % 25 == 0: print(i, len(jobs), round(time.time() - t0), flush=True)
res["slices"] = done; json.dump(res, open(OUT, "w"), indent=1, default=str); print("written", OUT, round(time.time() - t0))
