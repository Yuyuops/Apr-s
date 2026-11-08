#!/usr/bin/env python3
"""NUMERIC validation of the experimental print exports (NOT a Bambu Studio / printer validation) : every STL and every 3MF body must be a watertight, positively-oriented solid ; 3MF files must be well-formed
(zip, XML, indices in range) ; every build item must fit the bed ; bricks of a plate must not overlap. usage : validate_print_exports.py EXPORT_DIR [bed_mm]"""
import glob, json, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np, trimesh
root = Path(sys.argv[1]); bed = float(sys.argv[2]) if len(sys.argv) > 2 else 250.0; NS = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}; rep = dict(stl=0, stl_bad=[], threemf=0, bodies=0, bodies_bad=[], oversize=[], overlaps=0, xml_errors=[])
for f in glob.glob(str(root / "**" / "*.stl"), recursive=True):
    m = trimesh.load(f); rep["stl"] += 1
    if not (m.is_watertight and m.volume > 0): rep["stl_bad"].append(f)
for f in sorted(glob.glob(str(root / "**" / "*.3mf"), recursive=True)):
    rep["threemf"] += 1
    try: xml = ET.fromstring(zipfile.ZipFile(f).read("3D/3dmodel.model"))
    except Exception as e: rep["xml_errors"].append("%s: %s" % (f, e)); continue
    objs = {}; boxes = []
    for o in xml.findall(".//m:object", NS):
        v = np.array([[float(x.get(k)) for k in "xyz"] for x in o.findall(".//m:vertex", NS)]); t = np.array([[int(x.get(k)) for k in ("v1", "v2", "v3")] for x in o.findall(".//m:triangle", NS)])
        rep["bodies"] += 1
        if len(t) == 0 or t.max() >= len(v) or t.min() < 0: rep["bodies_bad"].append("%s object %s : indices" % (f, o.get("id"))); continue
        m = trimesh.Trimesh(v, t, process=False)
        if not (m.is_watertight and m.volume > 0): rep["bodies_bad"].append("%s object %s : not watertight or volume<=0" % (f, o.get("id")))
        objs[o.get("id")] = v
    for it in xml.findall(".//m:build/m:item", NS):
        tr = [float(x) for x in it.get("transform").split()]; v = objs[it.get("objectid")] + np.array(tr[9:12]); lo, hi = v.min(0), v.max(0); boxes.append((lo, hi))
        if hi[0] > bed + 1e-6 or hi[1] > bed + 1e-6 or lo.min() < -1e-6: rep["oversize"].append(f)
    if "plate_" in f:
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i], boxes[j]
                if np.all(np.minimum(a[1][:2], b[1][:2]) - np.maximum(a[0][:2], b[0][:2]) > 1e-6): rep["overlaps"] += 1
ok = not (rep["stl_bad"] or rep["bodies_bad"] or rep["oversize"] or rep["overlaps"] or rep["xml_errors"]); rep["all_ok"] = ok; print(json.dumps({k: (v if not isinstance(v, list) else (v[:3], len(v))) for k, v in rep.items()})); sys.exit(0 if ok else 1)
