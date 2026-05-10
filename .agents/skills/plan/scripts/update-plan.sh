#!/usr/bin/env bash
# update-plan.sh - Atomic lock-and-edit for PLAN.md files
# Usage: update-plan.sh <PLAN.md> <action> [args...]
#
# Actions:
#   set-task-status <Task X.Y> <emoji>   Set task status (NotStarted Question Doing Error Done)
#   set-phase-status <Phase X> <emoji>   Set phase status (NotStarted Question Doing Error Done)
#   get-task-status <Task X.Y>           Print current task emoji
#   get-phase-status <Phase X>           Print current phase emoji
#   get-plan-status                      Print current plan emoji
#   update-timestamp                     Update Updated field to current UTC time
#   set-current-task <value>             Set Current Task field
#   get-current-task                     Print Current Task value
#   set-current-phase <value>            Set Current Phase field
#   get-current-phase                    Print Current Phase value
#   set-plan-title <title>               Set plan title (after "# [emoji] Plan: ")
#   get-plan-title                       Print plan title
#   set-depends-on <value>               Set Depends On field
#   get-depends-on                       Print Depends On value
#   get-created                          Print Created timestamp
#   get-plan-header                      Print all header fields as key=value
#   rederive-all                         Re-derive all phase + plan emojis
#
# After set-task-status / set-phase-status, this script auto-derives the
# affected phase emoji and the plan emoji from their tasks/phases.

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
tmpfile=""

cleanup() {
  cleanup_temp "$tmpfile" "${tmpfile:-}.new"
  release_lock "$lockfile"
}
trap cleanup EXIT INT TERM

# Read-only actions (deterministic, no lock)
do_read() {
  case "$action" in
    get-task-status)
      if [[ $# -lt 1 ]]; then echo "ERROR: Usage: get-task-status <Task X.Y>"; exit 1; fi
      awk -v tid="$1" '
        /^- [^ ]+ / && match($0, /^- [^ ]+ (Task [0-9]+\.[0-9]+) /, arr) {
          if (arr[1] == tid) { print $2; found=1; exit }
        }
        END { if (!found) { print "ERROR: Task not found: " tid > "/dev/stderr"; exit 1 } }
      ' "$plan"
      ;;
    get-phase-status)
      if [[ $# -lt 1 ]]; then echo "ERROR: Usage: get-phase-status <Phase X>"; exit 1; fi
      awk -v pid="$1" '
        /^## [^ ]+ Phase [0-9]+/ && match($0, /## [^ ]+ (Phase [0-9]+) /, arr) {
          if (arr[1] == pid) { print $2; found=1; exit }
        }
        END { if (!found) { print "ERROR: Phase not found: " pid > "/dev/stderr"; exit 1 } }
      ' "$plan"
      ;;
    get-plan-status)
      get_plan_emoji_from_file "$plan"
      ;;
    get-current-task)
      get_header_field "$plan" "Current Task"
      ;;
    get-current-phase)
      get_header_field "$plan" "Current Phase"
      ;;
    get-plan-title)
      get_plan_title_from_file "$plan"
      ;;
    get-depends-on)
      local val
      val=$(get_header_field "$plan" "Depends On")
      if [[ -z "$val" ]]; then echo "NONE"; else echo "$val"; fi
      ;;
    get-created)
      get_header_field "$plan" "Created"
      ;;
    get-plan-header)
      echo "plan-title=$(get_plan_title_from_file "$plan")"
      echo "depends-on=$(get_header_field "$plan" "Depends On")"
      echo "created=$(get_header_field "$plan" "Created")"
      echo "updated=$(get_header_field "$plan" "Updated")"
      echo "current-phase=$(get_header_field "$plan" "Current Phase")"
      echo "current-task=$(get_header_field "$plan" "Current Task")"
      ;;
    *)
      echo "ERROR: Unknown read action: $action" >&2
      exit 1
      ;;
  esac
}

# Write actions (lock + atomic rename)
do_edit() {
  local plan_dir
  plan_dir=$(dirname "$plan")
  tmpfile=$(mktemp "${plan_dir}/.plan-edit.$$-XXXXXX")
  cp -- "$plan" "$tmpfile"

  local affected_phase=""
  local changed_task_id="" changed_task_emoji=""

  case "$action" in
    set-task-status)
      local task_id="$1" emoji="$2"
      changed_task_id="$task_id"
      changed_task_emoji="$emoji"
      affected_phase=$(printf '%s' "$task_id" | grep -oP '(?<=Task )\d+' || true)
      if ! awk -v tid="$task_id" -v em="$emoji" '
        /^- [^ ]+ / && match($0, /^- [^ ]+ (Task [0-9]+\.[0-9]+) /, arr) {
          if (arr[1] == tid) { sub(/^- [^ ]+ /, "- " em " "); found=1 }
        }
        { print }
        END { if (!found) { print "ERROR: Task not found: " tid > "/dev/stderr"; exit 1 } }
      ' "$tmpfile" > "${tmpfile}.new"; then
        rm -f "${tmpfile}.new" 2>/dev/null || true
        return 1
      fi
      mv -f "${tmpfile}.new" "$tmpfile"
      ;;
    set-phase-status)
      local phase_id="$1" emoji="$2"
      affected_phase=$(printf '%s' "$phase_id" | grep -oP '(?<=Phase )\d+' || true)
      if ! awk -v pid="$phase_id" -v em="$emoji" '
        /^## [^ ]+ Phase [0-9]+/ && match($0, /## [^ ]+ (Phase [0-9]+) /, arr) {
          if (arr[1] == pid) { sub(/^## [^ ]+ /, "## " em " "); found=1 }
        }
        { print }
        END { if (!found) { print "ERROR: Phase not found: " pid > "/dev/stderr"; exit 1 } }
      ' "$tmpfile" > "${tmpfile}.new"; then
        rm -f "${tmpfile}.new" 2>/dev/null || true
        return 1
      fi
      mv -f "${tmpfile}.new" "$tmpfile"
      ;;
    update-timestamp)
      set_header_field_in_file "$tmpfile" "Updated" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      ;;
    set-current-task)
      set_header_field_in_file "$tmpfile" "Current Task" "$1"
      ;;
    set-current-phase)
      set_header_field_in_file "$tmpfile" "Current Phase" "$1"
      ;;
    set-plan-title)
      local escaped_title
      escaped_title=$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g')
      awk -v title="$escaped_title" '{
        if ($0 ~ /^# .* Plan:/) {
          match($0, /^# ([^ ]+) Plan:/, arr)
          print "# " arr[1] " Plan: " title
          next
        }
        print
      }' "$tmpfile" > "${tmpfile}.new" && mv -f "${tmpfile}.new" "$tmpfile"
      ;;
    set-depends-on)
      set_header_field_in_file "$tmpfile" "Depends On" "$1"
      ;;
    rederive-all)
      rederive_all "$tmpfile"
      ;;
  esac

  # Auto-derive phase emoji if a task or phase was changed
  if [[ -n "$affected_phase" ]]; then
    local derived current
    derived=$(derive_phase_emoji "$tmpfile" "$affected_phase")
    current=$(get_phase_emoji_from_file "$tmpfile" "$affected_phase")
    if [[ "$derived" != "$current" ]]; then
      echo "  → Phase $affected_phase: $current → $derived (auto-derived from tasks)"
      update_phase_emoji_in_file "$tmpfile" "$affected_phase" "$derived"
    fi
  fi

  # Auto-derive plan emoji from phases (skip for rederive-all since it already did)
  if [[ "$action" != "rederive-all" ]]; then
    local derived_plan file_plan_emoji
    derived_plan=$(derive_plan_emoji "$tmpfile")
    file_plan_emoji=$(get_plan_emoji_from_file "$tmpfile")
    if [[ "$derived_plan" != "$file_plan_emoji" ]]; then
      echo "  → Plan: $file_plan_emoji → $derived_plan (auto-derived from phases)"
      update_plan_emoji_in_file "$tmpfile" "$file_plan_emoji" "$derived_plan"
    fi
  fi

  # Sync Current Task and Current Phase header emojis with actual statuses
  if [[ "$action" == "set-task-status" || "$action" == "set-phase-status" || "$action" == "rederive-all" ]]; then
    sync_current_task_emoji "$tmpfile"
    sync_current_phase_emoji "$tmpfile"

    # Auto-advance if a task was just completed
    if [[ "$action" == "set-task-status" && "$changed_task_emoji" == "$EM_DONE" ]]; then
      advance_current_on_completion "$tmpfile" "$changed_task_id"
    fi
  fi

  # Sync Current Phase header when current phase is set manually
  if [[ "$action" == "set-current-phase" ]]; then
    sync_current_phase_emoji "$tmpfile"
  fi

  # Sync Current Task header when current task is set manually
  if [[ "$action" == "set-current-task" ]]; then
    sync_current_task_emoji "$tmpfile"
  fi

  atomic_write "$plan" "$tmpfile"
  tmpfile=""
}

# Main dispatch
if is_read_action "$action"; then
  do_read "$@"
else
  # Pre-flight validation (before any temp files or locks)
  preflight_check "$action" "$@"

  if [[ -z "${PLAN_SKIP_LOCK:-}" ]]; then
    exec 200>"$lockfile"
    acquire_lock "$lockfile"
    set +e
    do_edit "$@"
    rc=$?
    set -e
    # Ensure tmpfile is cleaned even on failure (cleanup trap handles it)
    if [[ $rc -ne 0 ]]; then
      exit $rc
    fi
  else
    do_edit "$@"
  fi
  echo "OK: Applied '$action' to $plan"
fi
