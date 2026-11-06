"""Project manifest : light, versioned, strictly validated (types, enums, required keys, referenced files exist, source hashes match). The source stays distinct from derived data."""
import hashlib, json
from pathlib import Path
from .paths import SCHEMA
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def _check(node, sch, path, errs):
    t = sch.get("type"); pytype = {"object": dict, "array": list, "string": str, "number": (int, float)}.get(t)
    if "const" in sch and node != sch["const"]: errs.append("%s : must be %r" % (path, sch["const"]))
    if "enum" in sch and node not in sch["enum"]: errs.append("%s : %r not in %s" % (path, node, sch["enum"]))
    if pytype and not isinstance(node, pytype): errs.append("%s : expected %s" % (path, t)); return
    if t == "object":
        for k in sch.get("required", []):
            if k not in node: errs.append("%s : missing key %r" % (path, k))
        for k, sub in sch.get("properties", {}).items():
            if k in node: _check(node[k], sub, path + "." + k, errs)
    if t == "array":
        for i, it in enumerate(node):
            if "items" in sch: _check(it, sch["items"], "%s[%d]" % (path, i), errs)
def validate(m, root=None, schema_path=SCHEMA):
    errs = []; _check(m, json.load(open(schema_path)), "manifest", errs)
    if root is not None and not errs:
        root = Path(root)
        for f in m["source"]["files"]:
            p = root / f["path"] if not Path(f["path"]).is_absolute() else Path(f["path"])
            if not p.exists(): errs.append("source file missing : %s" % f["path"])
            elif sha256(p) != f["sha256"]: errs.append("source file changed (sha256 mismatch) : %s" % f["path"])
        for k, v in (m["geometry_source"].get("files") or {}).items():
            p = root / v
            if not p.exists(): errs.append("geometry file missing : %s (%s)" % (k, v))
        if m["status"] in ("ready_for_generation", "generated", "validated") and m["generator"] == "none": errs.append("status %s needs a generator" % m["status"])
    return errs
def write(m, root):
    errs = validate(m, root)
    if errs: raise ValueError("invalid manifest : " + "; ".join(errs))
    json.dump(m, open(Path(root) / "manifest.json", "w"), indent=1, ensure_ascii=False)
def read(root):
    m = json.load(open(Path(root) / "manifest.json")); errs = validate(m, root)
    if errs: raise ValueError("invalid manifest : " + "; ".join(errs))
    return m
