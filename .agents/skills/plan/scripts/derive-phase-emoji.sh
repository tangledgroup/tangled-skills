#!/usr/bin/env bash
# derive-phase-emoji.sh — Derive phase emoji from its tasks' emojis
# Usage: derive-phase-emoji.sh <PLAN.md> <phase-number>
#
# Output: single emoji character (☐ ❓ ⚙️ ❌ ☑) on stdout
# Priority: ⚙️ > ❓ > ❌ > ☑ > ☐

set -euo pipefail

usage() {
  echo "Usage: $0 <PLAN.md> <phase-number>"
  echo ""
  echo "Derives the phase emoji from its tasks' emojis using priority:"
  echo "  ⚙️ (Doing) > ❓ (Question) > ❌ (Error) > ☑ (Done) > ☐ (To Do)"
  exit "${1:-0}"
}

[[ $# -eq 0 ]] && usage 1
[[ "$1" == "--help" || "$1" == "-h" ]] && usage 0

plan="$1"
phase_num="$2"

if [[ ! -f "$plan" ]]; then
  echo "✗ File not found: $plan" >&2
  exit 1
fi

awk -v pn="$phase_num" '
  /^## .* Phase [0-9]+/ {
    # Extract phase number robustly via regex match
    if (match($0, /Phase ([0-9]+)/, arr)) {
      current = arr[1]
    }
  }
  current == pn && /^- .+ Task/ {
    # The emoji is the second field on the task line
    em = $2
    if (em == "⚙️") found_doing++
    else if (em == "❓") found_question++
    else if (em == "❌") found_error++
    else if (em == "☑") found_done++
    total++
  }
  END {
    if (found_doing) print "⚙️"
    else if (found_question) print "❓"
    else if (found_error) print "❌"
    else if (total && found_done == total) print "☑"
    else print "☐"
  }
' "$plan"
