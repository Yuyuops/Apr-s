"""Validation : engine-1 validator (collisions, joints, disconnected parts, indicative clutch stability ; read-only use) + engine-2 checks (dimensions, layer coverage, support, rigidity graph, seam stagger)."""
import json, os, subprocess, sys
from collections import Counter, defaultdict
import numpy as np, networkx as nx
from .common import E1
from _paths import LDRAW, RB_DB
from .build import y_top

def engine1(ldr, outdir, name):
    os.makedirs(outdir, exist_ok=True)
    subprocess.run([sys.executable, os.path.join(E1, "validate_v4.py"), "--ldr", ldr, "--ldraw", LDRAW, "--rbdb", RB_DB, "--out", outdir, "--name", name, "--dump", os.path.join(outdir, name + "_dump.pkl")], check=True, capture_output=True)
    return json.load(open(os.path.join(outdir, name + "_validation_v2.json")))

def overlap(a, b):
    w = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]); d = min(a["z"] + a["d"], b["z"] + b["d"]) - max(a["z"], b["z"]); return max(0, w) * max(0, d)

def checks(model, v1=None):
    P = model["parts"]; n = model["n"]; H = model["heights"]; res = {}
    byl = defaultdict(list)
    for p in P: byl[p["level"]].append(p)
    # layer coverage : every cell of every level is covered exactly once, and exactly where the heights say
    bad = []
    for lv in sorted(byl):
        cov = np.zeros((n, n), int)
        for p in byl[lv]: cov[p["x"]:p["x"] + p["w"], p["z"]:p["z"] + p["d"]] += 1
        want = np.ones((n, n), int) if lv < 0 else (H >= lv).astype(int)
        if not (cov == want).all(): bad.append((lv, int((cov != want).sum())))
    res["couvertures_de_couche_incorrectes"] = bad
    # support : every plate rests on at least one plate of the level below
    unsup = []; floating = []
    for p in P:
        below = [q for q in P if q["level"] == (p["level"] - 1 if p["level"] != 0 else -1) and overlap(p, q) > 0] if p["level"] not in (-2,) else [1]
        if not below: unsup.append(p["id"])
    res["pieces_sans_appui"] = unsup
    # graph : plates, edges weighted by engaged studs between consecutive levels
    G = nx.Graph(); G.add_nodes_from(p["id"] for p in P); lv_of = {p["id"]: p["level"] for p in P}
    for lv in sorted(byl):
        if lv + 1 not in byl: continue
        for a in byl[lv]:
            for b in byl[lv + 1]:
                o = overlap(a, b)
                if o: G.add_edge(a["id"], b["id"], weight=o)
    res["graphe_pieces"] = dict(noeuds=G.number_of_nodes(), liaisons=G.number_of_edges(), tenons_engages=int(sum(d["weight"] for _, _, d in G.edges(data=True))), composantes=nx.number_connected_components(G))
    res["pieces_isolees"] = [i for i in G.nodes if G.degree(i) == 0]
    ap = list(nx.articulation_points(G)); res["points_d_articulation"] = len(ap); res["ponts"] = len(list(nx.bridges(G)))
    if G.number_of_nodes() > 1 and nx.is_connected(G):
        cut, (A, B) = nx.stoer_wagner(G, weight="weight"); res["coupe_minimale_tenons"] = int(cut); res["coupe_minimale_cotes"] = [len(A), len(B)]
        res["coupe_minimale_force_N_indicative"] = float(cut) * 1.0   # engine-1 model : 1.0 N per stud (assumed, indicative)
    # structural core = backing + the sea-level layer : the board itself, without the small relief plates that sit on top
    core = G.subgraph([p["id"] for p in P if p["level"] <= 0])
    if core.number_of_nodes() > 1 and nx.is_connected(core):
        cut, (A, B) = nx.stoer_wagner(core, weight="weight"); res["noyau_dos_et_niveau_mer"] = dict(plaques=core.number_of_nodes(), coupe_minimale_tenons=int(cut), cotes=[len(A), len(B)])
    # weakest plate attachment : studs engaged with the level below
    att = []
    for p in P:
        if p["level"] == -2: continue
        s = sum(overlap(p, q) for q in P if q["level"] == (p["level"] - 1) and q is not p) if p["level"] != 0 else sum(overlap(p, q) for q in byl[-1])
        att.append(s)
    res["tenons_min_vers_le_niveau_inferieur"] = int(min(att)); res["plaques_attachees_par_1_tenon"] = int(sum(1 for a in att if a == 1))
    # stagger of the seams : fraction of internal seam segments of a level that coincide with a seam of the level below
    def seams(pl):
        S = set()
        for p in pl:
            for z in range(p["z"], p["z"] + p["d"]): S.add(("x", p["x"], z)); S.add(("x", p["x"] + p["w"], z))
            for x in range(p["x"], p["x"] + p["w"]): S.add(("z", p["z"], x)); S.add(("z", p["z"] + p["d"], x))
        return S
    al = {}
    for lv in sorted(byl):
        if lv + 1 in byl:
            a, b = seams(byl[lv]), seams(byl[lv + 1]); inner = {s for s in b if 0 < s[1] < n}
            al["%d->%d" % (lv, lv + 1)] = round(len(inner & a) / max(1, len(inner)), 3)
    res["alignement_des_joints_entre_niveaux"] = al
    # dimensions
    xs0 = min(p["x"] for p in P); xs1 = max(p["x"] + p["w"] for p in P); zs0 = min(p["z"] for p in P); zs1 = max(p["z"] + p["d"] for p in P)
    ytop = min(y_top(p) for p in P)
    res["dimensions_mm"] = dict(x=(xs1 - xs0) * 8.0, z=(zs1 - zs0) * 8.0, hauteur=round(-ytop * 0.4, 1)); res["dimensions_conformes_256mm"] = (xs1 - xs0) * 8 == 256 and (zs1 - zs0) * 8 == 256
    res["pieces"] = len(P); res["pieces_1x1"] = sum(1 for p in P if p["name_size"] == "1x1"); res["part_1x1"] = round(res["pieces_1x1"] / len(P), 4)
    res["pieces_par_niveau"] = {str(k): len(v) for k, v in sorted(byl.items())}
    return res
