"""replay the sequences written by run_seq.py with the independent geometry of verify_seq.py. usage: check_ear_seq.py <model.ldr> <seq.json> <out.json>"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import sys, json, time
sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, ENGINE_DIR)
import numpy as np
import notice_plan as N, verify_seq as V
model, seqf, outf = sys.argv[1:4]
P = N.parse(model); G = N.build_graph(P); S = json.load(open(seqf)); out = {}
def flat(order):
    return [dict(ids=x["ids"], e=x["e"], slide=x["slide"]) for x in order]
def run(order, label):
    res = V.replay(P, G, flat(order), bases=[order[0]["ids"][0]] if order else [])
    bad = [r for r in res if not r["ok"]]
    for x in order:
        if x["kind"] == "unit":
            sub = run(x["inside"], label + "/unite"); bad += sub
    return bad
for key, d in S.items():
    t = time.time(); bad = run(d["order"], key)
    out[key] = dict(parts=d["n"], steps=len(d["order"]), problemes=len(bad), detail=[dict(ids=b["ids"], problems=b["problems"]) for b in bad[:40]])
    print(key, d["n"], "parts", len(d["order"]), "steps", "problems", len(bad), "%.0fs" % (time.time() - t), flush=True)
json.dump(out, open(outf, "w"), indent=1)
