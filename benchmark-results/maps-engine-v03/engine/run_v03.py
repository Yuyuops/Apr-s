#!/usr/bin/env python3
"""LEGO Maps V0.3: opt-in support-aware generation on an isolated V0.2 copy.

This wrapper patches only the in-memory V0.3 builder during the process;
archives V0.0/V0.1/V0.2, engine 1 and every GLB remain unchanged.
"""
import argparse
import json
from pathlib import Path

from maps_engine import build as builder
from maps_engine import palette as palette
from maps_engine import run_map as v02
from maps_engine.common import PLATES
from maps_engine.support_opt import improve

LAST = {}
BEFORE_PARTS = []
ORIGINAL_BUILD = builder.build


def support_build(*args, **kwargs):
    result = ORIGINAL_BUILD(*args, **kwargs)
    BEFORE_PARTS.clear()
    BEFORE_PARTS.extend(dict(p) for p in result["parts"])
    updated, audit = improve(
        result["parts"], PLATES, palette.available, max_passes=3,
        max_cells=32, max_candidates_per_group=96, max_growth=0.15,
    )
    # All geometry, occupied cells, colours, layer heights and special parts
    # are unchanged. IDs are unique (some may be above the legacy range).
    assert len({p["id"] for p in updated}) == len(updated), "duplicate part ids"
    assert len(updated) <= int(len(result["parts"]) * 1.15 + 0.999), "piece growth cap exceeded"
    result["parts"] = updated
    result["support_audit_v03"] = audit
    LAST.clear()
    LAST.update(audit)
    return result


def run(args):
    builder.build = support_build
    out = Path(args.out)
    if out.resolve().is_relative_to((Path(__file__).resolve().parents[1] / "../maps-engine-v02").resolve()):
        raise ValueError("Do not write into an archived V0.2 folder")
    out.mkdir(parents=True, exist_ok=True)
    kw = dict(
        finish=args.finish, mode=args.mode, n=args.n, frame=args.frame,
        style_path=args.style, tries=args.tries, cut=False if args.no_cut else None,
        smooth=[x for x in args.smooth.split(",") if x] or None,
        cap=False if args.no_cap else None, improve=not args.no_improve,
        mat=args.mat,
    )
    if args.cmd == "generate":
        png = v02.load_input(args.input, str(out), 512 if 512 % args.n == 0 else args.n * 10)
        _, model, result = v02.generate(png, str(out), **kw)
    else:
        _, model, result = v02.full(
            args.input, str(out), render=not args.no_render, **kw
        )
    (out / "parts_before_v03.json").write_text(
        json.dumps(BEFORE_PARTS, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out / "support_report_v03.json").write_text(
        json.dumps(LAST, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    result["support_optimiser"] = {
        "baseline_critical": LAST["baseline"]["critical_carriers"],
        "final_critical": LAST["final"]["critical_carriers"],
        "operations": len(LAST["operations"]),
        "residual_count": len(LAST["residual"]),
    }
    if args.cmd == "full":
        vpath = out / "validation" / "validation_resume.json"
        checks = json.loads(vpath.read_text(encoding="utf-8"))
        m1 = checks["moteur1"]
        # Unlike V0.2, V0.3 refuses to silently call a broken assembly valid.
        errors = {k: m1.get(k) for k in ("collisions", "disconnected_parts", "islands", "blocked_studs", "unsupported_at_placement")
                  if isinstance(m1.get(k), int) and m1[k] > 0}
        if errors:
            raise RuntimeError("V0.3 model failed independent engine-1 validation: " + repr(errors))
        result["engine1_validated"] = True
    (out / "generation.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["support_optimiser"], indent=2, ensure_ascii=False))
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=("generate", "full"))
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--finish", default="A", choices=("A", "B"))
    ap.add_argument("--mode", default="2.5d", choices=("2.5d", "2d"))
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--frame", type=int)
    ap.add_argument("--style")
    ap.add_argument("--tries", type=int, default=8)
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--no-cut", action="store_true")
    ap.add_argument("--smooth", default="")
    ap.add_argument("--no-cap", action="store_true")
    ap.add_argument("--mat", type=int)
    ap.add_argument("--no-improve", action="store_true")
    a = ap.parse_args()
    run(a)


if __name__ == "__main__":
    main()
