#!/usr/bin/env bash
# validate-plan.sh — Structural validation of a PLAN.md file
# Usage: validate-plan.sh <PLAN.md>
# Exit 0 = pass, 1 = errors found
#
# Validates:
#   - Plan header (title line with valid emoji)
#   - Header fields (Depends On, Created, Updated, Current Phase, Current Task)
#   - Phase structure (numbering, uniqueness, formatting)
#   - Task structure (numbering, phase binding, formatting)
#   - Emoji validity for all phases and tasks
#   - Emoji derivation correctness (phase from tasks, plan from phases)
#   - Zero-task phases (warnings)
#   - Section completeness (each section has required elements)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/common.sh"

usage() {
  echo "Usage: $0 <PLAN.md>"
  echo ""
  echo "Validates structural integrity of a workflow PLAN.md file."
  exit "${1:-0}"
}

[[ $# -eq 0 ]] && usage 1
[[ "$1" == "--help" || "$1" == "-h" ]] && usage 0

plan="$1"
check_plan_file "$plan"

errors=0
warnings=0

# ── Helper: report error/warning ────────────────────────────────────
err() {
  echo "✗ $1"
  errors=$((errors + 1))
}

warn() {
  echo "⚠ $1"
  warnings=$((warnings + 1))
}

# ═══════════════════════════════════════════════════════════════════
# Section 1: Plan Header (title line)
# ═══════════════════════════════════════════════════════════════════

if ! grep -qP '^# \S+ Plan:' "$plan"; then
  err "Missing or invalid plan header (expected: # [emoji] Plan: Title)"
fi

# ═══════════════════════════════════════════════════════════════════
# Section 2: Header Fields
# ═══════════════════════════════════════════════════════════════════

for field in "Depends On" "Created" "Updated" "Current Phase" "Current Task"; do
  if ! grep -qP "^\*\*${field}:\*\*" "$plan"; then
    err "Missing header field: **${field}:**"
  fi
done

# ═══════════════════════════════════════════════════════════════════
# Section 3: Phases
# ═══════════════════════════════════════════════════════════════════

phases=$(grep -cP '^## \S+ Phase \d+' "$plan" || true)
if [[ "$phases" -eq 0 ]]; then
  err "No phases found"
fi

# Check phase numbering is sequential from 1
phase_nums=$(awk '/^## .* Phase [0-9]+/ { if (match($0, /Phase ([0-9]+)/, arr)) print arr[1] }' "$plan")
expected=1
for pn in $phase_nums; do
  if [[ "$pn" -ne "$expected" ]]; then
    err "Phase numbering gap: expected Phase $expected, found Phase $pn"
  fi
  expected=$((expected + 1))
done

# Check for duplicate phase numbers
dup_phases=$(echo "$phase_nums" | sort | uniq -d)
if [[ -n "$dup_phases" ]]; then
  err "Duplicate phase numbers: $dup_phases"
fi

# ═══════════════════════════════════════════════════════════════════
# Section 4: Tasks
# ═══════════════════════════════════════════════════════════════════

tasks=$(grep -cP '^- \S+ Task \d+\.\d+' "$plan" || true)
if [[ "$tasks" -eq 0 ]]; then
  err "No tasks found"
fi

# Check task numbering within each phase (sequential, no gaps/dupes)
awk '
  /^## .* Phase [0-9]+/ {
    if (match($0, /Phase ([0-9]+)/, arr)) {
      cur_phase = arr[1]
      expected_task = 1
    }
  }
  /^- .+ Task [0-9]+\.[0-9]+/ {
    if (match($0, /Task ([0-9]+)\.([0-9]+)/, arr)) {
      tp = arr[1]; tt = arr[2]
      if (tp != cur_phase) {
        print "✗ Task " tp "." tt " is outside any phase context"
      } else if (tt != expected_task) {
        print "✗ Task numbering gap in Phase " cur_phase ": expected Task " cur_phase "." expected_task ", found Task " tp "." tt
      }
      expected_task++
    }
  }
' "$plan" | while IFS= read -r line; do err "$line"; done

# ═══════════════════════════════════════════════════════════════════
# Section 5: Emoji Validity
# ═══════════════════════════════════════════════════════════════════

# Tasks with invalid emojis
total_task_lines=$(grep -cP '^- \S+ Task' "$plan" || true)
valid_task_lines=0
for _em in "☐" "❓" "⚙️" "❌" "☑"; do
  cnt=$(grep -cf <(printf '%s' "- ${_em} Task") "$plan" 2>/dev/null || true)
  valid_task_lines=$((valid_task_lines + cnt))
done
if [[ "$total_task_lines" -gt "$valid_task_lines" ]]; then
  err "$((total_task_lines - valid_task_lines)) task(s) with invalid emoji"
fi

# Phases with invalid emojis
total_phase_lines=$(grep -cP '^## \S+ Phase' "$plan" || true)
valid_phase_lines=0
for _em in "☐" "❓" "⚙️" "❌" "☑"; do
  cnt=$(grep -cf <(printf '%s' "## ${_em} Phase") "$plan" 2>/dev/null || true)
  valid_phase_lines=$((valid_phase_lines + cnt))
done
if [[ "$total_phase_lines" -gt "$valid_phase_lines" ]]; then
  err "$((total_phase_lines - valid_phase_lines)) phase(s) with invalid emoji"
fi

# ═══════════════════════════════════════════════════════════════════
# Section 6: Zero-Task Phases
# ═══════════════════════════════════════════════════════════════════

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
  warn "$empty_phases phase(s) with zero tasks (can never reach ☑)"
fi

# ═══════════════════════════════════════════════════════════════════
# Section 7: Emoji Derivation (Phase from Tasks)
# ═══════════════════════════════════════════════════════════════════

phase_mismatches=0
while IFS= read -r pn; do
  derived=$(derive_phase_emoji "$plan" "$pn")
  current=$(get_phase_emoji_from_file "$plan" "$pn")
  if [[ "$derived" != "$current" ]]; then
    err "Phase $pn: emoji is $current but should be $derived (derived from tasks)"
    phase_mismatches=$((phase_mismatches + 1))
  fi
done <<< "$(awk '/^## .* Phase [0-9]+/ { if (match($0, /Phase ([0-9]+)/, arr)) print arr[1] }' "$plan")"

# ═══════════════════════════════════════════════════════════════════
# Section 8: Emoji Derivation (Plan from Phases)
# ═══════════════════════════════════════════════════════════════════

derived_plan=$(derive_plan_emoji "$plan")
file_plan_emoji=$(get_plan_emoji_from_file "$plan")
if [[ "$derived_plan" != "$file_plan_emoji" ]]; then
  err "Plan emoji is $file_plan_emoji but should be $derived_plan (derived from phases)"
fi

# ═══════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════

if [[ "$errors" -eq 0 ]]; then
  echo "✓ PLAN.md passes checks ($tasks tasks, $phases phases)"
  [[ "$warnings" -gt 0 ]] && echo "  ($warnings warning(s))"
  exit 0
else
  echo "✗ $errors error(s) found"
  [[ "$warnings" -gt 0 ]] && echo "  ($warnings warning(s))"
  exit 1
fi
