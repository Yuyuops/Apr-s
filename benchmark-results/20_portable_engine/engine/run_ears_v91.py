"""plan every ear sub-assembly of a model : usage run_ears_v91.py <model.ldr> <out.json> [--all]"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import sys, json, time
sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, ENGINE_DIR)
import numpy as np, networkx as nx
from collections import defaultdict
import notice_plan as N, ear_plan as E
model, outf = sys.argv[1:3]; ALL = "--all" in sys.argv
P = N.parse(model); G = N.build_graph(P)
subs = defaultdict(list)
for p in P:
    if ALL: subs["all"].append(p["i"])
    elif p["sub"]: subs[p["sub"]].append(p["i"])
def ser(items):
    o = []
    for x in items:
        if x[0] == "part": o.append(dict(kind="part", ids=[int(x[1])], e=None if x[2] is None else [float(v) for v in x[2]], slide=None if x[3] is None else [float(v) for v in x[3]], conn=bool(x[4])))
        else: o.append(dict(kind="unit", ids=[int(i) for i in x[1]], e=None if x[2] is None else [float(v) for v in x[2]], slide=None if x[3] is None else [float(v) for v in x[3]], conn=bool(x[5]), inside=ser(x[4])))
    return o
out = {}
for sub, ids in subs.items():
    for ci, comp in enumerate(sorted(nx.connected_components(G.subgraph(ids)), key=lambda c: -len(c))):
        t = time.time(); r = E.plan_ear(P, G, sorted(comp))
        b = r["best"]
        print(sub, ci, len(comp), "parts | best:", b["name"], "| stuck", len(b["stuck"]), "| eval", b["eval"], "| replay problems", len(r["replay_problems"]), "| %.0fs" % (time.time() - t), flush=True)
        for a in r["all"]: print("    ", a["name"], "stuck", len(a["stuck"]), a["eval"], flush=True)
        out["%s:%d" % (sub, ci)] = dict(n=len(comp), ids=sorted(int(i) for i in comp), best=dict(name=b["name"], up=b["up"], stuck=b["stuck"], eval=b["eval"], rows=b["rows"], order=ser(b["items"])),
                                        orientations=r["all"], replay_problems=[dict(ids=x["ids"], problems=x["problems"]) for x in r["replay_problems"]],
                                        checks={str(k): v for k, v in r["checks"].items() if not isinstance(k, tuple)})
json.dump(out, open(outf, "w"), indent=1)
