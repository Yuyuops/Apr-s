# local run environment (engine-1 folder providing .venv, .deps, node_modules ; fetched via 20_portable_engine/scripts/install.sh)
export LEGO_ENGINE_HOME=${LEGO_ENGINE_HOME:-/tmp/claude-0/clean/Apr-s/benchmark-results/20_portable_engine}
export LEGO_NODE_MODULES=$LEGO_ENGINE_HOME/node_modules NODE_PATH=$LEGO_ENGINE_HOME/node_modules
export PY=$LEGO_ENGINE_HOME/.venv/bin/python
