#!/bin/bash
cd /home/user/v062/benchmark-results/maps-engine-v03/style_fidelity_v062; E1=/tmp/claude-0/clean/Apr-s/benchmark-results/20_portable_engine; export LEGO_ENGINE_HOME=$E1 LEGO_DEPS=$E1/.deps LEGO_NODE_MODULES=$E1/node_modules NODE_PATH=$E1/node_modules
d=work17/$1; cat > $d/views17.json <<'J'
{"top":{"box":[0,0,40,40],"h":26,"az":0,"el":89.9,"w":1500,"hpx":1500,"zoom":0.95},
"trois_quarts":{"box":[0,0,40,40],"h":26,"az":20,"el":38,"w":1600,"hpx":1150,"zoom":0.85},
"lateral":{"box":[4,4,36,36],"h":26,"az":90,"el":12,"w":1500,"hpx":700,"zoom":1.0},
"chateau":{"box":[10,14,26,30],"h":26,"az":200,"el":32,"w":1500,"hpx":1100,"zoom":0.9},
"ponts":{"box":[16,24,32,38],"h":26,"az":150,"el":35,"w":1500,"hpx":1100,"zoom":0.9}}
J
$E1/.venv/bin/python render_views.py $d $d/views17.json 2>&1 | tail -1
