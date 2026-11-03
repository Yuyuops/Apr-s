"""LEGO V9 - generic local reinforcement of the fragile sub-assemblies of an assembled LDraw model (no global rebuild).

Operates directly on the part list of the V8.2 model (parts that are not touched keep their exact lines), so nothing outside the declared regions can change.
R1  support plane   : the lowest plane of the model must be a real stance. Parts that touch the lowest plane are removed when (a) they are plain plates that carry nothing,
                      (b) the contact polygon of the model stands the centre of gravity with a margin below MIN_MARGIN_MM, (c) the next level gives a stance with the margin required.
                      The change is bounded by one plate height (3.2 mm) and recorded.
R2  internal bridges: for a fragile group G (indicative tip force < 0.5 N), the cells next to G in the same plate layer are examined. A neighbour cell can join G's region when
                      - it is occupied by a plain plate of the same colour (re-tiling only), or
                      - it is HIDDEN (its six neighbour cells are occupied, so it shows nowhere) : its colour is changed to G's colour (no visible effect, surface unchanged).
                      The cells are chosen by the number of real stud contacts they add between G's region and the rest (cell above / below belonging to another part, the lower
                      part carrying studs), until the gain reaches GAIN_GOAL or MAX_CELLS cells were added. The region of each layer is re-tiled with available plates of the colour,
                      and the plates that lost cells are re-cut. Geometry, exposed colours and finishes are unchanged by construction; this is checked by scope.py afterwards.
Only plain right-angle plates on the 20 x 8 x 20 lattice are modified (not tiles, slopes, wings, ears, details). Nothing is deleted except in R1.
usage: reinforce.py <in.ldr> <weak_groups.json> <out.ldr> <log.json> [per_layer=1] [skip_r1=0] [max_group_parts=60] [shorten_on_cut=0]
"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import ENGINE_DIR, LDRAW, RB_DB, BRICKIFY_PIPELINE, NODE_MODULES, EAR_FRAME_JSON, CTX, LEGACY_DATA, TARGETS_DIR
import json, os, sys
import numpy as np
from collections import Counter, defaultdict
sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, ENGINE_DIR); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conn, partlib as PL
import brickify_plus as BP
import scope
from scipy.spatial import ConvexHull

PLAIN = set(BP.PLATES.values())
LEN = [8, 6, 4, 3, 2, 1]
MAX_GROUP_PARTS = 60; GAIN_GOAL = 8; MAX_CELLS = 14; MIN_MARGIN_MM = 20.0
G_PER_LDU3 = 0.10 / (20 * 20 * 8)

def lattice_cells(p):
    """cells of a plain plate on the lattice, or None"""
    if p["num"] not in PLAIN or p["sub"] is not None: return None
    st, rc, lo, hi = conn.world(p["num"], p["M"], p["o"])
    if not np.all(np.isclose(np.abs(p["M"]), 0, atol=1e-4) | np.isclose(np.abs(p["M"]), 1, atol=1e-4)) or abs(abs(p["M"][1, 1]) - 1) > 1e-4: return None
    if abs((hi[1] - lo[1]) - 8) > 0.1: return None
    for v, u in ((lo[0], 20), (lo[2], 20), (lo[1], 8)):
        if abs(v / u - round(v / u)) > 0.05: return None
    a = np.round([lo[0] / 20, -hi[1] / 8, lo[2] / 20]).astype(int); b = np.round([hi[0] / 20, -lo[1] / 8, hi[2] / 20]).astype(int)
    return [(x, a[1], z) for x in range(a[0], b[0]) for z in range(a[2], b[2])]

def make_plate(num, colour, x0, y, z0, along_x):
    R = np.eye(3) if along_x else PL.rot_y(1)
    P = conn.part(num); lo, hi = np.array(P["lo"]), np.array(P["hi"])
    corners = np.array([[x, yy, zz] for x in (lo[0], hi[0]) for yy in (lo[1], hi[1]) for zz in (lo[2], hi[2])]) @ R.T
    o = np.array([20.0 * x0, -8.0 * (y + 1), 20.0 * z0]) - np.array([corners[:, 0].min(), corners[:, 1].min(), corners[:, 2].min()])
    return dict(c=colour, o=o, M=R, num=num, sub=None)

def line_of(p):
    return f"1 {p['c']} {p['o'][0]:.4f} {p['o'][1]:.4f} {p['o'][2]:.4f} " + " ".join(f"{v:.6f}" for v in np.asarray(p["M"]).ravel()) + f" {p['num']}.dat"

TILE_MODE = 0      # 0 : historical greedy cover ; 1 / 2 : prefer runs along z / x ; 3 : runs of at most 2 studs (V12.1 : alternative tilings tried when the first one cuts a link)
def tile_cells(cells, y, colour):
    """greedy cover of a set of (x, z) cells by available 1xN plates of the colour"""
    left = set(cells); out = []
    while left:
        x, z = min(left)
        best = None
        for along_x in ((True, False) if TILE_MODE in (0, 3) else ((False, True) if TILE_MODE == 1 else (True, False))):
            n = 1
            while ((x + n, z) if along_x else (x, z + n)) in left and n < (2 if TILE_MODE == 3 else 8): n += 1
            n = next(l for l in LEN if l <= n and BP.available(BP.PLATES[(l, 1)], colour)) if any(l <= n and BP.available(BP.PLATES[(l, 1)], colour) for l in LEN) else 1
            if best is None or n > best[0] or (n == best[0] and TILE_MODE in (1, 2) and (along_x == (TILE_MODE == 2))): best = (n, along_x)
        n, along_x = best
        run = [(x + k, z) if along_x else (x, z + k) for k in range(n)]
        for c in run: left.discard(c)
        out.append(make_plate(BP.PLATES[(n, 1)], colour, x, y, z, along_x) if along_x else make_plate(BP.PLATES[(n, 1)], colour, x, y, z, False))
    return out


_wcache = {}
def world_of(p):
    k = (p["num"], tuple(np.round(p["o"], 2)), tuple(np.round(np.asarray(p["M"]).ravel(), 3)))
    if k not in _wcache: _wcache[k] = conn.world(p["num"], p["M"], p["o"])
    return _wcache[k]

def ungrounded(P, alive):
    """number of live parts not connected by real stud joints to the support plane (graph rebuilt from the part geometry, as validate_v3 does)"""
    import networkx as nx
    idx = [i for i in range(len(P)) if alive[i]]
    W = {i: world_of(P[i]) for i in idx}
    rindex = defaultdict(list)
    for i in idx:
        for (pt, n) in W[i][1]: rindex[tuple(np.round(pt).astype(int))].append((i, n))
    G = nx.Graph(); G.add_nodes_from(idx)
    for i in idx:
        for (pt, ax) in W[i][0]:
            k = np.round(pt).astype(int)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        for (j, n) in rindex.get((k[0] + dx, k[1] + dy, k[2] + dz), []):
                            if j != i and np.dot(n, ax) < -0.9: G.add_edge(i, j)
    base = max(W[i][3][1] for i in idx)
    ground = [i for i in idx if abs(W[i][3][1] - base) < 0.5]
    seen = set()
    for g in ground:
        if g not in seen: seen |= nx.node_connected_component(G, g)
    return len([i for i in idx if i not in seen])


def tile_bridging(cells, gcells, y, colour):
    """tile a region so that every added cell is covered, whenever possible, by a plate that also covers a cell of the reinforced group (a plate straddling the two is
    the mechanical link; plates only side by side are not linked). The rest is tiled greedily."""
    left = set(cells); out = []
    ext = sorted(c for c in cells if c not in gcells)
    for e in ext:
        if e not in left: continue
        best = None
        for along_x in (True, False):
            for back in range(0, 4):
                for n in (3, 2):
                    run = [(e[0] - back + k, e[1]) if along_x else (e[0], e[1] - back + k) for k in range(n)]
                    if e not in run or not all(c in left for c in run): continue
                    g = sum(1 for c in run if c in gcells)
                    if g == 0 or not BP.available(BP.PLATES[(n, 1)], colour): continue
                    score = (g > 0, len([c for c in run if c not in gcells]), n)
                    if best is None or score > best[0]: best = (score, run, along_x, n)
        if best is None: continue
        _, run, along_x, n = best
        for c in run: left.discard(c)
        out.append(make_plate(BP.PLATES[(n, 1)], colour, min(c[0] for c in run), y, min(c[1] for c in run), along_x))
    return out + tile_cells(left, y, colour)

def mass(p):
    C = conn.part(p["num"]); return float(np.prod(C["hi"] - C["lo"])) * C["fill"] * G_PER_LDU3

def stance(P, level):
    ps = [p for p in P if abs(conn.world(p["num"], p["M"], p["o"])[3][1] - level) < 0.6]
    if len(ps) < 3: return len(ps), 0.0, -1e9
    pts = []
    for p in ps:
        _, _, lo, hi = conn.world(p["num"], p["M"], p["o"]); pts += [[x, z] for x in (lo[0], hi[0]) for z in (lo[2], hi[2])]
    pts = np.array(pts) * 0.4
    com = sum(mass(p) * (conn.world(p["num"], p["M"], p["o"])[2] + conn.world(p["num"], p["M"], p["o"])[3]) / 2 for p in P) / sum(mass(p) for p in P)
    try: h = ConvexHull(pts)
    except Exception: return len(ps), 0.0, -1e9
    c = np.array([com[0], com[2]]) * 0.4
    return len(ps), float(h.volume / 100), float(-max(np.dot(e[:2], c) + e[2] for e in h.equations))

def main():
    src, weakf, dst, logf = sys.argv[1:5]; per_layer = int(sys.argv[5]) if len(sys.argv) > 5 else 1; skip_r1 = len(sys.argv) > 6 and sys.argv[6] == "1"; max_parts = int(sys.argv[7]) if len(sys.argv) > 7 else MAX_GROUP_PARTS; shorten = len(sys.argv) > 8 and sys.argv[8] == "1"
    lines = open(src, encoding="utf-8", errors="replace").read().splitlines()
    P = []
    for l in lines:
        t = l.split()
        if t and t[0] == "1" and len(t) >= 15: P.append(dict(c=int(t[1]), o=np.array(t[2:5], float), M=np.array(t[5:14], float).reshape(3, 3), num=t[14].lower().replace(".dat", ""), sub=None, raw=l))
    sub = None; k = 0
    for l in lines:
        t = l.split()
        if len(t) > 4 and t[0] == "0" and t[1] == "BRICKIFY" and t[2] == "SUBASSEMBLY": sub = t[4] if t[3] == "BEGIN" else None; continue
        if t and t[0] == "1" and len(t) >= 15: P[k]["sub"] = sub; k += 1
    log = dict(r1=None, r2=[])
    alive = [True] * len(P)
    # ------------------------------------------------------------------ R1 support plane
    base = max(conn.world(p["num"], p["M"], p["o"])[3][1] for p in P)
    n0, area0, marg0 = stance(P, base)
    log["r1"] = dict(niveau_0=dict(pieces=n0, aire_cm2=round(area0, 1), marge_cdg_mm=round(marg0, 1)))
    if marg0 < MIN_MARGIN_MM and not skip_r1:
        ground = [i for i, p in enumerate(P) if abs(conn.world(p["num"], p["M"], p["o"])[3][1] - base) < 0.6]
        ok = all(P[i]["num"] in PLAIN and P[i]["sub"] is None for i in ground)
        keep = [p for i, p in enumerate(P) if i not in set(ground)]
        n1, area1, marg1 = stance(keep, base - 8)
        log["r1"]["niveau_1"] = dict(pieces=n1, aire_cm2=round(area1, 1), marge_cdg_mm=round(marg1, 1))
        if ok and marg1 >= MIN_MARGIN_MM:
            for i in ground: alive[i] = False
            log["r1"]["retirees"] = [dict(num=P[i]["num"], c=P[i]["c"], cellule=[int(round(P[i]["o"][0] / 20)), 0, int(round(P[i]["o"][2] / 20))]) for i in ground]
            log["r1"]["decision"] = "plan d'appui releve d'une plaque (3,2 mm) : %d plaques isolees retirees" % len(ground)
        else: log["r1"]["decision"] = "non applique (conditions non remplies)"
    # ------------------------------------------------------------------ R2 internal bridges
    weak = json.load(open(weakf))["groupes"]
    cellmap = {}; pcells = {}
    for i, p in enumerate(P):
        if not alive[i]: continue
        cs = lattice_cells(p)
        if cs is not None:
            pcells[i] = cs
            for c in cs: cellmap[c] = i
    A = scope.voxelise([dict(c=p["c"], o=p["o"], M=p["M"], num=p["num"], sub=p["sub"]) for i, p in enumerate(P) if alive[i]])
    occ = A["occ"]
    def hidden(c):
        x, y, z = c
        return all(0 <= q[0] < occ.shape[0] and 0 <= q[1] < occ.shape[1] and 0 <= q[2] < occ.shape[2] and occ[q] for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)))
    newparts = []
    base_ung = ungrounded(P, alive)
    log["non_relies_avant"] = base_ung
    for g in sorted(weak, key=lambda g: g["force_N"]):
        ids = [i for i in g["parts_ids"] if i < len(P) and alive[i] and i in pcells]
        if not ids or g["parties"] > max_parts: continue          # whole-model case: handled by R1 (V12.1 : the cap is a per-pass parameter, 60 = historical default)
        Gset = set(ids)
        colours = Counter(P[i]["c"] for i in ids); gcol = colours.most_common(1)[0][0]
        Gcells = {c for i in ids if P[i]["c"] == gcol for c in pcells[i]}
        layers = sorted({c[1] for c in Gcells}); region = set(Gcells); chosen = []; gain_total = 0
        def gain(c):
            x, y, z = c; gsum = 0
            for dy in (1, -1):
                r = cellmap.get((x, y + dy, z))
                if r is None or r in Gset or not alive[r]: continue
                if dy == 1 or not scope.is_tile(P[r]["num"]): gsum += 1
            return gsum
        for rnd in range(per_layer):
            for y in layers:
                cand = []
                for (x, yy, z) in list(region):
                    if yy != y: continue
                    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        n = (x + dx, y, z + dz)
                        if n in region: continue
                        r = cellmap.get(n)
                        if r is None or r in Gset or not alive[r] or P[r]["sub"] is not None: continue
                        same = P[r]["c"] == gcol
                        if not same and not hidden(n): continue
                        cand.append((gain(n), same, n))
                cand = [t for t in cand if t[0] > 0]
                if not cand: continue
                cand.sort(key=lambda t: (-t[0], not t[1])); n = cand[0][2]
                chosen.append(n); region.add(n); gain_total += cand[0][0]
        if not chosen:
            log["r2"].append(dict(groupe=g["id"], parties=g["parties"], force_avant_N=g["force_N"], tenons_avant=g["tenons"], decision="aucune cellule voisine utilisable (couleur et cellules cachees)", cellules_ajoutees=0)); continue
        # V12.1 : when the full set of bridge cells cuts an existing link between columns, the set is shortened (last cell chosen first) until the model stays connected
        done = None
        global TILE_MODE
        attempts = [(len(chosen), 0)] if not shorten else [(k_, m_) for k_ in sorted({len(chosen), max(1, len(chosen) // 2), 1}, reverse=True) for m_ in (0, 1, 2, 3)]
        for keep, TILE_MODE in attempts:
            sub = chosen[:keep]; reg = set(Gcells)
            for c_ in sub: reg.add(c_)          # same insertion history as the historical region set : same part order in the output
            by_layer = defaultdict(set)
            for (x, y, z) in reg: by_layer[y].add((x, z))
            removed_ids = set(); new = []
            for y, cells in by_layer.items():
                owners = {cellmap[(x, y, z)] for (x, z) in cells if (x, y, z) in cellmap}
                owners = {r for r in owners if not (r in Gset and P[r]["c"] != gcol)}
                removed_ids |= owners
                left = defaultdict(set)
                for r in owners:
                    for c in pcells[r]:
                        if (c[0], c[2]) not in cells: left[P[r]["c"]].add((c[0], c[2]))
                gl = {(c[0], c[2]) for c in Gcells if c[1] == y}
                new += tile_bridging(cells, gl, y, gcol)
                for col, cs in left.items(): new += tile_cells(cs, y, col)
            n0 = len(P)
            for r in removed_ids: alive[r] = False
            for p in new: p["raw"] = line_of(p); P.append(p); alive.append(True)
            if ungrounded(P, alive) > base_ung:
                for r in removed_ids: alive[r] = True
                for _ in new: P.pop(); alive.pop()
                continue
            done = (sub, by_layer, removed_ids, new, n0); break
        TILE_MODE = 0
        if done is None:
            log["r2"].append(dict(groupe=g["id"], parties=g["parties"], force_avant_N=g["force_N"], tenons_avant=g["tenons"], decision="annule : une liaison entre colonnes etait coupee (connectivite)", cellules_ajoutees=len(chosen))); continue
        chosen, by_layer, removed_ids, new, n0 = done
        for k_, p in enumerate(new):
            newparts.append(n0 + k_); cs = lattice_cells(p); pcells[n0 + k_] = cs
            for c in cs: cellmap[c] = n0 + k_
        for r in removed_ids: pcells.pop(r, None)
        log["r2"].append(dict(groupe=g["id"], parties=g["parties"], force_avant_N=g["force_N"], tenons_avant=g["tenons"], cellules_ajoutees=len(chosen), gain_tenons_estime=gain_total,
                              pieces_retirees=len(removed_ids), pieces_ajoutees=len(new), couches=sorted(by_layer), cellules=[list(map(int, c)) for c in chosen], decision="applique"))
    # ------------------------------------------------------------------ write (original lines for untouched parts, original order, new parts appended)
    out, k = [], 0
    for l in lines:
        t = l.split()
        if t and t[0] == "1" and len(t) >= 15:
            if alive[k]: out.append(l)
            k += 1
        else: out.append(l)
    out += ["0 BRICKIFY V9 RENFORTS"] + [line_of(P[i]) for i in newparts if alive[i]] + ["0 STEP"]
    open(dst, "w").write("\n".join(out) + "\n")
    log["pieces_avant"] = k; log["pieces_apres"] = sum(1 for l in out if l.startswith("1 "))
    json.dump(log, open(logf, "w"), indent=1, ensure_ascii=False, default=str)
    print(json.dumps({"r1": log["r1"].get("decision"), "groupes_traites": len(log["r2"]), "pieces": (log["pieces_avant"], log["pieces_apres"])}))

if __name__ == "__main__":
    main()
