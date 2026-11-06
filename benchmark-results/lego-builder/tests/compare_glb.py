#!/usr/bin/env python3
"""BLOCKING : two GLB files must have identical geometry and vertex colours (the container bytes may differ). usage : compare_glb.py A.glb B.glb"""
import sys
import numpy as np, trimesh
a, b = [list(trimesh.load(p, force="scene").geometry.values())[0] for p in sys.argv[1:3]]
ok = a.vertices.shape == b.vertices.shape and np.array_equal(a.vertices, b.vertices) and np.array_equal(a.faces, b.faces) and np.array_equal(a.visual.vertex_colors, b.visual.vertex_colors)
print("vertices %d/%d faces %d/%d identical geometry+colours: %s" % (len(a.vertices), len(b.vertices), len(a.faces), len(b.faces), ok)); sys.exit(0 if ok else 1)
