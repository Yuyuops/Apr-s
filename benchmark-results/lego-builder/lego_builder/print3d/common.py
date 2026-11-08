"""Shared pieces of the experimental 3D-print export : LDraw model reading, part classification (own parametric geometry only), colour and mesh writers (STL, 3MF).
EXPERIMENTAL : nothing here is validated in Bambu Studio or on a printer. Dimensions are PARAMETERS to be measured, not claims of LEGO compatibility."""
import json, math, struct, zipfile, sqlite3
from pathlib import Path
import numpy as np
LDU = 0.4        # mm per LDraw unit
PITCH, PLATE_H, BRICK_H = 8.0, 3.2, 9.6
PARAMS = dict(pitch=PITCH, plate_h=PLATE_H, brick_h=BRICK_H, stud_d=4.8, stud_h=1.7, wall=1.2, top=1.0, tube_od=6.5, tube_id=4.9, tol=0.10, peg_d=5.0, peg_len=6.0, socket_clear=0.30,
              density_g_cm3=1.24, filament_note="PLA assumed", effective_fill=1.0)
def read_ldr(path):
    """-> list of dict(part, colour, pos (LDU, LDraw axes), rot (3x3))"""
    out = []
    for l in open(path, errors="replace"):
        t = l.split()
        if t and t[0] == "1" and len(t) >= 15: out.append(dict(part=t[14].lower().removesuffix(".dat"), colour=int(t[1]), pos=np.array([float(x) for x in t[2:5]]), rot=np.array([float(x) for x in t[5:14]]).reshape(3, 3)))
    return out
def classify(part, catalog):
    """Rectangular plate/brick/tile of the catalogue -> dict(kind, nx, nz, h, studs) ; anything else -> None (not supported : reported, never silently approximated)."""
    c = catalog.get(part)
    if not c: return None
    lo, hi = np.array(c["lo"]), np.array(c["hi"]); title = c["title"].lower()
    import re
    m = re.match(r"(plate|brick|tile)\s+(\d+)\s*x\s*(\d+)\b(.*)", title)
    if not m or "round" in m.group(4) or "corner" in m.group(4) or "slope" in m.group(4) or "wedge" in m.group(4) or "curved" in m.group(4) or "with" in m.group(4) and "groove" not in m.group(4): return None
    kind, a, b = m.group(1), int(m.group(2)), int(m.group(3)); size = hi - lo
    if abs(size[0] - 20 * a) > 0.5 and abs(size[0] - 20 * b) > 0.5: return None
    return dict(kind=kind, nx=int(round(size[0] / 20)), nz=int(round(size[2] / 20)), h_ldu=float(size[1]), studs=(kind != "tile"), lo=lo.tolist(), hi=hi.tolist())
def colour_rgb(col, db):
    r = db.execute("select name,rgb from colors where id=?", (col,)).fetchone(); return (r[0], r[1]) if r else (str(col), "888888")
def write_stl(mesh_v, mesh_f, path):
    v = np.asarray(mesh_v, np.float32); f = np.asarray(mesh_f, int); tri = v[f]; n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); ln = np.linalg.norm(n, axis=1, keepdims=True); n = np.where(ln > 0, n / np.maximum(ln, 1e-12), 0).astype(np.float32)
    with open(path, "wb") as fh:
        fh.write(b"lego_builder experimental export".ljust(80, b" ")); fh.write(struct.pack("<I", len(f)))
        rec = np.zeros(len(f), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]); rec["n"] = n; rec["v"] = tri; fh.write(rec.tobytes())
def write_3mf(objects, path, title="lego_builder export"):
    """objects : list of dict(name, v, f, colour_hex, offset (x,y,z) mm). Core 3MF (one <object> per body, one build <item> each, per-object base colour). NOT validated in Bambu Studio."""
    res = ['<?xml version="1.0" encoding="UTF-8"?>', '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">', '<metadata name="Title">%s</metadata>' % title, "<resources>"]
    cols = sorted({o["colour_hex"] for o in objects}); res.append('<basematerials id="1">' + "".join('<base name="%s" displaycolor="#%sFF"/>' % (c, c) for c in cols) + "</basematerials>")
    for i, o in enumerate(objects):
        res.append('<object id="%d" type="model" pid="1" pindex="%d" name="%s"><mesh><vertices>' % (i + 2, cols.index(o["colour_hex"]), o["name"]))
        res.append("".join('<vertex x="%.4f" y="%.4f" z="%.4f"/>' % tuple(p) for p in np.asarray(o["v"])) + "</vertices><triangles>")
        res.append("".join('<triangle v1="%d" v2="%d" v3="%d"/>' % tuple(t) for t in np.asarray(o["f"])) + "</triangles></mesh></object>")
    res.append("</resources><build>")
    for i, o in enumerate(objects): res.append('<item objectid="%d" transform="1 0 0 0 1 0 0 0 1 %.3f %.3f %.3f"/>' % (i + 2, *o.get("offset", (0, 0, 0))))
    res.append("</build></model>")
    ct = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z: z.writestr("[Content_Types].xml", ct); z.writestr("_rels/.rels", rels); z.writestr("3D/3dmodel.model", "\n".join(res))
