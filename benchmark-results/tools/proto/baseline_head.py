"""Current brickify packing (functions imported unmodified, same loop as brickify.main) on the head grid.
usage: baseline_head.py <head.npz> <outdir> <name>"""
import os, sys, numpy as np, json
sys.path.insert(0, os.path.expanduser("~/bench/brickify/pipeline"))
import brickify as B
d = np.load(sys.argv[1]); out, name = sys.argv[2], sys.argv[3]; os.makedirs(out, exist_ok=True)
B.load_ldconfig(os.path.expanduser("~/bench/ldraw-parts-library/complete/ldraw/LDConfig.ldr"))
grid = d["grid"].astype(np.int32).copy(); surface = d["surface"]
fmask3d = None; B.pack_sheet.fixed = []; best = None
for it in range(14):
    parts, pid3d = B.pack(grid, fmask3d, surface)
    floating, n_conn, adj = B.connectivity(parts, pid3d)
    print(f"pack {it}: {len(parts)} parts, {n_conn} stud connections, {len(floating)} floating")
    if best is None or len(floating) < len(best[2]): best = (parts, pid3d, floating, n_conn)
    if not floating: break
    fmask3d = np.zeros(grid.shape, dtype=bool)
    for p in floating: fmask3d[p.x0:p.x0+p.w, p.y0:p.y0+p.h, p.z0:p.z0+p.d] = True
    if it >= 3: B.repair_floating(grid, floating)
parts, pid3d, floating, n_conn = best
B.assign_steps(parts, per_step=8)
B.write_ldraw(parts, os.path.join(out, f"{name}.ldr"), name, "brickify (unmodified) head baseline")
B.write_lists(parts, out, name)
json.dump(dict(parts=len(parts), floating=len(floating), stud_connections=n_conn), open(os.path.join(out, f"{name}_report.json"), "w"))
print("final", len(parts), "parts", len(floating), "floating")
