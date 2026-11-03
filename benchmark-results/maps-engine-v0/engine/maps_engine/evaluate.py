"""Evaluation against the oracle (ONLY after the blind first trial): IoU per class (pixel and cell level), boundary F1, height accuracy, real LEGO colour error. Read-only on the oracle."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from .common import lab, ROOT

KIND = {"land": "terre", "forest": "foret", "hills": "colline", "peak": "sommet", "lake": "lac", "road": "route", "river": "riviere", "village": "village"}
def hexrgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))

def oracle_rasters(path, size=512):
    o = json.load(open(path)); w, h = o["canvas_px"]; cls = Image.new("L", (w, h), 0); ht = Image.new("L", (w, h), o["base"]["height_plates"]); names = ["mer"] + sorted(set(KIND.values()))
    dc, dh = ImageDraw.Draw(cls), ImageDraw.Draw(ht)
    for it in o["regions"]:
        pts = [tuple(p) for p in it["points"]]; c = names.index(KIND[it["kind"]]); lv = it["height_plates"]
        if it["type"] == "polygon": dc.polygon(pts, fill=c); (dh.polygon(pts, fill=lv) if lv is not None else None)
        elif it["type"] == "polyline": dc.line(pts, fill=c, width=it["width"]); (dh.line(pts, fill=lv, width=it["width"]) if lv is not None else None)
        else: x, y = pts[0]; r = it["radius"]; dc.ellipse((x - r, y - r, x + r, y + r), fill=c)
    colours = {"mer": hexrgb(o["base"]["color"])}; colours.update({KIND[it["kind"]]: hexrgb(it["color"]) for it in o["regions"]})
    return np.asarray(cls), np.asarray(ht), names, colours

def boundary(g):
    b = np.zeros(g.shape, bool); b[:-1] |= g[:-1] != g[1:]; b[1:] |= g[:-1] != g[1:]; b[:, :-1] |= g[:, :-1] != g[:, 1:]; b[:, 1:] |= g[:, :-1] != g[:, 1:]; return b

def evaluate(result_json, oracle_json, out=None):
    R = json.load(open(result_json)); grid = np.array(R["grid"]); classes = R["classes"]; n = grid.shape[0]
    oc, oh, names, ocol = oracle_rasters(oracle_json); cell = oc.shape[0] // n
    mine_px = np.kron(grid, np.ones((cell, cell), int)); name_px = np.array(classes, dtype=object)[mine_px]; o_px = np.array(names, dtype=object)[oc]
    mine_cell = np.array(classes, dtype=object)[grid]
    # oracle at cell level : majority class, thin classes win from 20 % of the cell (same rule as the engine would be unfair : report both majority and any-coverage)
    ocell_maj = np.empty((n, n), dtype=object); ocell_any = np.empty((n, n), dtype=object)
    for r in range(n):
        for c in range(n):
            blk = oc[r * cell:(r + 1) * cell, c * cell:(c + 1) * cell]; cnt = np.bincount(blk.ravel(), minlength=len(names)); ocell_maj[r, c] = names[cnt.argmax()]
            thin = [i for i, nm in enumerate(names) if nm in ("route", "riviere", "village") and cnt[i] >= 0.2 * cell * cell]; ocell_any[r, c] = names[max(thin, key=lambda i: cnt[i])] if thin else names[cnt.argmax()]
    res = dict(classes={})
    for nm in names:
        a, b = (name_px == nm), (o_px == nm); ac, bc = (mine_cell == nm), (ocell_any == nm)
        res["classes"][nm] = dict(iou_pixels=round(float((a & b).sum() / max(1, (a | b).sum())), 3), iou_cellules=round(float((ac & bc).sum() / max(1, (ac | bc).sum())), 3), cellules_moteur=int(ac.sum()), cellules_oracle=int(bc.sum()))
    res["iou_pixels_moyen"] = round(float(np.mean([v["iou_pixels"] for v in res["classes"].values()])), 3); res["iou_cellules_moyen"] = round(float(np.mean([v["iou_cellules"] for v in res["classes"].values()])), 3)
    res["precision_pixels_globale"] = round(float((name_px == o_px).mean()), 4)
    # boundary F1 (tolerance : 1 cell)
    bm, bo = boundary(mine_cell.astype(str)), boundary(ocell_any.astype(str)); tol = np.ones((3, 3), bool)
    p = (bm & ndimage.binary_dilation(bo, structure=tol)).sum() / max(1, bm.sum()); r_ = (bo & ndimage.binary_dilation(bm, structure=tol)).sum() / max(1, bo.sum())
    res["frontieres_F1_tolerance_1_cellule"] = round(float(2 * p * r_ / max(1e-9, p + r_)), 3); res["frontieres_precision_rappel"] = [round(float(p), 3), round(float(r_), 3)]
    # fine features kept : connected components of thin classes
    for nm in ("riviere", "route"):
        for tag, g in (("moteur", mine_cell == nm), ("oracle", ocell_any == nm)):
            res.setdefault("composantes_connexes_8", {}).setdefault(nm, {})[tag] = int(ndimage.label(g, structure=np.ones((3, 3)))[1])
    # heights
    hh = np.array(R["heights"]); oh_c = np.zeros((n, n), int)
    for r in range(n):
        for c in range(n): oh_c[r, c] = np.bincount(oh[r * cell:(r + 1) * cell, c * cell:(c + 1) * cell].ravel()).argmax()
    res["hauteurs"] = dict(cellules_identiques=round(float((hh == oh_c).mean()), 4), erreur_absolue_moyenne_plaques=round(float(np.abs(hh - oh_c).mean()), 3), erreur_max=int(np.abs(hh - oh_c).max()), mode=R["mode"])
    # real LEGO colour error : LDraw value of the chosen colour vs the oracle source colour, per class and cell-weighted
    col = {}; tot = 0; cells = 0
    for nm, v in R["lego_colours"].items():
        if nm in ocol:
            d = float(np.linalg.norm(lab(v["rgb"]) - lab(ocol[nm]))); k = int((mine_cell == nm).sum()); col[nm] = dict(lego=v["name"], code=v["code"], dE76=round(d, 1), cellules=k); tot += d * k; cells += k
    res["couleurs_reelles"] = col; res["dE_moyen_pondere_surface"] = round(tot / max(1, cells), 2)
    if out: json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    return res

if __name__ == "__main__":
    r = evaluate(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); print(json.dumps(r, indent=1, ensure_ascii=False))

def evaluate_by_source_colours(result_json, png, class_hex, out=None):
    """second test (no oracle file) : the reference classes are the exact flat fills of the source SVG (class names given by the evaluator), compared pixel by pixel / cell by cell"""
    R = json.load(open(result_json)); grid = np.array(R["grid"]); classes = R["classes"]; n = grid.shape[0]
    img = np.asarray(Image.open(png).convert("RGB")).astype(int); names = list(class_hex); cols = np.array([hexrgb(class_hex[k]) for k in names])
    ref = np.linalg.norm(img[:, :, None, :] - cols[None, None, :, :], axis=3).argmin(2); cell = img.shape[0] // n
    mine_px = np.kron(grid, np.ones((cell, cell), int)); res = dict(classes={})
    for i, nm in enumerate(names):
        a = np.array([classes[v] == nm for v in mine_px.ravel()]).reshape(mine_px.shape); b = ref == i
        res["classes"][nm] = dict(iou_pixels=round(float((a & b).sum() / max(1, (a | b).sum())), 3))
    cellref = np.zeros((n, n), int)
    for r in range(n):
        for c in range(n): cellref[r, c] = np.bincount(ref[r * cell:(r + 1) * cell, c * cell:(c + 1) * cell].ravel(), minlength=len(names)).argmax()
    for i, nm in enumerate(names):
        a = np.array([[classes[v] == nm for v in row] for row in grid]); b = cellref == i; res["classes"][nm]["iou_cellules"] = round(float((a & b).sum() / max(1, (a | b).sum())), 3)
    res["iou_cellules_moyen"] = round(float(np.mean([v["iou_cellules"] for v in res["classes"].values()])), 3); res["iou_pixels_moyen"] = round(float(np.mean([v["iou_pixels"] for v in res["classes"].values()])), 3)
    res["classes_trouvees_par_le_moteur"] = classes
    col = {}; tot = 0; cells = 0
    for nm, v in R["lego_colours"].items():
        if nm in class_hex: d = float(np.linalg.norm(lab(v["rgb"]) - lab(hexrgb(class_hex[nm])))); k = int((np.array(classes, dtype=object)[grid] == nm).sum()); col[nm] = dict(lego=v["name"], dE76=round(d, 1), cellules=k); tot += d * k; cells += k
    res["couleurs_reelles"] = col; res["dE_moyen_pondere_surface"] = round(tot / max(1, cells), 2)
    if out: json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    return res
