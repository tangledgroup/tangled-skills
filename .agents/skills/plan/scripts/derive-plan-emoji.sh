#!/usr/bin/env bash
# derive-plan-emoji.sh — Derive plan emoji from its phases' tasks
# Usage: derive-plan-emoji.sh <PLAN.md>
#
# Output: single emoji character (☐ ❓ ⚙️ ❌ ☑) on stdout
# Priority: ⚙️ > ❓ > ❌ > ☑ > ☐
#
# This script re-derives each phase's status from its tasks (not from
# the phase emoji in the file, which may be stale), then aggregates
# across all phases to produce the plan emoji.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/common.sh"

usage() {
  cat <<EOF
Usage: $0 <PLAN.md>

Derives the plan emoji from its phases' tasks using priority:
  ⚙️ (Doing) > ❓ (Question) > ❌ (Error) > ☑ (Done) > ☐ (To Do)
EOF
  exit "${1:-0}"
}

[[ $# -eq 0 ]] && usage 1
[[ "$1" == "--help" || "$1" == "-h" ]] && usage 0

plan="$1"

check_plan_file "$plan"

derive_plan_emoji "$plan"
