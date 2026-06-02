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

# Constants
EM_TODO="☐"
EM_QUESTION="❓"
EM_DOING="⚙️"
EM_ERROR="❌"
EM_DONE="☑"

# All valid status emojis (space-separated for membership tests)
VALID_EMOJIS="$EM_TODO $EM_QUESTION $EM_DOING $EM_ERROR $EM_DONE"
