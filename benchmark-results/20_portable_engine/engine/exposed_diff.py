"""Compare two models of the same subject : occupancy, exposed colours and hidden colours (V12.1). usage: exposed_diff.py a.ldr b.ldr  (LEGO_SHAPE = grid shape)"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import sys, json, numpy as np, scope
def load(p): P = scope.read_parts(p); return scope.voxelise(P)
def diff(a, b):
    A, B = load(a), load(b); occ_d = int((A["occ"] != B["occ"]).sum()); both = A["occ"] & B["occ"]; ex = (A["exposed"] | B["exposed"]) & both
    return dict(cellules_occupation_differentes=occ_d, cellules_exposees_couleur_differente=int(((A["col"] != B["col"]) & ex).sum()), cellules_cachees_couleur_differente=int(((A["col"] != B["col"]) & both & ~ex).sum()), cellules_exposees=int(A["exposed"].sum()))
if __name__ == "__main__": print(json.dumps(diff(sys.argv[1], sys.argv[2])))
