#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

python -m pip install -r .github/env/macOS/requirements.txt
python setup.py bdist_wheel
