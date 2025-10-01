#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python -m pip install -r "${__dir}/requirements.txt"

# Can add --build-number <x> if necessary
python setup.py bdist_wheel --dist-dir dist.linux

# Note: auditwheel only works with a single file argument - we are relying on finding exactly one wheel
auditwheel \
  repair \
  --exclude libjvm.so \
  --wheel-dir dist/ \
  dist.linux/*
