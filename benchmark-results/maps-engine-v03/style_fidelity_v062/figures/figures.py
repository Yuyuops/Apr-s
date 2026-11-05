#!/usr/bin/env python3
"""Optional figures module (generic, offline, disabled by default). NOTHING IS INVENTED : figures come only from search.py (existing, catalogued LEGO minifigures) and are chosen by catalogue id.
 config : figures.enabled / mode (off | shelf | frame | free_zone) / theme / selected [0..4 catalogue ids] / support_build (build an EMPTY shelf of real plates under the chosen slots) / allow_overlap_with_geography
 behaviour : off (default) -> nothing. Otherwise : load results/<theme>_candidates.json (run search.py first) -> keep the selected ids that exist in it -> propose placements with the checks below -> report.
 Placement checks (dimensions, supports, connections) concern the SUPPORT only. A figure's own 3D model is NEVER fabricated : with no exact LDraw model, the figure is shown by its photo and catalogue data, and its 3D integration is reported 'non validee'.
 The only geometry this module can add to a model is an empty shelf/support made of ordinary plates clipped on studs ; it is built only if support_build is true."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
SLOT = (2, 2)       # generic standing footprint of a minifigure, in studs (generic range value, not measured per reference)
GAP = 1
def load_candidates(theme):
    p = os.path.join(HERE, "results", theme + "_candidates.json")
    return json.load(open(p)) if os.path.exists(p) else None
def shelf_size(n): return 4, n * SLOT[1] + max(0, n - 1) * GAP + 2          # rows (3 deep + 1), cols
def proposals(cfg, selected, zones):
    """zones : dict name -> dict(free=bool, rows, cols, studded_possible=bool, reason) supplied by the picture builder ; returns list of proposals (with accepted flag and reasons)"""
    n = len(selected); H, W = shelf_size(n) if n else (0, 0); out = []
    for name, z in zones.items():
        ok = n > 0 and z.get("free", False) and z["rows"] >= H and z["cols"] >= W
        reasons = []
        if n == 0: reasons.append("0 figure selected")
        if not z.get("free", False): reasons.append(z.get("reason", "zone not free"))
        if z["rows"] < H or z["cols"] < W: reasons.append("zone %dx%d too small for %dx%d" % (z["rows"], z["cols"], H, W))
        out.append(dict(zone=name, accepted=ok, support_needed="studded plates (shelf) clipped on studs of the picture", slots=[(i, SLOT) for i in range(n)], size_studs=[H, W], reasons=reasons,
                        constructibility="support : checkable in LDraw (real plates) ; figure : 3D model unavailable -> NOT validated" if ok else "rejected"))
    return out
def run(B, cfg_all, CAT, PAIRS):
    """called by the style builder before the layers are built. Returns (callback or None, log)."""
    cfg = cfg_all.get("figures", {}); log = dict(config=cfg, selected=[], rejected=[], proposals=[], status="off")
    if not cfg.get("enabled") or cfg.get("mode", "off") == "off": return None, log
    theme = cfg.get("theme", "auto"); theme = B.cp.get("theme", "italy") if theme == "auto" else theme
    cand = load_candidates(theme)
    if cand is None: log["status"] = "no search results for theme '%s' : run figures/search.py %s" % (theme, theme); return None, log
    byid = {c["fig_num"]: c for c in cand["candidates"]}; sel = []
    for fid in cfg.get("selected", [])[:4]:
        if fid in byid: sel.append(byid[fid])
        else: log["rejected"].append(dict(id=fid, reason="not in the catalogue search results of theme '%s' (no invented figure)" % theme))
    if len(cfg.get("selected", [])) > 4: log["rejected"].append(dict(id=cfg["selected"][4:], reason="more than 4 selected : extra ones ignored"))
    log["selected"] = [dict(fig_num=c["fig_num"], name=c["name"], sets=[s["set_num"] for s in c["sets"]], image=c.get("image_file"), availability=c["availability"], price=c["price"], model_3d=c["model_3d"]) for c in sel]
    if not sel: log["status"] = "no figure selected" if not cand["candidates"] else "0 selected among %d candidates" % cand["n"]; return None, log
    n = len(sel); H, W = shelf_size(n); mode = cfg.get("mode", "shelf"); zones = {}
    if mode in ("shelf", "free_zone"):
        for anchor in ("top-right", "top-left", "bottom-right", "bottom-left"):
            zones[anchor] = dict(free=True, rows=H, cols=W)      # tentatively free ; reserve() decides below
    elif mode == "frame":
        zones["frame"] = dict(free=False, rows=B.F, cols=B.C, reason="frame cap is made of smooth tiles (no studs) and %d studs wide : a studded section would have to be added ; not implemented" % B.F)
    log["proposals"] = proposals(cfg, sel, {k: v for k, v in zones.items()})
    if mode == "frame": log["status"] = "frame mode : proposal rejected (see proposals)"; return None, log
    z = None
    for anchor in zones:
        z = B.reserve(H, W, anchor, 3)
        if z: log["chosen_anchor"] = anchor; break
        for p in log["proposals"]:
            if p["zone"] == anchor: p["accepted"] = False; p["reasons"].append("overlaps land or a reserved zone")
    if not z: log["status"] = "no free zone for a %dx%d support" % (H, W); return None, log
    log["status"] = "placement proposed (support dimensions and studs checked ; figure 3D integration NOT validated)"
    if not cfg.get("support_build", False): return None, log
    B.studded[z[0]:z[0] + H, z[1]:z[1] + W] = True
    def after():
        r0, c0, L = z; F = B.F; S = B.S; y = B.y0 + L * B.thick + 1; from tiler import tile, PLATES
        cells = {(r0 + F + a, c0 + F + b) for a in range(3) for b in range(W)}
        for (r, c, nr, nc, part, rot) in tile(cells, {k: v for k, v in PLATES.items() if (k[0] == 1 and k[1] <= 4) or k == (2, 2)}, B.rng, 1.8, 8, S.stud_cells(y), 12): S.add(part, 15, r, c, y, rot, "shelf_support")
        log["support"] = dict(row=r0, col=c0, size=[H, W], level=L, note="empty shelf of real plates ; the studs of the shelf are where each minifigure would stand ; no figure model added")
    return after, log
