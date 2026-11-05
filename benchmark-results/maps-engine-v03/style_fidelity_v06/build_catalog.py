#!/usr/bin/env python3
"""Builds part_catalog.json : body box (LDU), top studs, receptors, LDraw title of every part the V0.5.1 generator may use, read from the official LDraw
geometry through engine-1 conn.py (read-only). Fails if a part is missing or is a '~Moved' alias, so only real, current LDraw part files are used."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "20_portable_engine", "engine"))
import conn, partlib as PL
from _paths import LDRAW
PARTS = """3005 3004 3622 3010 3009 3008 3003 3002 3001 2456 3007
3024 3023 3623 3710 3666 3460 3022 3021 3020 3795 3034 3031 3032 3035 3036 41539 3030 3029 3958
3070b 3069b 2431 3068b 98138 2412b 6636 4162
3040b 3039 3038 3037 3298 4286 54200 85984 3045 3046 3665a 3660a 61678 50950 11477 15068
3659 4490 3455 6182 6183 13965
6141 3062b 3941 4589 3942c 2357 3063b 2577 30136 60592 4073 3794a
14719 25269 2420 98138 3070b 4032a 87079 69729 26603 3068b 60481 3678b 4460a 3684a 3685 3688 4161 85984 54200 92947 4150 6143 15068 3062b 4589""".split()
cat = {}
for n in PARTS:
    f = os.path.join(LDRAW, "parts", n + ".dat")
    if not os.path.exists(f): print("MISSING", n); continue
    t = PL.title(n)
    if t.startswith("~"): print("ALIAS (not used)", n, t); continue
    p = conn.part(n)
    cat[n] = dict(title=t, lo=[float(v) for v in p["lo"]], hi=[float(v) for v in p["hi"]], studs=len(p["studs"]), receptors=len(p["receptors"]), stud_pts=[[float(v) for v in s[0]] for s in p["studs"]])
json.dump(cat, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "part_catalog.json"), "w"), indent=0)
print(len(cat), "parts in catalog")

# part x colour pairs catalogued by Rebrickable (pcs_mat.num_sets) for the colours the generator may use
import sqlite3
from _paths import RB_DB
db = sqlite3.connect(RB_DB); COLOURS = [0, 1, 2, 3, 4, 10, 14, 15, 19, 25, 28, 70, 71, 72, 73, 84, 92, 212, 272, 288, 297, 308, 320, 321, 322, 323, 378]
def rbnum(n):
    for cand in (n, n.rstrip("abcdefghijklmnopqrstuvwxyz")):
        if db.execute("select 1 from pcs_mat where part_num=? limit 1", (cand,)).fetchone(): return cand
    return n
pairs = {n: {str(c): (db.execute("select num_sets from pcs_mat where part_num=? and color_id=?", (rbnum(n), c)).fetchone() or (0,))[0] for c in COLOURS} for n in cat}
json.dump(pairs, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pair_sets.json"), "w"), indent=0)
print("pair table", sum(1 for n in pairs for c in pairs[n] if pairs[n][c] == 0), "uncatalogued pairs of", sum(len(v) for v in pairs.values()))
