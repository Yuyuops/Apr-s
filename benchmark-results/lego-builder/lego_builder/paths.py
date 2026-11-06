"""Locations of the existing engines (nothing is moved : the builder drives them). LEGO_ENGINE_HOME = the engine-1 portable install (venv, deps, node_modules), see 20_portable_engine/README.md."""
import os
from pathlib import Path
REPO = Path(__file__).resolve().parents[3]
BR = REPO / "benchmark-results"
MAPS = BR / "maps-engine-v03" / "style_fidelity_v062"          # maps generator (LEGO Maps V1.0)
E1_SRC = BR / "20_portable_engine"                              # sculpture generator + shared validator (engine 1, sources)
E1_HOME = Path(os.environ.get("LEGO_ENGINE_HOME", str(E1_SRC)))  # engine-1 install (venv, .deps, node_modules)
PY = str(E1_HOME / ".venv" / "bin" / "python")
DATA = Path(__file__).resolve().parents[1] / "data"
SCHEMA = Path(__file__).resolve().parents[1] / "schema" / "project_manifest.schema.json"
def env():
    e = dict(os.environ); e["LEGO_ENGINE_HOME"] = str(E1_HOME); e["LEGO_NODE_MODULES"] = str(E1_HOME / "node_modules"); e["NODE_PATH"] = str(E1_HOME / "node_modules"); return e
