#!/usr/bin/env bash
# derive-phase-emoji.sh — Derive phase emoji from its tasks' emojis
# Usage: derive-phase-emoji.sh <PLAN.md> <phase-number>
#
# Output: single emoji character (☐ ❓ ⚙️ ❌ ☑) on stdout
# Priority: ⚙️ > ❓ > ❌ > ☑ > ☐

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/common.sh"

usage() {
  echo "Usage: $0 <PLAN.md> <phase-number>"
  echo ""
  echo "Derives the phase emoji from its tasks' emojis using priority:"
  echo "  ⚙️ (Doing) > ❓ (Question) > ❌ (Error) > ☑ (Done) > ☐ (To Do)"
  exit "${1:-0}"
}

[[ $# -eq 0 ]] && usage 1
[[ "$1" == "--help" || "$1" == "-h" ]] && usage 0

plan="$1"
phase_num="$2"

check_plan_file "$plan"

derive_phase_emoji "$plan" "$phase_num"
