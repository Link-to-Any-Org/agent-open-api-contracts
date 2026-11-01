#!/usr/bin/env bash
# Rebuilds specs/lightspeed-x-series/openapi.json from the reference pages listed
# in specs/lightspeed-x-series/endpoints.txt. Each page embeds a one-operation
# OpenAPI definition; merge_openapi.py joins them and fails on any conflict.
set -euo pipefail

cd "$(dirname "$0")/.."
DIR=specs/lightspeed-x-series
BASE=https://x-series-api.lightspeedhq.com/reference
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

pages=()
while IFS= read -r slug; do
  [[ -z "$slug" || "$slug" == \#* ]] && continue
  curl -sfL -o "$TMP/$slug.md" "$BASE/$slug.md"
  pages+=("$TMP/$slug.md")
  sleep 0.3
done < "$DIR/endpoints.txt"

python3 -I scripts/merge_openapi.py "$DIR/openapi.json" "${pages[@]}" \
  --title "Lightspeed Retail X-Series API (agent contract)"
