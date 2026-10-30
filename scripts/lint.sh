#!/usr/bin/env bash
# Lints the template and every spec under specs/. Exits non-zero on lint errors.
set -euo pipefail

REDOCLY_VERSION="2.63.0"
cd "$(dirname "$0")/.."

files=(templates/openapi.yaml)
while IFS= read -r f; do files+=("$f"); done < <(find specs -type f \( -name 'openapi.json' -o -name 'openapi.yaml' -o -name 'openapi.yml' \) | sort)

echo "Linting ${#files[@]} file(s)"
npx --yes "@redocly/cli@${REDOCLY_VERSION}" lint "${files[@]}"
