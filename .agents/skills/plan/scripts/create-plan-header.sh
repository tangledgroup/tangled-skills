#!/usr/bin/env bash
# create-plan-header.sh - Deterministic PLAN.md header generator
#
# Usage:
#   bash create-plan-header.sh <PLAN.md> <title> [depends_on]
#
# Arguments:
#   PLAN.md      — File to write header to (required)
#   title        — Plan title (required, e.g. "My Project")
#   depends_on   — Relative path(s) to other PLAN.md files.
#                  Defaults to "NONE" if omitted.
#                  Multiple deps: "../a/PLAN.md , ../b/PLAN.md"
#
# Output:
#   Writes a canonical PLAN.md header with all required fields.
#   Phases and tasks are NOT included — they are appended separately.
#
# Example:
#   bash create-plan-header.sh path/to/PLAN.md "My Project" "../dep/PLAN.md"

set -euo pipefail

usage() {
  cat <<'EOF' >&2
Usage: create-plan-header.sh <PLAN.md> <title> [depends_on]

Arguments:
  PLAN.md      File to write header to (required)
  title        Plan title (required)
  depends_on   Relative path(s) to other PLAN.md files (optional, default: NONE)

Example:
  bash create-plan-header.sh path/to/PLAN.md "My Project" "../dep/PLAN.md"
EOF
  exit 1
}

# --- Argument parsing ---
[[ $# -lt 2 ]] && usage
output="$1"
title="$2"
depends="${3:-NONE}"

# --- Timestamps ---
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# --- Generate header ---
header=$(cat <<HEADER_EOF
<!-- Plan Title is short but descriptive title of current plan -->
# ☐ Plan: ${title}

<!-- default NONE if doesn't have dependencies, or relative paths to other PLAN.md files -->
**Depends On:** ${depends}

<!-- ISO 8601 / UTC (YYYY-MM-DDTHH:MM:SSZ) -->
**Created:** ${timestamp}

<!-- ISO 8601 / UTC (YYYY-MM-DDTHH:MM:SSZ) -->
**Updated:** ${timestamp}

<!-- [emoji-of-phase] Phase X Phase Title -->
**Current Phase:**

<!-- [emoji-of-phase] Phase X - [emoji-of-task] Task X.Y -->
**Current Task:**

<!-- required: PHASES with TASKS start here -->
HEADER_EOF
)

# --- Output ---
if [[ -n "$output" ]]; then
  # Ensure parent directory exists
  mkdir -p "$(dirname "$output")"
  printf '%s\n' "$header" > "$output"
else
  printf '%s\n' "$header"
fi
