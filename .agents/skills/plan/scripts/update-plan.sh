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
#   get-current-task                     Print **Current Task:** value
#   set-current-phase <value>            Set **Current Phase:** field
#   get-current-phase                    Print **Current Phase:** value
#   set-plan-title <title>               Set plan title (after "# [emoji] Plan: ")
#   get-plan-title                       Print plan title
#   set-depends-on <value>               Set **Depends On:** field
#   get-depends-on                       Print **Depends On:** value
#   get-created                          Print **Created:** timestamp
#   get-plan-header                      Print all header fields as key=value
#   rederive-all                         Re-derive all phase + plan emojis
#
# After set-task-status / set-phase-status, this script auto-derives the
# affected phase emoji and the plan emoji from their tasks/phases.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# ── Usage ────────────────────────────────────────────────────────────

usage() {
  cat <<EOF
Usage: $0 <PLAN.md> <action> [args...]

Atomic lock-and-edit for workflow PLAN.md files.

Actions:
  set-task-status <Task X.Y> <emoji>    Set task status
  set-phase-status <Phase X> <emoji>    Set phase status
  get-task-status <Task X.Y>            Print task emoji
  get-phase-status <Phase X>            Print phase emoji
  get-plan-status                       Print plan emoji
  update-timestamp                      Update timestamp to now
  set-current-task <value>              Set Current Task field
  get-current-task                      Print Current Task value
  set-current-phase <value>             Set Current Phase field
  get-current-phase                     Print Current Phase value
  set-plan-title <title>                Set plan title
  get-plan-title                        Print plan title
  set-depends-on <value>                Set Depends On field
  get-depends-on                        Print Depends On value
  get-created                           Print Created timestamp
  get-plan-header                       Print all header fields
  rederive-all                          Re-derive all phase + plan emojis

Valid emojis: ☐ ❓ ⚙️ ❌ ☑
EOF
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
tmpfile=""

cleanup() {
  cleanup_temp "$tmpfile" "${tmpfile:-}.new"
  release_lock "$lockfile"
}
trap cleanup EXIT INT TERM

# ── Read-only actions (deterministic, no lock) ───────────────────────

do_read() {
  case "$action" in
    get-task-status)
      [[ $# -lt 1 ]] && { echo "✗ Usage: get-task-status <Task X.Y>"; exit 1; }
      awk -v tid="$1" '
        /^- [^ ]+ / && match($0, /^- [^ ]+ (Task [0-9]+\.[0-9]+) /, arr) {
          if (arr[1] == tid) { print $2; found=1; exit }
        }
        END { if (!found) { print "✗ Task not found: " tid > "/dev/stderr"; exit 1 } }
      ' "$plan"
      ;;
    get-phase-status)
      [[ $# -lt 1 ]] && { echo "✗ Usage: get-phase-status <Phase X>"; exit 1; }
      awk -v pid="$1" '
        /^## [^ ]+ Phase [0-9]+/ && match($0, /## [^ ]+ (Phase [0-9]+) /, arr) {
          if (arr[1] == pid) { print $2; found=1; exit }
        }
        END { if (!found) { print "✗ Phase not found: " pid > "/dev/stderr"; exit 1 } }
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
      awk '/^# \S+ Plan:/ { sub(/^# \S+ Plan: */, ""); print; exit }' "$plan"
      ;;
    get-depends-on)
      local val
      val=$(get_header_field "$plan" "Depends On")
      [[ -z "$val" ]] && echo "NONE" || echo "$val"
      ;;
    get-created)
      get_header_field "$plan" "Created"
      ;;
    get-plan-header)
      echo "plan-title=$(get_header_field_helper_plan_title "$plan")"
      echo "depends-on=$(get_header_field "$plan" "Depends On")"
      echo "created=$(get_header_field "$plan" "Created")"
      echo "updated=$(get_header_field "$plan" "Updated")"
      echo "current-phase=$(get_header_field "$plan" "Current Phase")"
      echo "current-task=$(get_header_field "$plan" "Current Task")"
      ;;
    *)
      echo "✗ Unknown read action: $action" >&2
      exit 1
      ;;
  esac
}

# Helper for plan-title (special format: # [emoji] Plan: title)
get_header_field_helper_plan_title() {
  awk '/^# \S+ Plan:/ { sub(/^# \S+ Plan: */, ""); print; exit }' "$1"
}

# ── Pre-flight validation (before any temp files are created) ───────

preflight() {
  case "$action" in
    set-task-status)
      if [[ $# -lt 2 ]]; then echo "✗ Usage: set-task-status <Task X.Y> <emoji>"; exit 1; fi
      if ! is_valid_emoji "$2"; then
        echo "✗ Invalid emoji: $2 (valid: ☐ ❓ ⚙️ ❌ ☑)" >&2
        exit 1
      fi
      ;;
    set-phase-status)
      if [[ $# -lt 2 ]]; then echo "✗ Usage: set-phase-status <Phase X> <emoji>"; exit 1; fi
      if ! is_valid_emoji "$2"; then
        echo "✗ Invalid emoji: $2 (valid: ☐ ❓ ⚙️ ❌ ☑)" >&2
        exit 1
      fi
      ;;
    set-current-task|set-current-phase)
      if [[ $# -lt 1 ]]; then echo "✗ Usage: set-${action#set-} <value>"; exit 1; fi
      ;;
    set-plan-title|set-depends-on)
      if [[ $# -lt 1 ]]; then echo "✗ Usage: $action <value>"; exit 1; fi
      ;;
  esac
  return 0
}

# ── Write actions (lock + atomic rename) ────────────────────────────

do_edit() {
  local plan_dir
  plan_dir=$(dirname "$plan")
  tmpfile=$(mktemp "${plan_dir}/.plan-edit.$$-XXXXXX")
  cp -- "$plan" "$tmpfile"

  local affected_phase=""

  case "$action" in
    set-task-status)
      local task_id="$1" emoji="$2"
      affected_phase=$(printf '%s' "$task_id" | grep -oP '(?<=Task )\d+' || true)
      if ! awk -v tid="$task_id" -v em="$emoji" '
        /^- [^ ]+ / && match($0, /^- [^ ]+ (Task [0-9]+\.[0-9]+) /, arr) {
          if (arr[1] == tid) { sub(/^- [^ ]+ /, "- " em " "); found=1 }
        }
        { print }
        END { if (!found) { print "✗ Task not found: " tid > "/dev/stderr"; exit 1 } }
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
        END { if (!found) { print "✗ Phase not found: " pid > "/dev/stderr"; exit 1 } }
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
      awk -v title="$1" '{
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

  atomic_write "$plan" "$tmpfile"
  tmpfile=""
}

# ── Main dispatch ───────────────────────────────────────────────────

case "$action" in
  get-task-status|get-phase-status|get-plan-status|\
  get-current-task|get-current-phase|get-plan-title|get-depends-on|\
  get-created|get-plan-header)
    do_read "$@"
    ;;
  *)
    # Pre-flight validation (before any temp files or locks)
    preflight "$@"

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
    echo "✓ Applied '$action' to $plan"
    ;;
esac
