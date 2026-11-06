"""Generator 1 : maps and 2.5D reliefs (LEGO Maps V1.0). Coast/sea mode (real geodata composition) and biomes/relief mode (class raster) are two variants of the same generator : build_style.py."""
import json, os
from pathlib import Path
from .. import core
from ..paths import MAPS, PY
def build(out, style, composition, log=None, pdf=False, render=True, views=None, title_zone_h=None):
    out = Path(out); out.mkdir(parents=True, exist_ok=True); log = log or out / "build.log"
    core.run([PY, MAPS / "build_style.py", style, composition, out, "--flank", "vertical"], cwd=MAPS, log=log)
    for s in ("check_render.py", "verify_bom.py", "fragility.py", "notice_steps.py"):
        a = [PY, MAPS / s, out] + (["--no-render"] if s == "check_render.py" else []); core.run(a, cwd=MAPS, log=log)
    m = json.load(open(out / "metrics.json")); R, C = m["grid_studs"]; H = m["height_plates"] + 4
    v = views or {"face": dict(box=[0, 0, R + 8, C + 8], h=H, az=0, el=89, w=1100, hpx=int(1100 * (R + 8) / (C + 8)) + 40, zoom=0.92), "trois_quarts": dict(box=[0, 0, R + 8, C + 8], h=H, az=20, el=38, w=1300, hpx=950, zoom=0.8)}
    json.dump(v, open(out / "views.json", "w"))
    if render: core.run([PY, MAPS / "render_views.py", out, out / "views.json"], cwd=MAPS, log=log)
    if pdf: core.run([PY, MAPS / "make_step_pdf.py", out, out / "notice_pas_a_pas.pdf"], cwd=MAPS, log=log)
    r = core.run([PY, MAPS / "check_delivery.py", out], cwd=MAPS, log=log, check=False)
    chk = json.load(open(out / "delivery_check.json")); f = json.load(open(out / "fragility.json"))
    return dict(pieces=m["pieces"], references=m["references"], size_mm=m["physical_size_mm"], max_height_mm=m["max_height_mm"], delivery_check=chk,
                fragility={k: f[k] for k in ("parts_hanging_by_one_stud", "one_stud_and_carrying", "articulation_points_with_loss", "worst_single_failure")}, ldraw="diorama.ldr", bom="parts_list.csv")
