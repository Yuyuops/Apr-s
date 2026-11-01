#!/bin/bash
# renders of a V8.1 variant on the mouth views + normal-size views (from ~/bench). usage: render_v81.sh <A|B>
set -e
V=${1:-A}; cd ~/bench/tools
node render_ldr.js ../proto/v81/run$V/s.json ../proto/v81/viewsV81.json ../proto/v81/r_v81$V | tail -1
