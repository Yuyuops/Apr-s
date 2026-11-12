#!/usr/bin/env python3
"""Product V1 (Beagle) : build the BOM files from the VALIDATED engine outputs and cross-check them against the LDraw model itself.
No price, no stock, no availability claim : the only commercial signal is the number of Rebrickable sets in which a part/colour pair appears (a proxy for how common it is), and it is labelled as such.
usage : product_bom_v1.py MODEL.ldr CATALOGUE.csv NOMENCLATURE.csv OUTDIR [--model-parts-list parts_list.csv]"""
import csv, json, sys, collections, hashlib, os
ldr, cat, nom, out = sys.argv[1:5]; os.makedirs(out, exist_ok=True)
rows = list(csv.DictReader(open(cat))); mass = {(r["part"], r["ldraw_colour"]): r for r in csv.DictReader(open(nom))}
cnt = collections.Counter()
for l in open(ldr):
    t = l.split()
    if t and t[0] == "1": cnt[(t[-1][:-4], t[1])] += 1
bad = []; total = 0
for r in rows:
    k = (r["part"], r["ldraw_colour"]); q = int(r["qty"]); total += q
    if cnt.get(k) != q: bad.append((k, q, cnt.get(k)))
extra = [k for k in cnt if k not in {(r["part"], r["ldraw_colour"]) for r in rows}]
def rarity(s):
    s = int(s); return "rare" if s <= 30 else ("peu courante" if s <= 100 else "courante")
flag = {"rare": "Pièce/couleur présente dans 30 sets Rebrickable ou moins : à chercher en priorité, prévoir une alternative", "peu courante": "31 à 100 sets", "courante": "plus de 100 sets"}
bom = []
for r in rows:
    k = (r["part"], r["ldraw_colour"]); m = mass.get(k, {})
    bom.append(dict(part_num=r["part"], part_name=r["name"].replace("  ", " "), ldraw_file=r["part"] + ".dat", ldraw_colour_id=int(r["ldraw_colour"]), colour_name=r["colour"].replace("_", " "), rebrickable_colour_id=int(r["rebrickable_colour_id"]), quantity=int(r["qty"]),
                    rebrickable_sets_containing_pair=int(r["sets"]), first_year=int(r["first_year"]), last_year=int(r["last_year"]), rarity_proxy=rarity(r["sets"]), model_mass_g=float(m.get("masse_modele_g", 0) or 0), catalogue_status=r["status"]))
bom.sort(key=lambda b: (-b["quantity"], b["part_num"], b["ldraw_colour_id"]))
fields = list(bom[0]); w = csv.DictWriter(open(os.path.join(out, "Beagle_V1_BOM.csv"), "w", newline=""), fieldnames=fields); w.writeheader(); w.writerows(bom)
parts_types = sorted({b["part_num"] for b in bom}); cols = sorted({(b["ldraw_colour_id"], b["colour_name"]) for b in bom})
J = dict(model="Beagle V1 (engine V12.1 validated)", ldraw_sha256=hashlib.sha256(open(ldr, "rb").read()).hexdigest(), total_pieces=total, part_colour_lines=len(bom), distinct_part_numbers=len(parts_types), colours=[dict(ldraw_id=i, name=n) for i, n in cols],
         price="not provided (no price invented)", availability="not checked (no stock or availability claim)", rarity_proxy_definition="rare <= 30 Rebrickable sets, uncommon 31-100, common > 100; proxy only, NOT availability", lines=bom)
json.dump(J, open(os.path.join(out, "Beagle_V1_BOM.json"), "w"), indent=1)
with open(os.path.join(out, "Beagle_V1_ldraw_parts.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["ldraw_file", "ldraw_colour_id", "quantity"]); [w.writerow([b["ldraw_file"], b["ldraw_colour_id"], b["quantity"]]) for b in bom]
with open(os.path.join(out, "Beagle_V1_rebrickable_import.csv"), "w", newline="") as f:         # Rebrickable "import parts list" format : Part,Color,Quantity (Rebrickable colour ids)
    w = csv.writer(f); w.writerow(["Part", "Color", "Quantity"]); [w.writerow([b["part_num"], b["rebrickable_colour_id"], b["quantity"]]) for b in bom]
rare = [b for b in bom if b["rarity_proxy"] != "courante"]
with open(os.path.join(out, "Beagle_V1_rare_parts.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["part_num", "part_name", "colour_name", "rebrickable_colour_id", "quantity", "rebrickable_sets_containing_pair", "rarity_proxy", "note"]); [w.writerow([b["part_num"], b["part_name"], b["colour_name"], b["rebrickable_colour_id"], b["quantity"], b["rebrickable_sets_containing_pair"], b["rarity_proxy"], flag[b["rarity_proxy"]]]) for b in sorted(rare, key=lambda x: x["rebrickable_sets_containing_pair"])]
chk = dict(bom_total=total, ldr_total=sum(cnt.values()), lines_bom=len(bom), lines_ldr=len(cnt), mismatches=bad, in_ldr_not_in_bom=extra, exact=(not bad and not extra and total == sum(cnt.values())))
json.dump(chk, open(os.path.join(out, "bom_cross_check.json"), "w"), indent=1); print(json.dumps(dict(total=total, lines=len(bom), part_numbers=len(parts_types), rare=len(rare), **{k: chk[k] for k in ("exact",)})))
sys.exit(0 if chk["exact"] else 1)
