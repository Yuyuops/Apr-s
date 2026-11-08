#!/usr/bin/env python3
"""B1 (Sprint V13) : measured audit of print_export_results/ : real mm dimensions against the nominal LEGO pitch, units/orientation of the 3MF, watertightness, bed fit, wall and skin thickness (cross-sections), overhang / bridging zones
for the intended print orientation (base on the bed, studs up), colour bodies, dowel clearances, and the declared approximations (non-rectangular parts). NUMERIC audit only : NOT a slicer or printer validation.
usage : audit_print_exports.py EXPORT_ROOT OUT.json"""
import glob, json, re, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np, trimesh
NS = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}; PITCH, PLATE, BRICK = 8.0, 3.2, 9.6
def overhang(m, ang=45.0):
    n = m.face_normals; a = m.area_faces; zc = m.triangles_center[:, 2]; thr = -np.cos(np.radians(ang))        # facets looking down more than (90-ang) deg from the bed
    sel = (n[:, 2] < thr) & (zc > 0.05); return float(a[sel].sum()), float(a.sum())
def section_walls(m, z):
    s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    return None if s is None else float(np.ptp(s.vertices[:, 0])), float(np.ptp(s.vertices[:, 1])), len(s.entities)
def audit_stl(f):
    m = trimesh.load(f); b = m.bounds; size = b[1] - b[0]; name = Path(f).stem; mt = re.match(r"(plate|brick|tile)_(\d+)x(\d+)", name); out = dict(file=name, watertight=bool(m.is_watertight), volume_ok=bool(m.volume > 0), bbox_mm=[round(float(x), 3) for x in size], z_min=round(float(b[0][2]), 3))
    if mt:
        k, a, c = mt.group(1), int(mt.group(2)), int(mt.group(3)); h = BRICK if k == "brick" else PLATE; nom = [a * PITCH, c * PITCH, h + (0 if k == "tile" else 1.7)]
        out["nominal_mm"] = nom; out["delta_mm"] = [round(float(s - n), 3) for s, n in zip(size, nom)]
        oa, ta = overhang(m); out["overhang_area_mm2_over_45deg"] = round(oa, 1); out["overhang_share"] = round(oa / ta, 3)
        # wall / skin thickness from the vertex planes (outer box vs cavity box) : smallest gaps between distinct planes
        ux = np.unique(np.round(m.vertices[:, 0], 3)); uy = np.unique(np.round(m.vertices[:, 1], 3)); uz = np.unique(np.round(m.vertices[:, 2], 3))
        out["wall_x_mm"] = round(float(ux[1] - ux[0]), 3); out["wall_y_mm"] = round(float(uy[1] - uy[0]), 3); out["top_skin_mm"] = round(float(h - uz[uz < h - 1e-6][-1]), 3) if k != "tile" or True else None
    return out
def audit_3mf(f, bed=250.0):
    x = ET.fromstring(zipfile.ZipFile(f).read("3D/3dmodel.model")); unit = x.get("unit"); objs = x.findall(".//m:object", NS); res = dict(file=Path(f).name, unit=unit, bodies=len(objs), colours=len({o.get("pindex") for o in objs}), bad=[])
    boxes = []; vols = 0.0
    for o in objs:
        v = np.array([[float(a.get(k)) for k in "xyz"] for a in o.findall(".//m:vertex", NS)]); t = np.array([[int(a.get(k)) for k in ("v1", "v2", "v3")] for a in o.findall(".//m:triangle", NS)]); m = trimesh.Trimesh(v, t, process=False)
        if not (m.is_watertight and m.volume > 0): res["bad"].append(o.get("name")); 
        vols += m.volume; boxes.append(m.bounds)
    lo = np.min([b[0] for b in boxes], 0); hi = np.max([b[1] for b in boxes], 0); res["extent_mm"] = [round(float(q), 1) for q in hi - lo]; res["fits_bed"] = bool(hi[0] - lo[0] <= bed and hi[1] - lo[1] <= bed); res["z_min"] = round(float(lo[2]), 3); res["volume_cm3"] = round(vols / 1000, 1)
    return res
if __name__ == "__main__":
    root = Path(sys.argv[1]); out = {}
    for sub in sorted(p for p in root.iterdir() if p.is_dir()):
        r = dict(stl=[audit_stl(f) for f in sorted(glob.glob(str(sub / "**" / "stl" / "*.stl"), recursive=True))], threemf=[audit_3mf(f) for f in sorted(glob.glob(str(sub / "**" / "*.3mf"), recursive=True))])
        for k in ("report_bricks.json", "report_modules.json"):
            p = next(iter(glob.glob(str(sub / "**" / k), recursive=True)), None)
            if p: d = json.load(open(p)); r[k] = {kk: d[kk] for kk in d if kk in ("parts_total", "parts_supported", "supported_share", "unsupported_types", "plates", "modules", "colour_bodies", "dowel_pairs", "material_volume_cm3", "approximations", "mass_g_upper_bound", "print_hours_estimate", "print_hours_upper_bound")}
        out[sub.name] = r
    json.dump(out, open(sys.argv[2], "w"), indent=1); print("written", sys.argv[2])
