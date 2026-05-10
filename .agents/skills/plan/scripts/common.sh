#!/usr/bin/env bash
# common.sh — Shared helpers for PLAN.md scripts
# Source this file; do not execute directly.
#
# Provides:
#   - Allowed emoji constants
#   - Usage/argument parsing helpers
#   - File existence checks
#   - Phase number extraction from headings
#   - Emoji derivation logic (phase and plan) as pure awk functions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Constants ────────────────────────────────────────────────────────
# Allowed status emojis
EM_TODO="☐"
EM_QUESTION="❓"
EM_DOING="⚙️"
EM_ERROR="❌"
EM_DONE="☑"

# Priority order (highest first): Doing > Question > Error > Done > Todo

# ── Helpers ──────────────────────────────────────────────────────────

usage_exit() {
  echo "Usage: $0 <PLAN.md> $1" >&2
  exit "${2:-1}"
}

check_plan_file() {
  local plan="$1"
  if [[ ! -f "$plan" ]]; then
    echo "✗ File not found: $plan" >&2
    exit 1
  fi
}

# ── AWK snippet: extract phase number from a phase heading line ─────
# Expects the line to match /^## .* Phase [0-9]+/
# Outputs the phase number on stdout.

# ── AWK: derive phase emoji from tasks within a given phase ─────────
# Reads PLAN.md, collects task emojis for the given phase number.
# Outputs single emoji on stdout.
# Priority: ⚙️ > ❓ > ❌ > ☑ > ☐

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

# ── AWK: derive plan emoji from all phases (via their tasks) ────────
# Reads PLAN.md, re-derives each phase status from its tasks,
# then aggregates across all phases to produce the plan emoji.
# Outputs single emoji on stdout.

derive_plan_emoji() {
  local plan="$1"

  awk '
    /^## .* Phase [0-9]+/ {
      # Finalize previous phase if any
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

# ── Get current emoji of a phase from the file ───────────────────────
get_phase_emoji_from_file() {
  local plan="$1" phase_num="$2"
  awk -v pn="$phase_num" '
    /^## .* Phase [0-9]+/ {
      if (match($0, /Phase ([0-9]+)/, arr) && arr[1] == pn) { print $2; exit }
    }
  ' "$plan"
}

# ── Get plan emoji from file header ──────────────────────────────────
get_plan_emoji_from_file() {
  local plan="$1"
  head -1 "$plan" | grep -oP '^\# \K\S+' || echo "☐"
}

# ── Update phase emoji in file (awk-based, writes to tmpfile) ────────
# Usage: update_phase_emoji_in_file <tmpfile> <phase_num> <new_emoji>
update_phase_emoji_in_file() {
  local tmpfile="$1" phase_num="$2" new_emoji="$3"
  awk -v pn="$phase_num" -v em="$new_emoji" '
    /^## .* Phase [0-9]+/ && match($0, /Phase ([0-9]+)/, arr) && arr[1] == pn {
      sub(/^## [^ ]+ /, "## " em " "); print; next
    }
    { print }
  ' "$tmpfile" > "${tmpfile}.new" && mv -f "${tmpfile}.new" "$tmpfile"
}

# ── Update plan emoji in file header ─────────────────────────────────
update_plan_emoji_in_file() {
  local tmpfile="$1" old_emoji="$2" new_emoji="$3"
  sed -i "s/^# ${old_emoji} /# ${new_emoji} /" "$tmpfile"
}

# ── Re-derive all phase emojis + plan emoji, writing to tmpfile ─────
# Called after edits. Writes derived emojis back into tmpfile.
rederive_all() {
  local tmpfile="$1"
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[1]:-$0}")" && pwd)"

  # Re-derive each phase
  local phase_nums
  phase_nums=$(awk '/^## .* Phase [0-9]+/ { if (match($0, /Phase ([0-9]+)/, arr)) print arr[1] }' "$tmpfile")
  for pn in $phase_nums; do
    local derived current
    derived=$(derive_phase_emoji "$tmpfile" "$pn")
    current=$(get_phase_emoji_from_file "$tmpfile" "$pn")
    if [[ "$derived" != "$current" ]]; then
      echo "  → Phase $pn: $current → $derived (auto-derived from tasks)"
      update_phase_emoji_in_file "$tmpfile" "$pn" "$derived"
    fi
  done

  # Re-derive plan emoji
  local derived_plan file_plan_emoji
  derived_plan=$(derive_plan_emoji "$tmpfile")
  file_plan_emoji=$(get_plan_emoji_from_file "$tmpfile")
  if [[ "$derived_plan" != "$file_plan_emoji" ]]; then
    echo "  → Plan: $file_plan_emoji → $derived_plan (auto-derived from phases)"
    update_plan_emoji_in_file "$tmpfile" "$file_plan_emoji" "$derived_plan"
  fi
}
