#!/usr/bin/env bash
# derive-plan-emoji.sh — Derive plan emoji from its phases' tasks
# Usage: derive-plan-emoji.sh <PLAN.md>
#
# Output: single emoji character (☐ ❓ ⚙️ ❌ ☑) on stdout
# Priority: ⚙️ > ❓ > ❌ > ☑ > ☐
#
# This script re-derives each phase's status from its tasks (not from
# the phase emoji in the file, which may be stale), then aggregates
# across all phases to produce the plan emoji.

set -euo pipefail

usage() {
  echo "Usage: $0 <PLAN.md>"
  echo ""
  echo "Derives the plan emoji from its phases' tasks using priority:"
  echo "  ⚙️ (Doing) > ❓ (Question) > ❌ (Error) > ☑ (Done) > ☐ (To Do)"
  exit "${1:-0}"
}

[[ $# -eq 0 ]] && usage 1
[[ "$1" == "--help" || "$1" == "-h" ]] && usage 0

plan="$1"

if [[ ! -f "$plan" ]]; then
  echo "✗ File not found: $plan" >&2
  exit 1
fi

awk '
  /^## .* Phase [0-9]+/ {
    # Finalize previous phase if any
    if (phase_seen) {
      # Determine this phases derived status
      if (pt_doing)       max_status = "doing"
      else if (pt_quest)  max_status = "question"
      else if (pt_error)  max_status = "error"
      else if (pt_done == pt_total && pt_total > 0) max_status = "done"
      else max_status = "notstarted"

      # Track global highest status
      if (max_status == "doing")       g_doing++
      else if (max_status == "question") g_question++
      else if (max_status == "error")  g_error++
      else if (max_status == "done")   g_done++
      else                             g_notstarted++
      g_total++
    }

    # Reset for new phase
    phase_seen = 1
    pt_doing = 0; pt_quest = 0; pt_error = 0; pt_done = 0; pt_total = 0
  }
  phase_seen && /^- .+ Task/ {
    em = $2
    if (em == "⚙️") pt_doing++
    else if (em == "❓") pt_quest++
    else if (em == "❌") pt_error++
    else if (em == "☑") pt_done++
    pt_total++
  }
  END {
    # Finalize last phase
    if (phase_seen) {
      if (pt_doing)       max_status = "doing"
      else if (pt_quest)  max_status = "question"
      else if (pt_error)  max_status = "error"
      else if (pt_done == pt_total && pt_total > 0) max_status = "done"
      else max_status = "notstarted"

      if (max_status == "doing")       g_doing++
      else if (max_status == "question") g_question++
      else if (max_status == "error")  g_error++
      else if (max_status == "done")   g_done++
      else                             g_notstarted++
      g_total++
    }

    # Derive plan emoji from aggregated phase statuses
    if (g_doing + 0)              print "⚙️"
    else if (g_question + 0)      print "❓"
    else if (g_error + 0)         print "❌"
    else if (g_total > 0 && g_done + 0 == g_total) print "☑"
    else                          print "☐"
  }
' "$plan"
