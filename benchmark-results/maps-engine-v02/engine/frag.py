"""Fragility analysis of a part list (V0.2) : separates decorative leaves from carriers, and carriers whose carried parts have another support (redundant) from those they alone hold (critical)."""
import json, os, sys
from collections import defaultdict, Counter
import networkx as nx
def analyse(P, detail=False):
    by = {p["id"]: p for p in P}; by_top = defaultdict(list)
    for p in P: by_top[p["zbot"] + p["h"]].append(p)
    below = defaultdict(int); above = defaultdict(int); G = nx.Graph(); G.add_nodes_from(by); sup = defaultdict(list); car = defaultdict(list)
    for p in P:
        for q in by_top.get(p["zbot"], []):
            if q["kind"] == "tile": continue
            w = min(q["x"] + q["w"], p["x"] + p["w"]) - max(q["x"], p["x"]); d = min(q["z"] + q["d"], p["z"] + p["d"]) - max(q["z"], p["z"])
            if w > 0 and d > 0: below[p["id"]] += w * d; above[q["id"]] += w * d; G.add_edge(p["id"], q["id"]); sup[p["id"]].append(q["id"]); car[q["id"]].append(p["id"])
    ap = set(nx.articulation_points(G)); weak = [p for p in P if p["zbot"] > 0 and above[p["id"]] > 0 and below[p["id"]] < 4]
    critical = [p for p in weak if any(len(sup[c]) == 1 for c in car[p["id"]])]; one = [p for p in P if p["zbot"] > 0 and below[p["id"]] == 1]
    r = dict(porteuses_faibles=len(weak), porteuses_faibles_critiques=len(critical), porteuses_faibles_redondantes=len(weak) - len(critical), un_seul_tenon=len(one), feuilles_decoratives=sum(1 for p in one if above[p["id"]] == 0), porteuses_un_tenon=sum(1 for p in one if above[p["id"]] > 0),
             points_articulation=len(ap), pieces_dont_la_perte_isole_une_piece=len(ap))
    if detail: r["critiques"] = [dict(id=p["id"], couche=p["layer"], taille=p["size"], region=p["region"], tenons_dessous=below[p["id"]]) for p in critical]; r["un_tenon"] = dict(Counter("%s %s %s %s" % (p["layer"], p["size"], p["region"], "feuille" if above[p["id"]] == 0 else "porteuse") for p in one))
    return r
if __name__ == "__main__":
    for d in sys.argv[1:]: print(d, json.dumps(analyse(json.load(open(os.path.join(d, "parts.json"))), True), ensure_ascii=False, default=str))
