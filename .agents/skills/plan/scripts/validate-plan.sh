#!/usr/bin/env bash
# validate-plan.sh - Structural validation of a PLAN.md file
# Usage: validate-plan.sh <PLAN.md>
# Exit 0 = pass, 1 = errors found
#
# Validates (section by section):
#   1. Plan Header - title line exists with valid emoji format
#   2. Header Fields - all required fields present with non-empty values
#   3. Phases - at least one, sequential numbering from 1, no duplicates
#   4. Tasks - at least one per phase, sequential numbering, proper phase binding
#   5. Emoji Validity - all phase/task emojis from allowed set
#   6. Zero-Task Phases - flagged as warnings
#   7. Phase Emoji Derivation - each phase emoji matches derived status
#   8. Plan Emoji Derivation - plan emoji matches derived status from phases

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/common.sh"

[[ $# -eq 0 ]] && { echo "Usage: $0 <PLAN.md>" >&2; exit 1; }
[[ "$1" == "--help" || "$1" == "-h" ]] && { echo "Usage: $0 <PLAN.md>"; echo ""; echo "Validates structural integrity of a workflow PLAN.md file."; echo "Checks 8 sections: header, fields, phases, tasks, emojis, derivation."; echo "Exit 0 = pass, 1 = errors found."; exit 0; }

plan="$1"
check_plan_file "$plan"

errors=0
warnings=0

# Helpers
err() { echo "FAIL: $1"; errors=$((errors + 1)); }
warn() { echo "WARN: $1"; warnings=$((warnings + 1)); }

# Section 1: Plan Header (title line)
echo "Checking section 1: Plan Header"

if ! grep -qP '^# \S+ Plan:' "$plan"; then
  err "Missing or invalid plan header (expected: # [emoji] Plan: Title)"
else
  header_emoji=$(get_plan_emoji_from_file "$plan")
  if ! is_valid_emoji "$header_emoji"; then
    err "Plan header has invalid emoji: '$header_emoji' (valid: ☐ ❓ ⚙️ ❌ ☑)"
  fi
fi

# Section 2: Header Fields
echo "Checking section 2: Header Fields"

for field in "Depends On" "Created" "Updated" "Current Phase" "Current Task"; do
  if ! grep -qP "^\*\*${field}:\*\*" "$plan"; then
    err "Missing header field: **${field}:**"
  else
    val=$(get_header_field "$plan" "$field")
    if [[ -z "$val" && "$field" != "Depends On" ]]; then
      warn "Header field **${field}:** is empty"
    fi
  fi
done

# Section 3: Phases
echo "Checking section 3: Phases"

phase_nums_raw=$(get_phase_numbers "$plan")
if [[ -z "$phase_nums_raw" ]]; then
  phases=0
  phase_nums=""
else
  phase_nums="$phase_nums_raw"
  phases=$(( $(echo "$phase_nums_raw" | wc -w) ))
fi

if [[ "$phases" -eq 0 ]]; then
  err "No phases found"
else
  # Check sequential numbering from 1
  expected=1
  for pn in $phase_nums; do
    if [[ "$pn" -ne "$expected" ]]; then
      err "Phase numbering gap: expected Phase $expected, found Phase $pn"
    fi
    expected=$((expected + 1))
  done

  # Check for duplicate phase numbers
  dup_phases=$(echo "$phase_nums" | tr ' ' '\n' | sort -n | uniq -d)
  if [[ -n "$dup_phases" ]]; then
    err "Duplicate phase numbers: $dup_phases"
  fi

  # Check each phase heading format: ## [emoji] Phase N Title
  while IFS= read -r line; do
    if ! echo "$line" | grep -qP '^## \S+ Phase \d+ .+'; then
      err "Phase heading missing title: $line"
    fi
  done < <(grep -P '^## .* Phase \d+' "$plan" || true)
fi

# Section 4: Tasks
echo "Checking section 4: Tasks"

# Check task numbering within each phase (sequential, no gaps/dupes)
task_errors=$(awk '
  /^## .* Phase [0-9]+/ {
    if (match($0, /Phase ([0-9]+)/, arr)) {
      cur_phase = arr[1]
      expected_task = 1
      phase_has_tasks = 0
    }
  }
  /^- .+ Task [0-9]+\.[0-9]+/ {
    if (match($0, /Task ([0-9]+)\.([0-9]+)/, arr)) {
      tp = arr[1]; tt = arr[2]
      phase_has_tasks = 1
      if (tp != cur_phase) {
        print "Task " tp "." tt " belongs to Phase " tp " but is under Phase " cur_phase
      } else if (tt != expected_task) {
        print "Task numbering gap in Phase " cur_phase ": expected Task " cur_phase "." expected_task ", found Task " tp "." tt
      }
      expected_task++
    }
  }
' "$plan" || true)

if [[ -n "$task_errors" ]]; then
  while IFS= read -r line; do
    err "$line"
  done <<< "$task_errors"
fi

total_tasks=$(grep -cP '^- \S+ Task \d+\.\d+' "$plan" || true)
if [[ "$total_tasks" -eq 0 ]]; then
  err "No tasks found in any phase"
fi

# Section 5: Emoji Validity
echo "Checking section 5: Emoji Validity"

# Tasks with invalid emojis
invalid_tasks=$(awk '
  /^- .+ Task/ {
    em = $2
    if (em != "☐" && em != "❓" && em != "⚙️" && em != "❌" && em != "☑") {
      print NR ": " $0
      count++
    }
  }
  END { exit (count + 0 > 0) ? 1 : 0 }
' "$plan" || true)

if [[ -n "$invalid_tasks" ]]; then
  while IFS= read -r line; do
    err "Task with invalid emoji: $line"
  done <<< "$invalid_tasks"
fi

# Phases with invalid emojis
invalid_phases=$(awk '
  /^## .* Phase [0-9]+/ {
    em = $2
    if (em != "☐" && em != "❓" && em != "⚙️" && em != "❌" && em != "☑") {
      print NR ": " $0
      count++
    }
  }
  END { exit (count + 0 > 0) ? 1 : 0 }
' "$plan" || true)

if [[ -n "$invalid_phases" ]]; then
  while IFS= read -r line; do
    err "Phase with invalid emoji: $line"
  done <<< "$invalid_phases"
fi

# Section 6: Zero-Task Phases
echo "Checking section 6: Zero-Task Phases"

empty_phases=$(awk '
  /^## .* Phase [0-9]+/ {
    if (phase_seen && task_count == 0) {
      if (match($prev, /Phase ([0-9]+)/, arr)) print "Phase " arr[1]
    }
    phase_seen = 1
    task_count = 0
  }
  /^- .+ Task/ { task_count++ }
  { prev = $0 }
  END {
    if (phase_seen && task_count == 0) {
      if (match(prev, /Phase ([0-9]+)/, arr)) print "Phase " arr[1]
    }
  }
' "$plan")

if [[ -n "$empty_phases" ]]; then
  while IFS= read -r phase; do
    warn "$phase has zero tasks (can never reach Done)"
  done <<< "$empty_phases"
fi

# Section 7: Emoji Derivation (Phase from Tasks)
echo "Checking section 7: Phase Emoji Derivation"

if [[ -n "$phase_nums" ]]; then
  for pn in $phase_nums; do
    derived=$(derive_phase_emoji "$plan" "$pn")
    current=$(get_phase_emoji_from_file "$plan" "$pn")
    if [[ "$derived" != "$current" ]]; then
      err "Phase $pn: emoji is '$current' but should be '$derived' (derived from tasks)"
    fi
  done
fi

# Section 8: Emoji Derivation (Plan from Phases)
echo "Checking section 8: Plan Emoji Derivation"

derived_plan=$(derive_plan_emoji "$plan")
file_plan_emoji=$(get_plan_emoji_from_file "$plan")
if [[ "$derived_plan" != "$file_plan_emoji" ]]; then
  err "Plan emoji is '$file_plan_emoji' but should be '$derived_plan' (derived from phases)"
fi

# Summary
echo ""
if [[ "$errors" -eq 0 ]]; then
  echo "PASS: PLAN.md passes all checks ($total_tasks tasks, $phases phases)"
  if [[ "$warnings" -gt 0 ]]; then
    echo "  ($warnings warning(s))"
  fi
  exit 0
else
  echo "FAIL: $errors error(s) found"
  if [[ "$warnings" -gt 0 ]]; then
    echo "  ($warnings warning(s))"
  fi
  exit 1
fi
