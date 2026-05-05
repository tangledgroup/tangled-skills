#!/usr/bin/env bash
# download-skills.sh — Fetch latest skills from the tangled-skills GitHub repo.
#
# Downloads the main branch as a tarball and extracts .agents/skills/ into
# the local project, overwriting existing skills with the same name.
#
# Usage:
#   bash scripts/download-skills.sh [--backup]
#
# --backup  — Back up current .agents/skills/ to .agents/skills-backup/ before downloading
#
# Requires: curl, tar, bash 4+

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SKILLS_DIR="$REPO_ROOT/.agents/skills"

BACKUP=0
if [[ "${1:-}" == "--backup" ]]; then
    BACKUP=1
fi

# ── Validate prerequisites ───────────────────────────────────────────────────
if ! command -v curl &>/dev/null; then
    echo "ERROR: curl is not installed or not in PATH" >&2
    exit 1
fi

if ! command -v tar &>/dev/null; then
    echo "ERROR: tar is not installed or not in PATH" >&2
    exit 1
fi

# ── Backup if requested ──────────────────────────────────────────────────────
if [[ "$BACKUP" -eq 1 && -d "$SKILLS_DIR" ]]; then
    BACKUP_DIR="${SKILLS_DIR}-backup-$(date +%Y%m%d%H%M%S)"
    echo "Backing up current skills to $BACKUP_DIR ..."
    cp -r "$SKILLS_DIR" "$BACKUP_DIR"
fi

# ── Download and extract ─────────────────────────────────────────────────────
REPO_URL="https://github.com/tangledgroup/tangled-skills/archive/refs/heads/main.tar.gz"

echo "Downloading skills from $REPO_URL ..."
mkdir -p "$SKILLS_DIR"

if curl -fsSL "$REPO_URL" | tar -xz --strip-components=3 -C "$SKILLS_DIR" tangled-skills-main/.agents/skills; then
    # Count downloaded skills
    count=$(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l)
    echo "✓ Downloaded $count skill(s) into $SKILLS_DIR"
else
    echo "ERROR: Failed to download or extract skills from $REPO_URL" >&2
    exit 1
fi
