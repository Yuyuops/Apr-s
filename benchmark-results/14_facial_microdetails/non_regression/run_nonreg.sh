#!/bin/bash
# V8 non-regression: replay V6 (proto/ear11/autogen.py, modified in V7) and V6.1 (proto/ear12/autogen61.py on it) from the
# archived inputs (targets of proto/ear11/targets, identical to the archived ones: md5 checked), same commands as the
# archived run_all.sh, outputs in proto/v8/nonreg/ (archived references are never written).
set -e
cd ~/bench; LD=ldraw-parts-library/complete/ldraw; N=proto/v8/nonreg; REF=/home/user/Apr-s/benchmark-results
md5sum proto/ear11/targets/A_paco_silhouette.npy $REF/11_automatic_contour_proof/exemples/A_paco/A_paco_silhouette.npy proto/ear11/targets/B_beagle_silhouette.npy $REF/11_automatic_contour_proof/exemples/B_beagle/B_beagle_silhouette.npy > $N/md5_entrees.txt
for V in V6 V61; do
  if [ $V = V6 ]; then GEN=proto/ear11/autogen.py; else GEN=proto/ear12/autogen61.py; fi
  mkdir -p $N/${V}_A $N/${V}_B
  venv/bin/python $GEN A_paco $N/${V}_A --head > $N/${V}_A/gen_stdout.txt
  venv/bin/python $GEN B_beagle $N/${V}_B > $N/${V}_B/gen_stdout.txt
  for X in A B; do
    R=$N/${V}_$X; if [ $X = A ]; then IN=$R/tete_oreille_A_paco.ldr; NPZ="--npz proto/out/paco_head400.npz"; else IN=$R/oreille_B_beagle.ldr; NPZ=""; fi
    DROP_UNATTACHED=1 venv/bin/python tools/reorder_notice.py $IN $R/notice.ldr | tail -1
    if [ $V = V6 ]; then
      venv/bin/python tools/validate_v2_bigcases.py --ldr $R/notice.ldr --ldraw $LD --rbdb data/rb.db --out $R --name val $NPZ > $R/val_stdout.txt
    else
      venv/bin/python tools/validate_v3.py --ldr $R/notice.ldr --ldraw $LD --rbdb data/rb.db --out $R --name val3 $NPZ > $R/val3_stdout.txt
      venv/bin/python tools/validate_v2.py --ldr $R/notice.ldr --ldraw $LD --rbdb data/rb.db --out $R --name val2 $NPZ > $R/val2_stdout.txt
    fi
  done
done
venv/bin/python $N/compare_nonreg.py $N $REF > $N/nonreg_stdout.txt; cat $N/nonreg_stdout.txt
