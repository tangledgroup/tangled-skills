#!/usr/bin/env bash
# sync.sh — Sync local .agents/skills with tangled-skills repository
#
# Downloads the latest tangled-skills from GitHub and extracts the
# .agents/skills directory into the current working directory, merging
# with any existing local skills.
#
# Usage:
#   bash scripts/sync.sh [TARGET_DIR]
#
# Arguments:
#   TARGET_DIR  — Directory where .agents/skills will be created/updated
#                 (default: current directory ".")
#
# Dependencies: bash, curl, tar
# License: MIT

set -euo pipefail

TARGET_DIR="${1:-.}"

# Ensure target directory exists
if [[ ! -d "$TARGET_DIR" ]]; then
    echo "Error: Target directory '$TARGET_DIR' does not exist." >&2
    exit 1
fi

cd "$TARGET_DIR"

echo "Syncing tangled-skills into .agents/skills ..."

mkdir -p .agents/skills && \
curl -sL https://github.com/tangledgroup/tangled-skills/archive/refs/heads/main.tar.gz | \
tar -xz --strip-components=3 -C .agents/skills tangled-skills-main/.agents/skills

echo "Sync complete. Skills directory: .agents/skills/"
