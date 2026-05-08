#!/usr/bin/env bash
# example-html-search.sh — HTML endpoint search → markdown
#
# Execute this script to fetch HTML results from DuckDuckGo and convert
# to clean Markdown. Uses the new format system:
#   - scrapling backend: native .md output via --ai-targeted
#   - curl/wget backend: raw HTML → pandoc → markdown
#
# Usage:
#   bash assets/example-html-search.sh <query>
#
# Note: The HTML endpoint may trigger CAPTCHA for automated requests.
# If you see "CAPTCHA detected", use the JSON API (ddg-search.sh) instead.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUERY="${1:-Rust programming language}"

# Use --format html which always returns markdown
# (scrapling native or pandoc-converted depending on backend)
bash "${SCRIPT_DIR}/scripts/ddg-search.sh" "$QUERY" html
