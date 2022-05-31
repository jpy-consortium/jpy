#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

mkdir collect-wheels
mv download-wheels/*/*.whl collect-wheels/
