#!/usr/bin/env python3
"""Independent constructibility audit of a brick .ldr (does not reuse brickify's own checks).
Footprints come from the LDraw part geometry, catalogue facts from the Rebrickable database (rb.db).
Outputs <name>_validation.json, <name>_inventory.csv (with element ids / availability), <name>_bricklink.xml.
Numbers here are geometric / graph metrics. They are NOT a mechanical test."""
import argparse, csv, json, math, os, re, sqlite3, sys
from collections import Counter, defaultdict, deque
import numpy as np, networkx as nx
from scipy.spatial import ConvexHull, Delaunay
sys.path.insert(0, os.path.dirname(__file__))
from ldr_expand import Lib, ldconfig, read_ldr

STUD_MM, PLATE_MM = 8.0, 3.2

def norm(s): return re.sub(r"[^a-z]", "", s.lower()).replace("grey", "gray")  # LDraw "Grey" vs Rebrickable "Gray"

def colour_map(cols, db):
    """LDraw colour code -> Rebrickable colour row (by id when the names agree, else by name)."""
    rb = {r[0]: r for r in db.execute("select id,name,rgb,y1,y2 from colors")}
    byname = {norm(r[1]): r for r in rb.values()}
    alias = {"trans-lightblue": "transverylightblue"}
    out = {}
    for code, c in cols.items():
        n = norm(c["name"].replace("_", " "))
        if code in rb and norm(rb[code][1]) == n: out[code] = rb[code]
        elif n in byname: out[code] = byname[n]
        elif n.replace("medium", "") in byname: out[code] = byname[n.replace("medium", "")]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ldr", required=True); ap.add_argument("--ldraw", required=True); ap.add_argument("--rbdb", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--name", required=True)
    ap.add_argument("--front", default="+z", help="model front direction in LDraw coords (brickify: +z)")
    a = ap.parse_args()
    lib = Lib(a.ldraw); cols = ldconfig(os.path.join(a.ldraw, "LDConfig.ldr"))
    db = sqlite3.connect(a.rbdb); cmap = colour_map(cols, db)
    raw = read_ldr(a.ldr)
    nsteps = max([p["step"] for p in raw] + [0]) + 1
    # ---- footprints from geometry
    bbox = {}
    P = []
    for i, p in enumerate(raw):
        k = p["p"].lower()
        if k not in bbox:
            try:   # body box without studs, measured on the real geometry (works whatever the part origin)
                import partlib; os.environ.setdefault("LDRAW", a.ldraw)
                sh = partlib.part(k.replace(".dat", "")); bbox[k] = (np.array(sh["lo"]), np.array(sh["hi"]))
            except Exception:
                T, _ = lib.geom(p["p"]); V = T.reshape(-1, 3)
                body = V[V[:, 1] >= -0.01]  # drop studs (above y=0 in part coords)
                bbox[k] = (body.min(0), body.max(0))
        lo, hi = bbox[k]
        M = np.array(p["M"]).reshape(3, 3); o = np.array(p["o"])
        corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]) @ M.T + o
        mn, mx = corners.min(0), corners.max(0)
        x0, x1 = int(round(mn[0] / 20)), int(round(mx[0] / 20)); z0, z1 = int(round(mn[2] / 20)), int(round(mx[2] / 20))
        ytop, ybot = int(round(-mn[1] / 8)), int(round(-mx[1] / 8))   # plate indices, up positive
        P.append(dict(i=i, part=p["p"].lower().replace(".dat", ""), c=p["c"], x0=x0, x1=x1, z0=z0, z1=z1, y0=ybot, y1=ytop, step=p["step"]))
    xs0 = min(p["x0"] for p in P); zs0 = min(p["z0"] for p in P); ys0 = min(p["y0"] for p in P)
    for p in P:
        p["x0"] -= xs0; p["x1"] -= xs0; p["z0"] -= zs0; p["z1"] -= zs0; p["y0"] -= ys0; p["y1"] -= ys0
        p["vol"] = (p["x1"] - p["x0"]) * (p["z1"] - p["z0"]) * (p["y1"] - p["y0"])
    NX = max(p["x1"] for p in P); NZ = max(p["z1"] for p in P); NY = max(p["y1"] for p in P)
    # ---- collisions
    owner = -np.ones((NX, NY, NZ), np.int64); overlaps = Counter()
    for p in P:
        sl = owner[p["x0"]:p["x1"], p["y0"]:p["y1"], p["z0"]:p["z1"]]
        for q in np.unique(sl[sl >= 0]): overlaps[tuple(sorted((int(q), p["i"])))] += int((sl == q).sum())
        sl[...] = p["i"]
    # ---- stud connections: a joint needs a real stud on the lower part under a real receptor of the upper part.
    #      Stud and receptor cells come from the LDraw geometry (tools/partlib.py): a tile has no stud, a 45-degree
    #      slope has studs only on its high row, an inverted slope receives studs only under its vertical part.
    import partlib
    os.environ.setdefault("LDRAW", a.ldraw)
    shape_cache = {}
    def cells_world(p, which):
        k = p["part"]
        if k not in shape_cache:
            try: shape_cache[k] = partlib.part(k)
            except Exception: shape_cache[k] = None
        sh = shape_cache[k]
        full = {(x, z) for x in range(p["x0"], p["x1"]) for z in range(p["z0"], p["z1"])}
        if sh is None: return full
        M = np.array(raw[p["i"]]["M"]).reshape(3, 3); o = np.array(raw[p["i"]]["o"])
        out = set()
        for (i, j) in sh[which]:
            c = M @ np.array([sh["lo"][0] + (i + 0.5) * 20, 0, sh["lo"][2] + (j + 0.5) * 20]) + o
            out.add((int(np.floor(c[0] / 20)) - xs0, int(np.floor(c[2] / 20)) - zs0))
        return out & full
    for p in P:
        p["studs_xz"] = cells_world(p, "studs"); p["recv_xz"] = cells_world(p, "recv")
        sh = shape_cache.get(p["part"]); p["fill"] = sh["fill"] if sh else 1.0
    G = nx.Graph(); G.add_nodes_from(p["i"] for p in P)
    for p in P:
        if p["y1"] >= NY: continue
        top = owner[p["x0"]:p["x1"], p["y1"], p["z0"]:p["z1"]]
        for q in set(top[top >= 0].tolist()):
            if P[q]["y0"] == p["y1"]:
                cells = sorted(p["studs_xz"] & P[q]["recv_xz"])
                if cells: G.add_edge(p["i"], q, studs=len(cells), cells=cells, plane=p["y1"])
    ground = [p["i"] for p in P if p["y0"] == 0]
    comp_ground = set()
    for g in ground:
        if g not in comp_ground: comp_ground |= nx.node_connected_component(G, g)
    floating = [p["i"] for p in P if p["i"] not in comp_ground]
    # ---- placement order: a part placed with no connection to earlier parts and not on the ground floats in mid-air
    floating_at_placement = [p["i"] for p in P if p["y0"] > 0 and not any(P[q]["step"] <= p["step"] and P[q]["y1"] == p["y0"] for q in G.neighbors(p["i"]))]
    # of those, how many have empty space right under their whole footprint (can be pushed on from below later)
    reach_below = [i for i in floating_at_placement if (owner[P[i]["x0"]:P[i]["x1"], P[i]["y0"] - 1, P[i]["z0"]:P[i]["z1"]] < 0).all()]
    # ---- single points of failure: graph bridges
    bridges = []
    br = list(nx.bridges(G))
    H = G.copy(); H.remove_edges_from(br)
    cid = {}; csize = {}; cvol = {}
    for k, c in enumerate(nx.connected_components(H)):
        for n in c: cid[n] = k
        csize[k] = len(c); cvol[k] = sum(P[i]["vol"] for i in c)
    T = nx.Graph(); T.add_nodes_from(csize)
    for u, v in br: T.add_edge(cid[u], cid[v], studs=G[u][v]["studs"])
    for comp_nodes in nx.connected_components(T):
        rootk = max(comp_nodes, key=lambda k: cvol[k])
        tree = nx.bfs_tree(T.subgraph(comp_nodes), rootk)
        for k in reversed(list(nx.topological_sort(tree))):
            sub = [k] + list(nx.descendants(tree, k)) if False else None
        # subtree sums
        ss = {k: (csize[k], cvol[k]) for k in comp_nodes}
        for k in reversed(list(nx.topological_sort(tree))):
            for ch in tree.successors(k):
                ss[k] = (ss[k][0] + ss[ch][0], ss[k][1] + ss[ch][1])
        for par, ch in tree.edges():
            bridges.append(dict(parts_detached=ss[ch][0], cells_detached=ss[ch][1], studs=T[par][ch]["studs"], _root=(tree, ch)))
    bridges.sort(key=lambda b: -b["cells_detached"])
    members = {k: [n for n in cid if cid[n] == k] for k in csize} if bridges else {}
    for b in bridges[:10]:
        tree, ch = b["_root"]; ks = [ch] + list(nx.descendants(tree, ch)); nodes = [n for k in ks for n in members[k]]
        b["colours"] = dict(Counter(cols[P[n]["c"]]["name"] for n in nodes).most_common(3))
        b["layers"] = [min(P[n]["y0"] for n in nodes), max(P[n]["y1"] for n in nodes)]
        b["bbox_studs_x"] = [min(P[n]["x0"] for n in nodes), max(P[n]["x1"] for n in nodes)]
        b["bbox_studs_z"] = [min(P[n]["z0"] for n in nodes), max(P[n]["z1"] for n in nodes)]
    for b in bridges: b.pop("_root", None)
    # ---- load paths: for every layer boundary, every sub-assembly above it and the studs that hold it
    vol = np.array([p["vol"] for p in P], float)
    cen = np.array([[(p["x0"] + p["x1"]) / 2, (p["y0"] + p["y1"]) / 2 * PLATE_MM / STUD_MM, (p["z0"] + p["z1"]) / 2] for p in P])
    total_vol = vol.sum()
    hangs = []
    for b in range(1, NY):
        above = [p["i"] for p in P if p["y0"] >= b]
        if not above: continue
        H = G.subgraph(above)
        for comp in nx.connected_components(H):
            comp = list(comp)
            cs = set(comp)
            links = [(u, v, d["studs"]) for u in comp for v, d in G[u].items() if v not in cs]
            studs = sum(l[2] for l in links)
            if not links: continue
            cv = vol[comp].sum(); com = (cen[comp] * vol[comp, None]).sum(0) / cv
            sp = np.array([[ (max(P[u]["x0"], P[v]["x0"]) + min(P[u]["x1"], P[v]["x1"])) / 2, (max(P[u]["z0"], P[v]["z0"]) + min(P[u]["z1"], P[v]["z1"])) / 2] for u, v, _ in links])
            lever = float(np.min(np.hypot(sp[:, 0] - com[0], sp[:, 1] - com[2])))  # studs, from COM to the nearest support stud area
            hangs.append(dict(layer=b, parts=len(comp), cells=int(cv), frac_mass=round(cv / total_vol, 4), studs=studs, joints=len(links),
                              load_per_stud=round(cv / max(studs, 1), 1), lever_studs=round(lever, 1),
                              torque_index=round(cv * lever / max(studs, 1), 1), com_studs=[round(float(c), 1) for c in com],
                              where=None))
    # ---- numerical stability (indicative): every sub-assembly that only holds through stud joints at one level.
    #      Mass = part box volume x solid fraction x 0.10 g per stud x plate cell. A stud joint resists pull-out with
    #      F_CLUTCH newtons per stud (assumed, conservative; measured values on new bricks are typically 1-4 N).
    #      Resting sub-assembly: stable if its centre of mass is inside the stud polygon, otherwise
    #      SF = F*sum(d_i + r) / (W*d_com) about the critical polygon edge. Hanging sub-assembly (held from above):
    #      SF = F*n / W, reduced the same way when the load is off-centre. SF < 1: predicted to come apart under its
    #      own weight; SF < 2: no margin for handling. Not a physical test.
    F_CLUTCH, G_ACC, R_STUD = 1.0, 9.81, 0.3
    mass_g = np.array([p["vol"] * p["fill"] * 0.10 for p in P])
    cxz = np.array([[(p["x0"] + p["x1"]) / 2, (p["z0"] + p["z1"]) / 2] for p in P])
    def sf_for(comp, links, hanging):
        """returns (gravity safety factor, minimal horizontal tip force in N that peels the joint, mass g, studs)"""
        m = mass_g[comp].sum(); W = m / 1000 * G_ACC
        com = (cxz[comp] * mass_g[comp, None]).sum(0) / max(m, 1e-9)
        pts = np.array([[c[0] + 0.5, c[1] + 0.5] for _, _, d in links for c in d["cells"]])
        plane = np.mean([d["plane"] for _, _, d in links])
        n = len(pts)
        if n == 0: return 0.0, 0.0, m, 0
        # candidate tipping axes: convex hull edges of the stud points, or 8 directions for degenerate sets
        axes = []
        try:
            if n >= 3:
                for e in ConvexHull(pts).equations: axes.append((e[:2], e[2]))
        except Exception:
            pass
        if not axes:
            for t in np.linspace(0, 2 * np.pi, 8, endpoint=False):
                nv = np.array([np.cos(t), np.sin(t)]); axes.append((nv, -max(pts @ nv)))
        ys = [P[i]["y1"] for i in comp] if not hanging else [P[i]["y0"] for i in comp]
        h_mm = (max(ys) - plane) * PLATE_MM if not hanging else (plane - min(ys)) * PLATE_MM
        h_mm = max(h_mm, PLATE_MM)
        g_sf, f_tip = np.inf, np.inf
        for nv, off in axes:
            lever_mm = ((-(pts @ nv + off)).clip(0) + R_STUD) * STUD_MM     # each stud's distance to the axis, + stud radius
            m_res = F_CLUTCH * lever_mm.sum()                                 # N.mm resisting peel about this axis
            dcom_mm = (nv @ com + off) * STUD_MM                              # >0: COM beyond the axis (overturning)
            m_grav = W * dcom_mm                                              # N.mm (negative = stabilising)
            if dcom_mm > 0: g_sf = min(g_sf, m_res / m_grav)
            # horizontal force at the far end pushing outward across this axis, at height h above the joint plane
            f_tip = min(f_tip, max(m_res - m_grav, 0.0) / h_mm)
        if hanging: g_sf = min(g_sf, F_CLUTCH * n / max(W, 1e-9))
        return float(g_sf), float(f_tip), float(m), n
    clutch = []
    for b in range(1, NY):
        above = [p["i"] for p in P if p["y0"] >= b]
        below = [p["i"] for p in P if p["y1"] <= b]
        for side, nodes in (("resting", above), ("hanging", below)):
            if not nodes: continue
            H = G.subgraph(nodes)
            for comp in nx.connected_components(H):
                comp = sorted(comp); cs = set(comp)
                if side == "hanging" and any(P[i]["y0"] == 0 for i in comp): continue
                links = [(u, v, d) for u in comp for v, d in G[u].items() if v not in cs]
                if not links: continue
                sf, ftip, m, n = sf_for(np.array(comp), links, side == "hanging")
                cols_c = Counter(cols[P[i]["c"]]["name"] for i in comp).most_common(2)
                clutch.append(dict(kind=side, layer=b, parts=len(comp), mass_g=round(m, 1), studs=n,
                                   safety_factor=(round(sf, 2) if np.isfinite(sf) else None), tip_force_N=round(ftip, 2), colours=dict(cols_c),
                                   bbox_studs_x=[min(P[i]["x0"] for i in comp), max(P[i]["x1"] for i in comp)],
                                   bbox_studs_z=[min(P[i]["z0"] for i in comp), max(P[i]["z1"] for i in comp)],
                                   layers=[min(P[i]["y0"] for i in comp), max(P[i]["y1"] for i in comp)]))
    finite = [c for c in clutch if c["safety_factor"] is not None]
    # distinct weakest sub-assemblies by tip force (keep the worst cut of each region)
    tipw = []
    for c in sorted(clutch, key=lambda c: c["tip_force_N"]):
        if c["mass_g"] < 1.0: continue
        if all(abs(c["bbox_studs_x"][0] - t["bbox_studs_x"][0]) + abs(c["bbox_studs_z"][0] - t["bbox_studs_z"][0]) > 4 or abs(c["layers"][0] - t["layers"][0]) > 6 for t in tipw):
            tipw.append(c)
    big = [c for c in clutch if c["mass_g"] >= 1.0]
    clutch_summary = dict(model=f"clutch {F_CLUTCH} N per stud (assumed), 0.10 g per stud x plate cell; gravity, then a horizontal force at the far end of each sub-assembly",
                          cases=len(clutch), gravity_below_1=sum(1 for c in finite if c["safety_factor"] < 1),
                          gravity_below_2=sum(1 for c in finite if c["safety_factor"] < 2),
                          min_gravity_safety_factor=min([c["safety_factor"] for c in finite], default=None),
                          subassemblies_over_1g=len(big),
                          tip_force_below_0_5N=sum(1 for c in big if c["tip_force_N"] < 0.5),
                          tip_force_below_2N=sum(1 for c in big if c["tip_force_N"] < 2.0),
                          min_tip_force_N=min([c["tip_force_N"] for c in big], default=None),
                          weakest_by_tip_force=tipw[:12],
                          worst_gravity=sorted(finite, key=lambda c: c["safety_factor"])[:5])
    # label where each sub-assembly sits (heuristic, for reading only)
    fz = 1 if a.front == "+z" else -1
    def where(h):
        x, y, z = h["com_studs"]; zc = NZ / 2
        rel = (z - zc) * fz / max(NZ, 1)
        pos = "front" if rel > 0.2 else ("rear" if rel < -0.2 else "middle")
        hgt = "top" if y * STUD_MM / PLATE_MM > 0.66 * NY else ("low" if y * STUD_MM / PLATE_MM < 0.33 * NY else "mid")
        return f"{pos}/{hgt}"
    for h in hangs: h["where"] = where(h)
    # weakest: highest torque index among sub-assemblies of meaningful size, and lowest-stud joints holding >1% of the mass
    weak = sorted([h for h in hangs if h["frac_mass"] >= 0.005], key=lambda h: -h["torque_index"])[:12]
    appendages = sorted([h for h in hangs if 0.003 <= h["frac_mass"] <= 0.25], key=lambda h: -h["torque_index"])
    seen_app = []
    for h in appendages:   # keep the worst joint per distinct sub-assembly region
        if all(np.hypot(h["com_studs"][0]-s_["com_studs"][0], h["com_studs"][2]-s_["com_studs"][2]) > 3 or abs(h["com_studs"][1]-s_["com_studs"][1]) > 3 for s_ in seen_app):
            seen_app.append(h)
    appendages = seen_app[:12]
    # horizontal cantilevers (head, tail, snout): for each vertical cut plane, mass beyond it, lever arm,
    # and how many parts bridge the plane (the only things holding a horizontal overhang together)
    cantilevers = []
    for axis, lo_k, hi_k, N in (("z", "z0", "z1", NZ), ("x", "x0", "x1", NX)):
        ax = 2 if axis == "z" else 0
        for c in range(1, N):
            for side in (1, -1):
                beyond = [p["i"] for p in P if (p[lo_k] >= c if side > 0 else p[hi_k] <= c)]
                if not beyond or any(P[i]["y0"] == 0 for i in beyond): continue   # has its own legs: not a cantilever
                bv = vol[beyond].sum()
                if bv / total_vol < 0.003 or bv / total_vol > 0.4: continue
                cross = [p for p in P if p[lo_k] < c < p[hi_k]]
                comz = (cen[beyond, ax] * vol[beyond]).sum() / bv
                lever = abs(comz - c)
                cantilevers.append(dict(axis=axis, plane=c, side="+" if side > 0 else "-", frac_mass=round(bv / total_vol, 4), lever_studs=round(float(lever), 1),
                                        bridging_parts=len(cross), bridging_layers=len({p["y0"] for p in cross}),
                                        index=round(float(bv * lever / max(len(cross), 1)), 1)))
    cantilevers.sort(key=lambda h: -h["index"])
    thin = sorted([h for h in hangs if h["frac_mass"] >= 0.01], key=lambda h: (h["studs"], -h["cells"]))[:12]
    # ---- legs / feet: ground contact clusters
    base = np.zeros((NX, NZ), bool)
    for p in P:
        if p["y0"] == 0: base[p["x0"]:p["x1"], p["z0"]:p["z1"]] = True
    from scipy import ndimage
    lab, nfeet = ndimage.label(base)
    feet = [int((lab == k).sum()) for k in range(1, nfeet + 1)]
    # ---- centre of mass vs support polygon
    com = (cen * vol[:, None]).sum(0) / total_vol
    pts = np.argwhere(base).astype(float)
    pts = np.concatenate([pts + d for d in ([0, 0], [1, 0], [0, 1], [1, 1])])
    hull = ConvexHull(pts); poly = pts[hull.vertices]
    inside = bool(Delaunay(poly).find_simplex([[com[0], com[2]]])[0] >= 0)
    dmin = 1e9
    for i in range(len(poly)):
        p0, p1 = poly[i], poly[(i + 1) % len(poly)]; ab = p1 - p0
        t = np.clip(np.dot([com[0], com[2]] - p0, ab) / ab.dot(ab), 0, 1); dmin = min(dmin, float(np.linalg.norm([com[0], com[2]] - (p0 + t * ab))))
    com_h_mm = com[1] * STUD_MM
    tip_deg = math.degrees(math.atan2(dmin * STUD_MM, com_h_mm)) if inside else 0.0
    # ---- catalogue
    inv = Counter((p["part"], p["c"]) for p in P)
    rows = []
    for (part, c), n in sorted(inv.items(), key=lambda kv: (-kv[1])):
        rb = cmap.get(c)
        hdr = open(lib.resolve(part + ".dat"), encoding="utf-8", errors="replace").read(400)
        official = "!LDRAW_ORG Part" in hdr
        title = hdr.splitlines()[0][2:].strip()
        st = db.execute("select num_sets,min_year,max_year from pcs_mat where part_num=? and color_id=?", (part, rb[0] if rb else -999)).fetchone()
        el = [r[0] for r in db.execute("select element_id from elements where part_num=? and color_id=?", (part, rb[0] if rb else -999))]
        rows.append(dict(part=part, name=title, ldraw_colour=c, colour=cols[c]["name"], rebrickable_colour_id=rb[0] if rb else None,
                         rebrickable_colour=rb[1] if rb else None, qty=n, ldraw_official=official,
                         lego_element_ids=" ".join(map(str, el[:3])), sets_with_this_part_colour=st[0] if st else 0,
                         last_year_seen=st[2] if st else None, exists_in_this_colour=bool(st and st[0] > 0) or bool(el)))
    missing = [r for r in rows if not r["exists_in_this_colour"]]
    rare = [r for r in rows if r["exists_in_this_colour"] and (r["sets_with_this_part_colour"] or 0) < 5]
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, f"{a.name}_inventory.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    # BrickLink ids: brickify's colour table (PALETTE_INFO) holds the BrickLink colour id per LDraw code
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "brickify", "pipeline"))
    BL = {}
    try:
        import brickify as B
        BL = {k: v[3] for k, v in {**B.PALETTE_INFO, **B.COLOUR_INFO}.items()}
    except Exception as e:
        print("brickify colour table unavailable:", e)
    xml = ["<INVENTORY>"] + [f"  <ITEM><ITEMTYPE>P</ITEMTYPE><ITEMID>{r['part']}</ITEMID><COLOR>{BL.get(r['ldraw_colour'], '')}</COLOR><MINQTY>{r['qty']}</MINQTY></ITEM>" for r in rows] + ["</INVENTORY>"]
    open(os.path.join(a.out, f"{a.name}_bricklink.xml"), "w").write("\n".join(xml))
    layers = len({p["y0"] for p in P})
    rep = dict(
        name=a.name, source_ldr=os.path.abspath(a.ldr),
        disclaimer="Geometric/graph checks only. Not a mechanical test. Nothing here is 'physically validated'.",
        parts=len(P), part_types=len({p['part'] for p in P}), part_colour_lines=len(rows),
        bricks=sum(1 for p in P if p["y1"] - p["y0"] == 3), plates=sum(1 for p in P if p["y1"] - p["y0"] == 1),
        size_studs_xyz=[NX, NZ, NY], size_mm=dict(width_x=NX * STUD_MM, depth_z=NZ * STUD_MM, height=round(NY * PLATE_MM, 1)),
        colours={cols[c]["name"]: n for c, n in Counter(p["c"] for p in P).most_common()},
        collisions=dict(pairs=len(overlaps), cells=sum(overlaps.values())),
        connections=dict(stud_joints=G.number_of_edges(), studs=sum(d["studs"] for _, _, d in G.edges(data=True)),
                         single_stud_joints=sum(1 for _, _, d in G.edges(data=True) if d["studs"] == 1),
                         parts_with_one_joint=sum(1 for n in G if G.degree(n) == 1)),
        disconnected_parts=len(floating), disconnected_examples=[dict(part=P[i]['part'], colour=P[i]['c'], cell=[P[i]['x0'], P[i]['y0'], P[i]['z0']], size=[P[i]['x1']-P[i]['x0'], P[i]['y1']-P[i]['y0'], P[i]['z1']-P[i]['z0']]) for i in floating[:40]],
        connected_components=nx.number_connected_components(G),
        islands_not_attached_to_main_body=[dict(parts=len(cc), cells=sum((P[i]["x1"]-P[i]["x0"])*(P[i]["y1"]-P[i]["y0"])*(P[i]["z1"]-P[i]["z0"]) for i in cc), rests_on_ground=any(P[i]["y0"] == 0 for i in cc), bbox_studs_xyz_min=[min(P[i]["x0"] for i in cc), min(P[i]["z0"] for i in cc), min(P[i]["y0"] for i in cc)]) for cc in sorted(nx.connected_components(G), key=len, reverse=True)[1:]],
        floating_at_placement=dict(count=len(floating_at_placement), free_space_below=len(reach_below), note="parts that, in the LDraw step order, have nothing under them yet (must be sub-assembled or added later)"),
        single_points_of_failure=dict(count=len(bridges), largest=bridges[:10]),
        clutch_stability=clutch_summary,
        weakest_by_torque=weak, appendages_weakest=appendages, horizontal_cantilevers=cantilevers[:10], thinnest_supports=thin,
        feet=dict(count=nfeet, cells=sorted(feet, reverse=True)),
        centre_of_mass=dict(x_studs=round(com[0], 2), z_studs=round(com[2], 2), height_mm=round(com_h_mm, 1), inside_support_polygon=inside,
                            margin_mm=round(dmin * STUD_MM, 1), tipping_angle_deg=round(tip_deg, 1)),
        steps=nsteps, layers=layers, parts_per_step=round(len(P) / max(nsteps, 1), 1),
        catalogue=dict(all_parts_official_ldraw=all(r["ldraw_official"] for r in rows),
                       part_colour_combos_never_produced=[f"{r['part']} {r['name']} in {r['colour']} x{r['qty']}" for r in missing],
                       part_colour_combos_rare_lt5_sets=[f"{r['part']} {r['name']} in {r['colour']} ({r['sets_with_this_part_colour']} sets)" for r in rare],
                       rebrickable_db="rb.db (ojuuji/rb.db latest-v8)"),
        cost="coût non vérifié",
    )
    json.dump(rep, open(os.path.join(a.out, f"{a.name}_validation.json"), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(json.dumps({k: rep[k] for k in ("parts", "size_mm", "collisions", "connections", "disconnected_parts", "floating_at_placement", "feet", "centre_of_mass", "steps", "layers")}, default=str))
    print("single points of failure:", len(bridges), bridges[:3])
    print("never produced:", rep["catalogue"]["part_colour_combos_never_produced"])
    print("weakest:", weak[:2]); print("appendages:", appendages[:4]); print("cantilevers:", cantilevers[:5])

if __name__ == "__main__":
    main()
