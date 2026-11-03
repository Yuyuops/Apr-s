# Italia Gallery V0.4 — REAL LEGO engine pilot

Branch: `research/lego-maps-italie-v04-20261103`.

Aim: Test the next visible art-direction step **inside LEGO Maps V0.3**, not an AI illustration. Input coastlines are original Natural Earth public-domain Italy geometry, sourced from pinned commit `ca96624a56bd078437bca8184e78163e5039ad19`. Sicily and Sardinia remain geographic. Land and mountain colours/levels are **artistic**, not elevations from a digital elevation model.

New reproducible source: `art_direction.py` draws a decorative ITALIA plaque and compass on regions proven to be open sea. **Both ornaments are raster motifs** fed to the normal map classifier, not custom printed or physically verified decorative parts. They may be incorrectly segmented: the benchmark must evaluate this honestly. No manually composed AI render is accepted as a LEGO model.

Test two 64×64 stud maps (512×512 mm field, 544×544 mm including 2-stud frame) using `--finish A` and `--finish B`. Technical goal: determine whether raising resolution and adding ornaments improves aesthetics without unacceptable structural cost.

Generated assets: `art_source/italia_art_v04.png`, `outputs/A_64`, `outputs/B_64`, each with real `map.ldr`, `parts.json`, BOM, validation JSON, viewer, PNG render, notice PDF. No fabricated stock or price; no purchases.

**Stop criteria:** real source cannot be generated, imagery is unrecognisable, added motifs don't survive LEGO discretization, bad collisions/disconnections, or critical-support count materially deteriorates without justifiable aesthetics. Do not turn source-only decorations into claimed 3D monuments. Future work for monuments and real DEM requires separate modules and licensing checks.

No code changes to engine 1, no main merge, no model 1 regression changes.
