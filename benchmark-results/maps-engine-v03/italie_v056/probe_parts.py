#!/usr/bin/env python3
"""Probe LDraw parts (read-only): title, body box in studs/plates, top studs, receptors (via engine-1 conn.py)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "20_portable_engine", "engine"))
import conn, partlib as PL
def info(n):
    p = conn.part(n); lo, hi = p["lo"], p["hi"]
    return dict(num=n, title=PL.title(n), dx=(hi[0]-lo[0])/20, dz=(hi[2]-lo[2])/20, dy=(hi[1]-lo[1])/8, lo=[round(float(v), 1) for v in lo], hi=[round(float(v), 1) for v in hi], studs=len(p["studs"]), recep=len(p["receptors"]), fill=round(float(p["fill"]), 2))
if __name__ == "__main__":
    for n in sys.argv[1:]:
        try:
            i = info(n); print("%-7s %-48s %4.1fx%4.1f h=%4.1fpl studs=%d rec=%d fill=%.2f lo=%s hi=%s" % (n, i["title"][:48], i["dx"], i["dz"], i["dy"], i["studs"], i["recep"], i["fill"], i["lo"], i["hi"]))
        except Exception as e: print(n, "ERR", repr(e)[:70])
