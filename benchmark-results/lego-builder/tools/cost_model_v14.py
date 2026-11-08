#!/usr/bin/env python3
"""Sprint V14 : business cost model on top of benchmark_v14.py results. EVERY parameter in ASSUMPTIONS is either a vendor/retailer figure (tagged 'verified 2026-11-08' with its source) or an explicit ASSUMPTION to be replaced by a measurement. Nothing here is a measured print on a real machine.
usage : cost_model_v14.py BENCH.json OUT.json"""
import json, math, sys, collections
B = json.load(open(sys.argv[1]))
MERGED = {}
if len(sys.argv) > 3:
    for r in json.load(open(sys.argv[3])):
        if r.get("seconds") is not None: MERGED[(r["tag"], r["supports"])] = r
A = dict(
  vat=1.20, electricity_eur_kwh=0.25, avg_power_w=150, filament_eur_kg_ht=18.0, human_eur_h=25.0, machine_life_h=4000, maintenance_eur_h=0.05, duty_h_month=500, reprint_factor=1.10,
  plate_handling_min=4, spool_swap_min=3, brick_assembly_s=6, piece_assembly_s=40, module_assembly_min=15, support_removal_min_per_module=10,
  machines=dict(
    A1=dict(name="Bambu Lab A1 Combo (AMS Lite)", price_ttc=469.95, price_src="LDLC fiche PB00728850, en stock 2026-11-08", slots=4, extra_slot_unit_ttc=None, change_s=(30, 45, 90), purge_g=(0.3, 0.8, 1.5), bed="256x256x256"),
    Hi=dict(name="Creality Hi Combo (CFS)", price_ttc=474.90, price_src="PcComponentes 2026 (promos 359-370 non verifiees)", slots=4, extra_slot_unit_ttc=120.0, change_s=(30, 45, 90), purge_g=(0.3, 0.8, 1.5), bed="260x260x300"),
    U1=dict(name="Snapmaker U1 (4 toolheads)", price_ttc=699.0, price_src="eu.snapmaker.com 2026-11-08 (page 'Unavailable / Notify me')", slots=4, extra_slot_unit_ttc=None, change_s=(5, 5, 10), purge_g=(0.045, 0.12, 0.225), bed="270x270x270")))
SCEN = {"bas": 0, "median": 1, "haut": 2}
def hms(s): return round(s / 3600, 1)
def agg(model, kind, prof, sup):
    return [r for r in B["slices"] if r["model"] == model and r["kind"] == kind and r["profile"] == prof and r["supports"] == sup and r.get("seconds") is not None]
def plates_sum(model, kind, prof, sup):
    """totals over ALL plates. Bricks : only every 4th plate was sliced (A1) and every 8th for Hi/U1 : totals = mean of the sampled plates x number of plates (declared sampling, plates are near-full beds). Mono plates : all A1, sample for Hi/U1 (ratio)."""
    L = agg(model, kind, prof, sup); nplates = B["models"][model]["bricks"]["plates"] if kind == "bricks1" else (B["models"][model]["mono"]["plates"] if kind == "mono3" else len(L))
    if kind == "mod2": return dict(n=len(L), seconds=sum(r["seconds"] for r in L), g=sum(r["filament_g"] for r in L), warn=sum(1 for r in L if r["warn"]))
    if kind == "bricks1":
        A1 = agg(model, kind, "A1", sup); tot_s = sum(r["seconds"] for r in A1) / max(1, len(A1)) * nplates; tot_g = sum(r["filament_g"] for r in A1) / max(1, len(A1)) * nplates; ratio = 1.0
        if prof != "A1":
            tags = {r["tag"] for r in L}; a1c = [r for r in A1 if r["tag"] in tags]; ratio = sum(r["seconds"] for r in L) / max(1, sum(r["seconds"] for r in a1c))
        return dict(n=nplates, seconds=tot_s * ratio, g=tot_g, warn=sum(1 for r in A1 if r["warn"]), sampled=len(A1))
    if prof == "A1": return dict(n=len(L), seconds=sum(r["seconds"] for r in L), g=sum(r["filament_g"] for r in L), warn=sum(1 for r in L if r["warn"]))
    full = agg(model, kind, "A1", sup); tags = {r["tag"] for r in L}; a1s = [r for r in full if r["tag"] in tags]
    ratio = sum(r["seconds"] for r in L) / max(1, sum(r["seconds"] for r in a1s))
    return dict(n=len(full), seconds=sum(r["seconds"] for r in full) * ratio, g=sum(r["filament_g"] for r in full), warn=sum(1 for r in full if r["warn"]), sampled=len(L))
VOL = json.load(open("/tmp/v14/mono_vol.json"))
CRASH = collections.defaultdict(list)
for model in B["models"]:
    for sup in (False, True):
        ok = {r["tag"]: r for r in B["slices"] if r["model"] == model and r["kind"] == "mono3" and r["profile"] == "A1" and r["supports"] == sup and r.get("seconds") is not None}
        vols = {("%s_%s" % (model, k.split("|")[0])): v for k, v in VOL.items() if k.split("|")[1] == model}
        sv = sum(r["seconds"] for r in ok.values()) / sum(vols[t] for t in ok); gv = sum(r["filament_g"] for r in ok.values()) / sum(vols[t] for t in ok)
        for t, v in vols.items():
            if t not in ok:
                CRASH[model].append(t); B["slices"].append(dict(tag=t, profile="A1", supports=sup, kind="mono3", model=model, file=t, seconds=sv * v, filament_g=gv * v, layers=None, support_lines=None, warn=["ESTIMATED : PrusaSlicer crashed (segfault) on this plate, scaled from volume"], estimated=True))
out = {"assumptions": A, "crashed_plates_estimated": CRASH, "products": {}}
for model in ("paco", "hyrule"):
    M = B["models"][model]; ml = M["modules"]["module_list"]; res = {}
    for mk, mc in A["machines"].items():
        for sc, si in SCEN.items():
            ch_s, purge = mc["change_s"][si], mc["purge_g"][si]; price_ht = mc["price_ttc"] / A["vat"]; row = {}
            def finish(proc, hours, filament_g, purge_g, support_g, human_h, extra_capex_ht=0.0, note=""):
                mass = filament_g + purge_g; mat = mass / 1000 * A["filament_eur_kg_ht"] * A["reprint_factor"]; elec = hours * A["avg_power_w"] / 1000 * A["electricity_eur_kwh"] * A["reprint_factor"]
                human = human_h * A["human_eur_h"]; amort = hours * A["reprint_factor"] * (price_ht / A["machine_life_h"] + A["maintenance_eur_h"]) + extra_capex_ht / A["machine_life_h"] * hours * A["reprint_factor"]
                return dict(hours=round(hours, 1), filament_useful_g=round(filament_g - support_g, 1), support_g=round(support_g, 1), purge_g=round(purge_g, 1), material_eur=round(mat, 1), electricity_eur=round(elec, 1), human_h=round(human_h, 1), human_eur=round(human, 1),
                            amortisation_eur=round(amort, 1), full_cost_eur=round(mat + elec + human + amort, 1), note=note)
            # ---- process 1 bricks
            s = plates_sum(model, "bricks1", mk, False); ncol = M["bricks"]["colours"]; nb = M["bricks"]["supported"]
            human1 = s["n"] * A["plate_handling_min"] / 60 + ncol * A["spool_swap_min"] / 60 + nb * A["brick_assembly_s"] / 3600
            r1 = finish("bricks", s["seconds"] / 3600, s["g"], 0, 0, human1, note="%d plates, %d colours (manual spool swaps), %d printable bricks to assemble ; %d parts not printable (not rectangular)" % (s["n"], ncol, nb, M["bricks"]["parts"] - nb)); r1.update(feasible=True, plates=s["n"], colour_changes_in_print=0)
            row["1_briques"] = r1
            # ---- process 2 multicolour modules
            feas = []; hrs = g = sup_g = purge_g = 0.0; changes = 0; loads = 0; plates = 0; infeasible = 0
            for info in ml:
                key = "%s_%s" % (model, info["file"].replace(".3mf", ""))
                su = next((r for r in agg(model, "mod2", "A1", True) if r["tag"] == key), None); ns = next((r for r in agg(model, "mod2", mk, False) if r["tag"] == key), None)
                if not su or not ns: continue
                msu, mns = MERGED.get((key + "_merged", True)), MERGED.get((key + "_merged", False))
                if msu and mns: su = dict(seconds=msu["seconds"], filament_g=msu["filament_g"], nosup_g=mns["filament_g"], nosup_s=mns["seconds"])
                slots = mc["slots"]; need_slots = info["max_colours_in_layer"]
                if mk == "Hi": slots = 16
                ok = need_slots <= slots
                if not ok: infeasible += 1
                mod_loads = 0 if slots == 16 else (info["spool_loads_4slots"] or 0)
                base_hours = (su["seconds"] if su else ns["seconds"]) / 3600                                    # with supports (safe), A1 profile ; time scaled by the no-support ratio of this machine
                a1ns = next(r for r in agg(model, "mod2", "A1", False) if r["tag"] == key); ratio = ns["seconds"] / a1ns["seconds"]
                hrs += base_hours * ratio + info["colour_changes"] * ch_s / 3600; g += su["filament_g"]; sup_g += su["filament_g"] - (su["nosup_g"] if "nosup_g" in su else a1ns["filament_g"])
                purge_g += info["colour_changes"] * purge; changes += info["colour_changes"]; loads += mod_loads; plates += 1
            loads += (M["mono"]["colours"] if mk == "Hi" else 0)
            h2 = plates * (A["plate_handling_min"] + A["module_assembly_min"] + A["support_removal_min_per_module"]) / 60 + loads * A["spool_swap_min"] / 60
            extra = 0.0
            if mk == "Hi": extra = 3 * (mc["extra_slot_unit_ttc"] / A["vat"])
            r2 = finish("modules", hrs, g, purge_g, sup_g, h2, extra, note="%d modules, %d colour changes, %d manual spool loads, %d/%d modules exceed the colours-per-layer limit of %d slots (INFEASIBLE as such)" % (plates, changes, loads, infeasible, plates, mc["slots"] if mk != "Hi" else 16))
            r2.update(feasible=(infeasible == 0), plates=plates, colour_changes_in_print=changes, infeasible_modules=infeasible, extra_capex_ht=round(extra, 1)); row["2_modules_multicolores"] = r2
            # ---- process 3 monochrome pieces
            s3 = plates_sum(model, "mono3", mk, False); s3s = plates_sum(model, "mono3", "A1", True); s3n = plates_sum(model, "mono3", "A1", False)
            sup3 = max(0.0, s3s["g"] - s3n["g"]); hours3 = (s3s["seconds"] * (s3["seconds"] / s3n["seconds"] if s3n["seconds"] else 1)) / 3600; g3 = s3s["g"]; pieces = M["mono"]["pieces"]
            h3 = s3["n"] * A["plate_handling_min"] / 60 + M["mono"]["colours"] * A["spool_swap_min"] / 60 + pieces * A["piece_assembly_s"] / 3600 + len(ml) * (A["module_assembly_min"] + A["support_removal_min_per_module"]) / 60
            r3 = finish("mono", hours3, g3, 0, sup3, h3, note="%d plates, %d monochrome pieces to glue/assemble, %d colours" % (s3["n"], pieces, M["mono"]["colours"])); r3.update(feasible=True, plates=s3["n"], colour_changes_in_print=0, pieces=pieces); row["3_modules_monochromes"] = r3
            res.setdefault(mk, {})[sc] = row
    out["products"][model] = res
json.dump(out, open(sys.argv[2], "w"), indent=1); print("ok")
