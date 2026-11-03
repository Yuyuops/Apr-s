"""Validation (V0.1) : engine-1 validator (collisions, joints, disconnected parts ; read-only use) + engine-2 checks (coverage, support, rigidity graph, seam stagger, dimensions, mass estimate)."""
import json, os, subprocess, sys
from collections import defaultdict
import numpy as np, networkx as nx
from .common import E1, KINDS
from _paths import LDRAW, RB_DB
import conn

DENSITY = 1.05e-3        # g / mm3, ABS (hypothesis)
def engine1(ldr, outdir, name):
    os.makedirs(outdir, exist_ok=True)
    subprocess.run([sys.executable, os.path.join(E1, "validate_v4.py"), "--ldr", ldr, "--ldraw", LDRAW, "--rbdb", RB_DB, "--out", outdir, "--name", name, "--dump", os.path.join(outdir, name + "_dump.pkl")], check=True, capture_output=True)
    v = json.load(open(os.path.join(outdir, name + "_validation_v2.json"))); os.remove(os.path.join(outdir, name + "_dump.pkl")); return v

def overlap(a, b):
    w = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]); d = min(a["z"] + a["d"], b["z"] + b["d"]) - max(a["z"], b["z"]); return max(0, w) * max(0, d)

def mass_g(parts):
    tot = 0.0; by = defaultdict(float)
    for p in parts:
        c = conn.part(p["part"]); vol = (p["w"] * 8.0) * (p["d"] * 8.0) * (p["h"] * 3.2); m = vol * float(c["fill"]) * DENSITY; tot += m; by[p["layer"][0]] += m
    return tot, dict(by)

def checks(model):
    P = model["parts"]; N = model["N"]; n = model["n"]; m = model["m"]; res = {}
    byid = {p["id"]: p for p in P}
    # collisions inside the model (same volume), support, coverage of the field by the heights
    occ = defaultdict(list)
    for p in P:
        for z in range(p["zbot"], p["zbot"] + p["h"]): occ[z].append(p)
    col = 0
    for z, lst in occ.items():
        grid = np.zeros((N, N), int)
        for p in lst: grid[p["x"]:p["x"] + p["w"], p["z"]:p["z"] + p["d"]] += 1
        col += int((grid > 1).sum())
    res["cellules_en_collision_interne"] = col
    H = model["heights"]; z0 = model["z0"]; bad = 0
    for k in range(H.max() + 1):
        g = np.zeros((N, N), int)
        for p in occ.get(z0 + k, []):
            if p["zbot"] == z0 + k and p["layer"].startswith("L"): g[p["x"]:p["x"] + p["w"], p["z"]:p["z"] + p["d"]] += 1
        bad += int((g[m:m + n, m:m + n] != (H >= k).astype(int)).sum())
    res["cellules_de_champ_mal_couvertes"] = bad
    G = nx.Graph(); G.add_nodes_from(byid); below = defaultdict(int); bytop = defaultdict(list)
    for p in P: bytop[p["zbot"] + p["h"]].append(p)
    for p in P:
        for q in bytop.get(p["zbot"], []):
            o = max(0, overlap(p, q) - (1 if q.get("wedge") else 0))
            if o and KINDS[q["kind"]][2] and q["kind"] != "tile": G.add_edge(p["id"], q["id"], weight=o); below[p["id"]] += o
            elif o and q["kind"] == "tile": pass
    res["pieces_sans_appui"] = [p["id"] for p in P if p["zbot"] > 0 and below[p["id"]] == 0 and p["zbot"] > 0]
    res["graphe"] = dict(noeuds=G.number_of_nodes(), liaisons=G.number_of_edges(), tenons_engages=int(sum(d["weight"] for _, _, d in G.edges(data=True))), composantes=nx.number_connected_components(G))
    res["pieces_isolees"] = [i for i in G.nodes if G.degree(i) == 0]
    single = [p["id"] for p in P if p["zbot"] > 0 and below[p["id"]] == 1]; res["pieces_sur_un_seul_tenon"] = len(single); res["pieces_sur_un_seul_tenon_ids"] = single[:60]
    ap = list(nx.articulation_points(G)); res["points_d_articulation"] = len(ap); res["points_d_articulation_non_feuilles"] = sum(1 for a in ap if G.degree(a) > 1)
    res["ponts"] = len(list(nx.bridges(G)))
    core = G.subgraph([p["id"] for p in P if p["layer"] in ("B1", "B2") or p["layer"].startswith("F")])
    if core.number_of_nodes() > 1 and nx.is_connected(core): c, (A, B) = nx.stoer_wagner(core, weight="weight"); res["noyau_dos_et_cadre"] = dict(plaques=core.number_of_nodes(), coupe_minimale_tenons=int(c), cotes=[len(A), len(B)])
    if nx.is_connected(G): c, (A, B) = nx.stoer_wagner(G, weight="weight"); res["coupe_minimale_globale_tenons"] = int(c); res["coupe_minimale_globale_cotes"] = [len(A), len(B)]
    def seams(pl):
        S = set()
        for p in pl:
            for z in range(p["z"], p["z"] + p["d"]): S.add(("x", p["x"], z)); S.add(("x", p["x"] + p["w"], z))
            for x in range(p["x"], p["x"] + p["w"]): S.add(("z", p["z"], x)); S.add(("z", p["z"] + p["d"], x))
        return S
    al = {}; layers = defaultdict(list)
    for p in P: layers[p["layer"]].append(p)
    order = ["B1", "B2"] + ["L%d" % k for k in range(H.max() + 1)]
    for a, b in zip(order[:-1], order[1:]):
        if a in layers and b in layers:
            sa, sb = seams(layers[a]), seams(layers[b]); lo, hi = m, m + n; inner = {s for s in sb if (lo < s[1] < hi) or (s[0] == "x" and lo <= s[2] < hi and lo < s[1] < hi) or True}
            inner = {s for s in sb if 0 < s[1] < N}; al["%s->%s" % (a, b)] = round(len(inner & sa) / max(1, len(inner)), 3)
    res["alignement_des_joints_entre_couches"] = al
    zt = max(p["zbot"] + p["h"] for p in P); res["dimensions_mm"] = dict(champ=n * 8.0, tableau_complet=N * 8.0, epaisseur=round(zt * 3.2, 1), epaisseur_champ=round(model["field_top"] * 3.2, 1))
    res["pieces"] = len(P); res["pieces_1x1"] = sum(1 for p in P if p["size"] == "1x1"); res["part_1x1"] = round(res["pieces_1x1"] / len(P), 4)
    res["references"] = len({(p["part"], p["colour"]) for p in P}); res["modeles_de_piece"] = len({p["part"] for p in P}); res["couches_de_plaques"] = int(zt)
    res["pieces_par_section"] = {k: sum(1 for p in P if p["layer"][0] == k) for k in "BLF"}
    tot, by = mass_g(P); res["masse_estimee_g"] = round(tot, 0); res["masse_par_section_g"] = {k: round(v) for k, v in by.items()}
    res["masse_hypotheses"] = "ABS 1,05 g/cm3 x volume des boites x taux de remplissage de la geometrie LDraw (moteur 1) ; la masse reelle est plausiblement +-30 %, tenons non comptes"
    return res
