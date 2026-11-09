"""Need detection / request interpretation (Sprint V15). Offline and deterministic : no AI service. It combines (1) a structured requirements file filled by the operator (the reliable channel for anything a picture cannot say : subject,
version, reference, regions), (2) keyword rules on the request text (French/English) and (3) the existing source analysis (lego_builder.analyze). It returns a PLAN : construction type, generator, evidence, blockers and questions,
and the ordered steps. If the information is insufficient it returns status needs_input instead of guessing ; the semantic reading of a picture is NEVER simulated (only what the analysis measures is claimed)."""
import json, re
from pathlib import Path
from .paths import DATA
ROUTES = {"map_relief_25d": "maps", "sculpture_3d": "sculpture", "photos_3d": "photos_to_3d", "mosaic_2d": "mosaic"}
IMPLEMENTED = {"maps": True, "sculpture": True, "photos_to_3d": True, "mosaic": False}
KW = {"map_relief_25d": r"\b(carte|cartes|map|maps|pays|r[ée]gion|relief|topograph\w*|g[ée]ograph\w*|atlas|littoral|montagne\w*|royaume|kingdom|island|[iî]le)\b",
      "sculpture_3d": r"\b(sculpture\w*|statue|figurine|animal|animaux|chien|chat|personnage\w*|objet\w*|mod[eè]le 3d|glb|buste|creature)\b",
      "photos_3d": r"\b(photos?|quatre vues|4 vues|multi-?vues?|plusieurs vues|reconstruction|photogramm\w*|from photos)\b",
      "mosaic_2d": r"\b(mosa[iï]que\w*|mosaic|pixel ?art|logo|portrait 2d|tableau 2d|image 2d|affiche)\b"}
REQUIRED = ["request", "subject", "reference", "board", "routing"]
def validate_requirements(req):
    """-> list of problems (empty = valid)"""
    p = [f"missing field '{k}'" for k in REQUIRED if k not in req]
    if "subject" in req and not req["subject"].get("name"): p.append("subject.name missing")
    ref = req.get("reference", {})
    if ref and not ref.get("sha256"): p.append("reference.sha256 missing (the reference must be identified)")
    return p
def _subject_version_problem(req_subject):
    if not req_subject: return None
    key = req_subject.get("name", "").strip().lower(); tab = json.load(open(DATA / "subject_versions.json")); ent = tab.get(key)
    if not ent: return None
    sel = (req_subject.get("version") or {}).get("selected")
    if not sel: return "subject '%s' exists in several versions %s : none selected, refusing to mix geographies" % (req_subject["name"], ent["versions"])
    if sel not in ent["versions"]: return "selected version '%s' is not in the known versions %s" % (sel, ent["versions"])
    return None
def interpret(text=None, sources=(), requirements=None):
    """-> plan dict. sources : image/GLB paths ; requirements : dict (already loaded) or None."""
    from . import analyze as A
    ev = []; blockers = []; questions = []; scores = {k: 0.0 for k in KW}
    if text:
        for k, rx in KW.items():
            n = len(re.findall(rx, text.lower()))
            if n: scores[k] += min(2.0, 0.8 * n); ev.append("request text : %d keyword(s) for %s" % (n, k))
    srcs = [Path(s) for s in sources]; analyses = []
    imgs = [s for s in srcs if s.suffix.lower() in A.IMG]; glbs = [s for s in srcs if s.suffix.lower() in (".glb", ".gltf")]
    if len(imgs) >= 4 and not glbs: scores["photos_3d"] += 2.0; ev.append("%d pictures given : multi-view reconstruction candidate" % len(imgs))
    for s in srcs[:1] if len(imgs) < 2 else []:
        try: a = A.analyse(s); analyses.append(a); scores[{"map_relief_25d": "map_relief_25d", "sculpture_3d": "sculpture_3d", "mosaic_2d": "mosaic_2d"}.get(a["construction_type"], "mosaic_2d")] += (a["confidence"] if a["construction_type"] != "undetermined" else 0); ev += ["source analysis : " + e for e in a["evidence"]]
        except Exception as e: blockers.append("source analysis failed : %s" % e)
    if glbs: scores["sculpture_3d"] += 2.0; ev.append("a 3D model (GLB) is given")
    if text and not (requirements or {}).get("subject"):                                 # a subject known in several versions, named only in the text : the version must be asked, never guessed
        for key, ent in json.load(open(DATA / "subject_versions.json")).items():
            if key.startswith("_"): continue
            if re.search(r"\b%s\b" % re.escape(key), text.lower()): blockers.append("subject '%s' exists in several versions %s : none given (provide --requirements with subject.version.selected)" % (key, ent["versions"])); questions.append("Which version of %s ?" % key)
    source = "inferred"
    if requirements:
        pb = validate_requirements(requirements)
        if pb: blockers += ["requirements invalid : " + x for x in pb]
        vp = _subject_version_problem(requirements.get("subject"))
        if vp: blockers.append(vp); questions.append("Which version of the subject should be reproduced ?")
        rt = (requirements.get("routing") or {}).get("construction_type")
        if rt in scores: scores[rt] += 5.0; source = "structured_requirements"; ev.append("structured requirements declare construction_type=%s (operator input, takes precedence)" % rt)
    order = sorted(scores, key=lambda k: -scores[k]); top, second = order[0], order[1]; margin = scores[top] - scores[second]
    if scores[top] < 1.0 or margin < 0.8: ctype = "undetermined"; blockers.append("construction type undetermined (scores %s)" % {k: round(v, 2) for k, v in scores.items()}); questions.append("Is this a map, a sculpture, a reconstruction from photos or a 2D mosaic ?")
    else: ctype = top
    gen = ROUTES.get(ctype, "none")
    if ctype in ROUTES and not IMPLEMENTED[gen]: blockers.append("generator '%s' is not implemented in this version" % gen)
    if ctype == "map_relief_25d" and requirements and not (requirements.get("reference") or {}).get("map_rect_px"): questions.append("Where is the map inside the picture (map_rect_px) ?")
    steps = []
    if ctype == "map_relief_25d": steps = ["validate requirements", "semantic preparation of the reference (semantic_map)", "write composition + style (data only)", "maps generator (unchanged engine)", "independent validation + fragility", "renders + comparison with the reference"]
    elif ctype == "sculpture_3d": steps = ["GLB check", "engine 1 (known subject or generic configuration)", "validation", "notice"]
    elif ctype == "photos_3d": steps = ["identify the 4 views", "reconstruction (HF Space)", "colour projection + GLB check", "engine 1", "validation"]
    elif ctype == "mosaic_2d": steps = ["(not implemented) palette quantisation to plates/tiles"]
    status = "ready" if (ctype != "undetermined" and not blockers) else "needs_input"
    return dict(status=status, construction_type=ctype, generator=gen, decided_by=source, confidence=round(min(0.99, 0.5 + 0.1 * margin), 2), scores={k: round(v, 2) for k, v in scores.items()}, evidence=ev, blockers=blockers, questions=questions, steps=steps,
                subject=(requirements or {}).get("subject", {}).get("name"), subject_version=((requirements or {}).get("subject", {}).get("version") or {}).get("selected"), source_analysis=analyses[:1])
