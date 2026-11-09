#!/usr/bin/env python3
"""Sprint V16 structural reinforcement driver. Builds the model, finds the parts that are single points of failure (articulation points of the stud-joint graph whose removal cuts >= K parts from the base),
re-tiles THEIR footprint with small parts (no visible change : only hidden body layers are re-tiled) and rebuilds ; repeats for N passes and keeps the best build. Measured, not declared : every pass reports one-stud share and worst isolated failure.
usage : reinforce_v16.py STYLE COMPOSITION OUTDIR [--passes 3] [--threshold 8] [--frame 4]   (env LEGO_ENGINE_HOME / LEGO_DEPS)"""
import json, os, pickle, subprocess, sys, tempfile, time, collections
from pathlib import Path
import networkx as nx
MAPS = Path(__file__).resolve().parents[2] / "maps-engine-v03" / "style_fidelity_v062"; E1 = Path(os.environ["LEGO_ENGINE_HOME"]); PY = str(E1 / ".venv" / "bin" / "python")
a = sys.argv[1:]; style, comp, out = [str(Path(x).resolve()) for x in a[:3]]; passes = int(a[a.index("--passes") + 1]) if "--passes" in a else 3; K = int(a[a.index("--threshold") + 1]) if "--threshold" in a else 8; F = 4
sys.path.insert(0, str(MAPS / ".." / ".." / "20_portable_engine" / "engine")); from _paths import LDRAW, RB_DB
def build(d, rf=None):
    Path(d).mkdir(parents=True, exist_ok=True); cmd = [PY, "build_style.py", style, comp, d, "--flank", "vertical", "--no-title"] + (["--reinforce", rf] if rf else []); t = time.time(); subprocess.run(cmd, cwd=MAPS, check=True, capture_output=True)
    return time.time() - t
def analyse(d):
    P = json.load(open(d + "/parts.json")); order = []
    for y in sorted({p["y"] for p in P}): order += [p for p in P if p["y"] == y]
    tmp = tempfile.mkdtemp(); pk = tmp + "/d.pkl"; subprocess.run([PY, str(MAPS / ".." / ".." / "20_portable_engine" / "engine" / "validate_v4.py"), "--ldr", d + "/diorama.ldr", "--ldraw", LDRAW, "--rbdb", RB_DB, "--out", tmp, "--name", "map", "--dump", pk], check=True, capture_output=True)
    dd = pickle.load(open(pk, "rb")); n = len(order); G = nx.Graph(); G.add_nodes_from(range(n)); down = collections.Counter(); up = collections.defaultdict(int)
    for (i, j, area, studs) in dd["edges"]:
        G.add_edge(i, j); lo, hi = (i, j) if order[i]["y"] < order[j]["y"] else (j, i); down[hi] += len(studs); up[lo] += 1
    ground = set(dd["ground"]); crit = []
    for i in nx.articulation_points(G):
        if order[i]["y"] == 0: continue
        seen = {g for g in ground if g != i}; st = list(seen)
        while st:
            u = st.pop()
            for v in G._adj[u]:
                if v != i and v not in seen: seen.add(v); st.append(v)
        lost = n - 1 - len(seen)
        if lost: crit.append((lost, order[i]))
    crit.sort(key=lambda x: -x[0]); one = sum(1 for i in range(n) if down[i] == 1 and order[i]["y"] > 0)
    return dict(pieces=n, one_stud=one, one_stud_pct=round(100 * one / n, 1), carrying=sum(1 for i in range(n) if down[i] == 1 and order[i]["y"] > 0 and up[i]), worst=crit[0][0] if crit else 0, critical_ge_K=sum(1 for c in crit if c[0] >= K), crit=crit)
log = []; rf = None; best = None; cells = collections.defaultdict(list)         # cumulative : flagged cells are never removed between passes
for k in range(passes + 1):
    d = "%s/pass%d" % (out, k); secs = build(d, rf); r = analyse(d); crit = r.pop("crit"); r.update(pass_=k, build_seconds=round(secs, 1)); log.append(r); print(json.dumps(r), flush=True)
    if best is None or (r["worst"], r["one_stud"]) < (best["worst"], best["one_stud"]): best = dict(r, dir=d)
    if r["worst"] < K or k == passes: break
    for lost, p in crit:
        if lost < K: continue
        for rr in range(p["r"] - 1, p["r"] + p["nr"] + 1):
            for cc in range(p["c"] - 1, p["c"] + p["nc"] + 1): cells[str(p["y"])].append([rr - F, cc - F])
    # also split the layer just below the critical part : the part must be fed by >= 2 supporters
    for lost, p in crit:
        if lost < K: continue
        for rr in range(p["r"], p["r"] + p["nr"]):
            for cc in range(p["c"], p["c"] + p["nc"]): cells[str(p["y"] - 1)].append([rr - F, cc - F])
    rf = "%s/reinforce_pass%d.json" % (out, k); json.dump(dict(cells), open(rf, "w"))
json.dump(dict(log=log, best=best), open(out + "/reinforcement_log.json", "w"), indent=1); print("BEST", json.dumps({k: v for k, v in best.items()}))
