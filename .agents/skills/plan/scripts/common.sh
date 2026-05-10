#!/usr/bin/env bash
# common.sh - Shared helpers for PLAN.md scripts
# Source this file; do not execute directly.
#
# Provides:
#   - Allowed emoji constants and validation
#   - Deterministic header field read/write helpers
#   - File existence checks
#   - Emoji derivation logic (phase and plan) as pure awk functions
#   - Lock management with stale-lock detection
#   - Atomic file write helpers

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Constants
EM_TODO="☐"
EM_QUESTION="❓"
EM_DOING="⚙️"
EM_ERROR="❌"
EM_DONE="☑"

# All valid status emojis (space-separated for membership tests)
VALID_EMOJIS="$EM_TODO $EM_QUESTION $EM_DOING $EM_ERROR $EM_DONE"

# Lock timeout in seconds
LOCK_TIMEOUT="${PLAN_LOCK_TIMEOUT:-30}"

# Emoji validation
is_valid_emoji() {
  local em="$1"
  [[ "$em" == "$EM_TODO" || "$em" == "$EM_QUESTION" || "$em" == "$EM_DOING" || "$em" == "$EM_ERROR" || "$em" == "$EM_DONE" ]]
}

# File helpers
usage_exit() {
  echo "Usage: $0 <PLAN.md> $1" >&2
  exit "${2:-1}"
}

check_plan_file() {
  local plan="$1"
  if [[ ! -f "$plan" ]]; then
    echo "ERROR: File not found: $plan" >&2
    exit 1
  fi
}

# Print usage for a script, showing supported actions
print_usage() {
  local script_name="$1"
  shift
  cat <<EOF
Usage: $script_name <PLAN.md> <action> [args...]

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

# Deterministic header field access
# All header fields use a canonical format: **FieldName:** value
# Read helpers extract the value after the field marker, trimmed.
# Write helpers replace the entire line with the canonical format.

# Extract a header field value (deterministic: first match, trimmed)
# Usage: get_header_field <file> <Field Name>
get_header_field() {
  local file="$1" field="$2"
  awk -v f="**${field}:**" '
    index($0, f) == 1 {
      val = substr($0, length(f) + 1)
      # Trim leading/trailing whitespace
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", val)
      print val
      found = 1
      exit
    }
    END { if (!found) print "" }
  ' "$file"
}

# Set a header field value (deterministic: replaces entire line, canonical format)
# Usage: set_header_field_in_file <tmpfile> <Field Name> <value>
set_header_field_in_file() {
  local tmpfile="$1" field="$2" value="$3"
  # Escape special characters for awk string
  local escaped_val
  escaped_val=$(printf '%s' "$value" | sed 's/\\/\\\\/g; s/"/\\"/g')
  awk -v f="**${field}:**" -v val="$escaped_val" '
    index($0, f) == 1 {
      print f " " val
      next
    }
    { print }
  ' "$tmpfile" > "${tmpfile}.new" && mv -f "${tmpfile}.new" "$tmpfile"
}

# Extract plan title from header line: # [emoji] Plan: Title
get_plan_title_from_file() {
  local file="$1"
  awk '/^# \S+ Plan:/ { sub(/^# \S+ Plan: */, ""); print; exit }' "$file"
}

# Lock management
# Advisory lock with stale-lock detection.
# A lock file older than LOCK_TIMEOUT seconds is considered stale and removed.

acquire_lock() {
  local lockfile="$1"
  # Check for stale lock (older than timeout, no holding process)
  if [[ -f "$lockfile" ]]; then
    local age
    age=$(( $(date +%s) - $(stat -c %Y "$lockfile" 2>/dev/null || echo 0) ))
    if [[ "$age" -gt "$LOCK_TIMEOUT" ]]; then
      # Check if any process holds fd on this file
      if ! fuser "$lockfile" >/dev/null 2>&1; then
        rm -f "$lockfile"
      fi
    fi
  fi
  flock -w "$LOCK_TIMEOUT" 200 || { echo "ERROR: Timeout waiting for lock ($LOCK_TIMEOUT s)"; exit 1; }
}

release_lock() {
  local lockfile="$1"
  rm -f "$lockfile" 2>/dev/null || true
}

# Atomic write helper
# Write content to a temp file in the same directory, then atomic rename.
# Usage: atomic_write <target> <tmpfile>
atomic_write() {
  local target="$1" tmpfile="$2"
  mv -f "$tmpfile" "$target"
}

cleanup_temp() {
  rm -f "$@" 2>/dev/null || true
}

# Phase number extraction
# Extract all phase numbers from a PLAN.md file (one per line)
get_phase_numbers() {
  local plan="$1"
  awk '/^## .* Phase [0-9]+/ {
    if (match($0, /Phase ([0-9]+)/, arr)) print arr[1]
  }' "$plan"
}

# AWK: derive phase emoji from tasks within a given phase
# Reads PLAN.md, collects task emojis for the given phase number.
# Outputs single emoji on stdout.
# Priority: Doing > Question > Error > Done > Not Started
derive_phase_emoji() {
  local plan="$1" phase_num="$2"

  awk -v pn="$phase_num" '
    /^## .* Phase [0-9]+/ {
      if (match($0, /Phase ([0-9]+)/, arr)) {
        current = arr[1]
      }
    }
    current == pn && /^- .+ Task/ {
      em = $2
      if (em == "⚙️") found_doing++
      else if (em == "❓") found_question++
      else if (em == "❌") found_error++
      else if (em == "☑") found_done++
      total++
    }
    END {
      if (found_doing + 0) print "⚙️"
      else if (found_question + 0) print "❓"
      else if (found_error + 0) print "❌"
      else if (total && found_done + 0 == total) print "☑"
      else print "☐"
    }
  ' "$plan"
}

# AWK: derive plan emoji from all phases (via their tasks)
derive_plan_emoji() {
  local plan="$1"

  awk '
    /^## .* Phase [0-9]+/ {
      if (phase_seen) {
        _finalize_phase()
      }
      phase_seen = 1
      pt_doing = 0; pt_quest = 0; pt_error = 0; pt_done = 0; pt_total = 0
    }
    phase_seen && /^- .+ Task/ {
      em = $2
      if (em == "⚙️") pt_doing++
      else if (em == "❓") pt_quest++
      else if (em == "❌") pt_error++
      else if (em == "☑") pt_done++
      pt_total++
    }
    function _finalize_phase() {
      if (pt_doing)       g_doing++
      else if (pt_quest)  g_question++
      else if (pt_error)  g_error++
      else if (pt_done == pt_total && pt_total > 0) g_done++
      else g_notstarted++
      g_total++
    }
    END {
      if (phase_seen) _finalize_phase()
      if (g_doing + 0)              print "⚙️"
      else if (g_question + 0)      print "❓"
      else if (g_error + 0)         print "❌"
      else if (g_total > 0 && g_done + 0 == g_total) print "☑"
      else                          print "☐"
    }
  ' "$plan"
}

# Get current emoji of a phase from the file
get_phase_emoji_from_file() {
  local plan="$1" phase_num="$2"
  awk -v pn="$phase_num" '
    /^## .* Phase [0-9]+/ {
      if (match($0, /Phase ([0-9]+)/, arr) && arr[1] == pn) { print $2; exit }
    }
  ' "$plan"
}

# Get plan emoji from file header
get_plan_emoji_from_file() {
  local plan="$1"
  awk 'NR==1 && /^# \S+ / { print $2; found=1; exit } END { if (!found) print "☐" }' "$plan"
}

# Update phase emoji in file
update_phase_emoji_in_file() {
  local tmpfile="$1" phase_num="$2" new_emoji="$3"
  awk -v pn="$phase_num" -v em="$new_emoji" '
    /^## .* Phase [0-9]+/ && match($0, /Phase ([0-9]+)/, arr) && arr[1] == pn {
      sub(/^## [^ ]+ /, "## " em " "); print; next
    }
    { print }
  ' "$tmpfile" > "${tmpfile}.new" && mv -f "${tmpfile}.new" "$tmpfile"
}

# Update plan emoji in file header
update_plan_emoji_in_file() {
  local tmpfile="$1" old_emoji="$2" new_emoji="$3"
  awk -v old="$old_emoji" -v new="$new_emoji" '
    NR==1 && /^# / {
      if ($2 == old) { $2 = new }
    }
    { print }
  ' "$tmpfile" > "${tmpfile}.new" && mv -f "${tmpfile}.new" "$tmpfile"
}

# Re-derive all phase emojis + plan emoji + sync Current Phase/Task headers
rederive_all() {
  local tmpfile="$1"

  local phase_nums
  phase_nums=$(get_phase_numbers "$tmpfile")
  for pn in $phase_nums; do
    local derived current
    derived=$(derive_phase_emoji "$tmpfile" "$pn")
    current=$(get_phase_emoji_from_file "$tmpfile" "$pn")
    if [[ "$derived" != "$current" ]]; then
      echo "  → Phase $pn: $current → $derived (auto-derived from tasks)"
      update_phase_emoji_in_file "$tmpfile" "$pn" "$derived"
    fi
  done

  local derived_plan file_plan_emoji
  derived_plan=$(derive_plan_emoji "$tmpfile")
  file_plan_emoji=$(get_plan_emoji_from_file "$tmpfile")
  if [[ "$derived_plan" != "$file_plan_emoji" ]]; then
    echo "  → Plan: $file_plan_emoji → $derived_plan (auto-derived from phases)"
    update_plan_emoji_in_file "$tmpfile" "$file_plan_emoji" "$derived_plan"
  fi

  # Sync Current Task and Current Phase header emojis with actual statuses
  sync_current_task_emoji "$tmpfile"
  sync_current_phase_emoji "$tmpfile"
}

# Pre-flight validation for write actions
preflight_check() {
  local action="$1"
  shift
  case "$action" in
    set-task-status)
      if [[ $# -lt 2 ]]; then echo "ERROR: Usage: set-task-status <Task X.Y> <emoji>"; exit 1; fi
      if ! is_valid_emoji "$2"; then
        echo "ERROR: Invalid emoji: $2 (valid: ☐ ❓ ⚙️ ❌ ☑)" >&2
        exit 1
      fi
      ;;
    set-phase-status)
      if [[ $# -lt 2 ]]; then echo "ERROR: Usage: set-phase-status <Phase X> <emoji>"; exit 1; fi
      if ! is_valid_emoji "$2"; then
        echo "ERROR: Invalid emoji: $2 (valid: ☐ ❓ ⚙️ ❌ ☑)" >&2
        exit 1
      fi
      ;;
    set-current-task|set-current-phase)
      if [[ $# -lt 1 ]]; then echo "ERROR: Usage: set-${action#set-} <value>"; exit 1; fi
      ;;
    set-plan-title|set-depends-on)
      if [[ $# -lt 1 ]]; then echo "ERROR: Usage: $action <value>"; exit 1; fi
      ;;
  esac
  return 0
}

# Sync Current Task header emoji with the actual task status in the body.
# Extracts the task ID from **Current Task:**, finds its real emoji, and
# updates the header if they differ. If the task doesn't exist, leaves it alone.
sync_current_task_emoji() {
  local tmpfile="$1"
  local cur_val
  cur_val=$(get_header_field "$tmpfile" "Current Task")
  [[ -z "$cur_val" ]] && return 0

  # Extract emoji and task ID from current value (e.g. "⚙️ Task 2.3")
  local cur_emoji cur_tid
  cur_emoji=$(printf '%s' "$cur_val" | awk '{print $1}')
  cur_tid=$(printf '%s' "$cur_val" | sed 's/^[^ ]* //')

  # Look up actual emoji for this task in the body
  local actual_emoji
  actual_emoji=$(awk -v tid="$cur_tid" '
    /^- [^ ]+ / && match($0, /^- [^ ]+ (Task [0-9]+\.[0-9]+) /, arr) {
      if (arr[1] == tid) { print $2; found=1; exit }
    }
    END { if (!found) exit 1 }
  ' "$tmpfile" 2>/dev/null) || return 0

  if [[ "$cur_emoji" != "$actual_emoji" ]]; then
    set_header_field_in_file "$tmpfile" "Current Task" "$actual_emoji $cur_tid"
    echo "  → Current Task: $cur_emoji → $actual_emoji (synced with actual status)"
  fi
}

# Sync Current Phase header emoji with the actual phase status in the body.
sync_current_phase_emoji() {
  local tmpfile="$1"
  local cur_val
  cur_val=$(get_header_field "$tmpfile" "Current Phase")
  [[ -z "$cur_val" ]] && return 0

  local cur_emoji cur_pid
  cur_emoji=$(printf '%s' "$cur_val" | awk '{print $1}')
  cur_pid=$(printf '%s' "$cur_val" | sed 's/^[^ ]* //')

  # Extract phase number from ID like "Phase 2"
  local pn
  pn=$(printf '%s' "$cur_pid" | grep -oP '(?<=Phase )\d+' || true)
  [[ -z "$pn" ]] && return 0

  local actual_emoji
  actual_emoji=$(derive_phase_emoji "$tmpfile" "$pn")

  if [[ "$cur_emoji" != "$actual_emoji" ]]; then
    set_header_field_in_file "$tmpfile" "Current Phase" "$actual_emoji $cur_pid"
    echo "  → Current Phase: $cur_emoji → $actual_emoji (synced with derived status)"
  fi
}

# Auto-advance Current Task and Current Phase when a task completes (☑).
# Finds the next pending task in priority order: ⚙️ ❓ ❌ ☐ within same phase,
# then next phases. If completed task was the last overall, keeps pointing to it.
advance_current_on_completion() {
  local tmpfile="$1" completed_task="$2"

  local cur_task_val cur_phase_val
  cur_task_val=$(get_header_field "$tmpfile" "Current Task")
  cur_phase_val=$(get_header_field "$tmpfile" "Current Phase")

  # Extract current phase number
  local cur_pn
  cur_pn=$(printf '%s' "$cur_phase_val" | grep -oP '(?<=Phase )\d+' || true)
  [[ -z "$cur_pn" ]] && return 0

  # Find the next pending task
  local next_task next_phase
  next_task=$(awk -v cpn="$cur_pn" '
    /^## .* Phase [0-9]+/ {
      if (match($0, /Phase ([0-9]+)/, arr)) {
        cur_phase = arr[1] + 0
      }
    }
    cur_phase >= cpn && /^- .+ Task/ {
      em = $2
      if (em != "☑") {
        # Extract task ID
        if (match($0, /^- [^ ]+ (Task [0-9]+\.[0-9]+) /, arr)) {
          print em " " arr[1]
          found = 1
          exit
        }
      }
    }
    END { if (!found) print "" }
  ' "$tmpfile")

  if [[ -n "$next_task" ]]; then
    local next_emoji next_tid
    next_emoji=$(printf '%s' "$next_task" | awk '{print $1}')
    next_tid=$(printf '%s' "$next_task" | sed 's/^[^ ]* //')

    # Determine which phase this task belongs to
    local next_pn
    next_pn=$(printf '%s' "$next_tid" | grep -oP '(?<=Task )\d+' || true)

    set_header_field_in_file "$tmpfile" "Current Task" "$next_emoji $next_tid"
    # Sync Current Phase too — derive its actual emoji
    local next_phase_emoji
    next_phase_emoji=$(derive_phase_emoji "$tmpfile" "$next_pn")
    set_header_field_in_file "$tmpfile" "Current Phase" "$next_phase_emoji Phase $next_pn"
    echo "  → Current Task: $cur_task_val → $next_emoji $next_tid (advanced to next pending)"
    echo "  → Current Phase: $cur_phase_val → $next_phase_emoji Phase $next_pn (advanced with task)"
  fi
}

# Validate all read-only action names
is_read_action() {
  local action="$1"
  case "$action" in
    get-task-status|get-phase-status|get-plan-status|\
    get-current-task|get-current-phase|get-plan-title|get-depends-on|\
    get-created|get-plan-header)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}
