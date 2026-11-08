#!/usr/bin/env python3
"""B3 (Sprint V13) : independent slicing check with PrusaSlicer CLI (apt prusa-slicer 2.7.2). THIS IS NOT BAMBU STUDIO and does not validate Bambu Studio / any Bambu printer : it only shows that a second,
independent slicer imports the file, finds the dimensions, slices it and gives time / mass / support estimates with generic PLA settings (0.4 mm nozzle, 0.2 mm layers, 3 perimeters, 15 % gyroid-free default infill).
usage : slice_check.py FILE.3mf|stl OUT_DIR [--supports] [--bed 256]"""
import json, re, subprocess, sys
from pathlib import Path
def run(f, out, supports=False, bed=256):
    out = Path(out); out.mkdir(parents=True, exist_ok=True); g = out / (Path(f).stem + (".sup" if supports else "") + ".gcode")
    cmd = ["prusa-slicer", "--bed-shape", "0x0,%dx0,%dx%d,0x%d" % (bed, bed, bed, bed), "--layer-height", "0.2", "--first-layer-height", "0.2", "--nozzle-diameter", "0.4", "--filament-diameter", "1.75", "--temperature", "215",
           "--bed-temperature", "60", "--filament-density", "1.24", "--perimeters", "3", "--top-solid-layers", "5", "--bottom-solid-layers", "4", "--fill-density", "15%", "--max-print-height", "256", "--dont-arrange"]
    if supports: cmd += ["--support-material", "--support-material-auto", "--support-material-threshold", "45"]
    cmd += ["-g", "-o", str(g), str(f)]; p = subprocess.run(cmd, capture_output=True, text=True); txt = (p.stdout + p.stderr)
    res = dict(file=str(f), supports=supports, returncode=p.returncode, slicer="PrusaSlicer (apt 2.7.2) - NOT Bambu Studio", warnings=[l.strip() for l in txt.splitlines() if re.search(r"warn|error|fail|outside|too|stabil|unsupported|floating", l, re.I)][:10], log_tail=[l for l in txt.splitlines() if l.strip()][-6:])
    if g.exists():
        t = g.read_text(errors="replace"); tail = t
        def grab(rx, s=tail): m = re.findall(rx, s); return m[-1] if m else None
        res.update(est_time=grab(r"estimated printing time \(normal mode\) = ([^\n]+)"), filament_g=grab(r"filament used \[g\] = ([\d.]+)"), filament_mm=grab(r"filament used \[mm\] = ([\d.]+)"), filament_cm3=grab(r"filament used \[cm3\] = ([\d.]+)"),
                   layers=len(re.findall(r"^;LAYER_CHANGE", t, re.M)), max_z=max([float(x) for x in re.findall(r"^;Z:([\d.]+)", t, re.M)] or [0]), support_extrusion_lines=len(re.findall(r"^;TYPE:Support material", t, re.M)), gcode_bytes=len(t))
        g.unlink()                                                                       # g-code is bulky : only the numbers are kept
    json.dump(res, open(out / (Path(f).stem + (".sup" if supports else "") + ".slice.json"), "w"), indent=1); return res
if __name__ == "__main__":
    a = sys.argv[1:]; print(json.dumps(run(a[0], a[1], "--supports" in a, int(a[a.index("--bed") + 1]) if "--bed" in a else 256)))
