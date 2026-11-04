#!/usr/bin/env python3
"""Checks every (part, colour) of a parts_list.csv : (1) .dat exists in the pinned LDraw library and is not a '~Moved' alias, (2) colour id exists in Rebrickable `colors`
and in the LDraw LDConfig, (3) the pair is catalogued by Rebrickable (pcs_mat : number of sets containing it). Prices/stock stay empty (not verified). Writes bom_verification.csv/json."""
import csv, json, os, re, sqlite3, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "20_portable_engine", "engine"))
from _paths import LDRAW, RB_DB
folder = sys.argv[1]; db = sqlite3.connect(RB_DB)
cols = {r[0]: (r[1], r[2]) for r in db.execute("select id,name,rgb from colors")}
ld = set(int(m.group(1)) for m in re.finditer(r"!COLOUR\s+\S+\s+CODE\s+(\d+)", open(os.path.join(LDRAW, "LDConfig.ldr")).read()))
rows = list(csv.DictReader(open(os.path.join(folder, "parts_list.csv")))); out = []; bad = []
for r in rows:
    pn, col, q = r["part_num"], int(r["color_id"]), int(r["quantity"]); f = os.path.join(LDRAW, "parts", pn + ".dat"); exists = os.path.exists(f)
    title = open(f, errors="ignore").readline().strip()[2:] if exists else ""
    alias = title.startswith("~Moved")
    rb_part = db.execute("select name from parts where part_num=?", (pn,)).fetchone()
    n = db.execute("select num_sets from pcs_mat where part_num=? and color_id=?", (pn, col)).fetchone()
    o = dict(part_num=pn, part_name_ldraw=title, rebrickable_name=rb_part[0] if rb_part else "", color_id=col, color_name=cols.get(col, ("", ""))[0], rgb=cols.get(col, ("", ""))[1], quantity=q,
             ldraw_dat_exists=exists, not_alias=not alias, colour_in_rebrickable=col in cols, colour_in_ldraw=col in ld, part_in_rebrickable=bool(rb_part), pair_sets=int(n[0]) if n else 0, stock_verified=False, unit_price="")
    o["ok"] = exists and not alias and col in cols and col in ld and bool(rb_part); o["pair_catalogued"] = o["pair_sets"] > 0; out.append(o)
    if not o["ok"] or not o["pair_catalogued"]: bad.append(o)
with open(os.path.join(folder, "bom_verification.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
s = dict(references=len(out), pieces=sum(o["quantity"] for o in out), all_dat_exist=all(o["ldraw_dat_exists"] and o["not_alias"] for o in out), all_colours_valid=all(o["colour_in_rebrickable"] and o["colour_in_ldraw"] for o in out),
         pairs_not_catalogued=[(o["part_num"], o["color_id"], o["color_name"], o["quantity"]) for o in out if not o["pair_catalogued"]])
json.dump(s, open(os.path.join(folder, "bom_verification.json"), "w"), indent=1); print(json.dumps(s))
