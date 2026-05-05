#!/usr/bin/env bash
# upload-skills.sh — Stage skill changes, commit with conventional message, push.
#
# Stages all changes under .agents/skills/ and README.md, generates a
# Conventional Commits message based on which skills changed (added/updated/removed),
# and pushes to origin main.
#
# Usage:
#   bash scripts/upload-skills.sh [--dry-run]
#
# Requires: git 2+, bash 4+
# Assumes: repo root is the ancestor of this script's directory.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SKILLS_DIR="$REPO_ROOT/.agents/skills"

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=1
fi

# ── Validate prerequisites ───────────────────────────────────────────────────
if ! command -v git &>/dev/null; then
    echo "ERROR: git is not installed or not in PATH" >&2
    exit 1
fi

if [[ ! -d "$REPO_ROOT/.git" ]]; then
    echo "ERROR: Not a git repository (no .git found at $REPO_ROOT)" >&2
    exit 1
fi

if [[ ! -d "$SKILLS_DIR" ]]; then
    echo "ERROR: Skills directory not found: $SKILLS_DIR" >&2
    exit 1
fi

# ── Detect changed skills ────────────────────────────────────────────────────
cd "$REPO_ROOT"

# Get list of skill dirs that have changes (added, modified, or deleted)
CHANGED_SKILLS=()
while IFS= read -r line; do
    # Extract skill name from path like ".agents/skills/foo/SKILL.md"
    skill_name="$(echo "$line" | sed -n 's|^\.agents/skills/\([^/]*\)/.*|\1|p')"
    [[ -n "$skill_name" ]] && CHANGED_SKILLS+=("$skill_name")
done < <(git status --porcelain .agents/skills/ 2>/dev/null | awk '{print $2}' | sort -u)

# Also check if README.md changed
README_CHANGED=0
if git diff --cached --name-only 2>/dev/null | grep -q '^README\.md$' || \
   git status --porcelain 2>/dev/null | grep -q ' README\.md'; then
    README_CHANGED=1
fi

# ── Generate commit message ──────────────────────────────────────────────────
generate_message() {
    local count=${#CHANGED_SKILLS[@]}

    if [[ $count -eq 0 ]]; then
        echo "chore(skills): update skills index"
        return
    fi

    # Detect if any are new (untracked) vs existing (modified/deleted)
    local has_new=0 has_update=0 has_delete=0
    for skill in "${CHANGED_SKILLS[@]}"; do
        local path="$SKILLS_DIR/$skill/SKILL.md"
        if [[ ! -f "$path" ]]; then
            # Deleted
            has_delete=1
        elif ! git ls-files --error-unmatch "$path" &>/dev/null; then
            # New (untracked)
            has_new=1
        else
            # Modified
            has_update=1
        fi
    done

    local skill_list
    skill_list="$(printf '%s\n' "${CHANGED_SKILLS[@]}" | tr '\n' ', ' | sed 's/, $//')"

    if [[ $has_new -eq 1 && $has_update -eq 0 && $has_delete -eq 0 ]]; then
        echo "feat(skills): add ${skill_list}"
    elif [[ $has_delete -eq 1 && $has_new -eq 0 && $has_update -eq 0 ]]; then
        echo "chore(skills): remove ${skill_list}"
    else
        echo "chore(skills): update skills [${skill_list}]"
    fi
}

COMMIT_MSG="$(generate_message)"

# ── Stage and commit ─────────────────────────────────────────────────────────
echo "Staging skill changes..."
git add .agents/skills/ README.md 2>/dev/null || true

# Check if there's anything to commit
if ! git diff --cached --quiet 2>/dev/null; then
    echo "Commit message: $COMMIT_MSG"

    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "[dry-run] Would commit and push"
        git diff --cached --stat
        exit 0
    fi

    git commit -m "$COMMIT_MSG"
    echo "Committed. Pushing to origin main..."
    git push origin main
else
    echo "No changes to commit."
fi
