#!/usr/bin/env bash
# derive-plan-emoji.sh - Derive plan emoji from its phases' tasks
# Usage: derive-plan-emoji.sh <PLAN.md>
#
# Output: single emoji character (NotStarted Question Doing Error Done) on stdout
# Priority: Doing > Question > Error > Done > Not Started
#
# This script re-derives each phase's status from its tasks (not from
# the phase emoji in the file, which may be stale), then aggregates
# across all phases to produce the plan emoji.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/common.sh"

[[ $# -eq 0 ]] && { echo "Usage: $0 <PLAN.md>" >&2; exit 1; }
[[ "$1" == "--help" || "$1" == "-h" ]] && { echo "Usage: $0 <PLAN.md>"; echo ""; echo "Derives the plan emoji from its phases' tasks using priority:"; echo "  Doing > Question > Error > Done > Not Started"; exit 0; }

plan="$1"

check_plan_file "$plan"

derive_plan_emoji "$plan"
