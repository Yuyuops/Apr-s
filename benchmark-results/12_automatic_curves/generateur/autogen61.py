"""LEGO V6.1: same generator as V6 (autogen.py), with a new selection of the shaped parts on the contour.

Only the selection step changes (layout); extraction, catalogue, interior, V5.1 rules, fixation and checks are the
ones of V6, imported unchanged. New selection:
  1. arcs: connected runs of boundary pixels classified "arc" by the contour analysis, with their median radius;
     an arc is "characteristic" when it is at least 60 LDU long;
  2. candidates: every catalogue part x turn x stud position whose slanted or curved edge lies on the target boundary
     (tolerance 2 px = 8 LDU, 3 px for rounded parts); each candidate claims only the cells its REAL solid touches
     (not its box: the validator v3 tests rounded and wedge plates on their real solid);
  3. score of a candidate: gain over plain stud cells (agreement - 2 x excess - 2 x target area left empty in its
     cells) + bonus for each arc pixel followed by its edge;
  4. combination: integer programme (scipy milp) over all candidates at once, one part per cell, with for every
     characteristic arc a binary "arc lost" variable heavily penalised unless half of the arc is followed by the
     edges of the chosen parts. The interior is then filled as in V6.
No model-specific rule, no list of positions: same code and same catalogue for every contour.
usage: autogen61.py <target_name> <outdir> [--head]
"""
import json, os, sys
import numpy as np
from scipy import ndimage
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix
sys.path.insert(0, os.path.expanduser("~/bench/proto/ear11"))
import autogen as A6
import contour as CT
D = A6.D
V0 = A6.V0
ROUNDED = {"22888", "30565", "30357", "6003", "2450"}
W_ARC = 3.0            # bonus per arc pixel followed by a part edge
P_ARC_LOST = 400.0     # penalty when a characteristic arc is not represented
MIN_ARC_PX = 15        # characteristic arc: >= 15 boundary pixels (60 LDU)

def arc_segments(T, ia0, ib0):
    feats, summ, B = CT.analyse(T, ia0 * 4.0, ib0 * 4.0, res=4.0)
    pts = np.argwhere(B)
    arc = np.zeros_like(B)
    rad = {}
    for (a, b), f in zip(pts, feats):
        if f["kind"] == "arc" and f["radius"] is not None and f["radius"] < 300:
            arc[a, b] = True; rad[(a, b)] = f["radius"]
    lab, n = ndimage.label(arc, structure=np.ones((3, 3)))
    excl = getattr(A6, "LAST_EXCLUDED", set())        # skull and forbidden pixels: their border is not an ear contour
    segs = []
    for k in range(1, n + 1):
        px = [tuple(p) for p in np.argwhere(lab == k)]
        px = [p for p in px if not any((p[0] + ia0 + dx, p[1] + ib0 + dy) in excl for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2))]
        if len(px) < 4: continue
        r = float(np.median([rad[p] for p in px]))
        segs.append(dict(pixels={(a + ia0, b + ib0) for a, b in px}, radius=r, length_ldu=len(px) * 4.0,
                         characteristic=len(px) >= MIN_ARC_PX))
    return segs

def layout61(T, ia0, ib0, cat, gain_min, tol, fill_thr, plates_ok=True):
    NA, NB = T.shape
    Tset = {(ia0 + a, ib0 + b) for a, b in np.argwhere(T)}
    Bt = T & ~ndimage.binary_erosion(T); dist = ndimage.distance_transform_edt(~Bt)
    segs = arc_segments(T, ia0, ib0)
    arcpix = {}
    for s_i, s in enumerate(segs):
        for p in s["pixels"]: arcpix[p] = s_i
    cov = {}
    for (a, b) in Tset:
        c = A6.cell_of_pixel(a, b); cov[c] = cov.get(c, 0) + 1
    def cell_pixels(i, k):
        a0 = 5 * i; b0 = (V0 + 20 * k) // 4
        return {(a0 + x, b0 + y) for x in range(5) for y in range(5)}
    plain_cells = {c for c, n in cov.items() if n >= 13}
    imin = min(c[0] for c in cov) - 2; imax = max(c[0] for c in cov) + 2
    kmin = min(c[1] for c in cov) - 2; kmax = max(c[1] for c in cov) + 2
    cands = []
    for it in cat:
        t_ = tol + (1.0 if it["num"] in ROUNDED else 0.0)
        for i0 in range(imin, imax + 1):
            for k0 in range(kmin, kmax + 1):
                F = it["F"] + [5 * i0, 5 * k0]; e = it["edge"] + [5 * i0, 5 * k0]
                ea = e[:, 0] - ia0; eb = e[:, 1] - ib0
                if (ea < 0).any() or (eb < 0).any() or (ea >= NA).any() or (eb >= NB).any(): continue
                de = dist[ea, eb]
                if de.mean() > t_ or (de <= t_ + 1).mean() < 0.6: continue
                Fs = {tuple(p) for p in F}
                agree = len(Fs & Tset); extra = len(Fs) - agree
                cells = {}
                for p in Fs: c = A6.cell_of_pixel(*p); cells[c] = cells.get(c, 0) + 1
                P = set().union(*[cell_pixels(*c) for c in cells if c in plain_cells]) if any(c in plain_cells for c in cells) else set()
                plain = len(P & Tset) - 2 * len(P - Tset)
                cellpix = set().union(*[cell_pixels(*c) for c in cells])
                hole = len((cellpix & Tset) - Fs)
                gain = (agree - 2 * extra - 2 * hole) - plain
                full_even = [c for c, n in cells.items() if n >= 25 and c[1] % 2 == 0]
                if not full_even: continue
                # arc pixels followed by the slanted/curved edge (within 2 px)
                follow = {}
                ef = {tuple(p) for p in e}
                for p in ef:
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            q = (p[0] + dx, p[1] + dy)
                            if q in arcpix: follow.setdefault(arcpix[q], set()).add(q)
                bonus = W_ARC * sum(len(v) for v in follow.values())     # used only to admit the candidate
                score = gain + bonus
                if gain >= gain_min or (bonus > 0 and gain > -40):
                    cands.append(dict(score=score, gain=gain, num=it["num"], r=it["r"], i0=i0, k0=k0, cells=frozenset(cells), F=Fs,
                                      follow={s: len(v) for s, v in follow.items()}, followpix=set().union(*follow.values()) if follow else set()))
    layout61.cands = cands
    # ---- integer programme: one part per cell; characteristic arcs heavily penalised when lost
    chosen = []
    if cands:
        cell_ids = {}
        for c in cands:
            for cc in c["cells"]: cell_ids.setdefault(cc, len(cell_ids))
        char = [s_i for s_i, s in enumerate(segs) if s["characteristic"]]
        apx = sorted(set().union(*[c["followpix"] for c in cands]))             # arc pixels that some candidate follows
        aid = {p: k for k, p in enumerate(apx)}
        nx_, na_, ny_ = len(cands), len(apx), len(char)
        nv = nx_ + na_ + ny_
        # maximise sum(gain_j x_j) + W_ARC * sum(z_p) - P_ARC_LOST * sum(y_s)
        cobj = np.r_[-np.array([c["gain"] for c in cands], float), -W_ARC * np.ones(na_), P_ARC_LOST * np.ones(ny_)]
        nrow = len(cell_ids) + na_ + ny_
        A = lil_matrix((nrow, nv)); lbs = []; ubs = []
        for j, c in enumerate(cands):
            for cc in c["cells"]: A[cell_ids[cc], j] = 1
        lbs += [-np.inf] * len(cell_ids); ubs += [1.0] * len(cell_ids)
        r0 = len(cell_ids)
        for j, c in enumerate(cands):                                          # z_p <= sum of the candidates following p
            for p in c["followpix"]: A[r0 + aid[p], j] = -1
        for k in range(na_): A[r0 + k, nx_ + k] = 1
        lbs += [-np.inf] * na_; ubs += [0.0] * na_
        r1 = r0 + na_
        for r_, s_i in enumerate(char):                                        # half of each characteristic arc followed, or y_s = 1
            pix = segs[s_i]["pixels"]; n_s = len(pix)
            for p in pix:
                if p in aid: A[r1 + r_, nx_ + aid[p]] = 1
            A[r1 + r_, nx_ + na_ + r_] = n_s
            lbs.append(0.5 * n_s); ubs.append(np.inf)
        res = milp(cobj, constraints=LinearConstraint(A.tocsr(), np.array(lbs), np.array(ubs)), integrality=np.ones(nv),
                   bounds=Bounds(0, 1), options=dict(time_limit=30))
        x = np.round(res.x).astype(int) if res.x is not None else np.zeros(nx_ + ny_, int)
        lost = [segs[s_i] for r_, s_i in enumerate(char) if x[nx_ + na_ + r_]]
        for j, c in enumerate(cands):
            if x[j]: chosen.append((c["num"], c["r"], int(c["i0"]), int(c["k0"]), f"forme {c['num']} (score {c['score']:.0f})"))
        claimed = set().union(*[c["cells"] for j, c in enumerate(cands) if x[j]]) if x[:nx_].any() else set()
        layout61.last = dict(candidates=len(cands), characteristic_arcs=[dict(radius=round(segs[s]["radius"]), length_ldu=segs[s]["length_ldu"]) for s in char],
                             arcs_lost=len(lost), milp_status=int(res.status))
    else:
        claimed = set(); layout61.last = dict(candidates=0)
    # ---- interior: unchanged rule of V6 (largest rectangles on joint rows, 4 scan orders)
    free0 = {c for c, n in cov.items() if n >= fill_thr * 25} - claimed
    sizes = []
    for (L, W), num in A6.BP.PLATES.items():
        if A6.BP.available(num, 0):
            sizes.append((L, W, num, 0))
            if L != W: sizes.append((W, L, num, 1))
    sizes.sort(key=lambda s: -s[0] * s[1])
    best_pack = None
    for key in [lambda c: (c[1], c[0]), lambda c: (-c[1], c[0]), lambda c: (c[1], -c[0]), lambda c: (-c[1], -c[0])]:
        free = set(free0); rects_ = []
        while True:
            best = None
            for (w, h, num, rr) in sizes:
                for (i, k) in sorted(free, key=key):
                    blk = {(i + x_, k + y_) for x_ in range(w) for y_ in range(h)}
                    if not blk <= free: continue
                    if h == 1 and k % 2: continue
                    best = (w, h, num, rr, i, k, blk); break
                if best: break
            if not best: break
            w, h, num, rr, i, k, blk = best; free -= blk
            rects_.append((num, 0 if w >= h else 1, int(i), int(k), f"plaque {w}x{h}"))
        sc = (len(free), len(rects_))
        if best_pack is None or sc < best_pack[0]: best_pack = (sc, rects_, set(free))
    _, rects, free = best_pack
    return chosen, rects, len(free)

if __name__ == "__main__":
    A6.layout = layout61                     # the only replaced step
    # keep the per-setting information of the integer programme in the report
    _orig_layout = layout61
    log = []
    def logged(*a, **k):
        out = _orig_layout(*a, **k); log.append(dict(layout61.last)); return out
    A6.layout = logged
    A6.main()
    outdir = sys.argv[2]; name = f"oreille_{sys.argv[1]}"
    p = os.path.join(outdir, f"{name}_report.json"); r = json.load(open(p))
    r["selection"] = "V6.1: programme en nombres entiers (milp) sur les candidats de contour, arcs caracteristiques penalises"
    r["milp_runs"] = log
    json.dump(r, open(p, "w"), indent=1, default=str)
