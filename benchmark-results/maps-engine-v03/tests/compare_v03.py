#!/usr/bin/env python3
"""Independent archived-output verification of V0.3 generated outputs.

No regeneration or mutation of original V0.2 artifacts. This script fails
closed if required files are missing or if any geometric/colour invariant
breaks. A passed digital check is NOT physical assembly validation.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
from maps_engine.support_opt import support_report

CASES = {
    "ecosse/A_32": ("ecosse/A_32", 17),
    "ecosse/A_48": ("ecosse/A_48", 19),
    "ile_temoin/A_32": ("ile_temoin/A_corrigee", 0),
    "test_3_zones/A_32": ("test_3_zones/A_corrigee", 0),
    "archipel/A_32": (None, None),
}


def cells_by_height(parts):
    """Exact occupied cells with type and colour, including stacked plates."""
    cells = {}
    for p in parts:
        for x in range(p["x"], p["x"] + p["w"]):
            for z in range(p["z"], p["z"] + p["d"]):
                key = (p["zbot"], p["h"], x, z)
                if key in cells:
                    raise ValueError("Overlapping parts at " + repr(key))
                cells[key] = (p["colour"], p["kind"])
    return cells


def inspect_case(name, v02, original_expected):
    d = ROOT / "results" / name
    needed = ("parts.json", "parts_before_v03.json", "map.ldr",
              "parts_list.csv", "support_report_v03.json")
    missing = [x for x in needed if not (d / x).exists()]
    if missing:
        return dict(case=name, status="INCOMPLETE", missing=missing)

    before = json.loads((d / "parts_before_v03.json").read_text(encoding="utf-8"))
    after = json.loads((d / "parts.json").read_text(encoding="utf-8"))
    report = json.loads((d / "support_report_v03.json").read_text(encoding="utf-8"))
    pre, post = support_report(before), support_report(after)

    exact = cells_by_height(before) == cells_by_height(after)
    ids_unique = len({p["id"] for p in after}) == len(after)
    growth = (len(after) - len(before)) / max(1, len(before))
    ldr_count = sum(line.startswith("1 ") for line in (d / "map.ldr").read_text(encoding="utf-8").splitlines())
    with (d / "parts_list.csv").open(encoding="utf-8") as stream:
        bom = sum(int(row["quantity"]) for row in csv.DictReader(stream))
    checks = dict(
        exact_geometry_and_colours=exact,
        unique_part_ids=ids_unique,
        pieces_growth_max_15pct=growth <= 0.15 + 1e-9,
        critical_not_increased=post["critical_carriers"] <= pre["critical_carriers"],
        ldraw_bom_parts_agree=ldr_count == bom == len(after),
        report_counts_agree=(report["baseline"]["critical_carriers"] == pre["critical_carriers"]
                             and report["final"]["critical_carriers"] == post["critical_carriers"]),
    )
    historical = None
    if v02 is not None:
        src = ROOT.parent / "maps-engine-v02" / "results" / v02 / "parts.json"
        base = json.loads(src.read_text(encoding="utf-8"))
        basefrag = support_report(base)
        historical = {
            "v02_parts": len(base),
            "v02_critical": basefrag["critical_carriers"],
            "v02_expected_critical": original_expected,
            "v03_input_changed_vs_v02_archive": cells_by_height(base) != cells_by_height(before),
            "note": "An input change may be a catalogue/database drift; compare actual pre-opt input, not only archived counts."
        }
        checks["historical_ref_count_agree"] = basefrag["critical_carriers"] == original_expected
        if basefrag["critical_carriers"] == 0:
            checks["no_new_critical_on_legacy_zero_case"] = post["critical_carriers"] == 0

    status = "PASS" if all(checks.values()) else "FAIL"
    return {
        "case": name, "status": status, "checks": checks, "historical": historical,
        "before_parts": len(before), "after_parts": len(after),
        "growth_fraction": round(growth, 4),
        "before_critical": pre["critical_carriers"],
        "after_critical": post["critical_carriers"],
        "before_weak": pre["weak_carriers"],
        "after_weak": post["weak_carriers"],
        "unresolved": report.get("residual", []),
        "physical_validation": False,
    }


def main():
    records = [inspect_case(name, *data) for name, data in CASES.items()]
    complete = all(x["status"] != "INCOMPLETE" for x in records)
    passes = all(x["status"] == "PASS" for x in records)
    result = {"complete": complete, "all_digital_invariants_pass": passes,
              "overall": "PASS" if passes else "INCOMPLETE" if not complete else "FAIL",
              "cases": records,
              "limitations": [
                  "Support thresholds are graph heuristics; no shear, clutch-fatigue or wall mount test.",
                  "Briquestore prices and stock not verified.",
                  "Archival input/catalog drift is tracked, never silently counted as an optimisation gain.",
              ]}
    target = ROOT / "results" / "COMPARAISON_V03.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"overall": result["overall"],
                      "cases": [(x["case"], x["status"], x.get("after_critical")) for x in records]},
                     indent=2, ensure_ascii=False))
    return 0 if passes else 2


if __name__ == "__main__":
    sys.exit(main())
