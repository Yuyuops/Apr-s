"""export the notice plan : steps csv, tree json, bill of materials with the model mass. usage: export_notice.py <model.ldr> <plan.json> <catalogue.csv> <outdir>"""
import sys, json, csv, os
sys.path.insert(0, "/root/bench/proto/v9"); sys.path.insert(0, "/root/bench/tools")
import numpy as np, notice_plan as N, conn
from collections import Counter, defaultdict
model, planf, catf, out = sys.argv[1:5]; os.makedirs(out, exist_ok=True)
P = N.parse(model); D = json.load(open(planf)); plan = D["plan"]
G3 = 0.10 / (20 * 20 * 8)
def mass(p): C = conn.part(p["num"]); return float(np.prod(C["hi"] - C["lo"])) * C["fill"] * G3
with open(os.path.join(out, "etapes_notice.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["etape", "module", "section", "type", "pieces", "references", "sens_emboitement", "a_tenir", "verifie_ok", "remarque"])
    for k, st in enumerate(plan):
        refs = Counter(P[i]["num"] for i in st["parts"]); ch = st["checks"]
        sens = Counter(c.get("sens") for c in ch if c.get("sens")); tenir = any(c.get("tenir") or c.get("stable") is False for c in ch); ok = all(c.get("ok", True) for c in ch)
        rem = "; ".join(sorted({(c.get("reason") or "")[:90] for c in ch if c.get("reason")}))
        w.writerow([k + 1, st["module"], st["section"], st["kind"], len(st["parts"]), " ".join("%dx%s" % (v, r) for r, v in refs.most_common()), " ".join("%s:%d" % (a, b) for a, b in sens.items()), "oui" if tenir else "", "oui" if ok else "non", rem])
tree = defaultdict(lambda: dict(etapes=0, pieces=0))
for st in plan:
    top = st["module"].split(" > ")[0]; tree[top]["etapes"] += 1; tree[top]["pieces"] += len(st["parts"]) if st["kind"] != "attach" else 0
json.dump(dict(modules=tree, total_etapes=len(plan), total_pieces=len(P)), open(os.path.join(out, "arbre_notice.json"), "w"), indent=1, ensure_ascii=False)
cat = list(csv.DictReader(open(catf))); bypair = Counter(); mpair = defaultdict(float)
for p in P: bypair[(p["num"], p["c"])] += 1; mpair[(p["num"], p["c"])] += mass(p)
rows = []
for r in cat:
    k = (r["part"], int(r["ldraw_colour"])); r2 = dict(r); r2["masse_modele_g"] = round(mpair[k], 2); r2["masse_unitaire_modele_g"] = round(mpair[k] / bypair[k], 3); rows.append(r2)
with open(os.path.join(out, "nomenclature_complete.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(plan), "etapes ;", len(rows), "references ; masse du modele %.1f g" % sum(mpair.values()))
