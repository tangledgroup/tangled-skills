#!/usr/bin/env bash
# search.sh — DuckDuckGo search via HTML API using scrapling
#
# Usage:
#   search.sh <query> [--format md|html|json|yaml]
#
# Output formats (all sourced from the DuckDuckGo HTML endpoint):
#   md    — Markdown (default). scrapling's --ai-targeted produces clean markdown.
#   html  — Raw HTML of .web-result elements.
#   json  — Compact JSON array parsed from HTML by format.py.
#   yaml  — YAML parsed from HTML by format.py.
#
# Dependencies: bash, uvx (scrapling[shell]), python3

set -euo pipefail

# --- Constants ---
# DuckDuckGo HTML search endpoint
DDG_HTML_URL="https://html.duckduckgo.com/html/"
# CSS selector for individual search result blocks
CSS_SELECTOR=".web-result"
# User-agent impersonation target (safari reduces bot detection)
IMPERSONATE="safari"

# --- Argument Parsing ---
if [[ $# -lt 1 ]]; then
    echo "Usage: search.sh <query> [--format md|html|json|yaml]" >&2
    exit 1
fi

QUERY="$1"
FORMAT="md"

shift
while [[ $# -gt 0 ]]; do
    case "$1" in
        --format)
            if [[ $# -lt 2 ]]; then
                echo "Error: --format requires a value (md|html|json|yaml)" >&2
                exit 1
            fi
            FORMAT="$2"
            shift 2
            ;;
        *)
            echo "Error: Unknown argument '$1'" >&2
            exit 1
            ;;
    esac
done

# Validate format
case "$FORMAT" in
    md|html|json|yaml) ;;
    *)
        echo "Error: Invalid format '$FORMAT'. Must be one of: md, html, json, yaml" >&2
        exit 1
        ;;
esac

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

case "$FORMAT" in
    md)
        # Markdown output via scrapling's --ai-targeted flag
        # scrapling requires a .md file path (rejects '-' for stdout)
        TEMP_FILE=$(mktemp /tmp/ddg-search-XXXXXX.md)
        uvx 'scrapling[shell]' extract get \
            "$SEARCH_URL" \
            "$TEMP_FILE" \
            --css-selector "$CSS_SELECTOR" \
            --impersonate "$IMPERSONATE" \
            --ai-targeted
        cat "$TEMP_FILE"
        ;;

    html)
        # Raw HTML output — save to temp file, then cat to stdout
        # NOTE: --ai-targeted is intentionally omitted to preserve raw DOM structure
        TEMP_FILE=$(mktemp /tmp/ddg-search-XXXXXX.html)
        uvx 'scrapling[shell]' extract get \
            "$SEARCH_URL" \
            "$TEMP_FILE" \
            --css-selector "$CSS_SELECTOR" \
            --impersonate "$IMPERSONATE"
        cat "$TEMP_FILE"
        ;;

    json|yaml)
        # Parse HTML via format.py — save HTML to temp file first
        TEMP_FILE=$(mktemp /tmp/ddg-search-XXXXXX.html)
        uvx 'scrapling[shell]' extract get \
            "$SEARCH_URL" \
            "$TEMP_FILE" \
            --css-selector "$CSS_SELECTOR" \
            --impersonate "$IMPERSONATE" \
            --ai-targeted

        # Determine the path to format.py relative to this script
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        python3 -B "$SCRIPT_DIR/format.py" --format "$FORMAT" "$TEMP_FILE"
        ;;
esac
