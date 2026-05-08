#!/usr/bin/env bash
# validate-plan.sh — Structural validation of a PLAN.md file
# Usage: validate-plan.sh <PLAN.md>
# Exit 0 = pass, 1 = errors found

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
  echo "Usage: $0 <PLAN.md>"
  echo ""
  echo "Validates structural integrity of a workflow PLAN.md file:"
  echo "  - Plan header exists with valid emoji"
  echo "  - At least one phase and one task present"
  echo "  - All phase/task emojis are from the allowed set {☐ ❓ ⚙️ ❌ ☑}"
  echo "  - Zero-task phases flagged as warnings"
  echo "  - Phase emojis match derived status from their tasks"
  echo "  - Plan emoji matches derived status from its phases"
  exit "${1:-0}"
}

[[ $# -eq 0 ]] && usage 1
[[ "$1" == "--help" || "$1" == "-h" ]] && usage 0

plan="$1"

if [[ ! -f "$plan" ]]; then
  echo "✗ File not found: $plan"
  exit 1
fi

errors=0

# Must have plan header with valid emoji
if ! grep -qP '^# \S+ Plan:' "$plan"; then
  echo "✗ Missing or invalid plan header"
  errors=$((errors + 1))
fi

# Must have at least one phase
phases=$(grep -cP '^## \S+ Phase \d+' "$plan" || true)
if [[ "$phases" -eq 0 ]]; then
  echo "✗ No phases found"
  errors=$((errors + 1))
fi

# Must have at least one task
tasks=$(grep -cP '^- \S+ Task \d+\.\d+' "$plan" || true)
if [[ "$tasks" -eq 0 ]]; then
  echo "✗ No tasks found"
  errors=$((errors + 1))
fi

# No tasks with invalid emojis (compare total task lines vs valid-emoji task lines)
total_task_lines=$(grep -cP '^- \S+ Task' "$plan" || true)
valid_task_lines=0
for _em in "☐" "❓" "⚙️" "❌" "☑"; do
  cnt=$(grep -cf <(printf '%s' "- ${_em} Task") "$plan" 2>/dev/null || true)
  valid_task_lines=$((valid_task_lines + cnt))
done
if [[ "$total_task_lines" -gt "$valid_task_lines" ]]; then
  echo "✗ $((total_task_lines - valid_task_lines)) task(s) with invalid emoji"
  errors=$((errors + 1))
fi

# No phases with invalid emojis
total_phase_lines=$(grep -cP '^## \S+ Phase' "$plan" || true)
valid_phase_lines=0
for _em in "☐" "❓" "⚙️" "❌" "☑"; do
  cnt=$(grep -cf <(printf '%s' "## ${_em} Phase") "$plan" 2>/dev/null || true)
  valid_phase_lines=$((valid_phase_lines + cnt))
done
if [[ "$total_phase_lines" -gt "$valid_phase_lines" ]]; then
  echo "✗ $((total_phase_lines - valid_phase_lines)) phase(s) with invalid emoji"
  errors=$((errors + 1))
fi

# Check for zero-task phases
empty_phases=0
in_phase=0
task_count=0

while IFS= read -r line; do
  if echo "$line" | grep -qP '^## \S+ Phase \d+'; then
    [[ "$in_phase" -eq 1 ]] && [[ "$task_count" -eq 0 ]] && empty_phases=$((empty_phases + 1))
    in_phase=1
    task_count=0
  elif echo "$line" | grep -qP '^- \S+ Task'; then
    task_count=$((task_count + 1))
  fi
done < "$plan"

[[ "$in_phase" -eq 1 ]] && [[ "$task_count" -eq 0 ]] && empty_phases=$((empty_phases + 1))

if [[ "$empty_phases" -gt 0 ]]; then
  echo "⚠ $empty_phases phase(s) with zero tasks"
fi

# --- Emoji derivation checks ---

# Check each phase emoji matches its derived status from tasks
awk '
  /^## .* Phase [0-9]+/ {
    # Finalize previous phase
    if (phase_seen) {
      if (pt_doing)       derived = "⚙️"
      else if (pt_quest)  derived = "❓"
      else if (pt_error)  derived = "❌"
      else if (pt_done == pt_total && pt_total > 0) derived = "☑"
      else derived = "☐"

      if (derived != file_emoji) {
        print "✗ Phase " phase_num ": emoji is " file_emoji " but should be " derived " (derived from tasks)"
        mismatches++
      }
    }

    # Capture current phase emoji and number
    file_emoji = $2
    if (match($0, /Phase ([0-9]+)/, arr)) {
      phase_num = arr[1]
    }
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
      if (pt_doing)       derived = "⚙️"
      else if (pt_quest)  derived = "❓"
      else if (pt_error)  derived = "❌"
      else if (pt_done == pt_total && pt_total > 0) derived = "☑"
      else derived = "☐"

      if (derived != file_emoji) {
        print "✗ Phase " phase_num ": emoji is " file_emoji " but should be " derived " (derived from tasks)"
        mismatches++
      }
    }
    exit (mismatches + 0 > 0) ? 1 : 0
  }
' "$plan" || errors=$((errors + 1))

# Check plan emoji matches derived status from phases (via their tasks)
derived_plan=$(bash "$SCRIPT_DIR/derive-plan-emoji.sh" "$plan")
file_plan_emoji=$(head -1 "$plan" | grep -oP '^\# \K\S+')
if [[ "$derived_plan" != "$file_plan_emoji" ]]; then
  echo "✗ Plan emoji is $file_plan_emoji but should be $derived_plan (derived from phases)"
  errors=$((errors + 1))
fi

if [[ "$errors" -eq 0 ]]; then
  echo "✓ PLAN.md passes checks ($tasks tasks, $phases phases)"
  exit 0
else
  echo "✗ $errors error(s) found"
  exit 1
fi
