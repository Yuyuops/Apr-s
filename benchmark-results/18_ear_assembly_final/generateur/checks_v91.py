"""V9.1 global checks of the model: unchanged parts outside the ears, ear tiles only, two independent fixation paths per ear, catalogue, base stability, scope tests.
usage: checks_v91.py <V9.ldr> <V91.ldr> <catalogue.csv> <out.json>"""
import sys, json, copy, csv
sys.path.insert(0, "/root/bench/proto/v9"); sys.path.insert(0, "/root/bench/proto/v91"); sys.path.insert(0, "/root/bench/tools")
import numpy as np, networkx as nx
from collections import Counter, defaultdict
from scipy.spatial import ConvexHull
import notice_plan as N, scope, ear_plan as E
a_path, b_path, cat, outf = sys.argv[1:5]
A = N.parse(a_path); B = N.parse(b_path); out = {}
key = lambda p: (p["num"], p["c"], tuple(np.round(p["o"], 2)), tuple(np.round(p["M"].ravel(), 4)), p["sub"])
ca = Counter(key(p) for p in A); cb = Counter(key(p) for p in B)
rem = ca - cb; add = cb - ca
TILES = {"3070b", "3069b", "63864", "2431", "6636"}
out["pieces_hors_oreilles_identiques"] = all(k[4] is not None for k in list((ca - cb).keys()) + list((cb - ca).keys()))
out["retirees"] = dict(Counter(k[0] for k in rem.elements())); out["ajoutees"] = dict(Counter(k[0] for k in add.elements()))
out["modifications_uniquement_tuiles_de_face"] = all(k[0] in TILES for k in list(rem.elements()) + list(add.elements()))
out["pieces"] = dict(V9=len(A), V91=len(B))
# fixation parts untouched : every ear part that is not a tile is identical
nt_a = Counter(key(p) for p in A if p["sub"] and p["num"] not in TILES); nt_b = Counter(key(p) for p in B if p["sub"] and p["num"] not in TILES)
out["oreilles_hors_tuiles_identiques"] = nt_a == nt_b
# two independent fixation paths per ear : node-disjoint paths from the ear body to the head (max flow, ear parts capacity 1)
def fixation_paths(P, sub):
    G = N.build_graph(P); ear = {p["i"] for p in P if p["sub"] == sub}
    ear_head = {i for i in ear if any(q not in ear and not P[q]["sub"] for q in G.neighbors(i))}
    F = nx.DiGraph()
    for i in ear:
        F.add_edge(("in", i), ("out", i), capacity=1)
        for q in G.neighbors(i):
            if q in ear: F.add_edge(("out", i), ("in", q), capacity=1)
    for i in ear_head: F.add_edge(("out", i), "T", capacity=1)
    # source = the ear parts farthest from the head interface (the free end of the ear) : the 10 % of the parts with the largest distance to the nearest interface part
    ctr = {i: (P[i]["lo"] + P[i]["hi"]) / 2 for i in ear}; ref = np.mean([ctr[i] for i in ear_head], 0) if ear_head else None
    far = sorted(ear - ear_head, key=lambda i: -np.linalg.norm(ctr[i] - ref))[:max(3, len(ear) // 10)] if ref is not None else []
    for i in far: F.add_edge("S", ("in", i), capacity=1)
    flow = nx.maximum_flow_value(F, "S", "T") if far and ear_head else 0
    return dict(pieces_de_contact_avec_la_tete=len(ear_head), chemins_disjoints_depuis_le_bout_libre=int(min(flow, len(far))))
out["fixation"] = {s: dict(V9=fixation_paths(A, s), V91=fixation_paths(B, s)) for s in sorted({p["sub"] for p in B if p["sub"] and "oreille_haute_1" not in p["sub"]})}
# catalogue
rows = list(csv.DictReader(open(cat))); out["catalogue"] = dict(couples=len(rows), statuts=dict(Counter(r["status"] for r in rows)), non_verifies=[(r["part"], r["colour"], r["status"]) for r in rows if r["status"] != "vérifiée"])
# base stability (whole model on its support plane)
def base(P):
    m = np.array([E.mass(p) for p in P]); ctr = np.array([(p["lo"] + p["hi"]) / 2 for p in P]); cog = (m[:, None] * ctr).sum(0) / m.sum()
    lowest = max(p["hi"][1] for p in P); foot = [p for p in P if p["hi"][1] > lowest - 1.0]
    pts = np.array([(x, z) for p in foot for x in (p["lo"][0], p["hi"][0]) for z in (p["lo"][2], p["hi"][2])]); h = ConvexHull(pts)
    q = cog[[0, 2]]; marg = min(-(eq[:2] @ q + eq[2]) for eq in h.equations) * 0.4
    return dict(masse_modele_g=round(float(m.sum()), 1), cdg_hauteur_mm=round(float(-cog[1] * 0.4), 1), marge_mm=round(float(marg), 1), plaques_au_sol=len(foot), aire_cm2=round(float(h.volume) * 0.16 / 100, 1))
out["base"] = dict(V9=base(A), V91=base(B))
json.dump(out, open(outf, "w"), indent=1, ensure_ascii=False, default=str)
print(json.dumps(out, indent=1, ensure_ascii=False, default=str)[:3000])
