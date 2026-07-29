#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

python scripts/check_public_surface.py
python scripts/verify_release.py
python scripts/verify_prospective_confirmation.py
python scripts/build_main_tables.py
python scripts/build_main_figures.py
python -m pytest -q

echo "WMROUTE_ALL_CHECKS_PASS"
