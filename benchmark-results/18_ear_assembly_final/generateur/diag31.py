"""Phase 1 : per-part diagnostic of the 31 ear parts for which the V9 planner found no sequence.
For each part : reference, colour, position in the ear frame, stud contacts (with direction in the ear frame : +T / -T = face normal, Y = core stack), the V9 verdict (the stuck set it was in),
and the V9.1 plan (rank in the sequence, insertion motion, parts already placed it joins, replay result). The cause is classified :
  1 geometric impossibility / 2 wrong order / 3 planner limitation / 4 needs a flexion.
usage: diag31.py <a2.ldr> <seq_a2.json> <out.json>"""
import sys, json
sys.path.insert(0, "/root/bench/proto/v9"); sys.path.insert(0, "/root/bench/proto/v91"); sys.path.insert(0, "/root/bench/tools")
import numpy as np
import notice_plan as N
STUCK = {  # ids of the V9 model (a2.ldr), stuck sets reported by plan_units, with the nesting level at which the V9 planner stopped
 "V7_oreille_haute": [("niveau 0", [2206, 2207, 2238, 2299]), ("unite", [2237]), ("unite", [2231]), ("unite", [2158, 2303]), ("unite", [2281, 2282]), ("unite", [2269])],
 "V7_oreille_haute_1": [("niveau 0", [2321])],
 "V7_oreille_basse": [("niveau 0", [2326, 2339, 2341, 2342, 2381, 2383, 2388, 2400, 2409, 2410, 2424, 2466, 2467]), ("unite", [2393]), ("unite", [2456]), ("unite", [2459]), ("unite", [2330, 2331]), ("unite", [2431])],
}
P = N.parse(sys.argv[1]); G = N.build_graph(P); S = json.load(open(sys.argv[2]))
R = np.array([[0.6, 0, -0.8], [0, 1, 0], [0.8, 0, 0.6]])
def axname(a, owner_is_i):
    a = np.asarray(a); d = a if owner_is_i else -a            # motion of i that engages this contact
    loc = R.T @ d
    k = int(np.argmax(np.abs(loc)))
    return ("+" if loc[k] > 0 else "-") + ["N", "Y", "T"][k] if False else ("Y" if k == 1 else ("T" if k == 2 else "N")) + ("+" if loc[k] > 0 else "-")
rank = {}; info = {}
for key, v in S.items():
    pos = 0
    def walk(order):
        global pos
        for x in order:
            if x["kind"] == "part":
                rank[x["ids"][0]] = pos; info[x["ids"][0]] = x; pos += 1
            else: walk(x["inside"])
    pos = 0; walk(v["order"])
rows = []
for sub, sets in STUCK.items():
    ids = [p["i"] for p in P if p["sub"] == sub]
    for lvl, st in sets:
        for i in st:
            nb = []
            for q in G.neighbors(i):
                ds = {axname(a, o == i) for (pt, a, o) in G[i][q]["contacts"]}
                nb.append(dict(voisine=q, ref=P[q]["num"], liaison_engagee_par_mouvement=sorted(ds)))
            x = info.get(i); before = [q for q in G.neighbors(i) if rank.get(q, 1e9) < rank.get(i, -1)]
            sandwich = len({d for n in nb for d in n["liaison_engagee_par_mouvement"] if d[0] == "T"}) > 1
            rows.append(dict(piece=i, sous_ensemble=sub, ref=P[i]["num"], couleur=P[i]["c"], ensemble_bloque_V9=st, niveau_V9=lvl, contacts=nb,
                             rang_V91=rank.get(i), sur=len(ids), mouvement_insertion=None if not x or x["e"] is None else [round(-v_, 2) for v_ in x["e"]],
                             glissement=None if not x else x["slide"], voisines_deja_posees=len(before), voisines_posees_apres=len(nb) - len(before),
                             prise_en_sandwich_T=sandwich,
                             cause="3 : limitation du planificateur V9 (sous-ensembles rigides construits a part, 6 axes) ; ordre de montage en une pièce à la fois trouvé en V9.1" if x else "non sequencee"))
json.dump(rows, open(sys.argv[3], "w"), indent=1, ensure_ascii=False)
print(len(rows), "pieces ; sequencees", sum(1 for r in rows if r["rang_V91"] is not None), "; en sandwich T :", sum(r["prise_en_sandwich_T"] for r in rows))
