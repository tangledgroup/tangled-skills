#!/usr/bin/env bash
# example-captcha-detect.sh — Detect CAPTCHA on HTML endpoint
#
# Execute this script to test if your IP is being flagged by DuckDuckGo's
# bot detection on the HTML endpoint. Exit 0 = clean, exit 1 = blocked.
#
# Usage:
#   bash assets/example-captcha-detect.sh [query]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${SCRIPT_DIR}/scripts/ddg-utils.sh"

QUERY="${1:-test query}"

HTML=$(ddg_fetch_html "$QUERY") || {
  echo "Error: failed to fetch HTML (network error)" >&2
  exit 1
}

if echo "$HTML" | grep -q "anomaly-modal"; then
  echo "BLOCKED: CAPTCHA detected for query '$QUERY'"
  echo "Recommendation: Use JSON API (ddg-search.sh) — it does not trigger CAPTCHA."
  exit 1
else
  echo "CLEAN: HTML endpoint returned results for '$QUERY'"
  exit 0
fi
