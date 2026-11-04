#!/usr/bin/env python3
"""V0.5.2 vs V0.5.3 table : pieces, references, validation, fragility, assembly accessibility (layer-by-layer build, overhangs). Writes comparatif_metrics.json / .md"""
import json, os
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); rows = {}
for name, f in (("V0.5.1", "../italie_v052_mountain_refinement/v051_reference"), ("V0.5.2", "v052_reference"), ("V0.5.3", "results/diorama_v053")):
    f = os.path.join(H, f); P = json.load(open(f + "/parts.json")); fr = json.load(open(f + "/fragility.json")); me = json.load(open(f + "/metrics.json")); bom = json.load(open(f + "/bom_verification.json")) if os.path.exists(f + "/bom_verification.json") else {}
    iv = json.load(open(f + "/independent_validation.json")) if os.path.exists(f + "/independent_validation.json") else {}
    occ = {}
    for p in P:
        for r in range(p["r"], p["r"] + p["nr"]):
            for c in range(p["c"], p["c"] + p["nc"]):
                for y in range(p["y"], p["y"] + p["h"]): occ[(r, c, y)] = p["id"]
    over = sum(1 for p in P if p["y"] > 0 and any((r, c, p["y"] - 1) not in occ for r in range(p["r"], p["r"] + p["nr"]) for c in range(p["c"], p["c"] + p["nc"])))
    layers = Counter(p["y"] for p in P)
    rows[name] = dict(pieces=len(P), references=me["references"], max_height_mm=me["max_height_mm"], collisions=iv.get("collisions"), disconnected=iv.get("disconnected_parts"), islands=iv.get("islands"), unsupported_at_placement=iv.get("unsupported_at_placement"), blocked_studs=iv.get("blocked_studs"),
                      bom_all_pairs_catalogued=(not bom.get("pairs_not_catalogued")) if bom else None, ldraw_eq_bom_eq_json=(iv.get("ldraw_count") == iv.get("bom_count") == iv.get("source_parts") == len(P)) if iv else None,
                      hang_by_one_stud=fr["parts_hanging_by_one_stud"], one_stud_decorative_leaves=fr["one_stud_decorative_leaves"], one_stud_and_carrying=fr["one_stud_and_carrying"], articulation_points=fr["articulation_points_with_loss"],
                      worst_single_failure_mass_g=fr["worst_single_failure"]["mass_cut_off_g"], mountain_max_parts_cut_off=fr["failure_by_family"].get("mountain", {}).get("max_parts_cut_off"),
                      thin_wall_pieces_1stud_thick=fr["colosseum_one_stud_thick_wall_pieces"], colosseum_wall_parts_by_one_stud=(fr["families"].get("colosseum_wall") or {}).get("hangs_by_one_stud", 0), tree_trunks_by_one_stud=(fr["families"].get("tree_slim") or {}).get("hangs_by_one_stud", 0),
                      build_layers=len(layers), max_parts_in_one_layer=max(layers.values()), parts_with_overhang_cells=over, assembly="strictly bottom-up, every part dropped on studs (validator: unsupported_at_placement 0)" if iv else "")
json.dump(rows, open(os.path.join(H, "comparatif_metrics.json"), "w"), indent=1)
keys = list(rows["V0.5.3"]); md = "| metric | " + " | ".join(rows) + " |\n|---|" + "---|" * len(rows) + "\n" + "\n".join("| %s | %s |" % (k, " | ".join(str(rows[n][k]) for n in rows)) for k in keys); open(os.path.join(H, "comparatif_metrics.md"), "w").write(md); print(md)
