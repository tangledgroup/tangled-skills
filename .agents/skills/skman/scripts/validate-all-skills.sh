#!/usr/bin/env bash
# validate-all-skills.sh — Validate all agent skills in a directory
#
# Usage:
#   bash validate-all-skills.sh [--strict] [SKILLS_DIR]
#
# Arguments:
#   --strict    Promote warnings to errors for each skill validator
#   SKILLS_DIR  Directory containing skill subdirectories (default: .agents/skills)
#
# Delegates per-skill validation to validate-skill.sh. Pure bash — no Python,
# no external YAML parsers. Uses: grep, sed, awk, find, sort (all POSIX).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATE_SCRIPT="${SCRIPT_DIR}/validate-skill.sh"

if [[ ! -f "$VALIDATE_SCRIPT" ]]; then
  echo "Error: validate-skill.sh not found at '$VALIDATE_SCRIPT'" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
STRICT_FLAG=""
SKILLS_DIR=".agents/skills"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict) STRICT_FLAG="--strict"; shift ;;
    -h|--help)
      cat <<'EOF'
Usage: validate-all-skills.sh [--strict] [SKILLS_DIR]

Validates structural integrity of all agent skills in a directory.
Delegates to validate-skill.sh for per-skill checks.

Options:
  --strict    Promote warnings to errors (exit 1 on any warnings)
  -h, --help  Show this help message

Exit codes:
  0  All skills passed (no errors, no warnings in strict mode)
  1  One or more skills failed
EOF
      exit 0
      ;;
    -*) echo "Unknown option: $1" >&2; exit 1 ;;
    *) SKILLS_DIR="$1"; shift ;;
  esac
done

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "Error: Skills directory '$SKILLS_DIR' not found." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Collect skill directories (those with SKILL.md)
# ---------------------------------------------------------------------------
skills=()
for skill_dir in "$SKILLS_DIR"/*/; do
  [[ -d "$skill_dir" ]] || continue
  [[ -f "${skill_dir}SKILL.md" ]] || continue
  skills+=("$(basename "$skill_dir")")
done

# Sort for deterministic output
IFS=$'\n' sorted_skills=($(printf '%s\n' "${skills[@]}" | sort)); unset IFS

total=${#sorted_skills[@]}
if [[ $total -eq 0 ]]; then
  echo "No skills found in '$SKILLS_DIR'"
  exit 0
fi

echo "Validating all skills in ${SKILLS_DIR} (${total} skills)"
echo ""

# ---------------------------------------------------------------------------
# Validate each skill
# ---------------------------------------------------------------------------
passed=0
warnings_only=0
failed=0

# Track failed skills for final report
declare -a fail_names=()
declare -a warn_names=()

for skill_name in "${sorted_skills[@]}"; do
  skill_path="${SKILLS_DIR}/${skill_name}"

  # Run validate-skill.sh, capture output and exit code
  output=$(bash "$VALIDATE_SCRIPT" $STRICT_FLAG "$skill_path" 2>&1) && rc=0 || rc=$?

  # Parse summary lines from output
  p=$(echo "$output" | grep -oP 'Checks passed:\s+\K[0-9]+' || echo "?")
  e=$(echo "$output" | grep -oP 'Errors:\s+\K[0-9]+' || echo "?")
  w=$(echo "$output" | grep -oP 'Warnings:\s+\K[0-9]+' || echo "?")

  # Determine status icon and category
  if [[ $rc -eq 0 ]] && [[ "$w" == "0" ]]; then
    icon="✓"
    passed=$((passed + 1))
  elif [[ $rc -eq 0 ]] && [[ "$w" != "0" ]]; then
    icon="⚠"
    warnings_only=$((warnings_only + 1))
    warn_names+=("${skill_name} (w:${w})")
  else
    icon="✗"
    failed=$((failed + 1))
    fail_names+=("${skill_name} (e:${e}, w:${w})")
  fi

  printf "  %b %-30s (pass: %s, errors: %s, warnings: %s)\n" \
    "$icon" "$skill_name" "$p" "$e" "$w"
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "--- Summary ---"
echo "  Total skills:  ${total}"
echo "  Passed:        ${passed}"
echo "  Warnings only: ${warnings_only}"
echo "  Failed:        ${failed}"

if [[ $failed -gt 0 ]]; then
  echo ""
  echo "✗ Validation FAILED — ${failed} skill(s) with errors:"
  for name in "${fail_names[@]}"; do
    echo "    - ${name}"
  done
  exit 1
elif [[ $warnings_only -gt 0 ]] && [[ -n "$STRICT_FLAG" ]]; then
  echo ""
  echo "✗ Validation FAILED in strict mode — ${warnings_only} skill(s) with warnings:"
  for name in "${warn_names[@]}"; do
    echo "    - ${name}"
  done
  exit 1
elif [[ $warnings_only -gt 0 ]]; then
  echo ""
  echo "⚠ Validation passed — ${warnings_only} skill(s) with warnings:"
  for name in "${warn_names[@]}"; do
    echo "    - ${name}"
  done
  exit 0
else
  echo ""
  echo "✓ All ${total} skills passed validation"
  exit 0
fi
