"""LEGO V9.1 - R3 "seam stitching" for the faces of a SNOT-sandwich ear (generic, no coordinates of Paco).

An ear is a sandwich: outer face (plates whose studs point outward) + tiles on those studs, a one-stud core, and the mirrored inner face. A fragile group at the edge of an ear is
a cap of face plates that touches its neighbour plates only along a seam (two plates side by side in the same plane are not mechanically linked). The tiles lie on the studs of
the face plates : a tile that covers one stud of each plate on both sides of a seam LINKS the two plates with real stud joints (a joint offset from the plate seam).
For every fragile group of the ear : find the cell pairs (a in a tile of the group, b in a tile outside the group) that are neighbours in the same face layer, choose a spread-out
set of them in each layer (outer and inner), replace the two tiles involved by a 1 x 2 tile covering exactly the pair and re-tile the rest of the two tiles with 1 x k tiles
(k in 1, 2, 3, 4, 6, the references already used by the generator). The covered cells, the colours and the surface are identical (same cells, same colour : checked by scope.py).
usage: stitch.py <in.ldr> <weak.json> <out.ldr> <log.json> [n_per_layer=3]
"""
import json, os, sys
import numpy as np
from collections import Counter, defaultdict
sys.path.insert(0, os.path.expanduser("~/bench/tools")); sys.path.insert(0, os.path.expanduser("~/bench/proto/v9"))
import conn, notice_plan as N

TILE_SET_ALL = set()
TILE_LEN = {"3070b": 1, "3069b": 2, "63864": 3, "2431": 4, "6636": 6}
LEN_NUM = {v: k for k, v in TILE_LEN.items()}
PITCH = 20.0

def fmt(v):
    s = ("%.4f" % v).rstrip("0").rstrip("."); return "0" if s in ("-0", "") else s

def line_of(colour, M, o, num):
    return "1 %d %s %s %s %s %s %s %s %s %s %s %s %s %s.dat" % (colour, *[fmt(x) for x in o], *[fmt(x) for x in np.asarray(M).ravel()], num.upper() if num.isdigit() is False and False else num)

def ear_frame(P, ids):
    c = Counter(tuple(np.round(P[i]["M"].ravel(), 3)) for i in ids if abs(P[i]["M"][1, 1] - 1) < 1e-6)
    if not c: return None
    return np.array(c.most_common(1)[0][0]).reshape(3, 3)

class Layer:
    pass

def rotations():
    """the 24 proper rotations with entries 0, +-1"""
    import itertools
    out = []
    for perm in itertools.permutations(range(3)):
        for sg in itertools.product((1, -1), repeat=3):
            M = np.zeros((3, 3))
            for r, (c, s) in enumerate(zip(perm, sg)): M[r, c] = s
            if abs(np.linalg.det(M) - 1) < 1e-6: out.append(M)
    return out
ROT = rotations()

def stitch_ear(P, G, sub, groups, n_per_layer, lines_out, log):
    ids = [p["i"] for p in P if p["sub"] == sub]
    R = ear_frame(P, ids)
    if R is None: return
    loc = {}
    for i in ids:
        p = P[i]; Ml = R.T @ p["M"]; ol = R.T @ p["o"]; st, rc, lo, hi = conn.world(p["num"], Ml, ol); loc[i] = (Ml, ol, lo, hi)
    tiles = [i for i in ids if P[i]["num"] in TILE_LEN and abs((loc[i][3][2] - loc[i][2][2]) - 8) < 0.6 and
             np.all(np.isclose(np.abs(loc[i][0]), 0, atol=1e-3) | np.isclose(np.abs(loc[i][0]), 1, atol=1e-3))]
    if not tiles: return
    TILE_SET_ALL.clear(); TILE_SET_ALL.update(i for i in ids if P[i]["num"] in TILE_LEN)
    X0 = Counter(round(loc[i][2][0] % PITCH, 1) for i in tiles).most_common(1)[0][0]; Y0 = Counter(round(loc[i][2][1] % PITCH, 1) for i in tiles).most_common(1)[0][0]
    def cells(i):
        lo, hi = loc[i][2], loc[i][3]; a = np.round((lo[0] - X0) / PITCH).astype(int); b = np.round((hi[0] - X0) / PITCH).astype(int)
        c = np.round((lo[1] - Y0) / PITCH).astype(int); d = np.round((hi[1] - Y0) / PITCH).astype(int)
        return {(x, y) for x in range(a, b) for y in range(c, d)}
    layer_of = {i: int(round(loc[i][2][2])) for i in tiles}
    def plate_of(L, c):
        """face plate (not a tile, 8 ldu thick in the panel normal) that carries the stud cell c of tile layer L : the plate right under the tile layer on the core side"""
        cx = X0 + (c[0] + 0.5) * PITCH; cy = Y0 + (c[1] + 0.5) * PITCH
        for j in ids:
            if j in TILE_SET_ALL: continue
            lo, hi = loc[j][2], loc[j][3]
            if abs((hi[2] - lo[2]) - 8) > 0.6: continue
            if not (lo[2] - 0.6 <= L + 8 + 8 and abs(lo[2] - (L + 8)) < 0.6 or abs(hi[2] - (L)) < 0.6): continue
            if lo[0] <= cx <= hi[0] and lo[1] <= cy <= hi[1]: return j
        return None
    fam = defaultdict(set)
    for g in groups:
        for i in g["parts_ids"]: fam[i].add(g["id"])
    cell_tile = {}
    for i in tiles:
        for c in cells(i): cell_tile[(layer_of[i], c)] = i
    pseudo = [100000]; colour_of = {i: P[i]["c"] for i in ids}
    for g in groups:
        gid = g["id"]; gset = {i for i in list(tiles) + list(ids) if gid in fam.get(i, ())}
        if not any(i in gset for i in ids): continue
        gt = [i for i in tiles if i in gset]
        if not gt: log.append(dict(groupe=g["id"], sub=sub, resultat="aucune tuile dans le groupe")); continue
        # candidate pairs per layer : (cell in a group tile, neighbour cell in a non-group tile)
        per_layer = defaultdict(list)
        for i in gt:
            for (x, y) in cells(i):
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    j = cell_tile.get((layer_of[i], (x + dx, y + dy)))
                    if j is not None and j not in gset:
                        pa = plate_of(layer_of[i], (x, y)); pb = plate_of(layer_of[i], (x + dx, y + dy))
                        if pa is not None and pb is not None and pa != pb: per_layer[layer_of[i]].append(((x, y), (x + dx, y + dy), i, j))
        chosen = []
        for L, pairs in per_layer.items():
            # spread : farthest-point selection
            sel = []
            pairs = sorted(pairs, key=lambda t: (t[0][0], t[0][1]))
            def far(p_, s): return max(abs(p_[0][0] - s[0][0]), abs(p_[0][1] - s[0][1]), abs(p_[1][0] - s[1][0]), abs(p_[1][1] - s[1][1]))
            while len(sel) < n_per_layer and pairs:
                cand = pairs[0] if not sel else max(pairs, key=lambda p_: min(far(p_, s) for s in sel))
                sel.append(cand); pairs = [p_ for p_ in pairs if min(far(p_, s) for s in sel) >= 2]
            chosen += [(L,) + s for s in sel]
        if not chosen: log.append(dict(groupe=g["id"], sub=sub, resultat="aucun joint de plaques voisin dans une face")); continue
        removed = set(); new = []
        stitch_cells = defaultdict(set)
        for (L, a, b, ia, ib) in chosen:
            removed |= {ia, ib}; stitch_cells[L] |= {a, b}
        for L, sc in stitch_cells.items():
            pass
        # stitch tiles
        def make_tile(L, cs, ref):
            """a tile (num by length) covering the cells cs (a straight line of cells) in layer L, oriented like the reference tile ref for its normal"""
            cs = sorted(cs); k = len(cs); num = LEN_NUM[k]
            x0, y0 = cs[0]; x1, y1 = cs[-1]
            lo = np.array([X0 + x0 * PITCH, Y0 + y0 * PITCH, loc[ref][2][2]]); hi = np.array([X0 + (x1 + 1) * PITCH, Y0 + (y1 + 1) * PITCH, loc[ref][3][2]])
            up_ref = loc[ref][0] @ np.array([0, -1.0, 0])
            best = None
            for Mr in ROT:
                if not np.allclose(Mr @ np.array([0, -1.0, 0]), up_ref, atol=1e-3): continue
                st, rc, l0, h0 = conn.world(num, Mr, np.zeros(3))
                if np.allclose(h0 - l0, hi - lo, atol=0.6): best = (Mr, lo - l0); break
            if best is None: return None
            return dict(num=num, Ml=best[0], ol=best[1], layer=L, cells=set(cs), colour=(P[ref]["c"] if ref < 100000 else colour_of[ref]), ref=ref)
        ok = True
        for (L, a, b, ia, ib) in chosen:
            t = make_tile(L, [a, b], ia)
            if t is None: ok = False; break
            new.append(t)
        if not ok: log.append(dict(groupe=g["id"], sub=sub, resultat="orientation de tuile introuvable")); continue
        # leftover cells of removed tiles, re-tiled along their own long axis
        for i in sorted(removed):
            cs = cells(i); L = layer_of[i]; stc = stitch_cells[L]
            left = sorted(cs - stc)
            if not left: continue
            xs = sorted({c[0] for c in cs}); ys = sorted({c[1] for c in cs}); horizontal = len(xs) >= len(ys)
            runs = []; cur = []
            for c in sorted(left, key=(lambda c: (c[1], c[0])) if horizontal else (lambda c: (c[0], c[1]))):
                if cur and ((horizontal and c[1] == cur[-1][1] and c[0] == cur[-1][0] + 1) or (not horizontal and c[0] == cur[-1][0] and c[1] == cur[-1][1] + 1)): cur.append(c)
                else:
                    if cur: runs.append(cur)
                    cur = [c]
            if cur: runs.append(cur)
            for run in runs:
                k = 0
                while k < len(run):
                    for ln in (6, 4, 3, 2, 1):
                        if k + ln <= len(run): break
                    t = make_tile(L, run[k:k + ln], i); new.append(t); k += ln
        # sanity : the cells covered by new tiles equal the cells of the removed tiles
        before = Counter(); after = Counter()
        for i in removed:
            for c in cells(i): before[(layer_of[i], c)] += 1
        for t in new:
            for c in t["cells"]: after[(t["layer"], c)] += 1
        if before != after: log.append(dict(groupe=g["id"], sub=sub, resultat="couverture differente, abandonne")); continue
        n_stitch = len(chosen); stitch_ids = []
        for i in removed:
            if i < 100000: lines_out["remove"].add(i)
            else: lines_out["add"][sub].pop(i, None)
            tiles.remove(i)
            for c in cells(i): cell_tile.pop((layer_of[i], c), None)
        for k_, t in enumerate(new):
            pid = pseudo[0]; pseudo[0] += 1
            Mw = R @ t["Ml"]; ow = R @ t["ol"]
            lines_out["add"][sub][pid] = dict(colour=t["colour"], M=Mw, o=ow, num=t["num"])
            st_, rc_, lo_, hi_ = conn.world(t["num"], t["Ml"], t["ol"]); loc[pid] = (t["Ml"], t["ol"], lo_, hi_); layer_of[pid] = t["layer"]
            tiles.append(pid); colour_of[pid] = t["colour"]
            fam[pid] = {gid} if k_ < n_stitch else set(fam.get(t["ref"], ()))
            for c in t["cells"]: cell_tile[(t["layer"], c)] = pid
            if k_ < n_stitch: stitch_ids.append(pid)
        log.append(dict(groupe=g["id"], sub=sub, resultat="tuiles a cheval sur les joints", couples=[dict(couche=L, cellules=[list(a), list(b)]) for (L, a, b, ia, ib) in chosen],
                        tuiles_retirees=len(removed), tuiles_ajoutees=len(new), tuiles_a_cheval=len(chosen)))

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; src, weakf, out, logf = args[:4]; nper = int(args[4]) if len(args) > 4 else 3
    P = N.parse(src); G = N.build_graph(P); W = json.load(open(weakf))["groupes"]
    ALL = "--all" in sys.argv
    groups = [g for g in W if (list(g["sous_ensemble"])[0].startswith("V7_oreille") or ALL) and g["parties"] <= 100]
    lines_out = dict(remove=set(), add=defaultdict(dict)); log = []
    subs = sorted({p["sub"] for p in P if p["sub"]}) if not ALL else [None]
    for sub in subs:
        stitch_ear(P, G, sub, [g for g in groups if ALL or list(g["sous_ensemble"])[0] == sub], nper, lines_out, log)
    # rewrite the file : drop removed parts, add the new tiles at the end of each ear block
    raw = open(src, encoding="utf-8", errors="replace").read().split("\n"); out_l = []; idx = 0; cur = None
    def end_block(sub):
        for t in lines_out["add"].get(sub, {}).values(): out_l.append("1 %d %s %s %s %s %s %s %s %s %s %s %s %s %s.dat" % (t["colour"], *[fmt(x) for x in t["o"]], *[fmt(x) for x in t["M"].ravel()], t["num"]))
    for l in raw:
        t = l.split()
        if len(t) > 4 and t[0] == "0" and t[1] == "BRICKIFY" and t[2] == "SUBASSEMBLY":
            if t[3] == "END": end_block(cur); cur = None
            else: cur = t[4]
            out_l.append(l); continue
        if t and t[0] == "1" and len(t) >= 15:
            if idx in lines_out["remove"]: idx += 1; continue
            idx += 1
        out_l.append(l)
    if None in lines_out["add"]: end_block(None)
    open(out, "w").write("\n".join(out_l))
    json.dump(log, open(logf, "w"), indent=1, default=str)
    for e in log: print(e["groupe"], e["sub"], e["resultat"], e.get("tuiles_retirees"), e.get("tuiles_ajoutees"), e.get("tuiles_a_cheval"))

if __name__ == "__main__":
    main()
