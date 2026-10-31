#!/usr/bin/env python3
"""LDraw .ldr + official LDraw library -> real part geometry.
Writes (1) a scene JSON for the three.js renderer (unique part meshes with faces + edge lines,
plus one instance per placed part with its colour, matrix, layer and step), (2) a GLB of the
assembled LEGO model (real part triangles, LDraw colours, units mm, Y up).
No geometry is invented: every triangle comes from the library .dat files referenced by the .ldr."""
import argparse, base64, json, os, re, sys
import numpy as np

class Lib:
    def __init__(self, root):
        self.root = root; self.index = {}; self.cache = {}
        for sub in ("parts", "parts/s", "p", "p/48", "p/8"):
            d = os.path.join(root, sub)
            if os.path.isdir(d):
                for f in os.listdir(d):
                    if f.lower().endswith(".dat"):
                        self.index[(sub + "/" + f).lower()] = os.path.join(d, f)
                        self.index.setdefault(f.lower(), os.path.join(d, f))
    def resolve(self, name):
        n = name.strip().replace("\\", "/").lower()
        for c in (n, "parts/" + n, "p/" + n):
            if c in self.index: return self.index[c]
        return self.index.get(n.split("/")[-1])
    def geom(self, name, depth=0):
        """(tris (n,3,3), edges (m,2,3)) in part coordinates (LDU)"""
        key = name.strip().replace("\\", "/").lower()
        if key in self.cache: return self.cache[key]
        path = self.resolve(name)
        T, E = [], []
        if path is None:
            if depth == 0: raise SystemExit(f"part not found in library: {name}")
        else:
            for line in open(path, encoding="utf-8", errors="replace"):
                t = line.split()
                if not t: continue
                if t[0] == "3" and len(t) >= 11: T.append(np.array(t[2:11], float).reshape(1, 3, 3))
                elif t[0] == "4" and len(t) >= 14:
                    v = np.array(t[2:14], float).reshape(4, 3); T.append(v[[[0, 1, 2], [0, 2, 3]]])
                elif t[0] == "2" and len(t) >= 8: E.append(np.array(t[2:8], float).reshape(1, 2, 3))
                elif t[0] == "1" and len(t) >= 15:
                    o = np.array(t[2:5], float); M = np.array(t[5:14], float).reshape(3, 3)
                    st, se = self.geom(" ".join(t[14:]), depth + 1)
                    if len(st): T.append((st.reshape(-1, 3) @ M.T + o).reshape(-1, 3, 3))
                    if len(se): E.append((se.reshape(-1, 3) @ M.T + o).reshape(-1, 2, 3))
        out = (np.concatenate(T) if T else np.zeros((0, 3, 3)), np.concatenate(E) if E else np.zeros((0, 2, 3)))
        self.cache[key] = out
        return out

def ldconfig(path):
    cols = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"0 !COLOUR\s+(\S+)\s+CODE\s+(\d+)\s+VALUE\s+(#[0-9A-Fa-f]{6})\s+EDGE\s+(#[0-9A-Fa-f]{6})(.*)", line)
        if m:
            alpha = 1.0
            a = re.search(r"ALPHA\s+(\d+)", m.group(5))
            if a: alpha = int(a.group(1)) / 255
            cols[int(m.group(2))] = dict(name=m.group(1), hex=m.group(3), edge=m.group(4), alpha=alpha)
    return cols

def read_ldr(path):
    parts, step = [], 0
    for line in open(path, encoding="utf-8", errors="replace"):
        t = line.split()
        if not t: continue
        if t[:2] == ["0", "STEP"]: step += 1
        elif t[0] == "1" and len(t) >= 15:
            parts.append(dict(c=int(t[1]), o=[float(v) for v in t[2:5]], M=[float(v) for v in t[5:14]], p=" ".join(t[14:]), step=step))
    return parts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ldr", required=True); ap.add_argument("--ldraw", required=True)
    ap.add_argument("--json", required=True); ap.add_argument("--glb", default="")
    a = ap.parse_args()
    lib = Lib(a.ldraw); cols = ldconfig(os.path.join(a.ldraw, "LDConfig.ldr"))
    parts = read_ldr(a.ldr)
    meshes = {}
    for p in parts:
        k = p["p"].lower()
        if k not in meshes:
            T, E = lib.geom(p["p"])
            meshes[k] = dict(tris=T.astype(np.float32), edges=E.astype(np.float32))
    b64 = lambda arr: base64.b64encode(np.ascontiguousarray(arr, np.float32).tobytes()).decode()
    scene = dict(source=os.path.basename(a.ldr),
                 colours={str(c): v for c, v in cols.items() if c in {p["c"] for p in parts}},
                 meshes={k: dict(tris=b64(v["tris"]), edges=b64(v["edges"]), ntris=len(v["tris"])) for k, v in meshes.items()},
                 parts=[dict(p=p["p"].lower(), c=p["c"], o=p["o"], M=p["M"], step=p["step"],
                             y0=int(round(-(p["o"][1] + float((meshes[p["p"].lower()]["tris"].reshape(-1, 3) @ np.array(p["M"]).reshape(3, 3).T)[:, 1].max())) / 8)))
                        for p in parts])
    json.dump(scene, open(a.json, "w"))
    print(f"{len(parts)} parts, {len(meshes)} part shapes, {sum(meshes[p['p'].lower()]['tris'].shape[0] for p in parts):,} triangles")
    if a.glb:
        import trimesh
        groups = {}
        for p in parts:
            T = meshes[p["p"].lower()]["tris"].reshape(-1, 3).astype(np.float64)
            W = T @ np.array(p["M"]).reshape(3, 3).T + np.array(p["o"])
            groups.setdefault(p["c"], []).append(W)
        sc = trimesh.Scene()
        for c, Ws in groups.items():
            V = np.concatenate(Ws) * 0.4                     # LDU -> mm
            V = V * np.array([1, -1, -1])                    # LDraw (-Y up) -> glTF (Y up), proper rotation
            F = np.arange(len(V)).reshape(-1, 3)
            h = cols.get(c, dict(hex="#888888"))["hex"]
            rgba = [int(h[i:i+2], 16) for i in (1, 3, 5)] + [255]
            m = trimesh.Trimesh(V, F, process=False)
            m.visual = trimesh.visual.ColorVisuals(m, face_colors=np.tile(rgba, (len(F), 1)))
            sc.add_geometry(m, node_name=f"colour_{c}")
        sc.export(a.glb)
        print("glb", a.glb)

if __name__ == "__main__":
    main()
