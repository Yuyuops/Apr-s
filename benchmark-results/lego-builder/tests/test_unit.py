#!/usr/bin/env python3
"""Fast unit tests of the builder (no engine needed) : manifest strictness, view naming, analysis of synthetic pictures. Run : python tests/test_unit.py"""
import json, sys, tempfile, unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lego_builder import analyze, manifest, reconstruct
GOOD = {"schema_version": 1, "project_id": "t", "source": {"kind": "glb", "files": []}, "construction_type": "sculpture_3d", "generator": "sculpture", "geometry_source": {"kind": "none"}, "target": {}, "status": "analysed", "uncertainties": []}
class T(unittest.TestCase):
    def test_manifest_accepts_valid(self): self.assertEqual(manifest.validate(GOOD), [])
    def test_manifest_rejects_bad_enum_and_missing_key(self):
        bad = dict(GOOD, status="done"); self.assertTrue(manifest.validate(bad)); bad2 = {k: v for k, v in GOOD.items() if k != "generator"}; self.assertTrue(manifest.validate(bad2))
    def test_manifest_detects_changed_source(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.txt"; p.write_text("x"); m = json.loads(json.dumps(GOOD)); m["source"]["files"] = [{"path": "a.txt", "sha256": manifest.sha256(p)}]; self.assertEqual(manifest.validate(m, d), [])
            p.write_text("changed"); self.assertTrue(any("sha256 mismatch" in e for e in manifest.validate(m, d)))
    def test_views_by_name(self):
        v, pb = reconstruct.find_views(["x_face_rgba.png", "x_dos.png", "x_profil_gauche.png", "x_profil_droit.png"]); self.assertEqual(sorted(v), ["dos", "face", "profil_droit", "profil_gauche"]); self.assertEqual(pb, [])
        v, pb = reconstruct.find_views(["only_face.png"]); self.assertEqual(len(pb), 3)
    def test_cutout_refuses_textured_background(self):
        with tempfile.TemporaryDirectory() as d:
            a = (np.random.RandomState(0).rand(120, 120, 3) * 255).astype(np.uint8); Image.fromarray(a).save(Path(d) / "n.png"); r = reconstruct.ensure_rgba(Path(d) / "n.png", Path(d) / "o.png"); self.assertTrue(r["cutout"].startswith("failed"))
    def test_analysis_object_vs_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            im = np.zeros((200, 200, 4), np.uint8); im[60:140, 60:140] = (200, 120, 30, 255); Image.fromarray(im, "RGBA").save(Path(d) / "obj.png"); r = analyze.analyse(Path(d) / "obj.png"); self.assertEqual(r["construction_type"], "sculpture_3d")
            Image.fromarray(np.full((200, 200, 3), 128, np.uint8)).save(Path(d) / "grey.png"); r = analyze.analyse(Path(d) / "grey.png"); self.assertEqual(r["construction_type"], "undetermined")
if __name__ == "__main__": unittest.main(verbosity=2)
