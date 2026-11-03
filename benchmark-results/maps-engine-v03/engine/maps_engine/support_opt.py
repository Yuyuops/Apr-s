"""LEGO Maps V0.3: bounded support-aware repacking of rectangular plates.

The occupied cells, artistic heights, LDraw colours, and exposed surface are
immutable. Only coplanar regular plates of the SAME colour and region can be
repartitioned into catalogue-valid rectangles. Special/wedge/round parts and
tiles are protected. This is a GRAPH heuristic, not physical strength testing.
"""
from collections import defaultdict
import math


def overlap(a, b):
    return max(0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])) * max(
        0, min(a["z"] + a["d"], b["z"] + b["d"]) - max(a["z"], b["z"])
    )


def support_report(parts):
    """Same direct-support criterion as V0.2 frag.py, independent implementation."""
    bytop = defaultdict(lambda: defaultdict(list))
    for p in parts:
        if p["kind"] != "tile":
            for x in range(p["x"], p["x"] + p["w"]):
                for z in range(p["z"], p["z"] + p["d"]):
                    bytop[p["zbot"] + p["h"]][(x, z)].append(p["id"])

    beneath = {p["id"]: 0 for p in parts}
    supports = {p["id"]: [] for p in parts}
    children = {p["id"]: [] for p in parts}
    for p in parts:
        local = set()
        for x in range(p["x"], p["x"] + p["w"]):
            for z in range(p["z"], p["z"] + p["d"]):
                for qid in bytop.get(p["zbot"], {}).get((x, z), []):
                    beneath[p["id"]] += 1
                    local.add(qid)
        for qid in sorted(local):
            supports[p["id"]].append(qid)
            children[qid].append(p["id"])
    weak = [p["id"] for p in parts if p["zbot"] > 0 and children[p["id"]] and beneath[p["id"]] < 4]
    critical = [pid for pid in weak if any(len(supports[c]) == 1 for c in children[pid])]
    return {
        "weak_carriers": len(weak), "critical_carriers": len(critical),
        "weak_ids": weak, "critical_ids": critical,
        "one_stud_carriers": sum(bool(p["zbot"] > 0 and children[p["id"]] and beneath[p["id"]] == 1) for p in parts),
        "support_studs": beneath, "supports": supports, "children": children
    }


def public_report(report):
    return {k: report[k] for k in (
        "weak_carriers", "critical_carriers", "one_stud_carriers", "weak_ids", "critical_ids"
    )}


def footprint(parts):
    return {(p["x"] + x, p["z"] + z) for p in parts
            for x in range(p["w"]) for z in range(p["d"])}


def neighbors(a, b):
    if a["x"] + a["w"] == b["x"] or b["x"] + b["w"] == a["x"]:
        return max(a["z"], b["z"]) < min(a["z"] + a["d"], b["z"] + b["d"])
    if a["z"] + a["d"] == b["z"] or b["z"] + b["d"] == a["z"]:
        return max(a["x"], b["x"]) < min(a["x"] + a["w"], b["x"] + b["w"])
    return False


def regular(p, catalog):
    size = (max(p["w"], p["d"]), min(p["w"], p["d"]))
    return (p["kind"] == "plate" and not p.get("wedge")
            and p.get("rot") is None and catalog.get(size) == p.get("part"))


def partitions(cells, catalog, colour, available, max_parts, max_results=96):
    """Exact-cover enumeration for small bounded, same-colour local regions."""
    sizes = []
    for (long, short), part in catalog.items():
        if not available(part, colour):
            continue
        for w, d in (((long, short), (short, long)) if long != short else ((long, short),)):
            if w * d <= len(cells):
                sizes.append((w * d, w, d, part))
    sizes.sort(reverse=True)
    results = []

    def search(rem, chosen):
        if len(results) >= max_results:
            return
        if not rem:
            results.append(chosen)
            return
        if len(chosen) >= max_parts:
            return
        cx, cz = min(rem)
        for _, w, d, part in sizes:
            for x in range(cx - w + 1, cx + 1):
                for z in range(cz - d + 1, cz + 1):
                    block = {(a, b) for a in range(x, x + w) for b in range(z, z + d)}
                    if block <= rem:
                        search(rem - block, chosen + [dict(x=x, z=z, w=w, d=d, part=part)])
                        if len(results) >= max_results:
                            return
    search(set(cells), [])
    return results


def score(report, count):
    # Critical supports dominate every cosmetic or piece-count optimisation.
    return (report["critical_carriers"], report["weak_carriers"], report["one_stud_carriers"], count)


def groups(parts, critical_ids, catalog, max_cells=32):
    byid = {p["id"]: p for p in parts}
    for pid in critical_ids:
        p = byid.get(pid)
        if p is None or not regular(p, catalog):
            continue
        peers = [q for q in parts if q["id"] != pid and q["kind"] == p["kind"]
                 and q["colour"] == p["colour"] and q["zbot"] == p["zbot"]
                 and q["h"] == p["h"] and q["layer"] == p["layer"]
                 and q["region"] == p["region"] and regular(q, catalog) and neighbors(p, q)]
        peers.sort(key=lambda q: (abs(p["x"] - q["x"]) + abs(p["z"] - q["z"]), q["id"]))
        for q in peers[:12]:
            if p["w"] * p["d"] + q["w"] * q["d"] <= max_cells:
                yield [p, q]
        seen = set()
        for q in peers[:9]:
            others = [s for s in parts if s["id"] not in (pid, q["id"])
                      and s["kind"] == p["kind"] and s["colour"] == p["colour"]
                      and s["zbot"] == p["zbot"] and s["h"] == p["h"]
                      and s["layer"] == p["layer"] and s["region"] == p["region"]
                      and regular(s, catalog) and (neighbors(s, p) or neighbors(s, q))]
            for s in sorted(others, key=lambda q: q["id"])[:12]:
                ids = tuple(sorted((pid, q["id"], s["id"])))
                if ids in seen:
                    continue
                seen.add(ids)
                if sum(t["w"] * t["d"] for t in (p, q, s)) <= max_cells:
                    yield [p, q, s]


def improve(parts, catalog, available, *, max_passes=3, max_cells=32,
            max_candidates_per_group=96, max_growth=0.15):
    """Bounded same-colour local exact cover, with immutable geometry and a log."""
    current = [dict(p) for p in parts]
    initial = support_report(current)
    initial_count = len(current)
    next_id = max((p["id"] for p in current), default=0) + 1
    operations = []
    for pass_index in range(max_passes):
        before = support_report(current)
        if not before["critical_ids"]:
            break
        best = None
        seen = set()
        for old in groups(current, before["critical_ids"], catalog, max_cells):
            ids = frozenset(p["id"] for p in old)
            if ids in seen:
                continue
            seen.add(ids)
            cells = footprint(old)
            if len(cells) != sum(p["w"] * p["d"] for p in old):
                continue
            template = old[0]
            for rects in partitions(cells, catalog, template["colour"], available,
                                    len(old) + 1, max_candidates_per_group):
                if len(current) - len(old) + len(rects) > math.floor(initial_count * (1 + max_growth)):
                    continue
                old_signature = sorted((p["x"], p["z"], p["w"], p["d"]) for p in old)
                new_signature = sorted((p["x"], p["z"], p["w"], p["d"]) for p in rects)
                if old_signature == new_signature:
                    continue
                replacement = []
                for i, rect in enumerate(rects):
                    p = dict(template)
                    p.update(rect)
                    p["id"] = next_id + i
                    p["size"] = "%dx%d" % (max(p["w"], p["d"]), min(p["w"], p["d"]))
                    replacement.append(p)
                candidate = [p for p in current if p["id"] not in ids] + replacement
                after = support_report(candidate)
                key = score(after, len(candidate))
                if key < score(before, len(current)) and (best is None or key < best[0]):
                    best = (key, candidate, old, replacement, after)
        if best is None:
            break
        _, current, old, replacement, after = best
        operations.append(dict(
            pass_index=pass_index + 1, old_ids=[p["id"] for p in old],
            new_ids=[p["id"] for p in replacement],
            old_rects=[(p["x"], p["z"], p["w"], p["d"]) for p in old],
            new_rects=[(p["x"], p["z"], p["w"], p["d"]) for p in replacement],
            critical_before=before["critical_carriers"], critical_after=after["critical_carriers"],
            weak_before=before["weak_carriers"], weak_after=after["weak_carriers"]
        ))
        next_id = max(p["id"] for p in current) + 1
    final = support_report(current)
    residual = []
    for p in current:
        if p["id"] not in final["critical_ids"]:
            continue
        if not regular(p, catalog):
            reason = "special piece / non-rectangular plate; protected"
        elif not any(q["id"] != p["id"] and q["colour"] == p["colour"]
                     and q["zbot"] == p["zbot"] and q["layer"] == p["layer"]
                     and q["region"] == p["region"] and regular(q, catalog)
                     and neighbors(p, q) for q in current):
            reason = "no adjacent same-colour regular plate; may need a design tradeoff"
        else:
            reason = "not solved by bounded exact-cover search; NOT a global impossibility proof"
        residual.append(dict(id=p["id"], region=p["region"], layer=p["layer"],
                             x=p["x"], z=p["z"], w=p["w"], d=p["d"], reason=reason))
    report = dict(version="v03-same-colour-local-exact-cover",
                  baseline=public_report(initial), final=public_report(final),
                  operations=operations, residual=residual,
                  parts_before=initial_count, parts_after=len(current),
                  footprint_preserved=True, physical_test=False,
                  criterion="indicative connectivity graph; no physical strength / wall test")
    return current, report
