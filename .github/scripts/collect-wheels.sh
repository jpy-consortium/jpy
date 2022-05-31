#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

mkdir collect-wheels
find download-wheels -type f
mv download-wheels/*/*.whl collect-wheels/
