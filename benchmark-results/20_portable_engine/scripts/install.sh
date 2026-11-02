#!/usr/bin/env bash
# Install the engine from a fresh clone : Python venv with locked versions, Node modules (renders / notices), pinned third-party dependencies.
# usage: bash scripts/install.sh [--no-node]
set -euo pipefail
cd "$(dirname "$0")/.."; ROOT=$(pwd)
python3 -m venv .venv; .venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r locks/requirements.lock.txt
if [ "${1:-}" != "--no-node" ] && command -v npm >/dev/null; then npm ci --ignore-scripts --silent || echo "WARNING: npm ci failed (renders and PDF notices unavailable)"; fi
bash scripts/fetch_deps.sh
.venv/bin/python -c "import numpy,scipy,trimesh,networkx,sklearn,PIL; print('python deps ok :', numpy.__version__, scipy.__version__, trimesh.__version__)"
echo "install ok"
