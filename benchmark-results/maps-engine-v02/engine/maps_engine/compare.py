"""V0 / V0.1 A / V0.1 B comparison (island and three-zone map) : every number is computed from the output files ; V0 files are only READ."""
import json, os, sys
from collections import defaultdict
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
from .common import lab, dE2000, rb_colours, ROOT
from . import evaluate as E, validate as V

V0 = os.path.normpath(os.path.join(ROOT, "..", "maps-engine-v0", "results"))

def v0_parts():
    P = json.load(open(os.path.join(V0, "parts.json"))); out = []
    for p in P: out.append(dict(id=p["id"], kind="plate", x=p["z"], z=p["x"], w=p["d"], d=p["w"], zbot=p["level"] + 2, h=1, colour=p["colour"], layer=("B" if p["level"] < 0 else "L") + str(p["level"]), region=p["region"], part=p["part"], size=p["name_size"]))
    return out   # V0 x = image row, z = column : swapped to the V0.1 convention (x row, z col) is NOT needed for counts ; only counts and masses are used

def class_legibility(R, levels=None):
    """share of adjacent class pairs that stay distinguishable (colour contrast dE2000 >= 8, or one relief level of difference with contrast >= 4) and the weakest contrast"""
    grid = np.array(R["grid"]); classes = R["classes"]; n = grid.shape[0]; adj = set()
    for r in range(n):
        for c in range(n):
            for dr, dc in ((1, 0), (0, 1)):
                if r + dr < n and c + dc < n and grid[r, c] != grid[r + dr, c + dc]: adj.add(tuple(sorted((classes[grid[r, c]], classes[grid[r + dr, c + dc]]))))
    lv = dict(zip(classes, [None] * len(classes))); H = np.array(R["heights"])
    for i, nm in enumerate(classes): lv[nm] = int(np.bincount(H[grid == i]).argmax()) if (grid == i).any() else 0
    ok = 0; weakest = (99, None); rows = []
    for a, b in sorted(adj):
        d = float(dE2000(lab(np.array(R["lego_colours"][a]["rgb"], float)), lab(np.array(R["lego_colours"][b]["rgb"], float)))); step = abs(lv[a] - lv[b])
        dsrc = float(dE2000(lab(np.array(R["source_colours"][a], float)), lab(np.array(R["source_colours"][b], float)))); same_by_design = dsrc < 4          # the source itself draws them in one colour (a lake and its river)
        good = same_by_design or d >= 8 or step >= 2 or (step >= 1 and d >= 4); ok += good; rows.append(dict(paire=[a, b], dE2000=round(d, 1), dE2000_source=round(dsrc, 1), marche_de_hauteur=step, lisible=bool(good)))
        if d < weakest[0] and step == 0: weakest = (d, (a, b))
    return dict(paires_adjacentes=len(adj), paires_lisibles=ok, part_lisible=round(ok / max(1, len(adj)), 3), detail=rows)

def footprint_contour(parts_L, classes_n, cut_cells, oracle, level_class="terre", size=512):
    """contour displacement (mm) of the REAL land footprint at the top land level, wedge plates included (the cut triangle has legs of one stud)"""
    return None

def summarize(d, name):
    gen = json.load(open(os.path.join(d, "generation.json"))); val = json.load(open(os.path.join(d, "validation", "validation_resume.json"))); R = json.load(open(os.path.join(d, "classes_hauteurs.json")))
    m1, m2 = val["moteur1"], val["moteur2"]; steps = json.load(open(os.path.join(d, "etapes.json")))
    row = dict(nom=name, pieces=m2["pieces"], references=m2["references"], pieces_1x1=m2["pieces_1x1"], part_1x1=m2["part_1x1"], couches_de_plaques=m2["couches_de_plaques"], epaisseur_mm=m2["dimensions_mm"]["epaisseur"], masse_g=m2["masse_estimee_g"],
               pieces_sur_un_seul_tenon=m2["pieces_sur_un_seul_tenon"], points_articulation=m2["points_d_articulation"], collisions=m1["collisions"], deconnectees=m1["disconnected_parts"], composantes=m2["graphe"]["composantes"], liaisons=m1["joints"], tenons_engages=m1["studs_engaged"],
               coupe_noyau_tenons=m2.get("noyau_dos_et_cadre", {}).get("coupe_minimale_tenons"), etapes=len(steps), pieces_max_par_etape=max(len(s["pieces"]) for s in steps), coins_coupes=gen.get("coins_coupes", 0), force_bout_min_N=m1["stabilite_moteur1"].get("min_tip_force_N"),
               alignement_joints=m2["alignement_des_joints_entre_couches"], sections=m2["pieces_par_section"], tableau_complet_mm=m2["dimensions_mm"]["tableau_complet"], lisibilite=class_legibility(R))
    return row

def footprint_mask(parts, m, n, level_layer="L1", size=512, wedge_leg=1.0):
    """binary raster (size x size) of the real footprint of one relief layer (every cell at height >= 1), wedge plates with their cut triangle ; field only"""
    img = Image.new("L", (size, size), 0); dr = ImageDraw.Draw(img); s = size / n
    for p in parts:
        if p["layer"] != level_layer: continue
        x0 = (p["z"] - m) * s; y0 = (p["x"] - m) * s; x1 = x0 + p["d"] * s; y1 = y0 + p["w"] * s
        if not p.get("wedge"): dr.rectangle((x0, y0, x1 - 1, y1 - 1), fill=255); continue
        rot = p["rot"]; corner = {"1 0 0 0 1 0 0 0 1": "SE", "0 0 1 0 1 0 -1 0 0": "SW", "-1 0 0 0 1 0 0 0 -1": "NW", "0 0 -1 0 1 0 1 0 0": "NE"}[rot]; L = wedge_leg * s
        poly = {"SE": [(x0, y0), (x1, y0), (x1, y1 - L), (x1 - L, y1), (x0, y1)], "SW": [(x0, y0), (x1, y0), (x1, y1), (x0 + L, y1), (x0, y1 - L)], "NW": [(x0 + L, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0 + L)], "NE": [(x0, y0), (x1 - L, y0), (x1, y0 + L), (x1, y1), (x0, y1)]}[corner]
        dr.polygon(poly, fill=255)
    return np.asarray(img) > 0

def land_contour_error(mask, oracle_json, water_cells=None):
    """outer coastline error (mm) of the REAL footprint : lakes and rivers are counted as land on both sides (they are scored by their own class metrics), so that a river that reaches the sea in the LEGO but not in the source does not distort the coast"""
    oc, oh, names, _ = E.oracle_rasters(oracle_json); nm = np.array(names, dtype=object)[oc]; ref = np.isin(nm, ["terre", "foret", "colline", "sommet", "route", "village", "lac", "riviere"]); size = mask.shape[0]
    if ref.shape[0] != size: ref = np.asarray(Image.fromarray(ref.astype(np.uint8) * 255).resize((size, size), Image.NEAREST)) > 0
    if water_cells is not None: ci = (np.arange(size) * water_cells.shape[0]) // size; mask = mask | water_cells[ci][:, ci]
    mask = ndimage.binary_fill_holes(mask); ref = ndimage.binary_fill_holes(ref)
    ba, bb = mask ^ ndimage.binary_erosion(mask), ref ^ ndimage.binary_erosion(ref); d1 = ndimage.distance_transform_edt(~bb)[ba]; d2 = ndimage.distance_transform_edt(~ba)[bb]; mm = 256.0 / size
    return dict(deplacement_moyen_mm=round(float((d1.mean() + d2.mean()) / 2 * mm), 2), deplacement_max_mm=round(float(max(d1.max(), d2.max()) * mm), 2), iou_terre=round(float((mask & ref).sum() / (mask | ref).sum()), 4))
