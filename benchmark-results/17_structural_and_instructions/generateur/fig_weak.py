"""figures of the fragile groups on the model (group parts in colour, the rest pale). usage: fig_weak.py <scene.json> <weak.json> <out views.json>"""
import json, sys
import numpy as np
sc, weakf, out = sys.argv[1:4]
W = json.load(open(weakf))["groupes"]; S = json.load(open(sc))["parts"]
ids = {i for g in W for i in g["parts_ids"] if len(g["parts_ids"]) < 100}
items = [[i, "new" if i in ids else "old"] for i in range(len(S))]
fb = [[0, 0, -280], [280, 405, 0]]
views = [dict(name=n, az=a, el=e, w=900, h=1100, frameBox=fb, items=items) for n, a, e in (("face", 180, 8), ("profil_gauche", 270, 5), ("profil_droit", 90, 5), ("trois_quarts", 225, 18))]
json.dump(views, open(out, "w"))
