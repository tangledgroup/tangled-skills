#!/usr/bin/env bash
# remove-skill.sh — Remove a skill directory and regenerate the README table.
#
# Deletes .agents/skills/<skill-name>/ entirely, then runs gen-skill-list.sh
# to update the README.md skills table.
#
# Usage:
#   bash scripts/remove-skill.sh <skill-name> [--dry-run]
#
# Requires: bash 4+, find

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SKILLS_DIR="$REPO_ROOT/.agents/skills"

DRY_RUN=0

# ── Parse arguments ──────────────────────────────────────────────────────────
if [[ $# -lt 1 ]]; then
    echo "Usage: bash scripts/remove-skill.sh <skill-name> [--dry-run]" >&2
    echo "" >&2
    echo "Removes a skill directory and regenerates the README skills table." >&2
    exit 1
fi

SKILL_NAME="$1"
if [[ "${2:-}" == "--dry-run" ]]; then
    DRY_RUN=1
fi

# ── Validate skill name format ───────────────────────────────────────────────
if [[ ! "$SKILL_NAME" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
    echo "ERROR: Invalid skill name '$SKILL_NAME'. Must match: ^[a-z0-9]+(-[a-z0-9]+)*$" >&2
    exit 1
fi

# ── Validate skill exists ────────────────────────────────────────────────────
SKILL_PATH="$SKILLS_DIR/$SKILL_NAME"
if [[ ! -d "$SKILL_PATH" ]]; then
    echo "ERROR: Skill directory not found: $SKILL_PATH" >&2
    exit 1
fi

# ── Remove skill ─────────────────────────────────────────────────────────────
if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] Would remove: $SKILL_PATH"
    echo "[dry-run] Would regenerate README skills table"
    exit 0
fi

echo "Removing skill '$SKILL_NAME' from $SKILL_PATH ..."
rm -r "$SKILL_PATH"
echo "✓ Removed."

# ── Regenerate README table ──────────────────────────────────────────────────
GEN_SCRIPT="$SCRIPT_DIR/gen-skill-list.sh"
if [[ -f "$GEN_SCRIPT" ]]; then
    echo "Regenerating README skills table ..."
    bash "$GEN_SCRIPT"
else
    echo "WARNING: gen-skill-list.sh not found at $GEN_SCRIPT" >&2
    echo "Run 'bash scripts/gen-skill-list.sh' manually to update README.md." >&2
fi
