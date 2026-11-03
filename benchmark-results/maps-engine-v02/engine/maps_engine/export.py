import csv, json, os
from collections import Counter
import numpy as np
from PIL import Image
from . import palette as PAL
from .common import rb_colours
from _paths import LDRAW

def part_name(num):
    try: return open(os.path.join(LDRAW, "parts", num + ".dat"), errors="replace").readline().strip().lstrip("0").strip()
    except Exception: return ""

def write_bom(model, path):
    """parts_list.csv : reference, colour, quantity per section. Price and stock are EMPTY (null) : nothing verified at Briquestore (validation/briquestore_check.json)."""
    rb = rb_colours(); c = Counter((p["part"], p["colour"], {"B": "dos", "L": "relief", "F": "cadre"}[p["layer"][0]]) for p in model["parts"])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["part_num", "part_name", "colour_id", "colour_name", "rgb_hex", "section", "quantity", "rebrickable_sets_count", "price_eur", "stock", "verified_at", "supplier_source"])
        for (num, col, sec), q in sorted(c.items(), key=lambda kv: ({"dos": 0, "relief": 1, "cadre": 2}[kv[0][2]], -kv[1], kv[0])):
            w.writerow([num, part_name(num), col, rb[col]["name"], "%02X%02X%02X" % rb[col]["rgb"], sec, q, PAL.sets(num, col), "", "", "", "Briquestore: non verifie (null)"])
    return c

def write_all(cg, model, out):
    os.makedirs(out, exist_ok=True)
    json.dump(dict(classes=cg["classes"], grid=cg["grid"].tolist(), heights=model["heights"].tolist(), source_colours={k: [round(float(x), 1) for x in v] for k, v in cg["colour"].items()}, lego_colours=model["colours"], frame_colour=model["frame_colour"],
                   candidates=model["ncand"], objective=model["objective"], finish=model["finish"], mode=model["mode"], smooth_classes=model["smooth"], n=model["n"], frame_width=model["m"]), open(os.path.join(out, "classes_hauteurs.json"), "w"), indent=1)
    json.dump(model["parts"], open(os.path.join(out, "parts.json"), "w"))
    Image.fromarray(np.kron(np.array([[cg["colour"][cg["classes"][v]] for v in row] for row in cg["grid"]], np.uint8), np.ones((8, 8, 1), np.uint8))).save(os.path.join(out, "classes_couleurs_source.png"))
    return write_bom(model, os.path.join(out, "parts_list.csv"))
