"""V8 non-regression: compare the replayed V6 / V6.1 outputs with the archived references (git, read only).

Compared per case: LDraw models (multiset of part lines: colour, part, position rounded to 0.01 LDU, matrix rounded to
1e-4), generator report (every value, recursively), validator results (collisions, connections, islands, steps,
sideways joints, stability, fidelity, catalogue: full recursive diff), bill of materials (part, colour, quantity).
usage: compare_nonreg.py <nonreg dir> <benchmark-results dir>
"""
import csv, json, os, sys
from collections import Counter

def ldr_lines(path):
    out = Counter()
    for l in open(path):
        t = l.split()
        if not t or t[0] != "1": continue
        pos = tuple(round(float(v), 2) + 0.0 for v in t[2:5]); mat = tuple(round(float(v), 4) + 0.0 for v in t[5:14])
        out[(t[1], t[14].lower(), pos, mat)] += 1
    return out

def walk_diff(a, b, path="", out=None, ignore=("source_ldr", "name", "disclaimer", "out", "outdir", "path")):
    if out is None: out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in ignore: continue
            if k not in a or k not in b: out.append((path + "/" + str(k), a.get(k, "<absent>"), b.get(k, "<absent>"))); continue
            walk_diff(a[k], b[k], path + "/" + str(k), out, ignore)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b): out.append((path + "[len]", len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)): walk_diff(x, y, f"{path}[{i}]", out, ignore)
    elif isinstance(a, float) or isinstance(b, float):
        try:
            if abs(float(a) - float(b)) > 1e-6: out.append((path, a, b))
        except (TypeError, ValueError): out.append((path, a, b))
    elif isinstance(a, str) and isinstance(b, str) and (os.sep in a or os.sep in b):
        if os.path.basename(a) != os.path.basename(b): out.append((path, a, b))
    elif a != b: out.append((path, a, b))
    return out

def bom_from_catalogue(path):
    c = Counter()
    for r in csv.DictReader(open(path)): c[(r["part"], r.get("colour") or r.get("ldraw_colour"))] += int(r["qty"])
    return c

def main():
    N, REF = sys.argv[1], sys.argv[2]
    R11 = os.path.join(REF, "11_automatic_contour_proof", "exemples"); R12 = os.path.join(REF, "12_automatic_curves")
    cases = [
        ("V6 A Paco", "V6_A", [("oreille_A_paco.ldr", f"{R11}/A_paco/oreille_A_paco.ldr"), ("tete_oreille_A_paco.ldr", f"{R11}/A_paco/tete_C_avec_oreille_generee.ldr")],
         ("oreille_A_paco_report.json", f"{R11}/A_paco/oreille_A_paco_report.json"), [("val_validation_v2.json", f"{R11}/A_paco/validation.json")],
         ("val_catalogue.csv", f"{R11}/A_paco/nomenclature_modele_complet.csv")),
        ("V6 B Beagle", "V6_B", [("oreille_B_beagle.ldr", f"{R11}/B_beagle/oreille_B_beagle.ldr")],
         ("oreille_B_beagle_report.json", f"{R11}/B_beagle/oreille_B_beagle_report.json"), [("val_validation_v2.json", f"{R11}/B_beagle/validation.json")],
         ("val_catalogue.csv", f"{R11}/B_beagle/nomenclature.csv")),
        ("V6.1 A Paco", "V61_A", [("oreille_A_paco.ldr", f"{R12}/A_paco/oreille_A_paco.ldr"), ("tete_oreille_A_paco.ldr", f"{R12}/A_paco/tete_C_avec_oreille_V61.ldr")],
         ("oreille_A_paco_report.json", f"{R12}/A_paco/oreille_A_paco_report.json"),
         [("val3_validation_v2.json", f"{R12}/A_paco/validation_v3.json"), ("val2_validation_v2.json", f"{R12}/A_paco/validation_v2.json")],
         ("val3_catalogue.csv", f"{R12}/A_paco/nomenclature_modele.csv")),
        ("V6.1 B Beagle", "V61_B", [("oreille_B_beagle.ldr", f"{R12}/B_beagle/oreille_B_beagle.ldr"), ("notice.ldr", f"{R12}/B_beagle/oreille_B_beagle_V61_notice.ldr")],
         ("oreille_B_beagle_report.json", f"{R12}/B_beagle/oreille_B_beagle_report.json"),
         [("val3_validation_v2.json", f"{R12}/B_beagle/validation_v3.json"), ("val2_validation_v2.json", f"{R12}/B_beagle/validation_v2.json")],
         ("val3_catalogue.csv", f"{R12}/B_beagle/nomenclature_modele.csv")),
    ]
    res = {}
    for title, d, ldrs, rep, vals, bom in cases:
        r = dict(modeles={}, rapport=None, validations={}, nomenclature=None)
        for new, ref in ldrs:
            a, b = ldr_lines(os.path.join(N, d, new)), ldr_lines(ref)
            r["modeles"][os.path.basename(ref)] = dict(pieces_rejouees=sum(a.values()), pieces_reference=sum(b.values()),
                                                       lignes_absentes=sum((b - a).values()), lignes_en_plus=sum((a - b).values()), identique=(a == b))
        a, b = json.load(open(os.path.join(N, d, rep[0]))), json.load(open(rep[1]))
        df = walk_diff(a, b); r["rapport"] = dict(differences=len(df), exemples=[list(map(str, x)) for x in df[:12]])
        for new, ref in vals:
            a, b = json.load(open(os.path.join(N, d, new))), json.load(open(ref))
            df = walk_diff(a, b)
            keys = ("parts", "collisions", "disconnected_parts", "islands", "steps", "sideways_joints", "unsupported_at_placement", "blocked_studs")
            r["validations"][os.path.basename(ref)] = dict(differences=len(df), exemples=[list(map(str, x)) for x in df[:12]],
                                                          cles={k: [json.dumps(a.get(k))[:80], json.dumps(b.get(k))[:80]] for k in keys})
        a, b = bom_from_catalogue(os.path.join(N, d, bom[0])), bom_from_catalogue(bom[1])
        r["nomenclature"] = dict(identique=(a == b), lignes_rejouees=len(a), lignes_reference=len(b), ecarts=[str(k) for k in set(a) ^ set(b)][:10] + [f"{k}: {a[k]} vs {b[k]}" for k in set(a) & set(b) if a[k] != b[k]][:10])
        res[title] = r
    ok = all(all(m["identique"] for m in r["modeles"].values()) and r["rapport"]["differences"] == 0 and all(v["differences"] == 0 for v in r["validations"].values()) and r["nomenclature"]["identique"] for r in res.values())
    json.dump(dict(verdict="AUCUNE DIFFERENCE" if ok else "DIFFERENCES (voir le detail)", cas=res), open(os.path.join(N, "nonreg.json"), "w"), indent=1, ensure_ascii=False)
    for t, r in res.items():
        print(t, {k: (v["identique"], v["pieces_rejouees"], v["pieces_reference"]) for k, v in r["modeles"].items()}, "rapport diff", r["rapport"]["differences"],
              {k: v["differences"] for k, v in r["validations"].items()}, "BOM", r["nomenclature"]["identique"])
    print("VERDICT", "AUCUNE DIFFERENCE" if ok else "DIFFERENCES")

if __name__ == "__main__":
    main()
