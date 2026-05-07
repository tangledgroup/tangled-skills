#!/usr/bin/env bash
# workflow.sh — Full workflow: lock → edit → validate
# Usage: workflow.sh <PLAN.md> <action> [args...]
#
# Combines update-plan.sh and validate-plan.sh in one atomic operation.
# Edits are applied under flock, then the plan is validated before releasing
# the lock. If validation fails, the file is rolled back from backup.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
  echo "Usage: $0 <PLAN.md> <action> [args...]"
  echo ""
  echo "Full workflow: lock → edit → validate (atomic)"
  echo ""
  echo "Actions (same as update-plan.sh):"
  echo "  set-task-status <Task X.Y> <emoji>"
  echo "  set-phase-status <Phase X> <emoji>"
  echo "  update-timestamp"
  echo "  set-current-task <value>"
  echo "  set-current-phase <value>"
  exit "${1:-0}"
}

[[ $# -eq 0 ]] && usage 1
[[ "$1" == "--help" || "$1" == "-h" ]] && usage 0
[[ $# -lt 2 ]] && usage 1

plan="$1"
action="$2"
shift 2

if [[ ! -f "$plan" ]]; then
  echo "✗ File not found: $plan"
  exit 1
fi

lockfile="${plan}.lock"
backup="${plan}.bak"
tmpfile=""

cleanup() {
  rm -f "$backup" "$tmpfile" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

(
  flock -w 30 200 || { echo "✗ Timeout waiting for PLAN.md lock"; exit 1; }

  # Safety backup
  cp -- "$plan" "$backup"

  # Apply edit via update-plan.sh (without its own locking — we hold the lock)
  plan_dir=$(dirname "$plan")
  tmpfile=$(mktemp "${plan_dir}/.plan-edit.$$-XXXXXX")
  cp -- "$plan" "$tmpfile"

  case "$action" in
    set-task-status)
      [[ $# -lt 2 ]] && { echo "✗ Usage: set-task-status <Task X.Y> <emoji>"; exit 1; }
      escaped_id=$(echo "$1" | sed 's/\./\\./g')
      sed -i -E "s/^- (.+) ${escaped_id} /- ${2} ${escaped_id} /" "$tmpfile"
      ;;
    set-phase-status)
      [[ $# -lt 2 ]] && { echo "✗ Usage: set-phase-status <Phase X> <emoji>"; exit 1; }
      sed -i -E "s/^## (.+) ${1} /## ${2} ${1} /" "$tmpfile"
      ;;
    update-timestamp)
      sed -i "s/^\*\*Updated:\*\* .*/\*\*Updated:\*\* $(date -u +%Y-%m-%dT%H:%M:%SZ)/" "$tmpfile"
      ;;
    set-current-task)
      [[ $# -lt 1 ]] && { echo "✗ Usage: set-current-task <value>"; exit 1; }
      safe_val=$(printf '%s\n' "$1" | sed 's/[&\/\\]/\\&/g')
      sed -i "s/^\*\*Current Task:\*\* .*/\*\*Current Task:\*\* ${safe_val}/" "$tmpfile"
      ;;
    set-current-phase)
      [[ $# -lt 1 ]] && { echo "✗ Usage: set-current-phase <value>"; exit 1; }
      safe_val=$(printf '%s\n' "$1" | sed 's/[&\/\\]/\\&/g')
      sed -i "s/^\*\*Current Phase:\*\* .*/\*\*Current Phase:\*\* ${safe_val}/" "$tmpfile"
      ;;
    *)
      echo "✗ Unknown action: $action"
      rm -f "$tmpfile"
      exit 1
      ;;
  esac

  # Atomic rename
  mv -f "$tmpfile" "$plan"

  # Validate under lock
  if "$SCRIPT_DIR/validate-plan.sh" "$plan"; then
    echo "✓ Edit applied and validated: $plan"
    rm -f "$backup"
  else
    echo "✗ Validation failed — rolling back"
    mv -f "$backup" "$plan"
    exit 1
  fi

) 200>"$lockfile"
