import os, re, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ldr_expand import Lib
lib = Lib(os.environ.get("LDRAW", os.path.expanduser("~/bench/ldraw-parts-library/complete/ldraw")))
def refs(name, M=np.eye(3), o=np.zeros(3), out=None, depth=0):
    out = [] if out is None else out
    p = lib.resolve(name)
    if p is None: return out
    for line in open(p, encoding="utf-8", errors="replace"):
        t = line.split()
        if len(t) >= 15 and t[0] == "1":
            sub = " ".join(t[14:]).replace("\\", "/").lower(); base = sub.split("/")[-1]
            o2 = np.array(t[2:5], float); M2 = np.array(t[5:14], float).reshape(3, 3)
            Mn = M @ M2; on = M @ o2 + o
            if re.match(r"^stud", base): out.append((base, on, Mn))
            elif depth < 6 and not re.match(r"^(\d-\d|rect|box|ring|disc|ndis|edge|cyl|con|chrd|tri|axl|peg|bump)", base.split("/")[-1]):
                refs(sub, Mn, on, out, depth + 1)
    return out
if __name__ == "__main__":
    for n in sys.argv[1:]:
        r = refs(n + ".dat")
        print(n, [(b, np.round(o, 1).tolist(), round(float(M[1, 1]), 2)) for b, o, M in r])
