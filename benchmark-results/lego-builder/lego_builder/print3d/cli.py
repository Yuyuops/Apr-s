"""print-export : experimental STL/3MF export of a finished LDraw model. usage : python -m lego_builder.print3d.cli MODEL.ldr OUT_DIR [--mode bricks|modules|both]
Needs manifold3d (requirements-print3d.txt ; LEGO_PRINT_PATH = extra site dir). The exports are OPTIONAL and never touch the model or its validated results."""
import json, os, sys
from pathlib import Path
sys.path.insert(0, os.environ.get("LEGO_PRINT_PATH", "/nonexistent"))
HERE = Path(__file__).resolve().parents[3]
def main(argv=None):
    a = argv or sys.argv[1:]; ldr, out = a[0], Path(a[1]); mode = a[a.index("--mode") + 1] if "--mode" in a else "both"
    from . import bricks, modules, common
    from ..paths import MAPS, E1_HOME
    cat = json.load(open(MAPS / "part_catalog.json")); rb = str(E1_HOME / ".deps" / "rb.db"); res = {}
    if mode in ("bricks", "both"): res["bricks"] = bricks.export(ldr, cat, rb, out / "bricks")
    if mode in ("modules", "both"): res["modules"] = modules.build(ldr, cat, rb, out / ("modules_shape_export" if "--shape-aware" in a else "modules_export"), shape_aware="--shape-aware" in a)
    # LEGO mass with the validator convention (0.10 g per stud x stud x plate), for the comparison with real bricks
    parts = common.read_ldr(ldr); import numpy as np; m = 0.0
    for p in parts:
        c = cat.get(p["part"])
        if c: lo, hi = np.array(c["lo"]), np.array(c["hi"]); m += 0.1 * (hi[0] - lo[0]) / 20 * (hi[2] - lo[2]) / 20 * (hi[1] - lo[1]) / 8
    res["authentic_bricks"] = dict(pieces=len(parts), references=len({(p["part"], p["colour"]) for p in parts}), mass_g_validator_convention=round(m, 1), cost="NOT COMPUTED : no verified price or stock (fill prices.template.csv)")
    json.dump({k: {kk: vv for kk, vv in v.items() if kk not in ("geometry", "module_list")} for k, v in res.items()}, open(out / "comparison.json", "w"), indent=1); print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk in ("pieces", "parts_supported", "plates", "modules", "mass_g_upper_bound", "mass_g_validator_convention", "print_hours_estimate", "print_hours_upper_bound", "print_hours_estimate_30pct_fill", "mass_g_estimate_30pct_effective_fill")} for k, v in res.items()}))
if __name__ == "__main__": main()
