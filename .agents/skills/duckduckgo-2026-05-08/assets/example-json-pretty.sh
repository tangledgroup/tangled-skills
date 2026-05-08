#!/usr/bin/env bash
# example-json-pretty.sh — Pretty-printed JSON output
#
# Execute this script to search DuckDuckGo and get a nicely formatted
# full summary with pretty-printed JSON output.
#
# Usage:
#   bash assets/example-json-pretty.sh <query>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUERY="${1:-Rust programming language}"

# Must use --format json for JSON API (default format is now html→markdown)
# --pretty flag pretty-prints JSON output via jq
bash "${SCRIPT_DIR}/scripts/ddg-search.sh" "$QUERY" full --format json --pretty --limit 3
