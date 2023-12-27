#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python -m pip install -r "${__dir}/requirements.txt"

# Can add --build-number <x> if necessary
python setup.py bdist_wheel --dist-dir dist.linux

# Note: auditwheel only works with a single file argument - we are relying on finding exactly one wheel
python "${__dir}/auditwheel-keep-libjvm.py" \
  repair \
  --plat "manylinux_2_17_$(arch)" \
  --only-plat \
  --wheel-dir dist/ \
  dist.linux/*
