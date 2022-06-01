#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

mkdir collect-artifacts
find download-artifacts -type f

mv download-artifacts/*/*.whl collect-artifacts/
mv download-artifacts/*/*.tar.gz collect-artifacts/
