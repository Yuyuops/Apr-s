"""Paths and run context of the LEGO engine 1 : nothing is absolute, nothing refers to a developer's home directory.

LEGO_ENGINE_HOME  root of the portable engine folder (default : the parent of this file)
LEGO_DEPS         third-party dependencies fetched by scripts/fetch_deps.sh (default : <root>/.deps)
LEGO_TARGETS      writable folder of the ear silhouette targets (default : <engine>/targets ; the runner copies it into the run folder)
LEGO_EAR_FRAME    JSON of the ear frame of a subject (default : engine/data/paco_ear_frame.json : Paco-specific data, see ARCHITECTURE.md)
LEGO_CTX          JSON file giving the files of the current run (keys : full_npz, seg_npz, ref_full_frame, source_glb)
"""
import json, os
ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("LEGO_ENGINE_HOME", os.path.dirname(ENGINE_DIR))
DEPS = os.environ.get("LEGO_DEPS", os.path.join(ROOT, ".deps"))
LDRAW = os.path.join(DEPS, "ldraw-parts-library", "complete", "ldraw")
RB_DB = os.path.join(DEPS, "rb.db")
BRICKIFY_PIPELINE = os.path.join(DEPS, "brickify", "pipeline")
NODE_MODULES = os.path.join(ROOT, "node_modules")
TARGETS_DIR = os.environ.get("LEGO_TARGETS", os.path.join(ENGINE_DIR, "targets"))
EAR_FRAME_JSON = os.environ.get("LEGO_EAR_FRAME", os.path.join(ENGINE_DIR, "data", "paco_ear_frame.json"))
def CTX(key):
    f = os.environ.get("LEGO_CTX")
    if not f: raise RuntimeError("LEGO_CTX is not set : this stage needs the run context file (key %r)" % key)
    return json.load(open(f))[key]
def LEGACY_DATA(name):
    """data of the early ear-design iterations (V4 to V5) : not part of the engine ; fails loudly if a code path reaches it"""
    return os.path.join(DEPS, "legacy", name)
