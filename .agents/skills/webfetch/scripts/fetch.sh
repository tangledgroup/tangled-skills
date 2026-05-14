#!/usr/bin/env bash
# fetch.sh — Fetch any URL and save as AI-targeted markdown
#
# Usage:
#   fetch.sh <URL> [--output FILE]
#
# Fetches a web page using scrapling's --ai-targeted mode, which produces
# clean markdown optimized for AI context. Output is saved to a temp file
# by default, or to the specified --output path.
#
# Prints the output file path to stdout so the agent can read it.
# On failure, prints a clear error to stderr and exits non-zero.
#
# Dependencies: bash, uvx (scrapling[shell])

set -euo pipefail

# --- Constants ---
# User-agent impersonation target (safari reduces bot detection)
IMPERSONATE="safari"
# Request timeout in seconds — balances between patience and failing fast
TIMEOUT=30

# --- Argument Parsing ---
if [[ $# -lt 1 ]]; then
    echo "Usage: fetch.sh <URL> [--output FILE]" >&2
    exit 1
fi

URL="$1"
OUTPUT=""

shift
while [[ $# -gt 0 ]]; do
    case "$1" in
        --output)
            if [[ $# -lt 2 ]]; then
                echo "Error: --output requires a file path" >&2
                exit 1
            fi
            OUTPUT="$2"
            shift 2
            ;;
        *)
            echo "Error: Unknown argument '$1'" >&2
            exit 1
            ;;
    esac
done

# Validate URL has a scheme
if [[ ! "$URL" =~ ^https?:// ]]; then
    echo "Error: URL must start with http:// or https://" >&2
    exit 1
fi

# Create output file (temp or user-specified)
if [[ -n "$OUTPUT" ]]; then
    # Ensure parent directory exists
    OUTPUT_DIR="$(dirname "$OUTPUT")"
    if [[ ! -d "$OUTPUT_DIR" ]]; then
        mkdir -p "$OUTPUT_DIR"
    fi
    TEMP_FILE="$OUTPUT"
else
    TEMP_FILE=$(mktemp /tmp/webfetch-${$}-XXXXXX.md)
fi

# Fetch the URL via scrapling — saves markdown to file
# --ai-targeted produces clean markdown optimized for AI context
# --follow-redirects ensures 3xx responses are followed to final destination
# stderr is suppressed (scrapling INFO logs are noisy and not actionable)
if ! uvx 'scrapling[shell]' extract get \
    "$URL" \
    "$TEMP_FILE" \
    --impersonate "$IMPERSONATE" \
    --ai-targeted \
    --follow-redirects \
    --timeout "$TIMEOUT" \
    2>/dev/null; then
    echo "Error: Failed to fetch URL: $URL" >&2
    # Clean up empty or partial temp file on failure (only auto-created temps)
    if [[ -z "$OUTPUT" && -f "$TEMP_FILE" ]]; then
        rm -f "$TEMP_FILE"
    fi
    exit 1
fi

# Verify the output file was created and has content
if [[ ! -s "$TEMP_FILE" ]]; then
    echo "Error: Fetch succeeded but produced empty output for URL: $URL" >&2
    if [[ -z "$OUTPUT" && -f "$TEMP_FILE" ]]; then
        rm -f "$TEMP_FILE"
    fi
    exit 1
fi

# Print the output file path so the agent knows where to read it
echo "$TEMP_FILE"
