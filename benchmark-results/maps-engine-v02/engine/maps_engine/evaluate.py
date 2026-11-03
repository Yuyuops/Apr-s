"""Evaluation (V0.1), only after generation : IoU per class (pixel and cell level), contour displacement (mm), thin-feature surface ratio, height accuracy, colour error (dE76 and dE2000) of the REAL LEGO colour values. Works for any n (32, 48...)."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from .common import lab, dE2000, ROOT

KIND = {"land": "terre", "forest": "foret", "hills": "colline", "peak": "sommet", "lake": "lac", "road": "route", "river": "riviere", "village": "village"}
def hexrgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))

def oracle_rasters(path):
    o = json.load(open(path)); w, h = o["canvas_px"]; cls = Image.new("L", (w, h), 0); ht = Image.new("L", (w, h), o["base"]["height_plates"]); names = ["mer"] + sorted(set(KIND.values()))
    dc, dh = ImageDraw.Draw(cls), ImageDraw.Draw(ht)
    for it in o["regions"]:
        pts = [tuple(p) for p in it["points"]]; c = names.index(KIND[it["kind"]]); lv = it["height_plates"]
        if it["type"] == "polygon": dc.polygon(pts, fill=c); (dh.polygon(pts, fill=lv) if lv is not None else None)
        elif it["type"] == "polyline": dc.line(pts, fill=c, width=it["width"]); (dh.line(pts, fill=lv, width=it["width"]) if lv is not None else None)
        else: x, y = pts[0]; r = it["radius"]; dc.ellipse((x - r, y - r, x + r, y + r), fill=c)
    colours = {"mer": hexrgb(o["base"]["color"])}; colours.update({KIND[it["kind"]]: hexrgb(it["color"]) for it in o["regions"]})
    return np.asarray(cls), np.asarray(ht), names, colours

def cell_index(size, n): return (np.arange(size) * n) // size
def cell_counts(lab_img, n, k):
    S = lab_img.shape[0]; ci = cell_index(S, n); flat = (ci[:, None] * n + ci[None, :]).ravel(); cnt = np.zeros((n * n, k), int)
    np.add.at(cnt, (flat, lab_img.ravel()), 1); return cnt.reshape(n, n, k)
def bnd(a):
    b = np.zeros(a.shape, bool); b[:-1] |= a[:-1] != a[1:]; b[:, :-1] |= a[:, :-1] != a[:, 1:]; return b

def evaluate(result_json, oracle_json, out=None, mm_per_px=0.5):
    R = json.load(open(result_json)); grid = np.array(R["grid"]); classes = R["classes"]; n = grid.shape[0]
    oc, oh, names, ocol = oracle_rasters(oracle_json); S = oc.shape[0]; ci = cell_index(S, n)
    mine_px = grid[ci][:, ci]; name_px = np.array(classes, dtype=object)[mine_px]; o_px = np.array(names, dtype=object)[oc]
    cnt = cell_counts(oc, n, len(names)); cellpx = (S / n) ** 2; ocell = np.empty((n, n), dtype=object)
    for r in range(n):
        for c in range(n):
            thin = [i for i, nm in enumerate(names) if nm in ("route", "riviere", "village") and cnt[r, c, i] >= 0.2 * cellpx]
            ocell[r, c] = names[max(thin, key=lambda i: cnt[r, c, i])] if thin else names[int(cnt[r, c].argmax())]
    mine_cell = np.array(classes, dtype=object)[grid]; res = dict(n=n, classes={})
    for nm in names:
        a, b = name_px == nm, o_px == nm; ac, bc = mine_cell == nm, ocell == nm
        d = dict(iou_pixels=round(float((a & b).sum() / max(1, (a | b).sum())), 3), iou_cellules=round(float((ac & bc).sum() / max(1, (ac | bc).sum())), 3), cellules_moteur=int(ac.sum()), cellules_oracle=int(bc.sum()), rapport_surface_moteur_sur_oracle=round(float(a.sum() / max(1, b.sum())), 2))
        ba, bb = a ^ ndimage.binary_erosion(a), b ^ ndimage.binary_erosion(b)
        if ba.any() and bb.any(): d1 = ndimage.distance_transform_edt(~bb)[ba]; d2 = ndimage.distance_transform_edt(~ba)[bb]; d["deplacement_contour_moyen_mm"] = round(float((d1.mean() + d2.mean()) / 2 * mm_per_px), 2); d["deplacement_contour_max_mm"] = round(float(max(d1.max(), d2.max()) * mm_per_px), 2)
        res["classes"][nm] = d
    res["iou_pixels_moyen"] = round(float(np.mean([v["iou_pixels"] for v in res["classes"].values()])), 3); res["iou_cellules_moyen"] = round(float(np.mean([v["iou_cellules"] for v in res["classes"].values()])), 3)
    res["precision_pixels_globale"] = round(float((name_px == o_px).mean()), 4)
    cd = [v["deplacement_contour_moyen_mm"] for v in res["classes"].values() if "deplacement_contour_moyen_mm" in v]; res["deplacement_contour_moyen_mm"] = round(float(np.mean(cd)), 2)
    res["deplacement_contour_max_mm"] = round(float(max(v.get("deplacement_contour_max_mm", 0) for v in res["classes"].values())), 2)
    for nm in ("riviere", "route"):
        for tag, g in (("moteur", mine_cell == nm), ("oracle", ocell == nm)): res.setdefault("composantes_connexes_8", {}).setdefault(nm, {})[tag] = int(ndimage.label(g, structure=np.ones((3, 3)))[1])
    hh = np.array(R["heights"]); oh_c = np.zeros((n, n), int)
    for r in range(n):
        for c in range(n): oh_c[r, c] = np.bincount(oh[ci == r][:, ci == c].ravel()).argmax()
    res["hauteurs"] = dict(cellules_identiques=round(float((hh == oh_c).mean()), 4), erreur_absolue_moyenne_plaques=round(float(np.abs(hh - oh_c).mean()), 3), mode=R.get("mode"))
    col = {}; t76 = t00 = cells = 0
    for nm, v in R["lego_colours"].items():
        if nm in ocol:
            a = lab(np.array(v["rgb"], float)); b = lab(np.array(ocol[nm], float)); d76 = float(np.linalg.norm(a - b)); d00 = float(dE2000(a, b)); k = int((mine_cell == nm).sum())
            col[nm] = dict(lego=v["name"], code=v["code"], dE76=round(d76, 1), dE2000=round(d00, 1), cellules=k); t76 += d76 * k; t00 += d00 * k; cells += k
    res["couleurs_reelles"] = col; res["dE76_moyen_pondere_surface"] = round(t76 / max(1, cells), 2); res["dE2000_moyen_pondere_surface"] = round(t00 / max(1, cells), 2)
    if out: json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    return res

def evaluate_by_source_colours(result_json, png, class_hex, out=None):
    """second map (no oracle file) : reference classes = the exact flat fills of the source SVG (names given by the evaluator)"""
    R = json.load(open(result_json)); grid = np.array(R["grid"]); classes = R["classes"]; n = grid.shape[0]
    img = np.asarray(Image.open(png).convert("RGB")).astype(int); names = list(class_hex); cols = np.array([hexrgb(class_hex[k]) for k in names])
    ref = np.linalg.norm(img[:, :, None, :] - cols[None, None, :, :], axis=3).argmin(2); ci = cell_index(img.shape[0], n); mine_px = grid[ci][:, ci]; res = dict(n=n, classes={})
    cnt = cell_counts(ref, n, len(names)); cellref = cnt.argmax(2)
    for i, nm in enumerate(names):
        a = np.array([classes[v] == nm for v in mine_px.ravel()]).reshape(mine_px.shape); b = ref == i
        ac = np.array([[classes[v] == nm for v in row] for row in grid]); bc = cellref == i
        res["classes"][nm] = dict(iou_pixels=round(float((a & b).sum() / max(1, (a | b).sum())), 3), iou_cellules=round(float((ac & bc).sum() / max(1, (ac | bc).sum())), 3))
    res["iou_cellules_moyen"] = round(float(np.mean([v["iou_cellules"] for v in res["classes"].values()])), 3); res["iou_pixels_moyen"] = round(float(np.mean([v["iou_pixels"] for v in res["classes"].values()])), 3)
    col = {}; t76 = t00 = cells = 0
    for nm, v in R["lego_colours"].items():
        if nm in class_hex:
            a = lab(np.array(v["rgb"], float)); b = lab(np.array(hexrgb(class_hex[nm]), float)); d76 = float(np.linalg.norm(a - b)); d00 = float(dE2000(a, b)); k = int((np.array(classes, dtype=object)[grid] == nm).sum())
            col[nm] = dict(lego=v["name"], dE76=round(d76, 1), dE2000=round(d00, 1), cellules=k); t76 += d76 * k; t00 += d00 * k; cells += k
    res["classes_trouvees_par_le_moteur"] = classes; res["couleurs_reelles"] = col; res["dE76_moyen_pondere_surface"] = round(t76 / max(1, cells), 2); res["dE2000_moyen_pondere_surface"] = round(t00 / max(1, cells), 2)
    if out: json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    return res
