#!/bin/bash
# usage: board.sh <out.png> <title> <views, space separated> -- <label:dir> ...
cd ~/bench; out=$1; title=$2; shift 2; V=(); while [ "$1" != "--" ]; do V+=($1); shift; done; shift
args=(); for ld in "$@"; do l=${ld%%:*}; d=${ld#*:}; s=""; for v in "${V[@]}"; do s="$s,$d/$v.png"; done; args+=("$l:${s#,}"); done
venv/bin/python tools/make_board.py $out "$title" "${args[@]}" | tail -1
