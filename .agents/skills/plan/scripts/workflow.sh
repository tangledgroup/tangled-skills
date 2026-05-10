#!/usr/bin/env bash
# workflow.sh — Full workflow: lock → edit → derive → validate (atomic)
# Usage: workflow.sh <PLAN.md> <action> [args...]
#
# Wraps update-plan.sh with automatic validation and rollback.
# After applying the edit, it re-derives ALL phase emojis from tasks
# (not just the affected one), derives the plan emoji, validates,
# and rolls back if validation fails.
#
# Actions are the same as update-plan.sh:
#   set-task-status <Task X.Y> <emoji>
#   set-phase-status <Phase X> <emoji>
#   get-task-status <Task X.Y>
#   get-phase-status <Phase X>
#   get-plan-status
#   update-timestamp
#   set-current-task <value>
#   get-current-task
#   set-current-phase <value>
#   get-current-phase
#   set-plan-title <title>
#   get-plan-title
#   set-depends-on <value>
#   get-depends-on
#   get-created
#   get-plan-header
#   rederive-all

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/common.sh"

usage() {
  echo "Usage: $0 <PLAN.md> <action> [args...]"
  echo ""
  echo "Full workflow: lock → edit → derive → validate (atomic)"
  echo ""
  echo "Actions: same as update-plan.sh"
  exit "${1:-0}"
}

[[ $# -eq 0 ]] && usage 1
[[ "$1" == "--help" || "$1" == "-h" ]] && usage 0
[[ $# -lt 2 ]] && usage 1

plan="$1"
action="$2"
shift 2

check_plan_file "$plan"

lockfile="${plan}.lock"
backup="${plan}.bak"
tmpfile=""

cleanup() {
  rm -f "$backup" "$tmpfile" "${tmpfile}.new" 2>/dev/null || true
  # Remove the physical lock file — flock releases the advisory lock
  # when fd 200 closes, but the file itself persists on disk.
  rm -f "$lockfile" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Read-only actions pass through without locking
case "$action" in
  get-task-status|get-phase-status|get-plan-status|\
  get-current-task|get-current-phase|get-plan-title|get-depends-on|\
  get-created|get-plan-header)
    bash "$SCRIPT_DIR/update-plan.sh" "$plan" "$action" "$@"
    exit $?
    ;;
esac

(
  flock -w 30 200 || { echo "✗ Timeout waiting for PLAN.md lock"; exit 1; }

  # Safety backup
  cp -- "$plan" "$backup"

  # Delegate the edit + per-phase derive to update-plan.sh (skip its lock — we hold it)
  PLAN_SKIP_LOCK=1 bash "$SCRIPT_DIR/update-plan.sh" "$plan" "$action" "$@"

  # --- Re-derive ALL phase emojis + plan emoji for robustness ---
  plan_dir=$(dirname "$plan")
  tmpfile=$(mktemp "${plan_dir}/.plan-edit.$$-XXXXXX")
  cp -- "$plan" "$tmpfile"
  rederive_all "$tmpfile"

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
