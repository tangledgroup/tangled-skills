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
  echo "  get-current-task                      Print Current Task value"
  echo "  set-current-phase <value>             Set Current Phase field"
  echo "  get-current-phase                     Print Current Phase value"
  echo "  set-plan-title <title>                Set plan title"
  echo "  get-plan-title                        Print plan title"
  echo "  set-depends-on <value>                Set Depends On field"
  echo "  get-depends-on                        Print Depends On value"
  echo "  get-created                           Print Created timestamp"
  echo "  get-plan-header                       Print all header fields"
  echo "  rederive-all                          Re-derive all phase + plan emojis"
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

check_plan_file "$plan"

lockfile="${plan}.lock"
tmpfile=""

cleanup() {
  rm -f "$tmpfile" "${tmpfile}.new" 2>/dev/null || true
  # Remove lock file — flock advisory lock is released when fd closes,
  # but the physical lock file persists. Clean it up here.
  rm -f "$lockfile" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# ── Read-only actions (no lock needed) ──────────────────────────────

do_read() {
  case "$action" in
    get-task-status)
      [[ $# -lt 1 ]] && { echo "✗ Usage: get-task-status <Task X.Y>"; exit 1; }
      # Match task ID only at the start position, not in dependency refs
      awk -v tid="$1" '
        /^- [^ ]+ / && match($0, /^- [^ ]+ (Task [0-9]+\.[0-9]+) /, arr) {
          if (arr[1] == tid) { print $2; found=1; exit }
        }
        END { if (!found) { print "✗ Task not found: " tid > "/dev/stderr"; exit 1 } }
      ' "$plan"
      ;;
    get-phase-status)
      [[ $# -lt 1 ]] && { echo "✗ Usage: get-phase-status <Phase X>"; exit 1; }
      # Match phase ID only in the heading
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
      awk '/^\*\*Current Task:\*\*/ { sub(/^\*\*Current Task:\*\* */, ""); print; found=1; exit } END { if (!found) print "" }' "$plan"
      ;;
    get-current-phase)
      awk '/^\*\*Current Phase:\*\*/ { sub(/^\*\*Current Phase:\*\* */, ""); print; found=1; exit } END { if (!found) print "" }' "$plan"
      ;;
    get-plan-title)
      awk '/^# \S+ Plan:/ { sub(/^# \S+ Plan: */, ""); print; exit }' "$plan"
      ;;
    get-depends-on)
      awk '/^\*\*Depends On:\*\*/ { sub(/^\*\*Depends On:\*\* */, ""); print; found=1; exit } END { if (!found) print "NONE" }' "$plan"
      ;;
    get-created)
      awk '/^\*\*Created:\*\*/ { sub(/^\*\*Created:\*\* */, ""); print; found=1; exit } END { if (!found) print "" }' "$plan"
      ;;
    get-plan-header)
      awk '
        /^# \S+ Plan:/ { plan_title = substr($0, index($0, "Plan: ")+6) }
        /^\*\*Depends On:\*\*/ { sub(/^\*\*Depends On:\*\* */, ""); depends = $0 }
        /^\*\*Created:\*\*/    { sub(/^\*\*Created:\*\* */, ""); created = $0 }
        /^\*\*Updated:\*\*/    { sub(/^\*\*Updated:\*\* */, ""); updated = $0 }
        /^\*\*Current Phase:\*\*/ { sub(/^\*\*Current Phase:\*\* */, ""); cur_phase = $0 }
        /^\*\*Current Task:\*\*/  { sub(/^\*\*Current Task:\*\* */, ""); cur_task = $0 }
        END {
          print "plan-title=" plan_title
          print "depends-on=" depends
          print "created=" created
          print "updated=" updated
          print "current-phase=" cur_phase
          print "current-task=" cur_task
        }
      ' "$plan"
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
  tmpfile=$(mktemp "${plan_dir}/.plan-edit.$$-XXXXXX")
  cp -- "$plan" "$tmpfile"

  local affected_phase=""

  case "$action" in
    set-task-status)
      [[ $# -lt 2 ]] && { echo "✗ Usage: set-task-status <Task X.Y> <emoji>"; exit 1; }
      local task_id="$1" emoji="$2"
      affected_phase=$(printf '%s' "$task_id" | grep -oP '(?<=Task )\d+' || true)
      # Match task ID only at the start position after "- [emoji] ", not in dependency refs
      if ! awk -v tid="$task_id" -v em="$emoji" '
        /^- [^ ]+ / && match($0, /^- [^ ]+ (Task [0-9]+\.[0-9]+) /, arr) {
          if (arr[1] == tid) { sub(/^- [^ ]+ /, "- " em " "); found=1 }
        }
        { print }
        END { if (!found) { print "✗ Task not found: " tid > "/dev/stderr"; exit 1 } }
      ' "$tmpfile" > "${tmpfile}.new"; then
        rm -f "${tmpfile}.new"
        exit 1
      fi
      mv -f "${tmpfile}.new" "$tmpfile"
      ;;
    set-phase-status)
      [[ $# -lt 2 ]] && { echo "✗ Usage: set-phase-status <Phase X> <emoji>"; exit 1; }
      local phase_id="$1" emoji="$2"
      affected_phase=$(printf '%s' "$phase_id" | grep -oP '(?<=Phase )\d+' || true)
      # Match phase ID only in the heading, not elsewhere
      if ! awk -v pid="$phase_id" -v em="$emoji" '
        /^## [^ ]+ Phase [0-9]+/ && match($0, /## [^ ]+ (Phase [0-9]+) /, arr) {
          if (arr[1] == pid) { sub(/^## [^ ]+ /, "## " em " "); found=1 }
        }
        { print }
        END { if (!found) { print "✗ Phase not found: " pid > "/dev/stderr"; exit 1 } }
      ' "$tmpfile" > "${tmpfile}.new"; then
        rm -f "${tmpfile}.new"
        exit 1
      fi
      mv -f "${tmpfile}.new" "$tmpfile"
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
    set-plan-title)
      [[ $# -lt 1 ]] && { echo "✗ Usage: set-plan-title <title>"; exit 1; }
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
      [[ $# -lt 1 ]] && { echo "✗ Usage: set-depends-on <value>"; exit 1; }
      local safe_val
      safe_val=$(printf '%s\n' "$1" | sed 's/[&\/\\]/\\&/g')
      sed -i "s/^\*\*Depends On:\*\* .*/\*\*Depends On:\*\* ${safe_val}/" "$tmpfile"
      ;;
    rederive-all)
      rederive_all "$tmpfile"
      ;;
    *)
      echo "✗ Unknown action: $action" >&2
      exit 1
      ;;
  esac

  # Auto-derive phase emoji if a task or phase was changed (skip for rederive-all since it already did)
  if [[ -n "$affected_phase" ]]; then
    local derived current
    derived=$(derive_phase_emoji "$tmpfile" "$affected_phase")
    current=$(get_phase_emoji_from_file "$tmpfile" "$affected_phase")
    if [[ "$derived" != "$current" ]]; then
      echo "  → Phase $affected_phase: $current → $derived (auto-derived from tasks)"
      update_phase_emoji_in_file "$tmpfile" "$affected_phase" "$derived"
    fi
  fi

  # Auto-derive plan emoji from phases (skip for rederive-all)
  if [[ "$action" != "rederive-all" ]]; then
    local derived_plan file_plan_emoji
    derived_plan=$(derive_plan_emoji "$tmpfile")
    file_plan_emoji=$(get_plan_emoji_from_file "$tmpfile")
    if [[ "$derived_plan" != "$file_plan_emoji" ]]; then
      echo "  → Plan: $file_plan_emoji → $derived_plan (auto-derived from phases)"
      update_plan_emoji_in_file "$tmpfile" "$file_plan_emoji" "$derived_plan"
    fi
  fi

  mv -f "$tmpfile" "$plan"
}

# ── Main dispatch ───────────────────────────────────────────────────

case "$action" in
  get-task-status|get-phase-status|get-plan-status|\
  get-current-task|get-current-phase|get-plan-title|get-depends-on|\
  get-created|get-plan-header)
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
