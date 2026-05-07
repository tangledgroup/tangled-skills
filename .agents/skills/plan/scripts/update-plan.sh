#!/usr/bin/env bash
# update-plan.sh — Atomic lock-and-edit for PLAN.md files
# Usage: update-plan.sh <PLAN.md> <action> [args...]
#
# Actions:
#   set-task-status <Task X.Y> <emoji>   Set task status (☐ ❓ ⚙️ ❌ ☑)
#   set-phase-status <Phase X> <emoji>   Set phase status (☐ ❓ ⚙️ ❌ ☑)
#   get-task-status <Task X.Y>           Print current task emoji
#   get-phase-status <Phase X>           Print current phase emoji
#   get-plan-status                      Print current plan emoji
#   update-timestamp                     Update **Updated:** to current UTC time
#   set-current-task <value>             Set **Current Task:** field
#   set-current-phase <value>            Set **Current Phase:** field
#
# After set-task-status / set-phase-status, this script auto-derives the
# affected phase emoji and the plan emoji from their tasks/phases.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
  echo "Usage: $0 <PLAN.md> <action> [args...]"
  echo ""
  echo "Atomic lock-and-edit for workflow PLAN.md files."
  echo ""
  echo "Actions:"
  echo "  set-task-status <Task X.Y> <emoji>    Set task status"
  echo "  set-phase-status <Phase X> <emoji>    Set phase status"
  echo "  get-task-status <Task X.Y>            Print task emoji"
  echo "  get-phase-status <Phase X>            Print phase emoji"
  echo "  get-plan-status                       Print plan emoji"
  echo "  update-timestamp                      Update timestamp to now"
  echo "  set-current-task <value>              Set Current Task field"
  echo "  set-current-phase <value>             Set Current Phase field"
  echo ""
  echo "Valid emojis: ☐ ❓ ⚙️ ❌ ☑"
  exit "${1:-0}"
}

[[ $# -eq 0 ]] && usage 1
[[ "$1" == "--help" || "$1" == "-h" ]] && usage 0
[[ $# -lt 2 ]] && usage 1

plan="$1"
action="$2"
shift 2

if [[ ! -f "$plan" ]]; then
  echo "✗ File not found: $plan" >&2
  exit 1
fi

lockfile="${plan}.lock"
tmpfile=""

cleanup() {
  rm -f "$tmpfile" "${tmpfile}.new" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# ── Read-only actions (no lock needed) ──────────────────────────────

do_read() {
  case "$action" in
    get-task-status)
      [[ $# -lt 1 ]] && { echo "✗ Usage: get-task-status <Task X.Y>"; exit 1; }
      local task_id="$1"
      awk -v tid="$task_id" '
        $0 ~ ("^- .* " tid " ") { print $2; found=1; exit }
        END { if (!found) { print "✗ Task not found: " tid > "/dev/stderr"; exit 1 } }
      ' "$plan"
      ;;
    get-phase-status)
      [[ $# -lt 1 ]] && { echo "✗ Usage: get-phase-status <Phase X>"; exit 1; }
      local phase_id="$1"
      awk -v pid="$phase_id" '
        $0 ~ ("^## .* " pid " ") { print $2; found=1; exit }
        END { if (!found) { print "✗ Phase not found: " pid > "/dev/stderr"; exit 1 } }
      ' "$plan"
      ;;
    get-plan-status)
      head -1 "$plan" | grep -oP '^\# \K\S+' || { echo "✗ Could not read plan status" >&2; exit 1; }
      ;;
    *)
      echo "✗ Unknown read action: $action" >&2
      exit 1
      ;;
  esac
}

# ── Write actions (lock + atomic rename) ────────────────────────────

do_edit() {
  local plan_dir
  plan_dir=$(dirname "$plan")
  local tmpfile
  tmpfile=$(mktemp "${plan_dir}/.plan-edit.$$-XXXXXX")
  cp -- "$plan" "$tmpfile"

  local affected_phase=""

  case "$action" in
    set-task-status)
      [[ $# -lt 2 ]] && { echo "✗ Usage: set-task-status <Task X.Y> <emoji>"; exit 1; }
      local task_id="$1" emoji="$2"
      # Extract phase number from task ID (e.g., "Task 2.3" → 2)
      affected_phase=$(printf '%s' "$task_id" | grep -oP '(?<=Task )\d+' || true)
      # Use awk for precise single-line match (accounts for emoji between "- " and task ID)
      awk -v tid="$task_id" -v em="$emoji" '
        $0 ~ ("^- .* " tid " ") { sub(/^- [^ ]+ /, "- " em " "); found=1 }
        { print }
        END { if (!found) { print "✗ Task not found: " tid > "/dev/stderr"; exit 1 } }
      ' "$tmpfile" > "${tmpfile}.new" && mv -f "${tmpfile}.new" "$tmpfile"
      ;;
    set-phase-status)
      [[ $# -lt 2 ]] && { echo "✗ Usage: set-phase-status <Phase X> <emoji>"; exit 1; }
      local phase_id="$1" emoji="$2"
      affected_phase=$(printf '%s' "$phase_id" | grep -oP '(?<=Phase )\d+' || true)
      awk -v pid="$phase_id" -v em="$emoji" '
        $0 ~ ("^## .* " pid " ") { sub(/^## [^ ]+ /, "## " em " "); found=1 }
        { print }
        END { if (!found) { print "✗ Phase not found: " pid > "/dev/stderr"; exit 1 } }
      ' "$tmpfile" > "${tmpfile}.new" && mv -f "${tmpfile}.new" "$tmpfile"
      ;;
    update-timestamp)
      sed -i "s/^\*\*Updated:\*\* .*/\*\*Updated:\*\* $(date -u +%Y-%m-%dT%H:%M:%SZ)/" "$tmpfile"
      ;;
    set-current-task)
      [[ $# -lt 1 ]] && { echo "✗ Usage: set-current-task <value>"; exit 1; }
      local safe_val
      safe_val=$(printf '%s\n' "$1" | sed 's/[&\/\\]/\\&/g')
      sed -i "s/^\*\*Current Task:\*\* .*/\*\*Current Task:\*\* ${safe_val}/" "$tmpfile"
      ;;
    set-current-phase)
      [[ $# -lt 1 ]] && { echo "✗ Usage: set-current-phase <value>"; exit 1; }
      local safe_val
      safe_val=$(printf '%s\n' "$1" | sed 's/[&\/\\]/\\&/g')
      sed -i "s/^\*\*Current Phase:\*\* .*/\*\*Current Phase:\*\* ${safe_val}/" "$tmpfile"
      ;;
    *)
      echo "✗ Unknown action: $action" >&2
      exit 1
      ;;
  esac

  # Auto-derive phase emoji if a task or phase was changed
  if [[ -n "$affected_phase" ]]; then
    derived=$(bash "$SCRIPT_DIR/derive-phase-emoji.sh" "$tmpfile" "$affected_phase")
    current=$(awk -v pn="$affected_phase" '
      /^## .* Phase [0-9]+/ {
        if (match($0, /Phase ([0-9]+)/, arr) && arr[1] == pn) { print $2; exit }
      }
    ' "$tmpfile")
    if [[ "$derived" != "$current" ]]; then
      echo "  → Phase $affected_phase: $current → $derived (auto-derived from tasks)"
      awk -v pn="$affected_phase" -v em="$derived" '
        /^## .* Phase [0-9]+/ && match($0, /Phase ([0-9]+)/, arr) && arr[1] == pn {
          sub(/^## [^ ]+ /, "## " em " "); print; next
        }
        { print }
      ' "$tmpfile" > "${tmpfile}.new" && mv -f "${tmpfile}.new" "$tmpfile"
    fi
  fi

  # Auto-derive plan emoji from phases
  derived_plan=$(bash "$SCRIPT_DIR/derive-plan-emoji.sh" "$tmpfile")
  file_plan_emoji=$(head -1 "$tmpfile" | grep -oP '^\# \K\S+')
  if [[ "$derived_plan" != "$file_plan_emoji" ]]; then
    echo "  → Plan: $file_plan_emoji → $derived_plan (auto-derived from phases)"
    sed -i "s/^# ${file_plan_emoji} /# ${derived_plan} /" "$tmpfile"
  fi

  mv -f "$tmpfile" "$plan"
}

# ── Main dispatch ───────────────────────────────────────────────────

case "$action" in
  get-task-status|get-phase-status|get-plan-status)
    do_read "$@"
    ;;
  *)
    if [[ -z "${PLAN_SKIP_LOCK:-}" ]]; then
      (
        flock -w 30 200 || { echo "✗ Timeout waiting for PLAN.md lock"; exit 1; }
        do_edit "$@"
      ) 200>"$lockfile"
    else
      do_edit "$@"
    fi
    echo "✓ Applied '$action' to $plan"
    ;;
esac
