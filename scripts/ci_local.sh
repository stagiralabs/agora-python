#!/usr/bin/env bash
set -euo pipefail

python -m pip install -U pip
python -m pip install -e .
python -m mypy src
python -m pytest
python -m pip check
