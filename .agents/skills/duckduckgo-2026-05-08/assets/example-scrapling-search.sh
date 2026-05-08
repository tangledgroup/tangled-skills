#!/usr/bin/env bash
# example-scrapling-search.sh — HTML search using scrapling backend
#
# Execute this script to search DuckDuckGo's HTML endpoint using the
# scrapling anti-bot backend. Scrapling impersonates Safari and handles
# JS rendering, making it the most reliable option for HTML scraping.
#
# Output is clean markdown (native .md via --ai-targeted).
# Scrapling is now the default backend, so --backend scrapling is optional.
#
# Usage:
#   bash assets/example-scrapling-search.sh <query>
#
# Note: Requires uvx (Rust-based Python package runner).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUERY="${1:-Rust programming language}"

# scrapling is the default backend, html is the default command
# Output is native markdown via --ai-targeted
bash "${SCRIPT_DIR}/scripts/ddg-search.sh" "$QUERY"
