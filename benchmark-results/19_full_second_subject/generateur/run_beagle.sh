#!/bin/bash
# LEGO V10 : Beagle complet, chaine du moteur 1 (V9.1) + corrections generiques documentees. Depuis ~/bench :  bash proto/v10/run_beagle.sh <dossier de sortie>
# Entrees : le GLB source du depot (benchmark-results/02_glb_gratuit_hunyuan2mv/beagle.glb), la palette de references du Beagle (--exclude, commande de 03_lego_brickify/beagle_regle400).
set -e
cd ~/bench; O=$1; mkdir -p $O; LD=ldraw-parts-library/complete/ldraw; export LEGO_SHAPE=30,126,58
V="venv/bin/python proto/v10/tools"
EX=4,1,14,2,25,19,28,71,72,272,288,320,321,322,26,27,191,226,212,78,85,30,73,10,3,323,378,379,330,43
cp runs/beagle_hf2mv_shape_blanc/beagle_couleur_tex_miroirX.glb $O/beagle_miroirX.glb     # = GLB source (sommets et couleurs identiques, verifie) encode en texture puis miroir X (tools/mirror_x.py)
venv/bin/python proto/v7/fullgrid.py $O/beagle_miroirX.glb $O/beagle_full400.npz --height-mm 400 --neck auto --exclude $EX | tail -1
venv/bin/python proto/v7/segment.py $O/beagle_full400.npz $O/segmentation.json $O/segmentation.npz > /dev/null
venv/bin/python proto/v7/ref_glb_fullframe.py $O/beagle_miroirX.glb /home/user/Apr-s/benchmark-results/02_glb_gratuit_hunyuan2mv/beagle.glb $O/beagle_full400.npz $O/ref_full_frame.glb | tail -1
venv/bin/python proto/v8/detect.py $O/ref_full_frame.glb $O/beagle_full400.npz $O/segmentation.npz $O/segmentation.json $O/details.json > $O/detect_stdout.txt 2>&1
# pseudo "run V7" : aucune oreille trouvee par le moteur (le module d'oreille est lie au repere de Paco) -> ears.pkl vide ; masque de protection par la regle du moteur
mkdir -p $O/run7; venv/bin/python - <<PY
import numpy as np, json, pickle
d=dict(np.load("$O/beagle_full400.npz")); s=np.load("$O/segmentation.npz"); lab=s["labels"]; names={int(k):v for k,v in json.loads(str(s["names"])).items()}; idx={v:k for k,v in names.items()}
d["protect"]=np.isin(lab,[idx[n] for n in ("yeux","bouche","truffe") if n in idx]); d["head_in_full"]=np.array([0,int(d["neck"]),0])
np.savez_compressed("$O/run7/beagle_full_sans_oreilles.npz",**d)
pickle.dump(dict(ears={}, npz2="$O/run7/beagle_full_sans_oreilles.npz", delta=[0.0,0.0,0.0], prep={}, R=np.eye(3).tolist(), lower_shift_ldu=0), open("$O/run7/ears.pkl","wb"))
PY
mkdir -p $O/md; MD_SKIP_MOUTH=1 venv/bin/python proto/v8/microdetails.py $O/details.json $O/run7 $O/md > $O/microdetails_stdout.txt 2>&1
export GLB_REF=$O/ref_full_frame.glb
mkdir -p $O/v82; venv/bin/python proto/v82/assemble_v82.py $O/run7 $O/md/microdetails.pkl $O/v82 $O/details.json C > $O/assemble_stdout.txt 2>&1
DROP_UNATTACHED=1 venv/bin/python tools/reorder_notice.py $O/v82/paco_V82.ldr $O/v82/notice.ldr | tail -1
$V/validate_v4.py --ldr $O/v82/notice.ldr --ldraw $LD --rbdb data/rb.db --out $O/v82 --name val --dump $O/v82/dump.pkl > /dev/null 2>&1
$V/weak_groups.py $O/v82/dump.pkl $O/segmentation.npz $O/v82/weak.json 2>&1 | head -1
$V/reinforce.py $O/v82/notice.ldr $O/v82/weak.json $O/r1.ldr $O/r1_log.json 1 2>&1 | tail -1
$V/validate_v4.py --ldr $O/r1.ldr --ldraw $LD --rbdb data/rb.db --out $O --name r1 --dump $O/r1_dump.pkl > /dev/null 2>&1
$V/weak_groups.py $O/r1_dump.pkl $O/segmentation.npz $O/weak_r1.json 2>&1 | head -1
$V/reinforce.py $O/r1.ldr $O/weak_r1.json $O/r2.ldr $O/r2_log.json 1 1 2>&1 | tail -1
DROP_UNATTACHED=1 venv/bin/python tools/reorder_notice.py $O/r2.ldr $O/beagle_V10_notice.ldr | tail -1
$V/validate_v4.py --ldr $O/beagle_V10_notice.ldr --ldraw $LD --rbdb data/rb.db --out $O --name final --dump $O/final_dump.pkl > $O/final_stdout.txt 2>&1
$V/weak_groups.py $O/final_dump.pkl $O/segmentation.npz $O/weak_final.json 2>&1 | head -8
$V/final_scope.py $O/v82/notice.ldr $O/beagle_V10_notice.ldr $O/scope_final.json $O/v82/notice.ldr:$O/v82/weak.json:$O/r1_log.json $O/r1.ldr:$O/weak_r1.json:$O/r2_log.json 2>&1 | tail -1
