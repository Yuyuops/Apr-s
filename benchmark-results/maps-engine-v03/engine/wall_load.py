"""Load path of a board hung on a wall (STUDY ONLY, nothing is declared safe). For every horizontal interface of the stack : number of engaged studs, mass carried by the interface (everything above it, in the hanging direction : the board
is hung by its BACKING, so the relief hangs from the studs between the backing and the first relief layer), and the ratio capacity / weight with the engine-1 assumption of 1.0 N of clutch per stud (an assumption, never measured).
usage: python wall_load.py <output dir> > wall_load.json"""
import json, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maps_engine import validate as V, common
def study(d):
    P = json.load(open(os.path.join(d, "parts.json"))); G = 9.81e-3                                    # N per gram
    mass = {p["id"]: V.mass_g([p])[0] for p in P}; by_top = defaultdict(list)
    for p in P: by_top[p["zbot"] + p["h"]].append(p)
    rows = []; tot = sum(mass.values())
    for z in sorted({p["zbot"] for p in P if p["zbot"] > 0}):
        up = [p for p in P if p["zbot"] >= z]; studs = 0
        for p in up:
            if p["zbot"] != z: continue
            for q in by_top.get(z, []):
                if q["kind"] == "tile": continue
                w = min(q["x"] + q["w"], p["x"] + p["w"]) - max(q["x"], p["x"]); dd = min(q["z"] + q["d"], p["z"] + p["d"]) - max(q["z"], p["z"])
                if w > 0 and dd > 0: studs += w * dd
        m = sum(mass[p["id"]] for p in up); rows.append(dict(interface_plaque=z, tenons_engages=studs, masse_portee_g=round(m), poids_N=round(m * G, 2), capacite_supposee_N=studs * 1.0, rapport_capacite_sur_poids_suppose=round(studs / max(1e-9, m * G), 1)))
    return dict(masse_totale_g=round(tot), interfaces=rows, avertissement="Etude de repartition seulement. 1 N par tenon est une hypothese du moteur 1, non mesuree ; le glissement, les chocs, la fatigue du frottement et le moment du a l'epaisseur ne sont pas modelises. AUCUNE fixation murale n'est declaree sure sans essais physiques.")
if __name__ == "__main__": print(json.dumps(study(sys.argv[1]), indent=1, ensure_ascii=False))
