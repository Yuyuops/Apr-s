"""Generic selection of the LEGO colours of a subject from its GLB (V12).

The palette is DATA of the subject, derived from its own colours and from the real catalogue ; nothing is tied to a demonstration character.
  candidates : opaque solid LDraw colours (LDConfig) for which every CORE part (the plates and tiles the volume is built from) is listed in at least MIN_SETS Rebrickable sets
  measure    : mean Delta E (CIE76, Lab) between the colours of the GLB surface (area weighted samples) and the nearest colour of the selected set
  selection  : greedy forward selection ; a colour is added only if
               - it lowers the mean Delta E by at least MIN_GAIN,
               - it becomes the nearest colour of at least MIN_AREA of the surface (no colour for a handful of cells),
               - it is not rare : the smallest number of sets over the core parts is at least RARE_SETS (supply realism ; no commercial availability or price is invented),
               up to MAX_COLOURS ; colours imposed by the subject configuration (required) are kept.
  limits     : GLB tones whose best catalogue colour is still >= NO_MATCH_DE away are reported, never "fixed".
The parameters below are the same for every subject (they are written in the report) ; the subject configuration may only add required / forbidden codes.
usage: palette_select.py <source.glb> <out.json> [--required 0,15] [--forbidden 1,2] [--max-colours 8]"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import RB_DB
import argparse, json, sqlite3, sys
import numpy as np
import trimesh
import palette_util as PU

CORE_PARTS = ["3024", "3023", "3022", "3020", "3710", "3623", "3666", "3070b", "3069b"]
MIN_SETS = 20; RARE_SETS = 60; MIN_GAIN = 0.8; MIN_AREA = 0.03; MAX_COLOURS = 8; NO_MATCH_DE = 30.0; N_SAMPLES = 40000

def candidates(forbidden):
    codes = PU.codes(); db = sqlite3.connect(RB_DB); out = {}
    for c, (name, rgb) in codes.items():
        if c in forbidden or c >= 512: continue
        low = name.lower()
        if low.startswith(("trans", "chrome", "glitter", "pearl", "metal", "opal", "speckle", "milky", "glow", "flat_silver", "flat_gold", "rubber", "very_light_bluish", "light_bluish_gray")): continue
        sets = []
        for p in CORE_PARTS:
            r = db.execute("select num_sets from pcs_mat where part_num=? and color_id=?", (p, c)).fetchone(); sets.append(int(r[0]) if r else 0)
        if min(sets) >= MIN_SETS: out[c] = dict(nom=name, rgb=rgb, sets_min=min(sets))
    return out

def surface_samples(glb, n=N_SAMPLES):
    m = trimesh.load(glb, force="mesh", process=False); col = np.asarray(m.visual.vertex_colors)[:, :3].astype(float)
    fc = col[m.faces].mean(1); a = m.area_faces; rng = np.random.RandomState(0); idx = rng.choice(len(fc), n, p=a / a.sum())
    return fc[idx]

def select(glb, required=(), forbidden=(), max_colours=MAX_COLOURS):
    cand = candidates(set(forbidden)); codes = sorted(cand); X = PU.lab(surface_samples(glb)); CL = PU.lab([cand[c]["rgb"] for c in codes])
    D = np.linalg.norm(X[:, None, :] - CL[None, :, :], axis=2)                            # samples x candidates
    chosen = [codes.index(c) for c in required if c in cand]; steps = []
    cur = D[:, chosen].min(1) if chosen else np.full(len(X), 1e9)
    if not chosen:                                                                       # first colour : the one with the smallest mean delta E (not rare)
        ok = [j for j in range(len(codes)) if cand[codes[j]]["sets_min"] >= RARE_SETS]; j0 = min(ok, key=lambda j: D[:, j].mean()); chosen = [j0]; cur = D[:, j0].copy()
        steps.append(dict(code=codes[j0], nom=cand[codes[j0]]["nom"], gain_dE=None, part_de_surface=1.0, sets_min=cand[codes[j0]]["sets_min"], dE_moyen_apres=round(float(cur.mean()), 2)))
    while len(chosen) < max_colours:
        best = None
        for j in range(len(codes)):
            if j in chosen or cand[codes[j]]["sets_min"] < RARE_SETS: continue
            new = np.minimum(cur, D[:, j]); gain = float((cur - new).mean()); area = float((D[:, j] < cur).mean())
            if gain < MIN_GAIN or area < MIN_AREA: continue
            if best is None or gain > best[0]: best = (gain, j, area, new)
        if best is None: break
        gain, j, area, cur = best; chosen.append(j)
        steps.append(dict(code=codes[j], nom=cand[codes[j]]["nom"], gain_dE=round(gain, 2), part_de_surface=round(area, 3), sets_min=cand[codes[j]]["sets_min"], dE_moyen_apres=round(float(cur.mean()), 2)))
    # contrast colours : the detail modules (eyes, nose, mouth, ears) need a dark and a light colour ; if the selection has none, the best available one is added and reported
    Ls = lambda js: [CL[j][0] for j in js]; roles_added = []
    if not any(CL[j][0] < 20 and float(np.hypot(CL[j][1], CL[j][2])) < 15 for j in chosen):          # a dark NEUTRAL (black) : pupils, nose, mouth lines, ears
        j = min(range(len(codes)), key=lambda j: CL[j][0] + (0 if cand[codes[j]]["sets_min"] >= RARE_SETS else 100))
        if j not in chosen: chosen.append(j); roles_added.append(("sombre", codes[j]))
    chroma = lambda j: float(np.hypot(CL[j][1], CL[j][2]))
    if not any(CL[j][0] > 85 and chroma(j) < 15 for j in chosen):          # a light NEUTRAL (white) : eyes, teeth, highlights
        j = max(range(len(codes)), key=lambda j: CL[j][0] - chroma(j) - (0 if cand[codes[j]]["sets_min"] >= RARE_SETS else 100))
        if j not in chosen: chosen.append(j); roles_added.append(("clair", codes[j]))
    cur = D[:, chosen].min(1)
    sel = [codes[j] for j in chosen]; floor = D.min(1)
    nomatch = X[floor >= NO_MATCH_DE]
    rep = dict(couleurs_de_contraste_ajoutees=[dict(role=r, code=c) for r, c in roles_added], parametres=dict(core_parts=CORE_PARTS, min_sets=MIN_SETS, rare_sets=RARE_SETS, min_gain_dE=MIN_GAIN, min_area=MIN_AREA, max_colours=MAX_COLOURS, no_match_dE=NO_MATCH_DE),
               candidats=len(codes), choisies=[dict(code=c, nom=cand[c]["nom"], sets_min=cand[c]["sets_min"]) for c in sel], etapes=steps,
               dE_moyen_selection=round(float(cur.mean()), 2), dE_median_selection=round(float(np.median(cur)), 2), dE_moyen_catalogue_entier=round(float(floor.mean()), 2),
               part_surface_sans_correspondance=round(float((floor >= NO_MATCH_DE).mean()), 4))
    rejected = []
    for j in np.argsort(-np.maximum(0, (cur[:, None] - D).mean(0)))[:6]:
        if codes[j] in sel: continue
        g = float(np.maximum(0, cur - D[:, j]).mean()); why = "rare (%d sets)" % cand[codes[j]]["sets_min"] if cand[codes[j]]["sets_min"] < RARE_SETS else ("gain %.2f < %.1f" % (g, MIN_GAIN) if g < MIN_GAIN else "surface < %.0f %%" % (100 * MIN_AREA))
        rejected.append(dict(code=codes[j], nom=cand[codes[j]]["nom"], gain_dE=round(g, 2), raison=why))
    rep["meilleurs_candidats_refuses"] = rejected
    return sel, rep

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("glb"); ap.add_argument("out"); ap.add_argument("--required", default=""); ap.add_argument("--forbidden", default=""); ap.add_argument("--max-colours", type=int, default=MAX_COLOURS)
    a = ap.parse_args(); req = [int(x) for x in a.required.split(",") if x]; forb = [int(x) for x in a.forbidden.split(",") if x]
    sel, rep = select(a.glb, req, forb, a.max_colours)
    allc = [c for c in PU.codes()]; rep["exclude"] = [c for c in allc if c not in sel]; rep["selection"] = sel
    json.dump(rep, open(a.out, "w"), indent=1, ensure_ascii=False); print(json.dumps(dict(selection=[(c["code"], c["nom"]) for c in rep["choisies"]], dE_moyen=rep["dE_moyen_selection"], plancher_catalogue=rep["dE_moyen_catalogue_entier"], sans_correspondance=rep["part_surface_sans_correspondance"])))
