#!/usr/bin/env bash
# ddg-search.sh — DuckDuckGo search CLI
#
# Standalone command-line tool for searching DuckDuckGo via the JSON API
# or HTML endpoint. Sources ddg-utils.sh for URL building, multi-backend
# fetching, format conversion, and jq filtering.
#
# Fetch backends (scrapling is default):
#   1. scrapling — anti-bot, JS rendering, Safari impersonation (default)
#   2. curl      — enhanced browser headers, HTTP/2
#   3. wget      — fallback, mirrors curl behavior
#
# Output formats:
#   html       — HTML endpoint converted to markdown (default, scrapling native or pandoc)
#   json       — JSON API response (compact or pretty-printed)
#   markdown   — Alias for html output
#
# Usage:
#   ddg-search.sh <query> [command] [options]
#
# Commands (default: html):
#   html        — Fetch HTML endpoint, convert to markdown (default)
#   summary     — Heading + abstract + source attribution
#   results     — Search result links with titles
#   related     — Related topic summaries and links
#   definition  — Dictionary-style definition (for single words)
#   full        — Complete structured summary (abstract + results + related)
#   check       — Check if results/abstract/related exist
#
# Options:
#   --limit N      Limit results/related topics to N items (default: all for results, 5 for related)
#   --lang CODE    Language variant (e.g., en-us, zh-cn)
#   --timeout SEC  Fetch timeout in seconds (default: 15)
#   --backend B    Force fetch backend: auto, scrapling, curl, wget (default: auto)
#   --format F     Output format: json, html, markdown (default: json)
#   --pretty       Pretty-print JSON output via jq
#   --help         Show this help message
#
# Examples:
#   ddg-search.sh "Rust programming"                    # default: html→md via scrapling
#   ddg-search.sh "serendipity" summary --format json   # JSON API for structured data
#   ddg-search.sh "Tangled Group" full --format json --limit 3
#   ddg-search.sh "Python" --backend curl               # html→md with curl+pandoc fallback
#
# Exit codes:
#   0 — Success
#   1 — Error (missing args, network failure, HTTP error)

set -euo pipefail

# ── Resolve script directory and source utils ────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/ddg-utils.sh"

# ── Help ─────────────────────────────────────────────────────────────────────
show_help() {
  cat <<'EOF'
ddg-search.sh — DuckDuckGo search CLI

Usage: ddg-search.sh <query> [command] [options]

Default: HTML endpoint → markdown via scrapling (anti-bot, native .md output)

Commands:
  html        Fetch HTML endpoint → markdown (default)
  summary     Heading + abstract + source (--format json)
  results     Search result links with titles (--format json)
  related     Related topic summaries and links (--format json)
  definition  Dictionary-style definition (--format json)
  full        Complete structured summary (--format json)
  check       Check if abstract/results/related exist (--format json)

Options:
  --limit N      Limit output to N items
  --lang CODE    Language variant (e.g., en-us, zh-cn)
  --timeout SEC  Fetch timeout in seconds (default: 15)
  --backend B    Force backend: auto, scrapling, curl, wget (default: scrapling)
  --format F     Output format: html, json, markdown (default: html)
  --pretty       Pretty-print JSON output via jq
  --help         Show this help message

Fetch Backends:
  1. scrapling — anti-bot, JS rendering, Safari impersonation (default)
  2. curl      — enhanced browser headers, HTTP/2
  3. wget      — fallback, mirrors curl behavior

Output Formats:
  html       HTML endpoint → markdown (default, scrapling native or pandoc for curl/wget)
  json       JSON API response (curl/wget only, never scrapling)
  markdown   Alias for html output

Format × Backend Matrix:
  +------------+-----------+------------------------------------------+
  | Format     | Backend   | How it works                             |
  +------------+-----------+------------------------------------------+
  | html/md    | scrapling | Native .md via --ai-targeted (default)   |
  | html/md    | curl      | Raw HTML → pandoc → markdown             |
  | html/md    | wget      | Raw HTML → pandoc → markdown             |
  | json       | curl      | Raw JSON as-is (or pretty with --pretty) |
  | json       | wget      | Raw JSON as-is (or pretty with --pretty) |
  | json       | scrapling | Falls back to curl/wget (scrapling breaks)|
  +------------+-----------+------------------------------------------+

Examples:
  ddg-search.sh "Rust programming"                          # html→md via scrapling
  ddg-search.sh "Rust" summary --format json                # JSON API structured data
  ddg-search.sh "Tangled Group" full --format json --limit 3
  ddg-search.sh "Python" --backend curl                     # html→md with curl+pandoc
  ddg-search.sh "AI agents" full --format json --pretty     # pretty JSON
EOF
}

# ── Argument Parsing ─────────────────────────────────────────────────────────

if [[ $# -lt 1 ]] || [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
  show_help
  if [[ $# -lt 1 ]]; then
    echo "Error: missing search query" >&2
    exit 1
  fi
  exit 0
fi

QUERY="$1"
shift

COMMAND="html"
LIMIT=""
LANG_CODE=""
BACKEND="scrapling"
FORMAT="html"
PRETTY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    summary|results|related|definition|full|check|html)
      COMMAND="$1"
      ;;
    --limit)
      shift
      LIMIT="${1:-}"
      if [[ -z "$LIMIT" ]] || ! [[ "$LIMIT" =~ ^[0-9]+$ ]]; then
        echo "Error: --limit requires a positive integer" >&2
        exit 1
      fi
      ;;
    --lang)
      shift
      LANG_CODE="${1:-}"
      if [[ -z "$LANG_CODE" ]]; then
        echo "Error: --lang requires a language code (e.g., en-us)" >&2
        exit 1
      fi
      ;;
    --timeout)
      shift
      DDG_TIMEOUT="${1:-}"
      if [[ -z "$DDG_TIMEOUT" ]] || ! [[ "$DDG_TIMEOUT" =~ ^[0-9]+$ ]]; then
        echo "Error: --timeout requires a positive integer (seconds)" >&2
        exit 1
      fi
      ;;
    --backend)
      shift
      BACKEND="${1:-}"
      if [[ -z "$BACKEND" ]] || ! [[ "$BACKEND" =~ ^(auto|scrapling|curl|wget)$ ]]; then
        echo "Error: --backend must be one of: auto, scrapling, curl, wget" >&2
        exit 1
      fi
      ;;
    --format)
      shift
      FORMAT="${1:-}"
      if [[ -z "$FORMAT" ]] || ! [[ "$FORMAT" =~ ^(json|html|markdown)$ ]]; then
        echo "Error: --format must be one of: json, html, markdown" >&2
        exit 1
      fi
      ;;
    --pretty)
      PRETTY=1
      ;;
    *)
      echo "Error: unknown option '$1'" >&2
      show_help >&2
      exit 1
      ;;
  esac
  shift
done

# Export env vars so ddg-utils.sh picks them up
export DDG_HTTP_BACKEND="$BACKEND"
export DDG_OUTPUT_FORMAT="$FORMAT"
export DDG_PRETTY_JSON="$PRETTY"

# ── Build URL options ────────────────────────────────────────────────────────
URL_OPTS=()
if [[ -n "$LANG_CODE" ]]; then
  URL_OPTS+=("dl=${LANG_CODE}")
fi

# ── Fetch and Filter ─────────────────────────────────────────────────────────

case "$COMMAND" in
  summary|results|related|definition|full|check)
    # JSON API commands always use json format
    export DDG_OUTPUT_FORMAT="json"

    JSON=$(ddg_fetch_json "$QUERY" "${URL_OPTS[@]}") || {
      echo "Error: failed to fetch DuckDuckGo JSON API response" >&2
      exit 1
    }

    output=""
    case "$COMMAND" in
      summary)    output=$(echo "$JSON" | ddg_summary) ;;
      results)    output=$(echo "$JSON" | ddg_results "$LIMIT") ;;
      related)    output=$(echo "$JSON" | ddg_related "$LIMIT") ;;
      definition) output=$(echo "$JSON" | ddg_definition) ;;
      full)       output=$(echo "$JSON" | ddg_full "$LIMIT") ;;
      check)      output=$(echo "$JSON" | ddg_check) ;;
    esac

    # Apply --pretty to final JSON output
    if [[ "$PRETTY" == "1" ]]; then
      echo "$output" | jq . 2>/dev/null || echo "$output"
    else
      printf '%s\n' "$output"
    fi
    ;;

  html)
    # HTML command: always convert to markdown
    export DDG_OUTPUT_FORMAT="markdown"

    MD=$(ddg_fetch_html "$QUERY") || {
      echo "Error: failed to fetch DuckDuckGo HTML endpoint" >&2
      exit 1
    }
    printf '%s\n' "$MD"
    ;;
esac
