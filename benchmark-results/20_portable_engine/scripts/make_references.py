"""Fingerprint (sha256) the historical reference results, which stay where they are (never copied, never modified) : refs/references.json.
usage: python scripts/make_references.py   (from the portable engine folder)"""
import hashlib, json, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."); R = os.path.normpath(R)
REF = {
 "paco_V6_oreille": ["11_automatic_contour_proof/exemples/A_paco/oreille_A_paco.ldr", "11_automatic_contour_proof/exemples/A_paco/validation.json", "11_automatic_contour_proof/exemples/A_paco/nomenclature_oreille.csv"],
 "paco_V61_oreille": ["12_automatic_curves/A_paco/oreille_A_paco.ldr", "12_automatic_curves/A_paco/validation_v3.json", "12_automatic_curves/A_paco/nomenclature_oreille.csv"],
 "beagle_V6_oreille": ["11_automatic_contour_proof/exemples/B_beagle/oreille_B_beagle.ldr", "11_automatic_contour_proof/exemples/B_beagle/validation.json", "11_automatic_contour_proof/exemples/B_beagle/nomenclature_oreille.csv"],
 "beagle_V61_oreille": ["12_automatic_curves/B_beagle/oreille_B_beagle.ldr", "12_automatic_curves/B_beagle/validation_v3.json", "12_automatic_curves/B_beagle/nomenclature_oreille.csv"],
 "paco_V82": ["16_mouth_visibility_final/modeles/paco_V82_brut.ldr", "16_mouth_visibility_final/modeles/corps_seul_V82.ldr", "16_mouth_visibility_final/nomenclature_complete.csv"],
 "paco_V9": ["17_structural_and_instructions/modeles/paco_V9_brut.ldr", "17_structural_and_instructions/modeles/paco_V9_notice.ldr", "17_structural_and_instructions/nomenclature_complete.csv", "17_structural_and_instructions/validation/validation_v3_V9_notice.json"],
 "paco_V91": ["18_ear_assembly_final/modeles/paco_V91_brut.ldr", "18_ear_assembly_final/modeles/paco_V91_notice.ldr", "18_ear_assembly_final/nomenclature_complete.csv", "18_ear_assembly_final/validation/validation_v4_V91_notice.json", "18_ear_assembly_final/notice/plan_notice.json"],
 "beagle_V10": ["19_full_second_subject/modeles/beagle_V10_brut.ldr", "19_full_second_subject/modeles/beagle_V10_notice.ldr", "19_full_second_subject/modeles/beagle_avant_renforts.ldr", "19_full_second_subject/nomenclature_complete.csv", "19_full_second_subject/validation/final_validation_v2.json"],
 "sources_glb": ["02_glb_gratuit_hunyuan2mv/paco.glb", "02_glb_gratuit_hunyuan2mv/beagle.glb"],
 "intermediaires_archives": ["20_portable_engine/refs/intermediates/paco/paco_full400.npz", "20_portable_engine/refs/intermediates/paco/segmentation.npz", "20_portable_engine/refs/intermediates/paco/ears.pkl", "20_portable_engine/refs/intermediates/paco/details.json",
                             "20_portable_engine/refs/intermediates/beagle/beagle_full400.npz", "20_portable_engine/refs/intermediates/beagle/segmentation.npz", "20_portable_engine/refs/intermediates/beagle/details.json"]}
out = {}
for k, fs in REF.items():
    out[k] = {}
    for f in fs:
        p = os.path.join(R, f)
        if not os.path.exists(p): out[k][f] = None; continue
        out[k][f] = dict(sha256=hashlib.sha256(open(p, "rb").read()).hexdigest(), bytes=os.path.getsize(p), lines_parts=(sum(1 for l in open(p, errors="replace") if l.startswith("1 ")) if f.endswith(".ldr") else None))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "refs", "references.json"), "w"), indent=1)
print({k: sum(1 for v in d.values() if v) for k, d in out.items()}, "missing:", [f for d in out.values() for f, v in d.items() if v is None])
