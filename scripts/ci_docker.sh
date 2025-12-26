#!/usr/bin/env bash
set -euo pipefail

image_name="${1:-agora-ci}"

docker build -f containers/ci/Dockerfile -t "${image_name}" .
docker run --rm "${image_name}"
