#!/usr/bin/env python3
"""Delivery concordance check of one model folder (exit 1 on any failure). Verifies : validator all_pass (0 collision / 0 disconnected / 0 island / 0 unsupported), no colour substitution,
catalogue check (verify_bom), LDraw piece lines == parts.json == parts_list.csv (per part/colour), assembly-plan part ids == model part ids, optional fragility file present.
usage: check_delivery.py MODELDIR   -> writes MODELDIR/delivery_check.json"""
import csv, json, os, sys
from collections import Counter
D = sys.argv[1]; P = json.load(open(D + "/parts.json")); M = json.load(open(D + "/metrics.json")); V = json.load(open(D + "/independent_validation.json")); B = json.load(open(D + "/bom_verification.json")); r = {}
r["validator_all_pass"] = bool(V["all_pass"]); r["no_colour_substitution"] = not M.get("colour_substitutions"); r["catalogue_ok"] = bool(B["all_dat_exist"] and B["all_colours_valid"] and not B["pairs_not_catalogued"])
ldr = sum(1 for l in open(D + "/diorama.ldr") if l.startswith("1 ")); r["ldr_lines_eq_parts_json"] = ldr == len(P) == M["pieces"]
bom = Counter(); [bom.update({(x["part_num"], x["color_id"]): int(x["quantity"])}) for x in csv.DictReader(open(D + "/parts_list.csv"))]
r["bom_eq_model"] = bom == Counter((p["part"], str(p["colour"])) for p in P)
if os.path.exists(D + "/assembly_plan_v2.json"):
    plan = json.load(open(D + "/assembly_plan_v2.json")); ids = [i for s in plan["steps"] for i in s["part_ids"]]; r["plan_ids_eq_model"] = sorted(ids) == sorted(p["id"] for p in P); r["plan_steps"] = len(plan["steps"])
r["fragility_present"] = os.path.exists(D + "/fragility.json"); r["pieces"] = M["pieces"]; r["references"] = M["references"]; r["all_ok"] = all(v for k, v in r.items() if isinstance(v, bool))
json.dump(r, open(D + "/delivery_check.json", "w"), indent=1); print(json.dumps(r)); sys.exit(0 if r["all_ok"] else 1)
