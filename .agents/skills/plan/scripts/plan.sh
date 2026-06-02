#!/usr/bin/env bash
# plan.sh - PLAN.md lifecycle
# Usage: plan.sh <PLAN.md> <action> [args...]
#
# All write actions are atomic: lock → edit → unlock.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/common.sh"
