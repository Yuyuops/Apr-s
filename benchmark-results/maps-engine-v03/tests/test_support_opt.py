#!/usr/bin/env python3
"""Run with standard Python: python tests/test_support_opt.py (no LDraw/DB needed).

Historical results are never modified. Tests operate on the actual archived
V0.2 Scotland part lists and on synthetic adversarial part arrangements.
"""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
from maps_engine.support_opt import support_report, improve, footprint

BASE = ROOT.parent / "maps-engine-v02" / "results"
REFERENCE = ROOT / "references" / "baseline_scotland.json"


class SupportOptimiserTests(unittest.TestCase):
    def test_historical_scotland_counts_unchanged(self):
        data = json.loads(REFERENCE.read_text(encoding="utf-8"))
        for case in data["cases"]:
            size = case["size"].split("x")[0]
            p = BASE / "ecosse" / ("A_" + size) / "parts.json"
            parts = json.loads(p.read_text(encoding="utf-8"))
            result = support_report(parts)
            self.assertEqual(result["critical_carriers"], case["critical_carriers"])
            self.assertEqual(result["weak_carriers"], case["weak_carriers"])
            self.assertEqual(len(parts), case["parts"])
            self.assertEqual(
                sorted(result["critical_ids"]),
                sorted(x["id"] for x in case["critical_parts"])
            )

    def test_merges_weak_carrier_without_changing_surface(self):
        catalog = {(1, 1): "unit", (2, 1): "short", (4, 1): "long"}
        def p(i, x, z, w, d, bot):
            return dict(id=i, kind="plate", x=x, z=z, w=w, d=d, zbot=bot,
                        h=1, colour=1, layer="L" + str(bot), region="area",
                        part=catalog[(max(w, d), min(w, d))],
                        size=f"{max(w,d)}x{min(w,d)}")
        original = [
            p(1, 0, 0, 4, 1, 0),
            p(2, 0, 0, 2, 1, 1),
            p(3, 2, 0, 2, 1, 1),
            p(4, 0, 0, 1, 1, 2)
        ]
        self.assertEqual(support_report(original)["critical_carriers"], 1)
        result, report = improve(original, catalog, lambda part, col: True)
        self.assertEqual(report["final"]["critical_carriers"], 0)
        self.assertEqual(len(result), 3)
        self.assertEqual(
            footprint([p for p in result if p["zbot"] == 1]),
            footprint(original[1:3])
        )
        self.assertEqual({p["colour"] for p in result}, {1})
        self.assertTrue(report["operations"])

    def test_different_colours_never_merged(self):
        catalog = {(1, 1): "unit", (2, 1): "short"}
        parts = [
            dict(id=i+1, kind="plate", x=i, z=0, w=1, d=1,
                 zbot=1, h=1, colour=i+3, layer="L1", region="area",
                 part="unit", size="1x1")
            for i in range(2)
        ]
        result, report = improve(parts, catalog, lambda p, c: True)
        self.assertEqual(result, parts)
        self.assertEqual(report["operations"], [])

    def test_round_and_wedge_are_protected(self):
        catalog = {(1, 1): "unit", (2, 1): "short"}
        base = [
            dict(id=1, kind="plate", x=0, z=0, w=1, d=1, zbot=1, h=1,
                 colour=1, layer="L1", region="village", part="6141", size="1x1"),
            dict(id=2, kind="plate", x=1, z=0, w=1, d=1, zbot=1, h=1,
                 colour=1, layer="L1", region="village", part="unit", size="1x1"),
        ]
        result, report = improve(base, catalog, lambda p, c: True)
        self.assertEqual(result, base)
        self.assertFalse(report["operations"])

    def test_reproducible(self):
        catalog = {(1, 1): "unit", (2, 1): "short", (4, 1): "long"}
        parts = [
            dict(id=i+1, kind="plate", x=i*2, z=0, w=2, d=1,
                 zbot=1, h=1, colour=1, layer="L1", region="land",
                 part="short", size="2x1")
            for i in range(2)
        ]
        p1, r1 = improve(parts, catalog, lambda p, c: True)
        p2, r2 = improve(parts, catalog, lambda p, c: True)
        self.assertEqual(p1, p2)
        self.assertEqual(r1, r2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
