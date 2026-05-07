#!/usr/bin/env bash
# workflow.sh — Full workflow: lock → edit → derive → validate
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
#   set-current-phase <value>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
  echo "Usage: $0 <PLAN.md> <action> [args...]"
  echo ""
  echo "Full workflow: lock → edit → derive → validate (atomic)"
  echo ""
  echo "Actions:"
  echo "  set-task-status <Task X.Y> <emoji>"
  echo "  set-phase-status <Phase X> <emoji>"
  echo "  get-task-status <Task X.Y>"
  echo "  get-phase-status <Phase X>"
  echo "  get-plan-status"
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
  echo "✗ File not found: $plan" >&2
  exit 1
fi

lockfile="${plan}.lock"
backup="${plan}.bak"
tmpfile=""

cleanup() {
  rm -f "$backup" "$tmpfile" "${tmpfile}.new" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Read-only actions pass through without locking
case "$action" in
  get-task-status|get-phase-status|get-plan-status)
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

  # --- Re-derive ALL phase emojis (not just affected) for robustness ---
  plan_dir=$(dirname "$plan")
  tmpfile=$(mktemp "${plan_dir}/.plan-edit.$$-XXXXXX")
  cp -- "$plan" "$tmpfile"

  phase_nums=$(awk '/^## .* Phase [0-9]+/ { if (match($0, /Phase ([0-9]+)/, arr)) print arr[1] }' "$tmpfile")
  for pn in $phase_nums; do
    derived=$(bash "$SCRIPT_DIR/derive-phase-emoji.sh" "$tmpfile" "$pn")
    current=$(awk -v pn="$pn" '/^## .* Phase [0-9]+/ {
      if (match($0, /Phase ([0-9]+)/, arr) && arr[1] == pn) { print $2; exit }
    }' "$tmpfile")
    if [[ "$derived" != "$current" ]]; then
      echo "  → Phase $pn: $current → $derived (auto-derived from tasks)"
      awk -v pn="$pn" -v em="$derived" '
        /^## .* Phase [0-9]+/ && match($0, /Phase ([0-9]+)/, arr) && arr[1] == pn {
          sub(/^## [^ ]+ /, "## " em " "); print; next
        }
        { print }
      ' "$tmpfile" > "${tmpfile}.new" && mv -f "${tmpfile}.new" "$tmpfile"
    fi
  done

  # --- Re-derive plan emoji from phases ---
  derived_plan=$(bash "$SCRIPT_DIR/derive-plan-emoji.sh" "$tmpfile")
  file_plan_emoji=$(head -1 "$tmpfile" | grep -oP '^\# \K\S+')
  if [[ "$derived_plan" != "$file_plan_emoji" ]]; then
    echo "  → Plan: $file_plan_emoji → $derived_plan (auto-derived from phases)"
    sed -i "s/^# ${file_plan_emoji} /# ${derived_plan} /" "$tmpfile"
  fi

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
