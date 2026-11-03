import csv, json, os
from collections import Counter
import numpy as np
from PIL import Image
from . import palette as PAL
from .common import PLATES
import palette_util as PU
from _paths import LDRAW

def part_name(num):
    try: return open(os.path.join(LDRAW, "parts", num + ".dat"), errors="replace").readline().strip().lstrip("0").strip()
    except Exception: return ""

def write_bom(model, path):
    """parts_list.csv : reference, colour, quantity. Price and stock are NULL (empty) : nothing has been verified at Briquestore (see validation/briquestore_check.json)."""
    codes = PU.codes(); c = Counter((p["part"], p["colour"]) for p in model["parts"])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["part_num", "part_name", "colour_code", "colour_name", "quantity", "rebrickable_sets_count", "price_eur", "stock", "verified_at", "supplier_source"])
        for (num, col), q in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])):
            w.writerow([num, part_name(num), col, codes[col][0], q, PAL.sets(num, col), "", "", "", "Briquestore: non verifie (null)"])
    return c

def write_all(cg, model, out, name):
    os.makedirs(out, exist_ok=True)
    json.dump(dict(classes=cg["classes"], grid=cg["grid"].tolist(), heights=model["heights"].tolist(), source_colours={k: [round(float(x), 1) for x in v] for k, v in cg["colour"].items()},
                   lego_colours=model["colours"], backing_colour=model["backing_colour"], candidates=model["ncand"], mode=model["mode"]), open(os.path.join(out, "classes_hauteurs.json"), "w"), indent=1)
    json.dump([{k: (int(v) if isinstance(v, (np.integer,)) else v) for k, v in p.items()} for p in model["parts"]], open(os.path.join(out, "parts.json"), "w"))
    Image.fromarray(np.kron(np.array([[cg["colour"][cg["classes"][v]] for v in row] for row in cg["grid"]], np.uint8), np.ones((8, 8, 1), np.uint8))).save(os.path.join(out, "classes_32x32_couleurs_source.png"))
    return write_bom(model, os.path.join(out, "parts_list.csv"))
