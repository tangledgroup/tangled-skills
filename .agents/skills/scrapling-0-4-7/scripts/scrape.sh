#!/usr/bin/env bash
# scrape.sh — Scrapling CLI wrapper for AI agents
#
# Converts web pages to Markdown using Scrapling via uvx.
# Handles temp-file workflow automatically: creates temp .md file,
# runs scrapling, outputs content to stdout, cleans up.
#
# Usage:
#   bash scrape.sh 'https://example.com'                          # get mode (default)
#   bash scrape.sh --mode fetch 'https://app.example.com'         # browser fetch
#   bash scrape.sh --mode stealthy 'https://protected.example.com' # anti-bot bypass
#   bash scrape.sh -o output.md 'https://example.com'             # save to file
#   bash scrape.sh -s 'article' 'https://blog.example.com'        # CSS selector
#
# Exit codes:
#   0 — success
#   1 — missing URL argument
#   2 — uvx not found
#   3 — scrapling command failed

set -euo pipefail

# ── Defaults ───────────────────────────────────────────────────────
# Mode determines the scrapling subcommand and default flags.
MODE="get"
CSS_SELECTOR=""
OUTPUT=""
IMPERSONATE="safari"   # Default for get mode; ignored for fetch/stealthy
AI_TARGETED=1          # 1 = on (default), 0 = off
EXTRA_ARGS=""

# ── Help ───────────────────────────────────────────────────────────
usage() {
    cat <<'EOF'
Usage: scrape.sh [OPTIONS] <URL>

Scrape a web page and output clean Markdown to stdout.

Modes (default: get):
  --mode get        Plain HTTP request with Safari impersonation (default)
  --mode fetch      Browser automation for JavaScript-rendered pages
  --mode stealthy   Stealth mode for anti-bot protected sites

Options:
  -s, --css-selector TEXT   Extract specific content via CSS selector
  -o, --output FILE         Save to file instead of stdout
  --impersonate BROWSER     Browser to impersonate: safari (default), chrome, firefox
                            Only applies to 'get' mode
  --ai-targeted             Strip noise for AI consumption (default: on)
  --no-ai-targeted          Disable ai-targeted output
  --extra 'FLAGS'           Pass extra flags directly to scrapling
  -h, --help                Show this help message

Examples:
  bash scrape.sh 'https://example.com'
  bash scrape.sh --mode fetch 'https://app.example.com'
  bash scrape.sh --mode stealthy --solve-cloudflare 'https://protected.example.com'
  bash scrape.sh -s 'article' 'https://blog.example.com'
  bash scrape.sh -o notes.md 'https://example.com'
EOF
}

# ── Argument Parsing ───────────────────────────────────────────────
URL=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --mode)
            MODE="$2"
            shift 2
            ;;
        -s|--css-selector)
            CSS_SELECTOR="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        --impersonate)
            IMPERSONATE="$2"
            shift 2
            ;;
        --ai-targeted)
            AI_TARGETED=1
            shift
            ;;
        --no-ai-targeted)
            AI_TARGETED=0
            shift
            ;;
        --extra)
            EXTRA_ARGS="$2"
            shift 2
            ;;
        -*)
            echo "Error: Unknown option '$1'. Use --help for usage." >&2
            exit 1
            ;;
        *)
            if [[ -z "$URL" ]]; then
                URL="$1"
                shift
            else
                echo "Error: Unexpected argument '$1' after URL." >&2
                exit 1
            fi
            ;;
    esac
done

# ── Validation ─────────────────────────────────────────────────────
if [[ -z "$URL" ]]; then
    echo "Error: URL is required. Use --help for usage." >&2
    exit 1
fi

if ! command -v uvx &>/dev/null; then
    echo "Error: 'uvx' not found. Install uv: https://docs.astral.sh/uv/" >&2
    exit 2
fi

# ── Build Command ──────────────────────────────────────────────────
# Map mode name to scrapling subcommand
case "$MODE" in
    get)       SUBCMD="get" ;;
    fetch)     SUBCMD="fetch" ;;
    stealthy)  SUBCMD="stealthy-fetch" ;;
    *)
        echo "Error: Unknown mode '$MODE'. Valid modes: get, fetch, stealthy." >&2
        exit 1
        ;;
esac

# Build the uvx command arguments
CMD_ARGS=(extract "$SUBCMD" "$URL")

# Add mode-specific defaults
if [[ "$MODE" == "get" ]]; then
    CMD_ARGS+=(--impersonate "$IMPERSONATE")
fi

# Add optional flags
if [[ -n "$CSS_SELECTOR" ]]; then
    CMD_ARGS+=(-s "$CSS_SELECTOR")
fi

if [[ "$AI_TARGETED" -eq 1 ]]; then
    CMD_ARGS+=(--ai-targeted)
fi

# Add extra passthrough flags (word-split intentionally)
if [[ -n "$EXTRA_ARGS" ]]; then
    for arg in $EXTRA_ARGS; do
        CMD_ARGS+=("$arg")
    done
fi

# ── Execute ────────────────────────────────────────────────────────
if [[ -n "$OUTPUT" ]]; then
    # Direct file output — write straight to target path
    # Ensure parent directory exists
    OUTPUT_DIR=$(dirname "$OUTPUT")
    if [[ ! -d "$OUTPUT_DIR" ]]; then
        mkdir -p "$OUTPUT_DIR"
    fi

    CMD_ARGS+=("$OUTPUT")
    uvx 'scrapling[shell]' "${CMD_ARGS[@]}"
    EXIT_CODE=$?

    if [[ $EXIT_CODE -ne 0 ]]; then
        echo "Error: scrapling failed with exit code $EXIT_CODE" >&2
        rm -f "$OUTPUT"  # Clean up partial output
        exit 3
    fi

    echo "Saved to: $OUTPUT"
else
    # Inline output — use temp file, read back, clean up
    TMPFILE=$(mktemp /tmp/scrape-XXXXXX.md)
    trap 'rm -f "$TMPFILE"' EXIT

    CMD_ARGS+=("$TMPFILE")
    uvx 'scrapling[shell]' "${CMD_ARGS[@]}"
    EXIT_CODE=$?

    if [[ $EXIT_CODE -ne 0 ]]; then
        echo "Error: scrapling failed with exit code $EXIT_CODE" >&2
        exit 3
    fi

    cat "$TMPFILE"
fi
