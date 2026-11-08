"""PrusaSlicer proxy-profile runner shared by the V14 tools (see benchmark_v14.py)."""
import re, subprocess
from pathlib import Path
import os
W = Path(os.environ.get("V14_WORK", "/tmp/v14/work"))
PROFILES = {"A1": dict(accel=10000, flow=21), "Hi": dict(accel=12000, flow=21), "U1": dict(accel=20000, flow=21)}
def slice_(f, tag, prof, supports=False, extra=()):
    d = W / "slices"; d.mkdir(exist_ok=True); g = d / ("%s.%s.%s.gcode" % (tag, prof, "sup" if supports else "nosup")); P = PROFILES[prof]
    cmd = ["prusa-slicer", "--bed-shape", "0x0,256x0,256x256,0x256", "--layer-height", "0.2", "--first-layer-height", "0.2", "--nozzle-diameter", "0.4", "--filament-diameter", "1.75", "--temperature", "215", "--bed-temperature", "60",
           "--filament-density", "1.24", "--perimeters", "3", "--top-solid-layers", "5", "--bottom-solid-layers", "4", "--fill-density", "15%", "--max-print-height", "256", "--dont-arrange",
           "--max-volumetric-speed", str(P["flow"]), "--perimeter-speed", "200", "--external-perimeter-speed", "120", "--infill-speed", "250", "--solid-infill-speed", "200", "--top-solid-infill-speed", "120", "--travel-speed", "400", "--first-layer-speed", "50",
           "--default-acceleration", str(P["accel"]), "--perimeter-acceleration", str(P["accel"] // 2), "--infill-acceleration", str(P["accel"]), "--external-perimeter-acceleration", str(P["accel"] // 2), "--travel-acceleration", str(P["accel"]),
           "--machine-max-acceleration-extruding", str(P["accel"]), "--machine-max-acceleration-x", str(P["accel"]), "--machine-max-acceleration-y", str(P["accel"]), "--machine-max-feedrate-x", "500", "--machine-max-feedrate-y", "500"]
    if supports: cmd += ["--support-material", "--support-material-auto", "--support-material-threshold", "45"]
    cmd += list(extra) + ["-g", "-o", str(g), str(f)]; p = subprocess.run(cmd, capture_output=True, text=True); txt = p.stdout + p.stderr
    r = dict(tag=tag, profile=prof, supports=supports, rc=p.returncode, warn=sorted({l.strip() for l in txt.splitlines() if re.search(r"stabil|Floating|Long bridging|conflict", l)})[:3])
    if g.exists():
        t = g.read_text(errors="replace")
        def grab(rx): m = re.findall(rx, t); return m[-1] if m else None
        tm = grab(r"estimated printing time \(normal mode\) = ([^\n]+)"); s = 0
        for q, u in re.findall(r"(\d+)([dhms])", tm or ""): s += int(q) * dict(d=86400, h=3600, m=60, s=1)[u]
        r.update(seconds=s, filament_g=float(grab(r"filament used \[g\] = ([\d.]+)") or 0), layers=len(re.findall(r"^;LAYER_CHANGE", t, re.M)), support_lines=len(re.findall(r"^;TYPE:Support material", t, re.M))); g.unlink()
    return r
