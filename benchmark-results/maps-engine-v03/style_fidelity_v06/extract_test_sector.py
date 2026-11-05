#!/usr/bin/env python3
"""Extracts a representative physical-test sector from a full model : S11 (Tuscany, 32x32 studs) + an 8-stud junction strip into S12 and S21, as a stand-alone LDraw model (all pieces intersecting the window, re-based to 0,0) with BOM,
joint data and the same validation. usage: extract_test_sector.py MODELDIR OUTDIR [sector_row sector_col]"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import Scene
D, OUT = sys.argv[1], sys.argv[2]; sr, sc = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1, 1); F = 2; SZ = 32; H = 8
P = json.load(open(D + "/parts.json")); r0, r1, c0, c1 = F + sr * SZ, F + (sr + 1) * SZ + H, F + sc * SZ, F + (sc + 1) * SZ + H
sel = [p for p in P if p["r"] < r1 and p["r"] + p["nr"] > r0 and p["c"] < c1 and p["c"] + p["nc"] > c0]
byy = {}
for q in P: byy.setdefault(q['y'] + q['h'], []).append(q)
ids = {p['id'] for p in sel}; todo = list(sel)
while todo:        # closure : add every piece that carries a selected piece (so nothing floats), repeat
    p = todo.pop()
    if p['y'] == 0: continue
    for q in byy.get(p['y'], []):
        if q['id'] not in ids and q['r'] < p['r'] + p['nr'] and q['r'] + q['nr'] > p['r'] and q['c'] < p['c'] + p['nc'] and q['c'] + q['nc'] > p['c']: ids.add(q['id']); sel.append(q); todo.append(q)
r0, r1 = min(p['r'] for p in sel), max(p['r'] + p['nr'] for p in sel); c0, c1 = min(p['c'] for p in sel), max(p['c'] + p['nc'] for p in sel)      # bounding box of every piece touching the window : overhanging pieces are kept, so every piece keeps its support
R, C = r1 - r0, c1 - c0; S = Scene(R, C); n_cut = 0
for p in sorted(sel, key=lambda p: (p["y"], p["id"])):
    rr, cc = p["r"] - r0, p["c"] - c0
    if rr < 0 or cc < 0 or rr + p["nr"] > R or cc + p["nc"] > C: n_cut += 1; continue          # pieces overhanging the window are dropped 
    S.add(p["part"], p["colour"], rr, cc, p["y"], p["rot"], p["region"], p["nr"], p["nc"], p["h"])
m = S.write(OUT, "Test sector S%d%d + junction strips" % (sr, sc), dict(source=os.path.basename(D.rstrip("/")), window_rows=[r0, r1], window_cols=[c0, c1], dropped_overhanging_pieces=n_cut, junction_strip_studs=H)); print(m["pieces"], "pieces; dropped", n_cut, "; size studs", m["size_studs"])
