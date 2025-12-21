#!/usr/bin/env bash
set -euo pipefail

export AGORA_ENV=development
export AGORA_BASE_URL="http://localhost:8000"

echo "Development environment variables set:"
echo "  AGORA_ENV=$AGORA_ENV"
echo "  AGORA_BASE_URL=$AGORA_BASE_URL"
