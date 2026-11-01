#!/usr/bin/env python3
"""Independent, orientation-free audit of an LDraw model (v2). Does not reuse the generator's own checks.

* joints: a stud of part A (base point on A's face, outward axis, from the LDraw geometry, tools/conn.py) coincides
  (within 1 LDU) with a receptor of part B whose receiving-face normal is opposite. Works for SNOT and brackets.
* collisions: body boxes (studs excluded) rasterised on a 4-LDU grid; plus studs that do not enter a receptor and
  whose tip lies inside another part's solid ("blocked studs").
* support plane: parts whose body reaches the lowest plane of the model are grounded (here: the cut at the neck).
* build order: in file order, every part must connect to an already placed part (or the support plane). Parts between
  "0 BRICKIFY SUBASSEMBLY BEGIN <name>" and "... END" are built apart (first part free), and the finished
  sub-assembly must then connect to the placed model.
* catalogue: Rebrickable part x colour statistics (rb.db).
* numerical stability (indicative, NOT a strength guarantee): for every frame (stud direction) and every plane
  between layers of that frame, each sub-assembly that holds only through stud joints at that plane is checked
  (a) under its own weight, (b) against a force at its far end. Model: rigid parts; each stud resists pull-out
  with F_CLUTCH (assumed 1.0 N, conservative; measured values on new bricks are typically 1-4 N and drop with wear,
  colour batch and temperature); compression is free; rotation about an edge of the stud polygon is resisted by
  F_CLUTCH x distance of each stud to that edge (+ stud radius). Mass 0.10 g per stud x stud x plate of solid.
  Friction of side-by-side parts, clamping and play are ignored.
* fidelity (optional --npz): every part is rasterised from its real shape onto the fine grid of the mesh.
"""
import argparse, csv, json, math, os, re, sqlite3, sys
from collections import Counter, defaultdict
import numpy as np, networkx as nx
from scipy.spatial import ConvexHull
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ldr_expand import ldconfig
import conn, partlib as PL

F_CLUTCH, G_ACC, R_STUD_MM, G_PER_LDU3 = 1.0, 9.81, 2.4, 0.10 / (20 * 20 * 8)

def norm_name(s): return re.sub(r"[^a-z]", "", s.lower()).replace("grey", "gray")

def read(ldr):
    parts, step, sub = [], 0, None
    for line in open(ldr, encoding="utf-8", errors="replace"):
        t = line.split()
        if not t: continue
        if t[0] == "0":
            if len(t) > 1 and t[1] == "STEP": step += 1
            if len(t) > 3 and t[1] == "BRICKIFY" and t[2] == "SUBASSEMBLY":
                sub = t[4] if t[3] == "BEGIN" else None
            continue
        if t[0] == "1" and len(t) >= 15:
            parts.append(dict(c=int(t[1]), o=np.array(t[2:5], float), M=np.array(t[5:14], float).reshape(3, 3),
                              num=t[14].lower().replace(".dat", ""), step=step, sub=sub))
    return parts, step + 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ldr", required=True); ap.add_argument("--ldraw", required=True); ap.add_argument("--rbdb", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--name", required=True); ap.add_argument("--npz")
    a = ap.parse_args(); os.environ.setdefault("LDRAW", a.ldraw)
    cols = ldconfig(os.path.join(a.ldraw, "LDConfig.ldr"))
    P, nsteps = read(a.ldr)
    for i, p in enumerate(P):
        p["i"] = i
        st, rc, lo, hi = conn.world(p["num"], p["M"], p["o"])
        p["studs"], p["recv"], p["lo"], p["hi"] = st, rc, lo, hi
        p["fill"] = conn.part(p["num"])["fill"]
        Cp = conn.part(p["num"]); p["mass"] = float(np.prod(Cp["hi"] - Cp["lo"])) * p["fill"] * G_PER_LDU3   # own box (not the rotated AABB)
        p["up"] = tuple(np.round(p["M"] @ np.array([0, -1.0, 0]), 3))            # local up (stud side) in world
        p["aligned"] = bool(np.all(np.isclose(np.abs(p["M"]), 0, atol=1e-4) | np.isclose(np.abs(p["M"]), 1, atol=1e-4)))
        if "bracket" in PL.title(p["num"]).lower(): p["aligned"] = False      # L-shaped: its box is not its solid
    lo_all = np.min([p["lo"] for p in P], 0); hi_all = np.max([p["hi"] for p in P], 0)
    lo_all = np.floor(lo_all / 4.0) * 4.0 - 4.0      # grid origin on a 4-LDU multiple: right-angle boxes fall on cell edges
    # ---------------- collisions on a 4-LDU grid
    g = 4.0
    idx = lambda v: np.round((v - lo_all) / g).astype(int)
    shape = idx(hi_all) + 1
    owner = -np.ones(shape, np.int32); overlaps = Counter()
    for p in P:
        if not p["aligned"]: continue
        a0, a1 = idx(p["lo"]), idx(p["hi"])
        sl = owner[a0[0]:a1[0], a0[1]:a1[1], a0[2]:a1[2]]
        for q in np.unique(sl[sl >= 0]): overlaps[tuple(sorted((int(q), p["i"])))] += int((sl == q).sum())
        sl[sl < 0] = p["i"]
    # parts at non-right angles: points of their real solid (>= 1 LDU inside their faces) tested exactly against the
    # boxes of right-angle parts and, by proximity (< 1.5 LDU), against the solid points of the other angled parts
    from scipy.spatial import cKDTree
    rot = [p for p in P if not p["aligned"]]
    rpts = {p["i"]: conn.solid_points(p["num"]) @ p["M"].T + p["o"] for p in rot}
    for p in rot:
        pts = rpts[p["i"]]
        k = np.floor((pts - lo_all) / g).astype(int); ok = np.all((k >= 0) & (k < shape), axis=1)
        cand = set()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    kk = k[ok] + [dx, dy, dz]; kk = kk[np.all((kk >= 0) & (kk < shape), axis=1)]
                    cand |= set(np.unique(owner[tuple(kk.T)]).tolist())
        for q in cand - {-1}:
            Q = P[q]; inside = np.all((pts > Q["lo"] + 1e-6) & (pts < Q["hi"] - 1e-6), axis=1)
            if inside.any(): overlaps[tuple(sorted((int(q), p["i"])))] += int(inside.sum())
    for a_ in range(len(rot)):
        ta = cKDTree(rpts[rot[a_]["i"]])
        for b_ in range(a_ + 1, len(rot)):
            pa, pb = rot[a_], rot[b_]
            if np.any(pa["hi"] < pb["lo"] - 2) or np.any(pb["hi"] < pa["lo"] - 2): continue
            dd, _ = ta.query(rpts[pb["i"]], distance_upper_bound=1.5)
            nclash = int(np.isfinite(dd).sum())
            if nclash: overlaps[tuple(sorted((pa["i"], pb["i"])))] += nclash
    allowed_pairs = set()
    for p in P:
        if p["num"] != "3679": continue
        for q in P:
            if q["num"] == "3680" and np.linalg.norm(q["o"] - p["o"]) < 1.0 and abs(p["M"][1, 1] - 1) < 1e-4 and np.allclose(p["M"][1], [0, 1, 0], atol=1e-4):
                allowed_pairs.add(tuple(sorted((p["i"], q["i"]))))
    overlaps = Counter({k: v for k, v in overlaps.items() if k not in allowed_pairs})
    # ---------------- joints
    rindex = defaultdict(list)
    for p in P:
        for (pt, n) in p["recv"]:
            rindex[tuple(np.round(pt).astype(int))].append((p["i"], n))
    G = nx.Graph(); G.add_nodes_from(p["i"] for p in P)
    blocked = 0
    for p in P:
        for (pt, ax) in p["studs"]:
            key = np.round(pt).astype(int); hit = None
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        for (q, n) in rindex.get((key[0] + dx, key[1] + dy, key[2] + dz), []):
                            if q != p["i"] and np.dot(n, ax) < -0.9: hit = q
            if hit is not None:
                if G.has_edge(p["i"], hit): G[p["i"]][hit]["contacts"].append((pt, ax, p["i"]))
                else: G.add_edge(p["i"], hit, contacts=[(pt, ax, p["i"])])
            else:
                tip = pt + 2.0 * ax
                k = idx(tip)
                if np.all(k >= 0) and np.all(k < shape):
                    q = owner[tuple(k)]
                    if q >= 0 and q != p["i"]:
                        # inside the other part's box: blocked only if inside its real solid
                        Q = P[q]; loc = Q["M"].T @ (tip - Q["o"]); S = conn.part(Q["num"])
                        sol = S["solid"]; ix = int((loc[0] - S["plo"][0]) // 5); iy = int((S["phi"][1] - loc[1]) // 2); iz = int((loc[2] - S["plo"][2]) // 5)
                        if 0 <= ix < sol.shape[0] and 0 <= iy < sol.shape[1] and 0 <= iz < sol.shape[2] and sol[ix, iy, iz]: blocked += 1
    for (a_, b_) in allowed_pairs:     # turntable 2x2: top clicked on base, free rotation about the vertical axis
        G.add_edge(a_, b_, contacts=[(P[a_]["o"] + np.array([0, 8.0, 0]), np.array([0, -1.0, 0]), b_ if P[b_]["num"] == "3680" else a_)], kind="turntable")
    for u, v, d in G.edges(data=True): d["studs"] = len(d["contacts"])
    # ---------------- support plane, disconnected parts, islands
    base_y = hi_all[1]
    ground = {p["i"] for p in P if abs(p["hi"][1] - base_y) < 0.5}
    grounded = set()
    for gi in ground:
        if gi not in grounded: grounded |= nx.node_connected_component(G, gi)
    disconnected = [p["i"] for p in P if p["i"] not in grounded]
    comps = list(nx.connected_components(G)); islands = [c for c in comps if not (c & ground)]
    # ---------------- build order
    placed = set(); unsupported = []; sub_fail = []; cur = None; block = []
    def connects(i, pool): return any(j in pool for j in G.neighbors(i))
    for p in P + [dict(i=None, sub=None)]:
        if cur is not None and p["sub"] != cur:            # sub-assembly finished: must attach to the placed model
            if not any(connects(i, placed) for i in block) and not any(i in ground for i in block): sub_fail.append(cur)
            placed |= set(block); cur = None; block = []
        if p["i"] is None: break
        i = p["i"]
        if p["sub"] is not None:
            if cur is None: cur = p["sub"]; block = [i]; continue
            if not connects(i, set(block)): unsupported.append(i)
            block.append(i); continue
        if i not in ground and not connects(i, placed): unsupported.append(i)
        placed.add(i)
    # ---------------- catalogue
    db = sqlite3.connect(a.rbdb)
    rbcols = {r[0]: r[1] for r in db.execute("select id,name from colors")}
    byname = {norm_name(v): k for k, v in rbcols.items()}
    def rb_colour(code):
        n = norm_name(cols[code]["name"].replace("_", " "))
        if code in rbcols and norm_name(rbcols[code]) == n: return code
        return byname.get(n)
    inv = Counter((p["num"], p["c"]) for p in P); rows = []
    for (num, c), n in sorted(inv.items(), key=lambda kv: -kv[1]):
        rc = rb_colour(c)
        st = db.execute("select num_sets,min_year,max_year from pcs_mat where part_num=? and color_id=?", (num, rc if rc is not None else -1)).fetchone()
        known = db.execute("select 1 from parts where part_num=?", (num,)).fetchone() is not None
        status = ("non trouvée dans Rebrickable" if not known else "couleur jamais produite" if not st or st[0] == 0
                  else "rare (< 5 sets)" if st[0] < 5 else "vérifiée")
        rows.append(dict(part=num, name=PL.title(num), ldraw_colour=c, colour=cols[c]["name"], rebrickable_colour_id=rc, qty=n,
                         sets=st[0] if st else 0, first_year=st[1] if st else None, last_year=st[2] if st else None, status=status))
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, f"{a.name}_catalogue.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    # ---------------- numerical stability per frame / plane
    gdir = np.array([0, 1.0, 0])                       # gravity in LDraw coordinates (+Y is down)
    def peel(comp, cut_edges):
        m = sum(P[i]["mass"] for i in comp); W = m / 1000 * G_ACC
        com = sum(P[i]["mass"] * (P[i]["lo"] + P[i]["hi"]) / 2 for i in comp) / max(m, 1e-9)
        contacts = []
        for (u, v) in cut_edges:
            for (pt, ax, owner) in G[u][v]["contacts"]:
                inside = owner in comp                  # stud carried by the sub-assembly: its axis points away from it
                n_comp = -ax if inside else ax          # normal of the joint plane pointing into the sub-assembly
                contacts.append((pt, n_comp))
        if not contacts: return None
        # keep the dominant joint direction (other directions are ignored: conservative)
        dirs = Counter(tuple(np.round(n, 2)) for _, n in contacts); nd = np.array(dirs.most_common(1)[0][0], float); nd /= np.linalg.norm(nd)
        pts = np.array([pt for pt, n in contacts if np.dot(n, nd) > 0.99])
        e1 = np.cross(nd, [1, 0, 0]) if abs(nd[0]) < 0.9 else np.cross(nd, [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(nd, e1)
        q = np.c_[pts @ e1, pts @ e2]; p0 = pts.mean(0)
        far = max((((P[i]["lo"] + P[i]["hi"]) / 2 - p0) @ nd for i in comp), default=0) + 10
        axes = []
        try:
            if len(q) >= 3:
                for eq in ConvexHull(q).equations: axes.append((eq[:2], eq[2]))
        except Exception: pass
        if not axes:
            for t in np.linspace(0, 2 * np.pi, 8, endpoint=False):
                ev = np.array([math.cos(t), math.sin(t)]); axes.append((ev, -max(q @ ev)))
        g_sf, f_tip = math.inf, math.inf
        for ev2, off in axes:
            lever_mm = ((-(q @ ev2 + off)).clip(0)) * 0.4 + R_STUD_MM
            m_res = F_CLUTCH * lever_mm.sum()
            e3 = ev2[0] * e1 + ev2[1] * e2                     # outward in-plane direction of that edge
            l0 = p0 + e3 * ((-off) - (np.array([p0 @ e1, p0 @ e2]) @ ev2))   # a point on the edge line
            t = np.cross(nd, e3)                               # rotation axis that opens the joint
            m_g = float(np.dot(np.cross((com - l0) * 0.4, W * gdir), t))
            if m_g > 1e-9: g_sf = min(g_sf, m_res / m_g)
            tip = p0 + nd * far
            arm = float(np.dot(np.cross((tip - l0) * 0.4, e3), t))
            if arm > 1e-6: f_tip = min(f_tip, max(m_res - max(m_g, 0), 0) / arm)
        pull = float(np.dot(W * gdir, nd))                    # weight pulling the sub-assembly away from the joint
        if pull > 1e-9: g_sf = min(g_sf, F_CLUTCH * len(pts) / pull)
        return dict(mass_g=round(m, 1), studs=int(len(pts)), gravity_sf=None if math.isinf(g_sf) else round(g_sf, 2),
                    tip_force_N=None if math.isinf(f_tip) else round(f_tip, 2))
    cases = []
    frames = Counter(p["up"] for p in P)
    for up in frames:
        u = np.array(up, float)
        fp = [p["i"] for p in P if p["up"] == up]
        for d in (u, -u):
            a0 = {i: min(P[i]["lo"] @ d, P[i]["hi"] @ d) for i in fp}; a1 = {i: max(P[i]["lo"] @ d, P[i]["hi"] @ d) for i in fp}
            for s in sorted(set(round(v, 1) for v in a0.values())):
                above = {i for i in fp if a0[i] >= s - 0.1}; below_f = {i for i in fp if a0[i] < s - 0.1}
                if not above or not below_f: continue
                H = G.subgraph(set(G.nodes) - below_f)
                for comp in nx.connected_components(H):
                    if not (comp & above) or (comp & ground): continue
                    cut = [(x, y) for x in comp for y in G.neighbors(x) if y not in comp]
                    if not cut: continue
                    r = peel(comp, cut)
                    if r is None: continue
                    cc = Counter(cols[P[i]["c"]]["name"] for i in comp).most_common(2)
                    lo_c = np.min([P[i]["lo"] for i in comp], 0); hi_c = np.max([P[i]["hi"] for i in comp], 0)
                    r.update(frame=list(map(float, up)), parts=len(comp), colours=dict(cc), bbox_ldu=[np.round(lo_c).tolist(), np.round(hi_c).tolist()])
                    cases.append(r)
    # distinct weakest sub-assemblies by tip force
    big = [c for c in cases if c["mass_g"] >= 1.0 and c["tip_force_N"] is not None]
    weakest = []
    for c in sorted(big, key=lambda c: c["tip_force_N"]):
        if all(np.abs(np.array(c["bbox_ldu"][0]) - np.array(w["bbox_ldu"][0])).sum() > 60 for w in weakest): weakest.append(c)
    gs = [c["gravity_sf"] for c in cases if c["gravity_sf"] is not None]
    stability = dict(model="rigid parts; clutch %.1f N per stud (assumed); compression free; 0.10 g per stud x stud x plate; gravity, then a force at the far end of each sub-assembly. Indicative only." % F_CLUTCH,
                     cases=len(cases), gravity_sf_below_1=sum(1 for v in gs if v < 1), gravity_sf_below_2=sum(1 for v in gs if v < 2),
                     min_gravity_sf=min(gs, default=None), subassemblies_over_1g=len(big),
                     tip_force_below_0_5N=sum(1 for c in big if c["tip_force_N"] < 0.5), tip_force_below_2N=sum(1 for c in big if c["tip_force_N"] < 2),
                     min_tip_force_N=min([c["tip_force_N"] for c in big], default=None), weakest=weakest[:10])
    # ---------------- fidelity
    fid = None
    if a.npz:
        d = np.load(a.npz); Fm = d["fine"]; K = int(d["k"])
        S = np.zeros(Fm.shape, bool)
        for p in P:
            Cn = conn.part(p["num"]); sol = Cn["solid"]
            full_box = not (np.allclose(Cn["plo"], Cn["lo"], atol=0.6) and np.allclose(Cn["phi"], Cn["hi"], atol=0.6))
            i0 = np.floor(np.array([p["lo"][0] / 5, -p["hi"][1] / 2, p["lo"][2] / 5])).astype(int)
            i1 = np.ceil(np.array([p["hi"][0] / 5, -p["lo"][1] / 2, p["hi"][2] / 5])).astype(int)
            i0 = np.maximum(i0, 0); i1 = np.minimum(i1, Fm.shape)
            if np.any(i1 <= i0): continue
            gx, gy, gz = np.meshgrid(*[np.arange(i0[k], i1[k]) for k in range(3)], indexing="ij")
            pts = np.c_[(gx.ravel() + 0.5) * 5, -(gy.ravel() + 0.5) * 2, (gz.ravel() + 0.5) * 5]
            loc = (pts - p["o"]) @ p["M"]                      # M orthonormal: inverse = transpose
            if full_box:
                ins = np.all((loc >= Cn["lo"] - 1e-6) & (loc <= Cn["hi"] + 1e-6), axis=1)
            else:
                ix = np.floor((loc[:, 0] - Cn["plo"][0]) / 5).astype(int); iy = np.floor((Cn["phi"][1] - loc[:, 1]) / 2).astype(int)
                iz = np.floor((loc[:, 2] - Cn["plo"][2]) / 5).astype(int)
                ok = (ix >= 0) & (ix < sol.shape[0]) & (iy >= 0) & (iy < sol.shape[1]) & (iz >= 0) & (iz < sol.shape[2])
                ins = np.zeros(len(pts), bool); ins[ok] = sol[ix[ok], iy[ok], iz[ok]]
            S[gx.ravel()[ins], gy.ravel()[ins], gz.ravel()[ins]] = True
        inter = np.count_nonzero(S & Fm); uni = np.count_nonzero(S | Fm)
        fid = dict(volume_iou=round(inter / uni, 4), lego_volume_cells=round(S.sum() / K**3, 1), mesh_volume_cells=round(Fm.sum() / K**3, 1))
        for nm, ax in (("face", 2), ("profil", 0), ("dessus", 1)):
            A, B = S.any(axis=ax), Fm.any(axis=ax); fid[f"silhouette_iou_{nm}"] = round(np.count_nonzero(A & B) / np.count_nonzero(A | B), 4)
    rep = dict(name=a.name, source_ldr=os.path.abspath(a.ldr), disclaimer="Geometric and graph checks plus an indicative stud-clutch model. Not a physical test.",
               parts=len(P), part_types=len({p["num"] for p in P}), part_colour_lines=len(rows), steps=nsteps,
               collisions=dict(pairs=len(overlaps), cells_4ldu=int(sum(overlaps.values())), examples=[[P[x]["num"], P[y]["num"]] for (x, y) in list(overlaps)[:5]],
                           details=[dict(a=P[x]["num"], b=P[y]["num"], a_sub=P[x]["sub"], b_sub=P[y]["sub"], a_aligned=P[x]["aligned"], b_aligned=P[y]["aligned"],
                                         a_box=np.round(P[x]["lo"]).tolist(), b_box=np.round(P[y]["lo"]).tolist(), points=int(v)) for (x, y), v in list(overlaps.items())[:10]]),
               blocked_studs=int(blocked), joints=G.number_of_edges(), studs_engaged=int(sum(d["studs"] for _, _, d in G.edges(data=True))),
               single_stud_joints=sum(1 for _, _, d in G.edges(data=True) if d["studs"] == 1),
               sideways_joints=sum(1 for _, _, d in G.edges(data=True) if abs(d["contacts"][0][1][1]) < 0.5),
               groups_on_support_not_attached_to_main=max(0, sum(1 for c in comps if c & ground) - 1),
               disconnected_parts=len(disconnected), islands=len(islands),
               disconnected_examples=[dict(part=P[i]["num"], colour=P[i]["c"], sub=P[i]["sub"], box=[np.round(P[i]["lo"]).tolist(), np.round(P[i]["hi"]).tolist()]) for i in disconnected[:25]],
               unsupported_at_placement=len(unsupported), subassemblies_not_attachable=sub_fail,
               catalogue=dict(lines=len(rows), never_produced=[f"{r['part']} {r['colour']}" for r in rows if r["status"] == "couleur jamais produite"],
                              not_found=[f"{r['part']} {r['colour']}" for r in rows if r["status"] == "non trouvée dans Rebrickable"],
                              rare=[f"{r['part']} {r['colour']} ({r['sets']} sets)" for r in rows if r["status"].startswith("rare")]),
               frames=[list(map(float, k)) for k in frames], turntable_joints=len(allowed_pairs), stability=stability, fidelity=fid)
    json.dump(rep, open(os.path.join(a.out, f"{a.name}_validation_v2.json"), "w"), indent=1, default=float)
    print(json.dumps({k: rep[k] for k in ("parts", "part_types", "steps", "collisions", "blocked_studs", "disconnected_parts", "islands", "unsupported_at_placement",
                                          "subassemblies_not_attachable", "sideways_joints")}, default=float))
    print(json.dumps({k: v for k, v in stability.items() if k not in ("weakest", "model")}), json.dumps(fid))

if __name__ == "__main__":
    main()
