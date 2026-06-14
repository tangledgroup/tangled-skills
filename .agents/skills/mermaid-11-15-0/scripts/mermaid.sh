#!/usr/bin/env bash
# mermaid.sh — Mermaid diagram validation tool
#
# Passthrough wrapper that invokes bun against _mermaid.js.
# All arguments are forwarded to the Bun script which handles
# DOM setup (jsdom + svgdom + dompurify) and mermaid parsing.
#
# Usage:
#   mermaid.sh validate [OPTIONS] <file|directory|->
#   mermaid.sh --help

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MERMAID_JS="${SCRIPT_DIR}/_mermaid.js"

# --- Resolve bun ---
if ! command -v bun &>/dev/null; then
    echo "ERROR: 'bun' is required but not found. Install from https://bun.sh" >&2
    exit 2
fi

# --- Check that _mermaid.js exists ---
if [[ ! -f "$MERMAID_JS" ]]; then
    echo "ERROR: _mermaid.js not found at ${MERMAID_JS}" >&2
    exit 2
fi

# --- Passthrough: forward all args to bun ---
exec bun "$MERMAID_JS" "$@"
