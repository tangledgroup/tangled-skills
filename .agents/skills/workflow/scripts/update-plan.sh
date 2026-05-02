#!/usr/bin/env bash
# update-plan.sh — Atomic lock-and-edit for PLAN.md files
# Usage: update-plan.sh <PLAN.md> <action> [args...]
#
# Actions:
#   set-task-status <Task X.Y> <emoji>   Set task status (☐ ❓ ⚙️ ❌ ☑)
#   set-phase-status <Phase X> <emoji>   Set phase status (☐ ❓ ⚙️ ❌ ☑)
#   update-timestamp                     Update **Updated:** to current UTC time
#   set-current-task <value>             Set **Current Task:** field
#   set-current-phase <value>            Set **Current Phase:** field

set -euo pipefail

usage() {
  echo "Usage: $0 <PLAN.md> <action> [args...]"
  echo ""
  echo "Atomic lock-and-edit for workflow PLAN.md files."
  echo ""
  echo "Actions:"
  echo "  set-task-status <Task X.Y> <emoji>    Set task status"
  echo "  set-phase-status <Phase X> <emoji>    Set phase status"
  echo "  update-timestamp                       Update timestamp to now"
  echo "  set-current-task <value>               Set Current Task field"
  echo "  set-current-phase <value>              Set Current Phase field"
  echo ""
  echo "Valid emojis: ☐ ❓ ⚙️ ❌ ☑"
  exit "${1:-0}"
}

[[ $# -lt 2 ]] && usage 1
[[ "$1" == "--help" || "$1" == "-h" ]] && usage 0

plan="$1"
action="$2"
shift 2

if [[ ! -f "$plan" ]]; then
  echo "✗ File not found: $plan"
  exit 1
fi

lockfile="${plan}.lock"
tmpfile=""

cleanup() {
  rm -f "$tmpfile" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

do_edit() {
  local plan_dir
  plan_dir=$(dirname "$plan")
  local tmpfile
  tmpfile=$(mktemp "${plan_dir}/.plan-edit.$$-XXXXXX")
  cp -- "$plan" "$tmpfile"

  case "$action" in
    set-task-status)
      [[ $# -lt 2 ]] && { echo "✗ Usage: set-task-status <Task X.Y> <emoji>"; exit 1; }
      local task_id="$1" emoji="$2"
      # Escape dots in task ID for sed regex
      local escaped_id
      escaped_id=$(echo "$task_id" | sed 's/\./\\./g')
      sed -i -E "s/^- (.+) ${escaped_id} /- ${emoji} ${escaped_id} /" "$tmpfile"
      ;;
    set-phase-status)
      [[ $# -lt 2 ]] && { echo "✗ Usage: set-phase-status <Phase X> <emoji>"; exit 1; }
      local phase_id="$1" emoji="$2"
      sed -i -E "s/^## (.+) ${phase_id} /## ${emoji} ${phase_id} /" "$tmpfile"
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
      echo "✗ Unknown action: $action"
      exit 1
      ;;
  esac

  mv -f "$tmpfile" "$plan"
}

(
  flock -w 30 200 || { echo "✗ Timeout waiting for PLAN.md lock"; exit 1; }
  do_edit "$@"
) 200>"$lockfile"

echo "✓ Applied '$action' to $plan"
