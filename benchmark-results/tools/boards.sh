#!/usr/bin/env bash
# boards.sh <dog> <run_dir> <out_png> <title>  : reference views / GLB views / LEGO renders (crop+scale only)
set -euo pipefail
d=$1; R=$2; OUT=$3; T=$4
I=/home/user/Apr-s/benchmark-results/01_inputs_prepared/originaux
G=$HOME/bench/runs/${d}_hf2mv_shape_blanc/vues_couleur
~/bench/venv/bin/python -I ~/bench/tools/make_board.py "$OUT" "$T" \
 "Référence:face=$I/${d}_face.png,profil gauche=$I/${d}_profil_gauche.png,profil droit=$I/${d}_profil_droit.png,dos=$I/${d}_dos.png" \
 "GLB (entrée):face=$G/a_face.png,profil gauche=$G/b_profil_gauche.png,3/4=$G/c_trois_quarts.png,dos=$G/d_dos.png" \
 "LEGO brickify:face=$R/renders/1_front.png,profil gauche=$R/renders/2_left_profile.png,3/4 avant=$R/renders/3_three_quarter_front.png,dos=$R/renders/4_back.png,dessus=$R/renders/5_top.png,éclatée=$R/renders/6_exploded.png"
