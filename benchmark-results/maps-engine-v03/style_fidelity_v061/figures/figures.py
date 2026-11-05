#!/usr/bin/env python3
"""Optional figures module (generic, theme-agnostic, offline).
 config : figures.enabled / mode (off | shelf | frame | on_map) / theme / max_count / scale (nano | micro | mini) / placement / allow_overlap_with_geography
 catalogue : figures/catalog/<theme>.json (no theme is hard-coded in the engine : Italy, Hyrule, ... are data).
Pipeline : load catalogue -> keep figures whose status is verified_geometry AND whose recipe parts exist in the part catalogue, with catalogued part/colour pairs -> check scale and footprint against the free slots ->
reserve a support (shelf / frame strip / map patch) built from real plates clipped on studs -> add the figures as LDraw sub-assemblies (regions 'figure_<id>') -> report accepted/rejected with reasons.
A figure without a valid stud connection to the picture is rejected."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
SCALE_MAX_H = {"nano": 6, "micro": 10, "mini": 16}      # plates
def load_catalog(theme):
    p = os.path.join(HERE, "catalog", theme + ".json")
    if not os.path.exists(p): return None
    return json.load(open(p))
def screen(cat, cfg, CAT, PAIRS):
    """returns (candidates, rejected[(id, reason)])"""
    cand, rej = [], []
    for f in cat["figures"]:
        if f["status"] != "verified_geometry": rej.append((f["id"], "status=%s : no verified geometry (%s)" % (f["status"], f.get("notes", "")[:80]))); continue
        if f["recipe"] is None: rej.append((f["id"], "no recipe")); continue
        if f["height_plates"] > SCALE_MAX_H[cfg["scale"]]: rej.append((f["id"], "taller (%d plates) than scale '%s' allows (%d)" % (f["height_plates"], cfg["scale"], SCALE_MAX_H[cfg["scale"]]))); continue
        bad = [(p, c) for (_, _, _, p, c, _) in f["recipe"] if p not in CAT or PAIRS.get(p, {}).get(str(c), 0) < 1]
        if bad: rej.append((f["id"], "part/colour pair not catalogued : %s" % bad[:2])); continue
        cand.append(f)
    return cand, rej
def shelf_dims(n, gap=1, base=2, depth=3, margin=1):
    return depth + 1, n * base + (n - 1) * gap + 2 * margin
def place_shelf(B, cand, cfg, log):
    """B = style Builder (uses B.reserve, B.S, B.F, B.y0, B.thick) ; builds a shelf of white plates over a studded patch and the figures on it ; returns list of placed ids"""
    n = min(cfg["max_count"], len(cand))
    if n == 0: log["placement"] = "no accepted figure"; return []
    H, W = shelf_dims(n)
    z = None
    for anchor in ("top-right", "top-left", "bottom-right", "bottom-left"):
        z = B.reserve(H, W, anchor, 3)
        if z: log["shelf_anchor"] = anchor; break
        log.setdefault("refused_anchors", []).append((anchor, "overlaps land or another reserved zone"))
    if not z: log["placement"] = "no free slot for a %dx%d shelf" % (H, W); return []
    r0, c0, L = z; F = B.F; S = B.S; y = B.y0 + L * B.thick + 1       # the patch was marked studded : the surface under the shelf is plates
    placed = []
    # shelf : 3 rows x W of white plates (3710 1x4 / 3023 1x2 / 3024) clipped on the studs of the patch
    from tiler import tile, PLATES
    cells = {(r0 + F + a, c0 + F + b) for a in range(3) for b in range(W)}
    for (r, c, nr, nc, part, rot) in tile(cells, {k: v for k, v in PLATES.items() if k[0] == 1 and k[1] <= 4 or k == (2, 2)}, B.rng, 1.8, 8, S.stud_cells(y), 12): S.add(part, 15, r, c, y, rot, "shelf")
    yf = y + 1
    for i, f in enumerate(cand[:n]):
        cc0 = c0 + F + 1 + i * 3
        for (dr, dc, dy, part, col, rot) in f["recipe"]: S.add(part, col, r0 + F + dr, cc0 + dc, yf + dy, rot, "figure_" + f["id"])
        placed.append(f["id"])
    # gold label strip under the shelf (tiles clipped on the studs of the patch, row 3)
    lab = {(r0 + F + 3, c0 + F + b) for b in range(W)}
    for (r, c, nr, nc, part, rot) in tile(lab, {(1, 2): "3069b"}, B.rng, 1.0, 2, S.stud_cells(y), 4) if W % 2 == 0 else []: pass
    log["shelf"] = dict(row=r0, col=c0, size=[H, W], level=L); return placed
def run(B, cfg_all, CAT, PAIRS):
    """entry point called by the style builder before the layers are built (reserve) -> returns a callback to place after the layers"""
    cfg = cfg_all.get("figures", {}); log = dict(config=cfg, accepted=[], rejected=[])
    if not cfg.get("enabled") or cfg.get("mode", "off") == "off": log["status"] = "off"; return None, log
    theme = cfg.get("theme", "auto")
    if theme == "auto": theme = B.cp.get("theme", "italy")
    cat = load_catalog(theme)
    if not cat: log["status"] = "no catalogue for theme %s" % theme; return None, log
    cand, rej = screen(cat, cfg, CAT, PAIRS); log["rejected"] = [dict(id=i, reason=r) for i, r in rej]; log["candidates"] = [f["id"] for f in cand]
    if cfg["mode"] == "on_map": log["status"] = "on_map not implemented in V0.6.1 : rejected (would need land-safe patches ; see report)"; return None, log
    if cfg["mode"] == "frame": log["status"] = "frame mode not implemented in V0.6.1 (would need a wider frame strip) : rejected"; return None, log
    if not cand: log["status"] = "no accepted figure"; return None, log
    n = min(cfg["max_count"], len(cand)); H, W = shelf_dims(n); z = None
    for anchor in ("top-right", "top-left"):
        z = B.reserve(H, W, anchor, 3)
        if z: break
        log.setdefault("refused_anchors", []).append(dict(anchor=anchor, reason="overlaps land or a reserved zone"))
    if not z: log["status"] = "no free slot"; return None, log
    B.studded[z[0]:z[0] + H, z[1]:z[1] + W] = True
    def after():
        r0, c0, L = z; F = B.F; S = B.S; y = B.y0 + L * B.thick + 1; W_ = W
        from tiler import tile, PLATES
        cells = {(r0 + F + a, c0 + F + b) for a in range(3) for b in range(W_)}
        for (r, c, nr, nc, part, rot) in tile(cells, {k: v for k, v in PLATES.items() if (k[0] == 1 and k[1] <= 4) or k == (2, 2)}, B.rng, 1.8, 8, S.stud_cells(y), 12): S.add(part, 15, r, c, y, rot, "shelf")
        yf = y + 1; placed = []
        for i, f in enumerate(cand[:n]):
            cc0 = c0 + F + 1 + i * 3
            for (dr, dc, dy, part, col, rot) in f["recipe"]: S.add(part, col, r0 + F + dr, cc0 + dc, yf + dy, rot, "figure_" + f["id"])
            placed.append(f["id"])
        log["accepted"] = placed; log["status"] = "shelf placed"; log["shelf"] = dict(row=r0, col=c0, size=[H, W_], level=L, anchor_note="top-right if free")
    return after, log
