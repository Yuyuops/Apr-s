"""LEGO engine 1 : automatic audit of colour and placement fidelity between the source GLB and the generated LDraw model.

Nothing is rendered : the colours of the real parts (exposed cells of the assembled model) are compared with the colours of the GLB surface around them, so the joints and the
shadows of a render can never be counted as defects. Everything is derived from the data of the run ; no coordinate of a subject is coded.

  colours   : every exposed cell of the model (a cell of 20 x 8 x 20 ldu touching the outside) gets the colour of its LDraw part ; the colour of the GLB is the mean of the nearest
              surface vertices ; delta E (CIE76 in Lab) ; the "floor" is the smallest delta E reachable with the allowed palette (colours not excluded and available as a plate in
              >= 20 Rebrickable sets) ; excess = delta E - floor : the part of the error that the palette could have avoided.
              A cell is a parasite when its excess is >= PARASITE_DE (40) : its colour is another colour than the palette colour nearest to the GLB.
  no match  : GLB samples whose floor is >= NO_MATCH_DE (30) : no acceptable colour in the catalogue.
  confusion : (colour expected from the GLB, colour actually built) -> number of exposed cells.
  placement : occupancy IoU zone by zone (fine occupancy of the GLB against the model) ; ears (centroid, axes, extent against the dark GLB cloud of the ear zone, asymmetry against
              the sagittal plane) ; GLB patches (eyes, nose, mouth) against the built detail parts and exposed cells ; visible structural parts (SNOT bricks).
  module    : the responsible module of every defect (palette of the volume, ear module, detail modules, mouth module, rebuild/reinforcement) from the part types and, when the run
              folder is given, from the intermediate grids of the run.
usage: audit_fidelity.py --glb ref_full_frame.glb --ldr model.ldr --grid full400.npz --seg segmentation.npz --details details.json --exclude 1,2,.. --out folder [--run <run folder>]
"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import LDRAW, RB_DB
import argparse, json, os, re, sqlite3, sys
from collections import Counter, defaultdict
import numpy as np
from scipy.spatial import cKDTree
import trimesh

PARASITE_DE = 40.0; NO_MATCH_DE = 30.0; RADIUS_LDU = 24.0
DETAIL_NUMS = {"43898", "98138", "87087", "6141", "3960", "54200", "4740", "14769", "18674", "85861", "3941", "4150"}
SNOT_STRUCT = {"52107", "47905", "87087", "99207", "3937"}
CODE_RGB = {"noir": 0, "blanc": 15, "rouge": 4, "jaune": 14}

def ldconfig(path):
    out = {}
    for l in open(path, errors="replace"):
        m = re.search(r"!COLOUR\s+(\S+)\s+CODE\s+(\d+)\s+VALUE\s+#([0-9A-Fa-f]{6})", l)
        if m:
            nm = m.group(1); special = ("ALPHA" in l) or ("MATERIAL" in l) or nm.lower().startswith(("trans", "chrome", "glitter", "pearl", "metal", "opal", "speckle", "milky", "glow", "flat_silver", "flat_gold", "rubber"))
            out[int(m.group(2))] = (nm, tuple(int(m.group(3)[i:i + 2], 16) for i in (0, 2, 4)), special)
    return out

def lab(rgb):
    c = np.asarray(rgb, float) / 255.0; c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]); xyz = (c @ M.T) / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)

def allowed_palette(codes, exclude, rb):
    db = sqlite3.connect(rb); ok = []
    for c, (name, rgb, special) in codes.items():
        if special or c in exclude or c >= 512: continue
        r = db.execute("select num_sets from pcs_mat where part_num='3024' and color_id=?", (c,)).fetchone()
        if r and r[0] >= 20: ok.append(c)
    return ok

def audit(glb, ldr, grid_npz, seg_npz, details_json, exclude, run=None, outdir=None):
    import scope
    codes = ldconfig(os.path.join(LDRAW, "LDConfig.ldr")); pal = allowed_palette(codes, set(exclude), RB_DB)
    pal_lab = lab([codes[c][1] for c in pal])
    g = np.load(grid_npz); shape = g["grid"].shape; scope.SHAPE = tuple(max(s, 8) for s in shape)
    P = scope.read_parts(ldr); V = scope.voxelise(P)
    seg = np.load(seg_npz); labels = seg["labels"]; names = {int(k): v for k, v in json.loads(str(seg["names"])).items()}
    zone_of = lambda c: names.get(int(labels[tuple(c)]), "hors zone") if all(0 <= c[k] < labels.shape[k] for k in range(3)) and labels[tuple(c)] > 0 else "hors zone"
    m = trimesh.load(glb, force="mesh", process=False); Vx = np.asarray(m.vertices); col = np.asarray(m.visual.vertex_colors)[:, :3].astype(float)
    L = np.c_[Vx[:, 0] / 0.4, -Vx[:, 1] / 0.4, -Vx[:, 2] / 0.4]; tree = cKDTree(L)
    out = dict(modele=os.path.basename(ldr), pieces=len(P), palette_autorisee=[codes[c][0] for c in pal])
    # ------------------------------------------------------------------ colours
    ex = V["exposed"] & V["occ"]; cells = np.argwhere(ex); ctr = np.c_[(cells[:, 0] + 0.5) * 20, -(cells[:, 1] + 0.5) * 8, (cells[:, 2] + 0.5) * 20]
    d, idx = tree.query(ctr, k=10, distance_upper_bound=RADIUS_LDU)
    has = np.isfinite(d[:, 0]); w = np.isfinite(d).astype(float); idx = np.where(np.isfinite(d), idx, 0)
    glb_rgb = (col[idx] * w[..., None]).sum(1) / np.maximum(w.sum(1), 1)[:, None]
    codes_cell = V["col"][tuple(cells.T)]; built_lab = lab([codes[int(c)][1] if int(c) in codes else (128, 128, 128) for c in codes_cell]); glb_lab = lab(glb_rgb)
    dE = np.linalg.norm(built_lab - glb_lab, axis=1)
    dist_pal = np.linalg.norm(glb_lab[:, None, :] - pal_lab[None, :, :], axis=2); floor_cat = dist_pal.min(1)          # best colour of the whole allowed catalogue
    eng = sorted(int(c) for c in np.unique(g["grid"]) if c >= 0); eng_lab = lab([codes[c][1] for c in eng])             # colours the quantiser of the engine kept for this subject
    dist_eng = np.linalg.norm(glb_lab[:, None, :] - eng_lab[None, :, :], axis=2); floor = dist_eng.min(1); expected = np.array(eng)[dist_eng.argmin(1)]
    excess = dE - floor; par = has & (excess >= PARASITE_DE); nomatch = has & (floor_cat >= NO_MATCH_DE)
    out["palette_moteur"] = [codes[c][0] for c in eng]
    zone = np.array([zone_of(c) for c in cells]); pid = V["pid"][tuple(cells.T)]
    ptype = np.array([P[i]["num"] if i >= 0 else "?" for i in pid]); sub = np.array([(P[i]["sub"] or "") if i >= 0 else "" for i in pid])
    # module attribution
    def module(k):
        if sub[k]: return "oreilles (generateur V6.1)"
        if ptype[k] in DETAIL_NUMS: return "micro-details / module de bouche (V8 - V8.2)"
        return "volume (palette brickify, reconstruction brickify_plus, renforts)"
    mod = np.array([module(k) for k in range(len(cells))])
    if run:
        try:
            g0 = np.load(os.path.join(run, "grid", "full400.npz"))["grid"]; g2 = np.load(os.path.join(run, "v82", "pre_lcm.npz"))["grid"]; g3 = np.load(os.path.join(run, "v82", "corps_V82.npz"))["grid"]
            for k in range(len(cells)):
                if mod[k].startswith("volume"):
                    c = tuple(cells[k]);
                    if all(c[i] < g0.shape[i] for i in range(3)):
                        if g0[c] == codes_cell[k]: mod[k] = "volume : palette brickify (couleur choisie par le quantificateur)"
                        elif g3[c] == codes_cell[k] and g3[c] != g2[c]: mod[k] = "module de bouche (lcm82)"
                        elif g3[c] == codes_cell[k]: mod[k] = "assemblage V8 (recoloration de surface, micro-details)"
                        else: mod[k] = "reconstruction / renforts (brickify_plus, ponts)"
        except Exception as e: out["attribution_detaillee"] = "indisponible : %s" % e
    out["couleurs"] = dict(cellules_exposees=int(len(cells)), cellules_avec_surface_glb=int(has.sum()), dE_moyen=round(float(dE[has].mean()), 1), dE_median=round(float(np.median(dE[has])), 1),
                            plancher_palette_moteur_moyen=round(float(floor[has].mean()), 1), plancher_catalogue_moyen=round(float(floor_cat[has].mean()), 1), exces_moyen=round(float(excess[has].mean()), 1),
                            cellules_parasites=int(par.sum()), part_parasites=round(float(par.sum() / max(has.sum(), 1)), 4), cellules_sans_correspondance=int(nomatch.sum()))
    out["couleurs"]["par_zone"] = {z: dict(cellules=int(((zone == z) & has).sum()), dE_moyen=round(float(dE[(zone == z) & has].mean()), 1), parasites=int(((zone == z) & par).sum()), exces_moyen=round(float(excess[(zone == z) & has].mean()), 1)) for z in sorted(set(zone[has]))}
    out["couleurs"]["parasites_par_module"] = dict(Counter(mod[par]).most_common())
    conf = Counter((codes[int(e)][0], codes[int(b)][0] if int(b) in codes else str(b)) for e, b, h in zip(expected, codes_cell, has) if h and int(e) != int(b))
    out["couleurs"]["confusions_attendu_construit"] = [dict(attendu=a, construit=b, cellules=int(n)) for (a, b), n in conf.most_common(12)]
    out["couleurs"]["parasites_par_couleur_construite"] = dict(Counter(codes[int(b)][0] if int(b) in codes else str(b) for b in codes_cell[par]).most_common(8))
    out["couleurs"]["parasites_par_type_de_piece"] = dict(Counter(ptype[par]).most_common(8))
    # colours without acceptable match : cluster the GLB samples
    if nomatch.any():
        from sklearn.cluster import KMeans
        X = glb_rgb[nomatch]; k = int(min(4, max(1, len(X) // 40))); km = KMeans(k, n_init=5, random_state=0).fit(X)
        out["couleurs"]["sans_correspondance_groupes"] = [dict(rgb_glb=[int(v) for v in c], cellules=int((km.labels_ == i).sum()), meilleur_catalogue=codes[int(pal[int(lab_d.argmin())])][0], dE_plancher_catalogue=round(float(lab_d.min()), 1))
                                                          for i, c in enumerate(km.cluster_centers_) for lab_d in [np.linalg.norm(lab(c) - pal_lab, axis=1)]]
    # ------------------------------------------------------------------ occupancy IoU by zone
    F = g["fine"]; K = int(g["k"]); NX, NY, NZ = shape; glb_occ = (g["grid"] >= 0) & (F.reshape(NX, K, NY, K, NZ, K).mean(axis=(1, 3, 5)) >= 0.5)
    lego = np.zeros(shape, bool); sl = tuple(slice(0, s) for s in shape); lego[sl] = V["occ"][sl]
    iou = {}
    for lid, nm in names.items():
        z = labels == lid; a, b = glb_occ & z, lego & z
        if a.sum() >= 10: iou[nm] = dict(iou=round(float((a & b).sum() / max((a | b).sum(), 1)), 3), cellules_glb=int(a.sum()), cellules_lego=int(b.sum()))
    out["placement"] = dict(iou_global=round(float((glb_occ & lego).sum() / max((glb_occ | lego).sum(), 1)), 3), iou_par_zone=iou)
    # ------------------------------------------------------------------ ears
    det = json.load(open(details_json)); rep = det["repere"]; n = np.array(rep["normale_plan_sagittal"], float); off = float(rep["plan_offset_mm"])
    ears = {}; subs = sorted({p["sub"] for p in P if p["sub"] and "oreille" in p["sub"] and not p["sub"].endswith("_1")})
    for s in subs:
        lid = [k for k, v in names.items() if v == s.replace("V7_", "")]
        if not lid: continue
        zc = np.argwhere(labels == lid[0]); lo, hi = zc.min(0) - 1, zc.max(0) + 2
        box = np.c_[lo * [20, -8, 20], hi * [20, -8, 20]]; lo_l = np.minimum(box[:, 0], box[:, 1]); hi_l = np.maximum(box[:, 0], box[:, 1])
        dark = col.mean(1) < 80; sel = dark & np.all((L >= lo_l) & (L <= hi_l), axis=1)
        pts_l = []
        for p in P:
            if p["sub"] == s:
                import conn
                pts_l.append(conn.solid_points(p["num"]) @ p["M"].T + p["o"])
        if sel.sum() < 50 or not pts_l: ears[s] = dict(statut="non evaluable (nuage GLB trop petit)"); continue
        A = L[sel] * 0.4 * np.array([1, -1, -1]); B = np.vstack(pts_l) * 0.4 * np.array([1, -1, -1])           # mm, render frame
        ca, cb = A.mean(0), B.mean(0); ua, sa, vta = np.linalg.svd(A - ca, full_matrices=False); ub, sb, vtb = np.linalg.svd(B - cb, full_matrices=False)
        ang = float(np.degrees(np.arccos(min(1.0, abs(vta[2] @ vtb[2])))))                      # angle between the panel normals (smallest axis)
        ears[s] = dict(ecart_centre_mm=round(float(np.linalg.norm(ca - cb)), 1), ecart_normale_deg=round(ang, 1), etendue_glb_mm=[round(float(x), 1) for x in np.ptp(A, 0)], etendue_lego_mm=[round(float(x), 1) for x in np.ptp(B, 0)],
                       distance_plan_sagittal_glb_mm=round(float(ca @ n - off), 1), distance_plan_sagittal_lego_mm=round(float(cb @ n - off), 1), hauteur_glb_mm=round(float(ca[1]), 1), hauteur_lego_mm=round(float(cb[1]), 1))
    if len(ears) >= 2 and all("ecart_centre_mm" in e for e in ears.values()):
        e = list(ears.values()); out["placement"]["asymetrie_oreilles"] = dict(
            glb=dict(somme_distances_au_plan_mm=round(e[0]["distance_plan_sagittal_glb_mm"] + e[1]["distance_plan_sagittal_glb_mm"], 1), ecart_hauteur_mm=round(abs(e[0]["hauteur_glb_mm"] - e[1]["hauteur_glb_mm"]), 1)),
            lego=dict(somme_distances_au_plan_mm=round(e[0]["distance_plan_sagittal_lego_mm"] + e[1]["distance_plan_sagittal_lego_mm"], 1), ecart_hauteur_mm=round(abs(e[0]["hauteur_lego_mm"] - e[1]["hauteur_lego_mm"]), 1)),
            lecture="si la somme des distances (ou l'ecart de hauteur) differe peu entre GLB et LEGO, l'asymetrie vient de la source ; sinon elle est introduite par le generateur")
    out["placement"]["oreilles"] = ears if ears else "aucun module d'oreille : les oreilles sont dans le volume (voir iou_par_zone)"
    # ------------------------------------------------------------------ GLB patches (eyes, nose, mouth) against the model
    pat = []
    for dd in det["details"]:
        if dd["classe"] not in ("oeil", "pupille", "truffe", "bouche", "oeil_douteux", "pupille_douteuse"): continue
        c = np.array(dd["centre_mm"], float) / 0.4 * np.array([1, -1, -1]); want = CODE_RGB.get(dd["couleur"])
        dp = [(np.linalg.norm((p["o"] - c)) * 0.4, p["num"]) for p in P if p["num"] in DETAIL_NUMS]
        near_part = min(dp) if dp else (None, None)
        cell_d = None
        if want is not None:
            sel = (codes_cell == want)
            if sel.any(): cell_d = float(np.min(np.linalg.norm(ctr[sel] - c, axis=1)) * 0.4)
        pat.append(dict(id=dd["id"], classe=dd["classe"], couleur=dd["couleur"], diametre_mm=dd.get("diametre_eq_mm"), piece_de_detail_la_plus_proche_mm=None if near_part[0] is None else round(float(near_part[0]), 1), type_piece=near_part[1],
                        cellule_exposee_de_meme_couleur_mm=None if cell_d is None else round(cell_d, 1),
                        construit=bool(near_part[0] is not None and near_part[0] <= 12.0 and dd["classe"] in ("oeil", "pupille", "truffe"))))
    out["placement"]["taches_glb"] = pat
    out["placement"]["details_attendus_non_construits"] = [p["id"] for p in pat if p["classe"] in ("oeil", "pupille", "truffe") and not p["construit"]]
    # ------------------------------------------------------------------ visible structural parts
    vis = Counter(); where = []
    for k in range(len(cells)):
        if ptype[k] in SNOT_STRUCT and not sub[k]: vis[ptype[k]] += 1; where.append((ptype[k], [int(x) for x in cells[k]]))
    out["pieces_structurelles_visibles"] = dict(cellules=int(sum(vis.values())), par_type=dict(vis), exemples=where[:10])
    out["_arrays"] = dict(cells=cells, excess=excess, par=par, has=has, codes_cell=codes_cell, expected=expected, zone=zone, mod=mod, glb_rgb=glb_rgb)
    return out

def heatmaps(res, outdir, tag):
    from PIL import Image, ImageDraw
    a = res["_arrays"]; cells = a["cells"]; ex = a["excess"]; par = a["par"]; has = a["has"]
    S = 4; views = {"face_XY": (0, 1), "profil_ZY": (2, 1), "dessus_XZ": (0, 2)}
    for nm, (u, v) in views.items():
        W = (cells[:, u].max() + 2) * S; H = (cells[:, v].max() + 2) * S; img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
        order = np.argsort(cells[:, 3 - u - v])                     # far to near
        for k in order:
            if not has[k]: continue
            e = float(np.clip(ex[k] / 60.0, 0, 1)); col = (int(255 * e), int(200 * (1 - e)), 40)
            x, y = cells[k, u] * S, (cells[k, v] if v != 1 else cells[:, 1].max() - cells[k, 1]) * S
            d.rectangle([x, y, x + S - 1, y + S - 1], fill=col)
            if par[k]: d.rectangle([x, y, x + S - 1, y + S - 1], outline=(0, 0, 0))
        img.save(os.path.join(outdir, "carte_defauts_couleur_%s_%s.png" % (tag, nm)))

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("glb", "ldr", "grid", "seg", "details", "out"): ap.add_argument("--" + k, required=True)
    ap.add_argument("--exclude", required=True); ap.add_argument("--run"); ap.add_argument("--tag", default="modele")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    res = audit(a.glb, a.ldr, a.grid, a.seg, a.details, [int(x) for x in a.exclude.split(",") if x], a.run, a.out)
    heatmaps(res, a.out, a.tag); res.pop("_arrays")
    json.dump(res, open(os.path.join(a.out, "audit_%s.json" % a.tag), "w"), indent=1, ensure_ascii=False)
    c = res["couleurs"]; print("%s : dE moyen %.1f (plancher moteur %.1f, catalogue %.1f), parasites %d (%.1f %%), sans correspondance %d ; IoU global %.3f" % (a.tag, c["dE_moyen"], c["plancher_palette_moteur_moyen"], c["plancher_catalogue_moyen"], c["cellules_parasites"], 100 * c["part_parasites"], c["cellules_sans_correspondance"], res["placement"]["iou_global"]))

if __name__ == "__main__":
    main()
