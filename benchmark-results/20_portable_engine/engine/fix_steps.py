"""repair the steps of an ear plan that the fine replay rejects : for each failing step try every straight direction (stud rule + dense-mesh path) and keep the first that passes.
usage: fix_steps.py <model.ldr> <ears.json> <out.json>"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import sys, json
sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, ENGINE_DIR)
import numpy as np
import notice_plan as N, verify_seq as V, ear_plan as E
model, inf, outf = sys.argv[1:4]
P = N.parse(model); G = N.build_graph(P); D = json.load(open(inf))
def level(order, label, log):
    steps = [dict(ids=x["ids"], e=x["e"], slide=x["slide"]) for x in order]
    res = V.replay(P, G, steps, bases=[steps[0]["ids"][0]])
    for k, r in enumerate(res):
        if r["ok"]:
            if order[k]["kind"] == "unit": level(order[k]["inside"], label, log)
            continue
        placed = set(i for x in order[:k] for i in x["ids"]); fixed = False
        cands = [np.array(d) for d in E.ear_dirs(P, G, sorted(placed | set(order[k]["ids"])))]
        for d in cands:
            test = steps[:k] + [dict(ids=steps[k]["ids"], e=list(d), slide=None)]
            rr = V.replay(P, G, test, bases=[steps[0]["ids"][0]])[k]
            if rr["ok"]:
                log.append(dict(niveau=label, pas=k, pieces=order[k]["ids"], avant=dict(e=order[k]["e"], glissement=order[k]["slide"], defaut=r["problems"]), apres=dict(e=[float(v) for v in d], glissement=None)))
                order[k]["e"] = [float(v) for v in d]; order[k]["slide"] = None; fixed = True; break
        if not fixed:
            for d in cands:
                for sl in cands:
                    if abs(float(np.dot(d, sl))) > 0.99: continue
                    test = steps[:k] + [dict(ids=steps[k]["ids"], e=list(d), slide=list(sl))]
                    rr = V.replay(P, G, test, bases=[steps[0]["ids"][0]])[k]
                    if rr["ok"]:
                        log.append(dict(niveau=label, pas=k, pieces=order[k]["ids"], avant=dict(e=order[k]["e"], glissement=order[k]["slide"], defaut=r["problems"]), apres=dict(e=[float(v) for v in d], glissement=[float(v) for v in sl])))
                        order[k]["e"] = [float(v) for v in d]; order[k]["slide"] = [float(v) for v in sl]; fixed = True; break
                if fixed: break
        if not fixed: log.append(dict(niveau=label, pas=k, pieces=order[k]["ids"], defaut=r["problems"], resolu=False))
for key, v in D.items():
    log = []; level(v["best"]["order"], key, log); v["corrections_de_pas"] = log
    def flat(order):
        out = []
        for x in order: out.append(dict(ids=x["ids"], e=x["e"], slide=x["slide"]) if x["kind"] == "part" else dict(ids=x["ids"], e=x["e"], slide=x["slide"]))
        return out
    steps = flat(v["best"]["order"]); res = V.replay(P, G, steps, bases=[steps[0]["ids"][0]])
    v["replay_problems"] = [dict(ids=x["ids"], problems=x["problems"]) for x in res if not x["ok"]]
    v["checks"] = {}
    def collect(order):
        r_ = V.replay(P, G, flat(order), bases=[order[0]["ids"][0]])
        for x, r in zip(order, r_):
            for i in x["ids"]: v["checks"][str(i)] = dict(ok=r["ok"], reason="; ".join(r["problems"]), motion=None if x["e"] is None else [-float(c) for c in x["e"]], contact_serre=r.get("graze"))
            if x["kind"] == "unit": collect(x["inside"])
    collect(v["best"]["order"])
    print(key, "corrections", len(log), "problemes restants", len(v["replay_problems"]))
json.dump(D, open(outf, "w"), indent=1)
