#!/usr/bin/env bash
# create-plan-header.sh - Deterministic PLAN.md header generator
# Usage: create-plan-header.sh <title> [depends-on] [emoji]
#
# Prints a canonical PLAN.md header to stdout. Every newline, comment line,
# and blank line is exactly positioned — no variation between runs.
#
# Arguments:
#   title       - Short descriptive plan title (required)
#   depends-on  - Comma-separated relative paths to other PLAN.md files (optional, default: NONE)
#   emoji       - Plan status emoji (optional, default: ☐)
#
# Output: Writes the complete header block to stdout. Append phases/tasks below it.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Defaults
title="${1:-}"
depends_on="${2:-NONE}"
emoji="${3:-$EM_TODO}"

# Validate title
if [[ -z "$title" ]]; then
  echo "ERROR: Plan title is required. Usage: $0 <title> [depends-on] [emoji]" >&2
  exit 1
fi

# Validate emoji
if ! is_valid_emoji "$emoji"; then
  echo "ERROR: Invalid plan emoji: '$emoji' (valid: ☐ ❓ ⚙️ ❌ ☑)" >&2
  exit 1
fi

# Generate timestamp
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Print deterministic header — every line and blank line is fixed
cat <<EOF
<!-- Plan Title is short but descriptive title of current plan -->
# ${emoji} Plan: ${title}

<!-- default NONE if doesn't have dependencies, or relative paths to other PLAN.md files -->
**Depends On:** ${depends_on}

<!-- ISO 8601 / UTC (YYYY-MM-DDTHH:MM:SSZ) -->
**Created:** ${now}

<!-- ISO 8601 / UTC (YYYY-MM-DDTHH:MM:SSZ) -->
**Updated:** ${now}

<!-- [emoji-of-phase] Phase X Phase Title -->
**Current Phase:** ☐ Phase 1

<!-- [emoji-of-phase] Phase X - [emoji-of-task] Task X.Y -->
**Current Task:** ☐ Task 1.1

<!-- required: PHASES with TASKS start here -->
EOF
