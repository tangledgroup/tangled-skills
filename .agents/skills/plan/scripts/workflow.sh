#!/usr/bin/env bash
# workflow.sh - Full workflow: lock → edit → derive → validate (atomic)
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

[[ $# -eq 0 ]] && print_usage "$0" 1
[[ "$1" == "--help" || "$1" == "-h" ]] && print_usage "$0" 0
[[ $# -lt 2 ]] && print_usage "$0" 1

plan="$1"
action="$2"
shift 2

check_plan_file "$plan"

lockfile="${plan}.lock"
backup="${plan}.bak"

cleanup() {
  cleanup_temp "$backup"
  release_lock "$lockfile"
}
trap cleanup EXIT INT TERM

# Read-only actions pass through without locking
if is_read_action "$action"; then
  bash "$SCRIPT_DIR/update-plan.sh" "$plan" "$action" "$@"
  exit $?
fi

(
  acquire_lock "$lockfile"

  # Safety backup
  cp -- "$plan" "$backup"

  # Delegate the edit + per-phase derive to update-plan.sh (skip its lock - we hold it)
  PLAN_SKIP_LOCK=1 bash "$SCRIPT_DIR/update-plan.sh" "$plan" "$action" "$@"

  # Re-derive ALL phase emojis + plan emoji for robustness
  plan_dir=$(dirname "$plan")
  tmpfile=$(mktemp "${plan_dir}/.plan-edit.$$-XXXXXX")
  cp -- "$plan" "$tmpfile"
  rederive_all "$tmpfile"

  # Atomic rename
  atomic_write "$plan" "$tmpfile"

  # Validate under lock
  if "$SCRIPT_DIR/validate-plan.sh" "$plan"; then
    echo "OK: Edit applied and validated: $plan"
    rm -f "$backup"
  else
    echo "ERROR: Validation failed - rolling back"
    mv -f "$backup" "$plan"
    exit 1
  fi

) 200>"$lockfile"
exit "$?"
