#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

python -m pip install -r .github/env/Linux/requirements.txt
python setup.py bdist_wheel --dist-dir dist.linux
# Note: auditwheel only works with a single file argument - we are relying on finding exactly one wheel
python .github/env/Linux/auditwheel-keep-libjvm.py \
  repair \
  --plat manylinux_2_17_x86_64 \
  --only-plat \
  --wheel-dir dist/ \
  dist.linux/*
