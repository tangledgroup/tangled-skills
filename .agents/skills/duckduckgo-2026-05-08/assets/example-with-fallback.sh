#!/usr/bin/env bash
# example-with-fallback.sh — Search with result existence check
#
# Execute this script to search a query, check if results exist,
# and decide next action based on what the API returned.
#
# Usage:
#   bash assets/example-with-fallback.sh <query>
#
# Output:
#   Prints a check JSON showing which result types exist, then
#   prints the full summary if any content was found.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUERY="${1:-some obscure topic}"

# Step 1: Check what exists (must use --format json for JSON API)
CHECK=$(bash "${SCRIPT_DIR}/scripts/ddg-search.sh" "$QUERY" check --format json)
echo "Check: $CHECK"

# Step 2: If content exists, show full summary
HAS_CONTENT=$(echo "$CHECK" | jq -r 'if .has_abstract or .has_results then "yes" else "no" end')

if [[ "$HAS_CONTENT" == "yes" ]]; then
  echo ""
  echo "Full summary:"
  bash "${SCRIPT_DIR}/scripts/ddg-search.sh" "$QUERY" full --format json
else
  echo ""
  echo "No results found — try alternative queries or other sources."
fi
