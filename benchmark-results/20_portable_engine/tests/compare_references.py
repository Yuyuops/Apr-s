"""Compare a regenerated model with a historical reference : sha256 of the file, then multiset of part lines (reference, colour, position, matrix), then the grid intermediates.
usage: compare_references.py <subject paco|beagle> <run folder> <out.json>     exit code 0 = identical, 1 = differences (listed and measured, never hidden)"""
import hashlib, json, os, sys
from collections import Counter
import numpy as np
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
REF = {"paco": dict(brut="18_ear_assembly_final/modeles/paco_V91_brut.ldr", notice="18_ear_assembly_final/modeles/paco_V91_notice.ldr", grid="20_portable_engine/refs/intermediates/paco/paco_full400.npz", name="paco"),
       "beagle": dict(brut="19_full_second_subject/modeles/beagle_V10_brut.ldr", notice="19_full_second_subject/modeles/beagle_V10_notice.ldr", grid="20_portable_engine/refs/intermediates/beagle/beagle_full400.npz", name="beagle")}
def parts(p):
    c = Counter()
    for l in open(p, errors="replace"):
        t = l.split()
        if t and t[0] == "1" and len(t) >= 15: c[(t[14].lower(), int(t[1]), tuple(round(float(x), 3) for x in t[2:5]), tuple(round(float(x), 4) for x in t[5:14]))] += 1
    return c
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def main():
    subj, run, outf = sys.argv[1:4]; R = REF[subj]; res = {}
    # intermediates
    a = np.load(os.path.join(run, "grid", "full400.npz")); b = np.load(os.path.join(ROOT, R["grid"]))
    res["grille"] = {k: bool(np.array_equal(a[k], b[k])) if a[k].shape == b[k].shape else False for k in ("grid", "surface", "fine")}
    for kind in ("brut", "notice"):
        new = os.path.join(run, "final", "%s_%s.ldr" % (R["name"], kind)); old = os.path.join(ROOT, R[kind])
        if not os.path.exists(new): res[kind] = "absent"; continue
        pn, po = parts(new), parts(old); only_new, only_old = pn - po, po - pn
        d = dict(sha256_identique=sha(new) == sha(old), pieces_nouveau=sum(pn.values()), pieces_reference=sum(po.values()), pieces_en_plus=sum(only_new.values()), pieces_en_moins=sum(only_old.values()),
                 identique_pieces=(not only_new and not only_old))
        d["types_en_plus"] = dict(Counter(k[0] for k in only_new.elements()).most_common(8)); d["types_en_moins"] = dict(Counter(k[0] for k in only_old.elements()).most_common(8))
        d["couleurs_en_plus"] = dict(Counter(k[1] for k in only_new.elements()).most_common(6)); d["couleurs_en_moins"] = dict(Counter(k[1] for k in only_old.elements()).most_common(6))
        res[kind] = d
    ok = all(res["grille"].values()) and all(isinstance(res[k], dict) and res[k]["identique_pieces"] for k in ("brut", "notice") if k in res)
    res["identique"] = ok; json.dump(res, open(outf, "w"), indent=1); print(json.dumps(res, indent=1)); sys.exit(0 if ok else 1)
main()
