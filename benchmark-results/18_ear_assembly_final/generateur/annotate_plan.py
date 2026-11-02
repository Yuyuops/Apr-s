"""add to the checks of a plan the steps where the sub-assembly must be held by hand (from suspended_analysis) : usage annotate_plan.py <plan.json> <suspended.json> <out.json>"""
import json, sys
D = json.load(open(sys.argv[1])); S = json.load(open(sys.argv[2]))
hold = {(r["module"], r["piece"]): r for r in S["lignes"] if r["a_tenir"]}
n = 0
for st in D["plan"]:
    top = st["module"].split(" > ")[0]
    if st["kind"] == "attach": continue
    for j, i in enumerate(st["parts"]):
        r = hold.get((top, i))
        if r: st["checks"][j]["tenir"] = "le sous-ensemble (%.0f g deja pose) n'est pas stable seul pendant cet emboitement par-dessous : le tenir a la main" % r["masse_placee_g"]; n += 1
json.dump(D, open(sys.argv[3], "w"), indent=1, default=float)
print("pieces annotees", n)
