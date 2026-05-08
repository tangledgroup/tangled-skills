#!/usr/bin/env bash
# example-batch-search.sh — Batch search multiple terms
#
# Execute this script to search for multiple topics and get markdown results.
# Default format is html→markdown via scrapling. Useful for comparing or
# surveying multiple subjects at once.
#
# Usage:
#   bash assets/example-batch-search.sh [term1 term2 term3 ...]
#
# Default terms if none provided: Python Rust Go

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TERMS=("$@")
if [[ ${#TERMS[@]} -eq 0 ]]; then
  TERMS=("Python" "Rust" "Go")
fi

for term in "${TERMS[@]}"; do
  echo "--- $term ---"
  # Default: html→markdown via scrapling
  bash "${SCRIPT_DIR}/scripts/ddg-search.sh" "$term"
  echo
done
