"""Mechanical comparison of several models of the same subject, same method (validate_v4 + weak_groups) for all (V12.1).
usage: mech_compare.py out.json label=model.ldr:validation.json:weak.json [label=...]"""
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import sys, json
from collections import Counter
def rows(spec):
    out = {}
    for s in spec:
        lab, rest = s.split("=", 1); ldr, val, weak = rest.split(":")
        v = json.load(open(val)); st = v["stability"]; w = json.load(open(weak))
        P = [l.split() for l in open(ldr) if l.startswith("1 ")]; types = Counter(t[14].lower().replace(".dat", "") for t in P); cols = Counter(t[1] for t in P)
        zones = Counter(); 
        for g in w["groupes"]: zones[(g["zone"][0][0] if g["zone"] else "?")] += g["cas_emboites"]
        out[lab] = dict(pieces=len(P), types_de_pieces=len(types), pieces_par_type=dict(types.most_common(8)), couleurs_lignes=len(cols), liaisons=v["joints"], tenons_engages=v["studs_engaged"],
                        liaisons_a_un_tenon=v["single_stud_joints"], collisions=v["collisions"].get("pairs"), pieces_deconnectees=v["disconnected_parts"], sans_appui_a_la_pose=v["unsupported_at_placement"],
                        cas=st["cases"], cas_sous_0_5N=st["tip_force_below_0_5N"], cas_sous_2N=st["tip_force_below_2N"], sf_gravite_min=st["min_gravity_sf"], force_bout_min_N=st["min_tip_force_N"],
                        groupes_faibles=w["cas_distincts"], cas_faibles_par_zone=dict(zones), groupes=[dict(parties=g["parties"], tenons=g["tenons"], force_N=g["force_N"], cas=g["cas_emboites"], couleurs=g["couleurs"], zone=g["zone"][:2], bbox_ldu=g["bbox_ldu"]) for g in w["groupes"]],
                        etapes_ldr=v["steps"])
    return out
if __name__ == "__main__":
    r = rows(sys.argv[2:]); json.dump(r, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
    for k, v in r.items(): print(k, {x: v[x] for x in ("pieces", "liaisons", "collisions", "pieces_deconnectees", "cas_sous_0_5N", "groupes_faibles", "sf_gravite_min", "force_bout_min_N", "etapes_ldr")})
