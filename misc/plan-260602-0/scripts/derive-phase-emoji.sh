#!/usr/bin/env bash
# derive-phase-emoji.sh - Derive phase emoji from its tasks' emojis
# Usage: derive-phase-emoji.sh <PLAN.md> <phase-number>
#
# Output: single emoji character (NotStarted Question Doing Error Done) on stdout
# Priority: Doing > Question > Error > Done > Not Started

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/common.sh"

[[ $# -eq 0 ]] && { echo "Usage: $0 <PLAN.md> <phase-number>" >&2; exit 1; }
[[ "$1" == "--help" || "$1" == "-h" ]] && { echo "Usage: $0 <PLAN.md> <phase-number>"; echo ""; echo "Derives the phase emoji from its tasks' emojis using priority:"; echo "  Doing > Question > Error > Done > Not Started"; exit 0; }
[[ $# -lt 2 ]] && { echo "Usage: $0 <PLAN.md> <phase-number>" >&2; exit 1; }

plan="$1"
phase_num="$2"

check_plan_file "$plan"

derive_phase_emoji "$plan" "$phase_num"
