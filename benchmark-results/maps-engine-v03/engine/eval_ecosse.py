"""Evaluation of the third map (no oracle file) : the reference is the set of flat colours the map was drawn with (fixtures/make_ecosse_map.py). Reports : how the engine's classes cover each reference colour (semantic purity), IoU after the best 1-to-1 mapping,
thin-feature recall (river, road, cities), coast displacement of the REAL footprint, and what the engine did with every colour. usage: python eval_ecosse.py <run dir> <input png> > eval.json"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.optimize import linear_sum_assignment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maps_engine import compare as K, evaluate as E
REF = {"mer": (49, 92, 156), "terre_Angleterre_Ecosse": (236, 226, 190), "Irlande": (110, 158, 98), "lac_riviere": (120, 170, 215), "massif": (150, 118, 78), "route": (176, 128, 84), "ville": (170, 55, 40)}
def run(d, png):
    R = json.load(open(os.path.join(d, "classes_hauteurs.json"))); grid = np.array(R["grid"]); classes = R["classes"]; n = grid.shape[0]
    img = np.asarray(Image.open(png).convert("RGB")).astype(int); S = img.shape[0]; names = list(REF); cols = np.array([REF[k] for k in names]); ref = np.linalg.norm(img[:, :, None, :] - cols[None, None, :, :], axis=3).argmin(2)
    ci = (np.arange(S) * n) // S; mine = grid[ci][:, ci]; out = dict(n=n, classes_moteur=classes)
    conf = np.zeros((len(names), len(classes)), int)
    for i in range(len(names)): conf[i] = np.bincount(mine[ref == i], minlength=len(classes))
    out["couverture_pixels_de_chaque_couleur_de_la_source_par_classe_moteur"] = {names[i]: {classes[j]: round(float(conf[i, j] / max(1, conf[i].sum())), 3) for j in range(len(classes)) if conf[i, j] / max(1, conf[i].sum()) > 0.02} for i in range(len(names))}
    r, c = linear_sum_assignment(-conf); mapping = {names[i]: classes[j] for i, j in zip(r, c)}; out["meilleure_correspondance_1_a_1"] = mapping
    iou = {}
    for i, j in zip(r, c): a = mine == j; b = ref == i; iou[names[i]] = round(float((a & b).sum() / max(1, (a | b).sum())), 3)
    out["iou_pixels_apres_correspondance"] = iou; out["classes_de_la_source_sans_classe_propre"] = [names[i] for i in range(len(names)) if i not in r]
    # thin features : a thin pixel counts as found when its cell is not a plain sea / main-land cell
    base = {classes.index(mapping[k]) for k in ("mer", "terre_Angleterre_Ecosse") if k in mapping}
    for nm in ("lac_riviere", "route", "ville"):
        i = names.index(nm); m = ref == i; out["rappel_" + nm] = round(float((~np.isin(mine[m], list(base))).mean()), 3) if m.any() else None
    comp = {}
    for nm in ("lac_riviere", "route"):
        if nm in mapping: comp[nm] = dict(composantes_moteur=int(ndimage.label(grid == classes.index(mapping[nm]), structure=np.ones((3, 3)))[1]), composantes_source=int(ndimage.label(ref[::4, ::4] == names.index(nm), structure=np.ones((3, 3)))[1]))
    out["composantes_connexes"] = comp
    P = json.load(open(os.path.join(d, "parts.json"))); m_ = R["frame_width"]; mask = K.footprint_mask(P, m_, n); land_ref = ref != names.index("mer")
    wc = np.isin(np.array(classes, dtype=object)[grid], [mapping.get("lac_riviere")]) if "lac_riviere" in mapping else np.zeros((n, n), bool)
    mm = (np.arange(512) * n) // 512; mask = mask | wc[mm][:, mm]; mask = ndimage.binary_fill_holes(mask); lr = np.asarray(Image.fromarray(land_ref.astype(np.uint8) * 255).resize((512, 512), Image.NEAREST)) > 0; lr = ndimage.binary_fill_holes(lr)
    ba, bb = mask ^ ndimage.binary_erosion(mask), lr ^ ndimage.binary_erosion(lr); d1 = ndimage.distance_transform_edt(~bb)[ba]; d2 = ndimage.distance_transform_edt(~ba)[bb]; mmpx = 256.0 / 512
    out["cote_reelle"] = dict(deplacement_moyen_mm=round(float((d1.mean() + d2.mean()) / 2 * mmpx * (R["n"] / 32.0 if False else 1)), 2), iou_terre=round(float((mask & lr).sum() / (mask | lr).sum()), 4), champ_mm=round(n * 8.0, 0))
    col = {}; t76 = t00 = tot = 0
    from maps_engine.common import lab, dE2000
    for nm, v in R["lego_colours"].items():
        cells = int((grid == classes.index(nm)).sum()); i = [k for k, vv in mapping.items() if vv == nm]
        if i: a = lab(np.array(v["rgb"], float)); b = lab(np.array(REF[i[0]], float)); d76 = float(np.linalg.norm(a - b)); d00 = float(dE2000(a, b)); col[nm] = dict(source=i[0], lego=v["name"], dE76=round(d76, 1), dE2000=round(d00, 1), cellules=cells); t76 += d76 * cells; t00 += d00 * cells; tot += cells
    out["couleurs"] = col; out["dE2000_moyen_pondere"] = round(t00 / max(1, tot), 2); out["dE76_moyen_pondere"] = round(t76 / max(1, tot), 2)
    return out
if __name__ == "__main__": print(json.dumps(run(sys.argv[1], sys.argv[2]), indent=1, ensure_ascii=False))
