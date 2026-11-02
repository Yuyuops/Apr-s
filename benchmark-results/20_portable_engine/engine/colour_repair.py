"""Local colour repair of EXPOSED parts, decided on the colour of the GLB (V12). Colours only : no part is moved, added, removed or re-cut ; the stud graph is unchanged.

For every part that has exposed cells (cells touching the outside of the assembled model) :
  * the colour of the GLB surface around each exposed cell is measured (mean of the nearest vertices, Lab) ;
  * for every colour of the subject palette in which this exact part exists in the real catalogue (>= MIN_SETS Rebrickable sets), the sum of the Delta E over the exposed cells is computed ;
  * the part takes the colour with the smallest sum when it lowers the Delta E of its exposed cells by at least GAIN_REL (relative) and GAIN_ABS (per exposed cell) ;
Two scopes, reported separately :
  structure : parts outside the 20 x 8 x 20 lattice (turned fixation plates, ear modules) : evaluated whenever they have exposed cells (a structural part must not show its own colour) ;
  volume    : lattice parts (plates of the body) : evaluated only when at least one exposed cell is a parasite (excess >= PARASITE_DE), i.e. a quantisation error, never a rendering impression.
Detail parts (eyes, nose, mouth) and parts of the ear FACES are not touched here (their colour is decided by their own module from the GLB).
usage: colour_repair.py --ldr in.ldr --glb ref_full_frame.glb --grid full400.npz --out out.ldr --report report.json"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from _paths import RB_DB
import argparse, json, os, sqlite3, sys
from collections import Counter
import numpy as np
import trimesh
from scipy.spatial import cKDTree
import palette_util as PU, scope

MIN_SETS = 20; GAIN_REL = 0.30; GAIN_ABS = 8.0; PARASITE_DE = 40.0; RADIUS_LDU = 24.0
DETAIL_NUMS = {"43898", "98138", "87087", "6141", "3960", "54200", "4740", "14769", "18674", "85861"}

def repair(ldr, glb, grid_npz, out_ldr, report):
    os.environ.setdefault("LEGO_SHAPE", ",".join(map(str, np.load(grid_npz)["grid"].shape))); shape = np.load(grid_npz)["grid"].shape; scope.SHAPE = tuple(max(s, 8) for s in shape)
    codes = PU.codes(); pal = PU.subject_palette(grid_npz); pal_lab = PU.lab([codes[c][1] for c in pal]); db = sqlite3.connect(RB_DB)
    avail = {}
    def ok(num, c):
        k = (num, c)
        if k not in avail:
            r = db.execute("select num_sets from pcs_mat where part_num=? and color_id=?", (num.replace(".dat", ""), c)).fetchone(); avail[k] = bool(r and r[0] >= MIN_SETS)
        return avail[k]
    P = scope.read_parts(ldr); V = scope.voxelise(P); exact = set(V["exact"])
    m = trimesh.load(glb, force="mesh", process=False); Vx = np.asarray(m.vertices); col = np.asarray(m.visual.vertex_colors)[:, :3].astype(float)
    L = np.c_[Vx[:, 0] / 0.4, -Vx[:, 1] / 0.4, -Vx[:, 2] / 0.4]; tree = cKDTree(L)
    cells = np.argwhere(V["exposed"] & V["occ"]); pid = V["pid"][tuple(cells.T)]
    ctr = np.c_[(cells[:, 0] + 0.5) * 20, -(cells[:, 1] + 0.5) * 8, (cells[:, 2] + 0.5) * 20]
    d, idx = tree.query(ctr, k=10, distance_upper_bound=RADIUS_LDU); has = np.isfinite(d[:, 0]); w = np.isfinite(d).astype(float); idx = np.where(np.isfinite(d), idx, 0)
    glb_lab = PU.lab((col[idx] * w[..., None]).sum(1) / np.maximum(w.sum(1), 1)[:, None])
    cur_code = V["col"][tuple(cells.T)]; cur_lab = PU.lab([codes[int(c)][1] if int(c) in codes else (128, 128, 128) for c in cur_code])
    dE_cur = np.linalg.norm(cur_lab - glb_lab, axis=1); floor = np.linalg.norm(glb_lab[:, None, :] - pal_lab[None, :, :], axis=2).min(1)
    parasite = has & (dE_cur - floor >= PARASITE_DE)
    by_part = {}
    for k, p in enumerate(pid):
        if p >= 0 and has[k]: by_part.setdefault(int(p), []).append(k)
    changes = []; lines = open(ldr, encoding="utf-8", errors="replace").read().split("\n"); part_line = [i for i, l in enumerate(lines) if l.startswith("1 ")]
    for p, ks in by_part.items():
        part = P[p]
        if part["num"] in DETAIL_NUMS: continue
        scope_name = "structure" if p in exact else "volume"
        if scope_name == "volume" and not parasite[ks].any(): continue
        if scope_name == "structure" and part["sub"] and part["num"] in ("3070b", "3069b", "63864", "2431", "6636", "3068b", "26603", "87079", "3024", "3023", "3022", "3623", "3710", "3666") and False: continue
        G_ = glb_lab[ks]; cur = float(np.linalg.norm(cur_lab[ks] - G_, axis=1).sum())
        best = (cur, part["c"])
        for j, c in enumerate(pal):
            if c == part["c"] or not ok(part["num"], c): continue
            cost = float(np.linalg.norm(pal_lab[j] - G_, axis=1).sum())
            if cost < best[0]: best = (cost, c)
        if best[1] != part["c"] and (cur - best[0]) >= GAIN_REL * cur and (cur - best[0]) / len(ks) >= GAIN_ABS:
            t = lines[part_line[p]].split(); t[1] = str(best[1]); lines[part_line[p]] = " ".join(t)
            changes.append(dict(piece=p, ref=part["num"], portee=scope_name, sous_ensemble=part["sub"], de=codes[part["c"]][0], vers=codes[best[1]][0], cellules_exposees=len(ks),
                                dE_somme_avant=round(cur, 1), dE_somme_apres=round(best[0], 1), cellule_exemple=[int(x) for x in cells[ks[0]]]))
    open(out_ldr, "w").write("\n".join(lines))
    rep = dict(parametres=dict(min_sets=MIN_SETS, gain_relatif=GAIN_REL, gain_par_cellule=GAIN_ABS, seuil_parasite_dE=PARASITE_DE), pieces_recolorees=len(changes),
               par_portee=dict(Counter(c["portee"] for c in changes)), par_transition=dict(Counter("%s -> %s" % (c["de"], c["vers"]) for c in changes).most_common(12)),
               cellules_exposees_concernees=int(sum(c["cellules_exposees"] for c in changes)), exemples=changes[:40])
    json.dump(rep, open(report, "w"), indent=1, ensure_ascii=False); return rep

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for k in ("ldr", "glb", "grid", "out", "report"): ap.add_argument("--" + k, required=True)
    a = ap.parse_args(); r = repair(a.ldr, a.glb, a.grid, a.out, a.report)
    print("pieces recolorees : %d %s ; cellules exposees concernees %d" % (r["pieces_recolorees"], r["par_portee"], r["cellules_exposees_concernees"]))
