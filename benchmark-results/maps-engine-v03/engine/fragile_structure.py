"""Structural fragility from parts.json only (works for V0 and V0.1) : (1) parts held by ONE stud, split into leaves (carry nothing above) and carriers ; (2) parts that carry other parts and are held by fewer than 4 studs ; (3) articulation points.
usage: python fragile_structure.py <output dir> ..."""
import json, os, sys
from collections import defaultdict
import networkx as nx
def analyse(d):
    P = json.load(open(os.path.join(d, "parts.json")))
    for p in P:
        p.setdefault("zbot", p.get("level", 0) + 2 if "level" in p else 0); p.setdefault("h", 1); p.setdefault("kind", "plate")
    by_top = defaultdict(list)
    for p in P: by_top[p["zbot"] + p["h"]].append(p)
    below = defaultdict(int); above = defaultdict(int); G = nx.Graph(); G.add_nodes_from(p["id"] for p in P)
    for p in P:
        for q in by_top.get(p["zbot"], []):
            w = min(q["x"] + q["w"], p["x"] + p["w"]) - max(q["x"], p["x"]); dd = min(q["z"] + q["d"], p["z"] + p["d"]) - max(q["z"], p["z"])
            if w > 0 and dd > 0 and q["kind"] != "tile": below[p["id"]] += w * dd; above[q["id"]] += w * dd; G.add_edge(p["id"], q["id"])
    one = [p for p in P if p["zbot"] > 0 and below[p["id"]] == 1]; leaves = [p for p in one if above[p["id"]] == 0]; carriers = [p for p in one if above[p["id"]] > 0]
    weak_carriers = [p for p in P if p["zbot"] > 0 and above[p["id"]] > 0 and below[p["id"]] < 4]; ap = list(nx.articulation_points(G))
    return dict(tenue_par_un_tenon=len(one), feuilles_decoratives=len(leaves), porteuses=len(carriers), porteuses_tenues_par_moins_de_4_tenons=len(weak_carriers), points_articulation=len(ap),
                exemples_porteuses_faibles=[dict(id=p["id"], part=p["part"], couche=p["layer"], tenons_dessous=below[p["id"]], tenons_dessus=above[p["id"]]) for p in weak_carriers[:8]])
if __name__ == "__main__":
    print(json.dumps({d: analyse(d) for d in sys.argv[1:]}, indent=1, ensure_ascii=False))
