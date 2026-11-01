"""LEGO V9 - spatial scope control of the modifications (guard against the V8.1 error).

Every module declares the spatial zone it may modify (boxes of 20 x 8 x 20 LDU cells). Two assembled LDraw models (before / after) are voxelised from the real part
shapes and compared cell by cell:
  * occupancy        : a cell occupied in one model and not in the other                        (geometry)
  * exposed colour   : colour of a cell that touches the outside, seen from the outside          (surface appearance)
  * hidden colour    : colour change of an interior cell that touches no outside cell           (interior: reported, no visual effect)
  * finish           : stud / tile finish of an exposed top face                               (material appearance)
  * tessellation     : same occupancy and same colour but another part split                  (reconstruction noise: counted, never a violation)
Every difference is attributed to the declared zones that contain it (provenance). A surface difference (occupancy, exposed colour, finish) outside every declared
zone is a VIOLATION, unless the cell lies in an explicitly authorised interface (a zone declared with kind="interface").
Non-right-angle parts (ear sub-assemblies, rotated plates) are compared as exact part lines (type, colour, position, matrix): any difference is reported.
"""
import json, os, sys
import numpy as np
from collections import Counter
from scipy import ndimage
sys.path.insert(0, os.path.expanduser("~/bench/tools"))
import conn, partlib as PL

SHAPE = (40, 130, 40)
TILE_NUMS = {"3070b", "3069b", "63864", "2431", "24246", "98138", "6141b", "3068b", "2431", "87079"}

def read_parts(ldr):
    P, sub = [], None
    for l in open(ldr, encoding="utf-8", errors="replace"):
        t = l.split()
        if len(t) > 4 and t[0] == "0" and t[1] == "BRICKIFY" and t[2] == "SUBASSEMBLY": sub = t[4] if t[3] == "BEGIN" else None; continue
        if t and t[0] == "1" and len(t) >= 15:
            P.append(dict(c=int(t[1]), o=np.array(t[2:5], float), M=np.array(t[5:14], float).reshape(3, 3), num=t[14].lower().replace(".dat", ""), sub=sub))
    return P

def is_tile(num):
    try: return "tile" in PL.title(num).lower()
    except Exception: return num in TILE_NUMS

def voxelise(P):
    occ = np.zeros(SHAPE, bool); col = -np.ones(SHAPE, np.int16); pid = -np.ones(SHAPE, np.int32); tile = np.zeros(SHAPE, bool); exact = []
    for i, p in enumerate(P):
        st, rc, lo, hi = conn.world(p["num"], p["M"], p["o"])
        aligned = bool(np.all(np.isclose(np.abs(p["M"]), 0, atol=1e-4) | np.isclose(np.abs(p["M"]), 1, atol=1e-4))) and conn.part(p["num"])["fill"] >= 0.97 and "bracket" not in PL.title(p["num"]).lower()
        on_lattice = aligned and abs(lo[0] / 20 - round(lo[0] / 20)) < 0.05 and abs(lo[2] / 20 - round(lo[2] / 20)) < 0.05 and abs(lo[1] / 8 - round(lo[1] / 8)) < 0.05
        if on_lattice and p["sub"] is None:
            a = np.round([lo[0] / 20, -hi[1] / 8, lo[2] / 20]).astype(int); b = np.round([hi[0] / 20, -lo[1] / 8, hi[2] / 20]).astype(int)
            sl = tuple(slice(max(a[k], 0), min(b[k], SHAPE[k])) for k in range(3))
            occ[sl] = True; col[sl] = p["c"]; pid[sl] = i; tile[sl] = is_tile(p["num"])
        else:
            exact.append(i)
            pts = conn.solid_points(p["num"]) @ p["M"].T + p["o"]
            q = np.floor(np.c_[pts[:, 0] / 20, -pts[:, 1] / 8, pts[:, 2] / 20]).astype(int)
            ok = (q >= 0).all(1) & (q < SHAPE).all(1); q = q[ok]
            occ[tuple(q.T)] = True; col[tuple(q.T)] = p["c"]; pid[tuple(q.T)] = i
    lab, n = ndimage.label(~occ); border = np.unique(np.concatenate([lab[0].ravel(), lab[-1].ravel(), lab[:, 0].ravel(), lab[:, -1].ravel(), lab[:, :, 0].ravel(), lab[:, :, -1].ravel()]))
    outside = np.isin(lab, border[border > 0]) & ~occ
    near = ndimage.binary_dilation(outside, structure=ndimage.generate_binary_structure(3, 1)) & occ
    top_open = np.zeros(SHAPE, bool); top_open[:, :-1, :] = occ[:, :-1, :] & outside[:, 1:, :]
    return dict(occ=occ, col=col, pid=pid, tile=tile, exposed=near, top_open=top_open, parts=P, exact=exact)

def part_key(p): return (p["num"], p["c"], tuple(np.round(p["o"], 2)), tuple(np.round(p["M"].ravel(), 4)))

def zone_names(cell, zones):
    return [z["name"] for z in zones if all(z["lo"][k] <= cell[k] <= z["hi"][k] for k in range(3))]

def compare(A, B, zones, max_listed=40):
    """A = before, B = after (voxelised models). zones = [dict(name, lo=[ix,iy,iz], hi=[...], kind='module'|'interface')]"""
    occd = A["occ"] != B["occ"]
    both = A["occ"] & B["occ"]
    expo = A["exposed"] | B["exposed"]
    cold = both & (A["col"] != B["col"])
    fin = both & (A["top_open"] | B["top_open"]) & (A["tile"] != B["tile"])
    same_geom = both & (A["col"] == B["col"])
    kinds = dict(occupation=occd, couleur_exposee=cold & expo, couleur_interieure=cold & ~expo, finition_dessus=fin)
    report = dict(categories={}, violations=[], par_zone=Counter(), ignores_tessellation=0)
    for k, m in kinds.items():
        cells = np.argwhere(m); report["categories"][k] = int(len(cells))
        for c in cells:
            names = zone_names(c, zones)
            surface = k != "couleur_interieure"
            rec = dict(type=k, cell=[int(v) for v in c], avant=int(A["col"][tuple(c)]), apres=int(B["col"][tuple(c)]), zones=names)
            if names:
                for n_ in names: report["par_zone"][n_] += 1
            elif surface:
                report["violations"].append(rec)
            else:
                report.setdefault("interieur_hors_zone", []).append(rec)
    # tessellation: same occupancy + colour, different part identity
    ka = {i: part_key(p) for i, p in enumerate(A["parts"])}; kb = {i: part_key(p) for i, p in enumerate(B["parts"])}
    ia, ib = A["pid"][same_geom], B["pid"][same_geom]
    diff_id = np.array([ka.get(int(x)) != kb.get(int(y)) for x, y in zip(ia, ib)]) if len(ia) else np.zeros(0, bool)
    report["ignores_tessellation"] = int(diff_id.sum()); report["cellules_identiques"] = int((~diff_id).sum())
    # non-right-angle parts: exact lines
    ea = Counter(part_key(A["parts"][i]) for i in A["exact"]); eb = Counter(part_key(B["parts"][i]) for i in B["exact"])
    report["pieces_hors_reseau_modifiees"] = dict(retirees=sum((ea - eb).values()), ajoutees=sum((eb - ea).values()))
    report["violations_total"] = len(report["violations"]); report["violations"] = report["violations"][:max_listed]
    report["par_zone"] = dict(report["par_zone"])
    if "interieur_hors_zone" in report: report["interieur_hors_zone_total"] = len(report["interieur_hors_zone"]); report["interieur_hors_zone"] = report["interieur_hors_zone"][:10]
    return report

def check_module_output(recolour, carve, parts_cells, zone):
    """module-level check on the declared output of a module (recolour dict, carve cells, cells of the parts it adds) against its own declared zone"""
    out = []
    for kind, cells in (("recolorie", list(recolour)), ("creuse", list(carve)), ("piece_ajoutee", list(parts_cells))):
        for c in cells:
            if not all(zone["lo"][k] <= c[k] <= zone["hi"][k] for k in range(3)): out.append(dict(type=kind, cell=[int(v) for v in c]))
    return out

def box_zone(name, cells, margin=2, kind="module"):
    a = np.array(list(cells)); return dict(name=name, kind=kind, lo=(a.min(0) - margin).tolist(), hi=(a.max(0) + margin).tolist())

if __name__ == "__main__":
    A, B = voxelise(read_parts(sys.argv[1])), voxelise(read_parts(sys.argv[2])); zones = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else []
    r = compare(A, B, zones); print(json.dumps({k: v for k, v in r.items() if k != "violations"}, indent=1, default=str)); print("violations", r["violations_total"])
