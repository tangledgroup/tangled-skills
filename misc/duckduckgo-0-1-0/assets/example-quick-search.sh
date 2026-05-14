#!/usr/bin/env bash
# example-quick-search.sh — Quick search using ddg-search.sh CLI
#
# Execute this script to get clean markdown search results for a topic.
# Default format is html→markdown via scrapling (anti-bot, native .md).
#
# Usage:
#   bash assets/example-quick-search.sh <query>
#
# Output: Clean markdown with search result snippets and links.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUERY="${1:-Rust programming language}"

# Default: html→markdown via scrapling (no command arg needed)
bash "${SCRIPT_DIR}/scripts/ddg-search.sh" "$QUERY"
