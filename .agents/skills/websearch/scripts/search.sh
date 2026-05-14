#!/usr/bin/env bash
# search.sh — DuckDuckGo search via HTML API, outputs raw YAML only
#
# Usage:
#   search.sh <query> [--limit N]
#
# Always outputs YAML to stdout. Output is never summarized or transformed.
# The agent runs this script and shows its exact output to the user.
#
# Dependencies: bash, uvx (scrapling[shell]), python3

set -euo pipefail

# --- Constants ---
# DuckDuckGo HTML search endpoint — deterministic, no API key required
DDG_HTML_URL="https://html.duckduckgo.com/html/"
# CSS selector for individual search result blocks
CSS_SELECTOR=".web-result"
# User-agent impersonation target (safari reduces bot detection)
IMPERSONATE="safari"

# --- Argument Parsing ---
if [[ $# -lt 1 ]]; then
    echo "Usage: search.sh <query> [--limit N]" >&2
    exit 1
fi

QUERY="$1"
LIMIT=""

shift
while [[ $# -gt 0 ]]; do
    case "$1" in
        --limit)
            if [[ $# -lt 2 ]]; then
                echo "Error: --limit requires a numeric value" >&2
                exit 1
            fi
            LIMIT="$2"
            shift 2
            ;;
        *)
            echo "Error: Unknown argument '$1'" >&2
            exit 1
            ;;
    esac
done

# Validate limit if provided
if [[ -n "$LIMIT" ]] && ! [[ "$LIMIT" =~ ^[0-9]+$ ]]; then
    echo "Error: --limit must be a positive integer" >&2
    exit 1
fi

# --- Temp File Setup with Cleanup ---
TEMP_FILE=""
cleanup() {
    if [[ -n "$TEMP_FILE" && -f "$TEMP_FILE" ]]; then
        rm -f "$TEMP_FILE"
    fi
}
trap cleanup EXIT INT TERM

# URL-encode the query safely via stdin to avoid shell injection
# (unquoted $QUERY expansion was vulnerable to shell metacharacters)
ENCODED_QUERY=$(printf '%s' "$QUERY" | python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.stdin.read().strip(), safe=''))")
SEARCH_URL="${DDG_HTML_URL}?q=${ENCODED_QUERY}"

# Fetch HTML via scrapling — save to temp file for parsing
# scrapling requires a file path (rejects '-' for stdout)
TEMP_FILE=$(mktemp /tmp/websearch-${$}-XXXXXX.html)
uvx 'scrapling[shell]' extract get \
    "$SEARCH_URL" \
    "$TEMP_FILE" \
    --css-selector "$CSS_SELECTOR" \
    --impersonate "$IMPERSONATE" \
    --ai-targeted

# Parse HTML and output YAML — exact data, no summarization
# Determine the path to format.py relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -n "$LIMIT" ]]; then
    python3 -B "$SCRIPT_DIR/format.py" --limit "$LIMIT" "$TEMP_FILE"
else
    python3 -B "$SCRIPT_DIR/format.py" "$TEMP_FILE"
fi
