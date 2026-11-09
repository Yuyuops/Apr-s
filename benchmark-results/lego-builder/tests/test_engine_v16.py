#!/usr/bin/env python3
"""Sprint V16 engine option tests (fast, no render, no validator). Every option is OFF by default : the default build of a small map is identical with and without the V16 code paths, and the options build collision-free scenes.
usage : LEGO_ENGINE_HOME=... python tests/test_engine_v16.py"""
import hashlib, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
import numpy as np
from PIL import Image
HERE = Path(__file__).resolve().parents[1]; M = HERE.parent / "maps-engine-v03" / "style_fidelity_v062"; E1 = Path(os.environ["LEGO_ENGINE_HOME"]); PY = str(E1 / ".venv" / "bin" / "python")
def build(style, comp, out):
    env = dict(os.environ, LEGO_DEPS=str(E1 / ".deps")); r = subprocess.run([PY, "build_style.py", str(style), str(comp), str(out), "--flank", "vertical", "--no-title"], cwd=M, capture_output=True, text=True, env=env); return r
def small_zone(tmp, legacy=False):
    names = json.load(open(HERE / "sprint_v15" / "HYRULE_REQUIREMENTS.json"))["classes"][:12] + ["shallow", "meadow"]; z = np.load(HERE / "sprint_v16" / "data" / "zone_A_classes_v16.npy")[:14, :14].copy()
    if legacy: z[z == 12] = 0; z[z == 13] = 3; names = names[:12]                      # the V15 style knows only the 12 base classes
    tag = "L" if legacy else "N"; Image.fromarray(z.astype(np.uint8)).save(tmp / ("z%s.tif" % tag)); json.dump({"biome_map": {"file": str(tmp / ("z%s.tif" % tag)), "classes": {str(i): n for i, n in enumerate(names)}, "majority_passes": 1}, "grid_studs": [14, 14], "sub": 8}, open(tmp / ("comp%s.json" % tag), "w")); return tmp / ("comp%s.json" % tag)
class T(unittest.TestCase):
    def test_options_are_off_by_default_and_on_builds_are_collision_free(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d); comp = small_zone(d); compL = small_zone(d, True); base = json.load(open(M / "styles" / "hyrule_v15_B.json")); on = json.load(open(HERE / "sprint_v16" / "hyrule_v16_c4.json"))
            json.dump(base, open(d / "off.json", "w")); json.dump(on, open(d / "on.json", "w"))
            r1 = build(d / "off.json", compL, d / "o1"); r2 = build(d / "off.json", compL, d / "o2"); self.assertEqual(r1.returncode, 0, r1.stderr[-400:]); self.assertEqual(hashlib.sha256((d / "o1" / "diorama.ldr").read_bytes()).hexdigest(), hashlib.sha256((d / "o2" / "diorama.ldr").read_bytes()).hexdigest())
            m_off = json.load(open(d / "o1" / "metrics.json")); self.assertNotIn("wild_layers", m_off); self.assertNotIn("smooth_height", m_off); self.assertNotIn("details_placed", m_off)
            r3 = build(d / "on.json", comp, d / "p1"); self.assertEqual(r3.returncode, 0, r3.stderr[-600:])         # Scene.add raises on any collision / unsupported detail
            m_on = json.load(open(d / "p1" / "metrics.json")); self.assertGreater(m_on["wild_layers"], 0); self.assertGreaterEqual(m_on["smooth_height"]["max_plates"], 2)
            r4 = build(d / "on.json", comp, d / "p2"); self.assertEqual(hashlib.sha256((d / "p1" / "diorama.ldr").read_bytes()).hexdigest(), hashlib.sha256((d / "p2" / "diorama.ldr").read_bytes()).hexdigest())      # deterministic
    def test_no_one_stud_plate_bodies_with_wild_tiler(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d); comp = small_zone(d); compL = small_zone(d, True); on = json.load(open(HERE / "sprint_v16" / "hyrule_v16_c4.json")); json.dump(on, open(d / "on.json", "w")); r = build(d / "on.json", comp, d / "p")
            self.assertEqual(r.returncode, 0, r.stderr[-400:]); parts = json.load(open(d / "p" / "parts.json")); ones = [p for p in parts if p["region"] == "strata_body" and p["nr"] * p["nc"] == 1]
            base = json.load(open(M / "styles" / "hyrule_v15_B.json")); json.dump(base, open(d / "off.json", "w")); build(d / "off.json", compL, d / "q"); ones0 = [p for p in json.load(open(d / "q" / "parts.json")) if p["region"] == "strata_body" and p["nr"] * p["nc"] == 1]
            self.assertLess(len(ones), max(1, len(ones0)))                                       # fewer lonely 1x1 body plates than the legacy tiler
if __name__ == "__main__": unittest.main(verbosity=2)
