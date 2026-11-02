"""V9 - risk classification of the fragile groups (before / after). usage: classify_weak.py <dump.pkl> <weak.json> <out.json>"""
import json, pickle, sys
import numpy as np
from collections import Counter
dump, weakf, out = sys.argv[1:4]
D = pickle.load(open(dump, "rb")); P = D["parts"]; E = D["edges"]; W = json.load(open(weakf))["groupes"]
def zone(g):
    x, y, z = g["centre_mm"]
    sub = list(g["sous_ensemble"])[0]
    if sub.startswith("V7_oreille"): return "bord d'oreille"
    if y > 228: return "visage / tete"
    if y < 45: return "pieds / semelles"
    if y < 150 and (x < 70 or x > 215): return "mains / doigts"
    if y < 150: return "jambes"
    if x < 70 or x > 215: return "epaules / bras"
    return "torse"
res = []
for g in W:
    ids = set(g["parts_ids"]); ct = Counter(); n_studs = 0
    for u, v, n, c in E:
        if (u in ids) != (v in ids):
            for pt, ax in c: ct["vertical" if abs(ax[1]) > 0.9 else "lateral"] += 1; n_studs += 1
    z = zone(g); mass = g["masse_g"]; force = g["force_N"]; sub = list(g["sous_ensemble"])[0]
    exposed = z in ("bord d'oreille", "mains / doigts", "visage / tete", "epaules / bras", "pieds / semelles")
    structurel = mass >= 5.0 or z in ("bord d'oreille", "mains / doigts") and mass >= 3.0 or g["parties"] >= 15
    deco = mass < 2.0 and g["parties"] <= 12
    cat = "structurel" if structurel else "decoration legere" if deco else "intermediaire"
    # assembly risk: a group joined by one stud whose parts are placed before the next layer locks it
    r_mont = "eleve" if (g["tenons"] <= 1 and mass >= 3.0) else "moyen" if g["tenons"] <= 2 else "faible"
    r_manip = ("eleve" if (exposed and force < 0.3 and mass >= 3.0) else "moyen" if (exposed and force < 0.5) else "faible")
    res.append(dict(id=g["id"], zone=z, sous_ensemble=sub, pieces=g["parties"], masse_g=mass, tenons=n_studs or g["tenons"], types_de_liaison=dict(ct), force_decrochage_indicative_N=force, centre_mm=g["centre_mm"],
                    couleurs=g["couleurs"], categorie=cat, risque_montage=r_mont, risque_manipulation=r_manip, expose=exposed))
json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
for r in sorted(res, key=lambda r: r["force_decrochage_indicative_N"]): print(r["id"], r["zone"], r["pieces"], "p", r["masse_g"], "g", r["tenons"], "t", r["force_decrochage_indicative_N"], "N", r["categorie"], "montage", r["risque_montage"], "manip", r["risque_manipulation"])
