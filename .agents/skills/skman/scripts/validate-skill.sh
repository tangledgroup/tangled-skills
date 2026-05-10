#!/usr/bin/env bash
# validate-skill.sh — Structural validation of an agent skill directory
# Usage: validate-skill.sh [--strict] <SKILL_DIR>
# Exit 0 = pass, 1 = errors found, 2 = warnings only (no --strict)
#
# Validates structural integrity only. Semantic correctness of content
# (accuracy, completeness, no hallucinations) is the LLM's responsibility.
#
# Requires: bash 4+, awk, grep, sed, find, wc (all POSIX).

set -euo pipefail

# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------
STRICT=0
SKILL_DIR=""
errors=0
warnings=0
passes=0

# Per-category counters (reserved for future detailed reporting)

# ---------------------------------------------------------------------------
# Usage / Help
# ---------------------------------------------------------------------------
usage() {
  cat <<'EOF'
Usage: validate-skill.sh [--strict] <SKILL_DIR>

Validates structural integrity of an agent skill directory:
  - YAML header fields (name, description, license, author, version, tags)
  - Directory structure (SKILL.md, reference/, scripts/, assets/)
  - Content sections (Overview, When to Use, Advanced Topics)
  - Script references (if scripts/ exists)

Options:
  --strict    Promote warnings to errors (exit 1 on warnings)
  -h, --help  Show this help message

Exit codes:
  0  All checks passed (no errors, no warnings in strict mode)
  1  Errors found (or warnings in strict mode)
EOF
  exit "${1:-0}"
}

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
pass() {
  passes=$((passes + 1))
  echo "  ✓ $1"
}

fail() {
  errors=$((errors + 1))
  echo "  ✗ $1"
}

warn() {
  warnings=$((warnings + 1))
  echo "  ⚠ $1"
}

# ---------------------------------------------------------------------------
# YAML extraction utilities
# ---------------------------------------------------------------------------

# extract_yaml_field SKILL_FILE FIELD
#   Extract a single-line or block-scalar YAML field from the header.
#   Handles > (folded), >- (strip), and quoted values.
extract_yaml_field() {
  local file="$1"
  local field="$2"
  awk -v field="$field" '
    BEGIN { found=0; in_block=0; buf="" ; strip_mode=0 }
    # Skip the very first ---
    NR==1 && /^---$/ { next }
    # Second --- ends the header
    /^---$/ {
      if (!header_end) {
        header_end=1
        # Flush any pending block scalar
        if (in_block && found == 1) {
          gsub(/^ +| +$/, "", buf)
          print buf
        }
        next
      }
      exit
    }
    !header_end {
      if (in_block) {
        # Continuation line starts with 2+ spaces (YAML block scalar)
        if ($0 ~ /^  [^ ]/ || $0 ~ /^  $/) {
          line = substr($0, 3)
          gsub(/^ +| +$/, "", line)
          if (buf != "") buf = buf " " line
          else buf = line
          next
        } else {
          # End of block scalar
          gsub(/^ +| +$/, "", buf)
          if (strip_mode) {
            # >- strips trailing newline — just print without extra
            printf "%s", buf
          } else {
            print buf
          }
          in_block=0
          buf=""
          found=2
          # Fall through to process this line
        }
      }
      if (found == 0 && $0 ~ "^" field ":") {
        val = $0
        sub("^" field ": *", "", val)
        # Check for block scalar > or >-
        if (val ~ /^ *>- *$/) {
          in_block=1
          strip_mode=1
          buf=""
          found=1
          next
        }
        if (val ~ /^ *> *$/) {
          in_block=1
          strip_mode=0
          buf=""
          found=1
          next
        }
        # Single-line value — strip quotes and whitespace
        gsub(/^ +| +$/, "", val)
        gsub(/^"|"$/, "", val)
        gsub(/^'"'"'|'"'"'$/, "", val)
        print val
        found=2
        next
      }
    }
  ' "$file"
}

# extract_tags SKILL_FILE
#   Extract tags array from YAML header. Returns one tag per line.
extract_tags() {
  local file="$1"
  awk '
    BEGIN { in_tags=0; count=0 }
    /^tags:/ { in_tags=1; next }
    in_tags && /^[[:space:]]*-/ {
      tag = $0
      sub(/^[[:space:]]*-[[:space:]]*/, "", tag)
      gsub(/^ +| +$/, "", tag)
      gsub(/^"|"$/, "", tag)
      print tag
      count++
      next
    }
    in_tags && !/^[[:space:]]*-/ && !/^[[:space:]]*$/ {
      exit
    }
  ' "$file"
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict) STRICT=1; shift ;;
    -h|--help) usage 0 ;;
    -*) echo "Unknown option: $1" >&2; usage 1 ;;
    *) SKILL_DIR="$1"; shift ;;
  esac
done

[[ -z "$SKILL_DIR" ]] && usage 1

# Resolve to absolute path
SKILL_DIR=$(cd "$SKILL_DIR" 2>/dev/null && pwd) || { echo "Error: Directory not found: $SKILL_DIR"; exit 1; }

SKILL_FILE="${SKILL_DIR}/SKILL.md"
[[ -f "$SKILL_FILE" ]] || { echo "Error: SKILL.md not found in: $SKILL_DIR"; exit 1; }

DIR_NAME=$(basename "$SKILL_DIR")

echo "Validating skill: ${DIR_NAME}"
echo "Directory: ${SKILL_DIR}"
echo ""

# ===========================================================================
# YAML Header Validation
# ===========================================================================
echo "--- YAML Header ---"

# Check file starts with --- on line 1
first_line=$(head -1 "$SKILL_FILE")
if [[ "$first_line" == "---" ]]; then
  pass "File starts with --- on line 1"
else
  fail "File does not start with --- on line 1 (got: '${first_line}')"
fi

# Check YAML block ends with --- (second --- closes the header)
second_dash_line=$(grep -n '^---$' "$SKILL_FILE" | sed -n '2p' | cut -d: -f1)
if [[ -z "$second_dash_line" ]]; then
  fail "No closing --- found for YAML header"
elif [[ "$second_dash_line" -le 1 ]]; then
  fail "YAML header not properly closed (closing --- on or before line 1)"
else
  pass "YAML header block properly closed with --- (line ${second_dash_line})"
fi

# Extract and validate required fields
yaml_name=$(extract_yaml_field "$SKILL_FILE" "name")
yaml_description=$(extract_yaml_field "$SKILL_FILE" "description")
yaml_license=$(extract_yaml_field "$SKILL_FILE" "license")
yaml_author=$(extract_yaml_field "$SKILL_FILE" "author")
yaml_version=$(extract_yaml_field "$SKILL_FILE" "version")

# name: required, matches regex, matches directory
if [[ -z "$yaml_name" ]]; then
  fail "Missing 'name' field in YAML header"
  yaml_errors=$((yaml_errors + 1))
elif [[ "$yaml_name" != "$DIR_NAME" ]]; then
  fail "'name' field '$yaml_name' does not match directory name '$DIR_NAME'"
else
  pass "'name' field matches directory name"
fi

if [[ -n "$yaml_name" ]] && ! echo "$yaml_name" | grep -qP '^[a-z0-9]+(-[a-z0-9]+)*$'; then
  fail "'name' '$yaml_name' does not match regex ^[a-z0-9]+(-[a-z0-9]+)*$"
else
  [[ -n "$yaml_name" ]] && pass "'name' matches required format"
fi

# description: required, 1-1024 chars
if [[ -z "$yaml_description" ]]; then
  fail "Missing 'description' field in YAML header"
elif [[ ${#yaml_description} -gt 1024 ]]; then
  warn "'description' is ${#yaml_description} chars (max recommended: 1024)"
else
  pass "'description' present (${#yaml_description} chars)"
fi

# license: must be "MIT"
if [[ -z "$yaml_license" ]]; then
  fail "Missing 'license' field in YAML header"
elif [[ "$yaml_license" != "MIT" ]]; then
  fail "'license' is '$yaml_license', expected 'MIT'"
else
  pass "'license' is MIT"
fi

# author: format "Name <email@example.com>"
if [[ -z "$yaml_author" ]]; then
  fail "Missing 'author' field in YAML header"
elif ! echo "$yaml_author" | grep -qP '^\S+ <\S+@\S+\.\S+>$'; then
  warn "'author' format '$yaml_author' does not match 'Name <email@example.com>'"
else
  pass "'author' format is valid"
fi

# version: required, must be valid SemVer (skill file version, not upstream project version)
if [[ -z "$yaml_version" ]]; then
  fail "Missing 'version' field in YAML header"
elif ! echo "$yaml_version" | grep -qP '^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$'; then
  fail "'version' '$yaml_version' is not valid SemVer (expected MAJOR.MINOR.PATCH, e.g. '0.1.0'). This is the skill file's own version, not the upstream project version."
else
  pass "'version' present ('$yaml_version')"
fi

# tags: required, must be a non-empty array
tags=$(extract_tags "$SKILL_FILE")
tag_count=$(echo "$tags" | grep -c . || true)
if [[ $tag_count -eq 0 ]]; then
  fail "Missing or empty 'tags' field in YAML header"
else
  pass "'tags' present ($tag_count tags)"
fi

# category: optional but recommended
yaml_category=$(extract_yaml_field "$SKILL_FILE" "category")
if [[ -z "$yaml_category" ]]; then
  warn "Missing 'category' field in YAML header (recommended)"
else
  pass "'category' present ('$yaml_category')"
fi

echo ""

# ===========================================================================
# Directory Structure Validation
# ===========================================================================
echo "--- Directory Structure ---"

# SKILL.md exists (already checked above, but report here too)
pass "SKILL.md exists"

# Directory name matches skill name (already validated in YAML section)
# Skip duplicate check

# Check for reference/ directory
if [[ -d "${SKILL_DIR}/reference" ]]; then
  has_reference=1
  pass "reference/ directory exists"

  # Check flat structure — no subdirectories
  nested_dirs=$(find "${SKILL_DIR}/reference" -mindepth 1 -type d 2>/dev/null || true)
  if [[ -n "$nested_dirs" ]]; then
    fail "reference/ contains subdirectories (should be flat): $nested_dirs"
  else
    pass "reference/ has flat structure (no subdirectories)"
  fi

  # Check file naming: NN-*.md pattern
  ref_files=$(find "${SKILL_DIR}/reference" -maxdepth 1 -name "*.md" -type f 2>/dev/null || true)
  bad_named=""
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    fname=$(basename "$f")
    if ! echo "$fname" | grep -qP '^[0-9][0-9]-.*\.md$'; then
      bad_named="${bad_named} ${fname}"
    fi
  done <<< "$ref_files"

  if [[ -n "$bad_named" ]]; then
    fail "reference/ files not matching NN-*.md pattern:${bad_named}"
  else
    ref_count=$(echo "$ref_files" | grep -c . || true)
    pass "reference/ files match NN-*.md naming ($ref_count files)"
  fi

  # Check reference files are non-empty
  empty_refs=""
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    if [[ ! -s "$f" ]]; then
      empty_refs="${empty_refs} $(basename "$f")"
    fi
  done <<< "$ref_files"

  if [[ -n "$empty_refs" ]]; then
    fail "Empty reference files:${empty_refs}"
  else
    pass "Reference files are non-empty"
  fi

else
  has_reference=0
  pass "No reference/ directory (simple skill)"
fi

# Check for scripts/ and assets/ directories
if [[ -d "${SKILL_DIR}/scripts" ]]; then
  has_scripts=1
  warn "scripts/ directory exists (ensure this was intentional)"
else
  has_scripts=0
  pass "No scripts/ directory"
fi

if [[ -d "${SKILL_DIR}/assets" ]]; then
  warn "assets/ directory exists (ensure this was intentional)"
else
  pass "No assets/ directory"
fi

# Check for disallowed files/directories
disallowed=""
[[ -d "${SKILL_DIR}/.git" ]] && disallowed="${disallowed} .git/"
[[ -d "${SKILL_DIR}/.svn" ]] && disallowed="${disallowed} .svn/"
[[ -d "${SKILL_DIR}/.hg" ]] && disallowed="${disallowed} .hg/"
for env_file in "${SKILL_DIR}"/.env*; do
  [[ -e "$env_file" ]] && disallowed="${disallowed} $(basename "$env_file")"
done

if [[ -n "$disallowed" ]]; then
  fail "Disallowed files/dirs found:${disallowed}"
else
  pass "No disallowed files/directories (.git, .env*, etc.)"
fi

# Check for backslashes in file paths (should use forward slashes)
backslash_files=$(find "${SKILL_DIR}" -name '*\\*' 2>/dev/null || true)
if [[ -n "$backslash_files" ]]; then
  fail "Files with backslashes in names found"
else
  pass "No backslashes in file paths"
fi

echo ""

# ===========================================================================
# Content Section Validation
# ===========================================================================
echo "--- Content Sections ---"

# Check ## Overview section
if grep -q '^## Overview' "$SKILL_FILE"; then
  pass "## Overview section present"
else
  fail "Missing '## Overview' section"
fi

# Check ## When to Use section
if grep -q '^## When to Use' "$SKILL_FILE"; then
  pass "## When to Use section present"
else
  fail "Missing '## When to Use' section"
fi

# If reference/ exists, check SKILL.md line count < 500
if [[ $has_reference -eq 1 ]]; then
  skill_lines=$(wc -l < "$SKILL_FILE")
  if [[ $skill_lines -gt 500 ]]; then
    warn "SKILL.md is ${skill_lines} lines (max recommended: 500 when reference/ exists)"
  else
    pass "SKILL.md under 500 lines (${skill_lines} lines)"
  fi

  # Check ## Advanced Topics section with links to reference files
  if grep -q '^## Advanced Topics' "$SKILL_FILE"; then
    pass "## Advanced Topics section present"

    # Check that reference files are linked from SKILL.md
    ref_md_files=$(find "${SKILL_DIR}/reference" -maxdepth 1 -name "*.md" -type f 2>/dev/null | while read -r f; do basename "$f"; done)
    missing_links=""
    while IFS= read -r rf; do
      [[ -z "$rf" ]] && continue
      if ! grep -q "reference/${rf}" "$SKILL_FILE"; then
        missing_links="${missing_links} ${rf}"
      fi
    done <<< "$ref_md_files"

    if [[ -n "$missing_links" ]]; then
      warn "Reference files not linked from SKILL.md:${missing_links}"
    else
      pass "All reference files linked from SKILL.md"
    fi

  else
    fail "Missing '## Advanced Topics' section (required when reference/ exists)"
  fi

  # Check reference files have headings
  no_heading=""
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    if ! head -5 "$f" | grep -q '^#'; then
      no_heading="${no_heading} $(basename "$f")"
    fi
  done <<< "$ref_files"

  if [[ -n "$no_heading" ]]; then
    fail "Reference files missing headings:${no_heading}"
  else
    pass "Reference files have headings"
  fi
fi

echo ""

# ===========================================================================
# Script Validation (only if scripts/ exists)
# ===========================================================================
if [[ $has_scripts -eq 1 ]]; then
  echo "--- Scripts ---"

  # Check scripts referenced in SKILL.md actually exist
  # Match patterns like [scripts/foo.sh](scripts/foo.sh) or scripts/foo.sh
  referenced_scripts=$(grep -oP '(?<=\[)[^\]]*scripts/[^\]]*' "$SKILL_FILE" 2>/dev/null | sort -u || true)
  # Also match bare references (not in markdown links)
  referenced_scripts2=$(grep -oP 'scripts/[a-zA-Z0-9_.-]+' "$SKILL_FILE" 2>/dev/null | grep -v '^scripts/$' | sort -u || true)
  referenced_scripts=$(printf '%s\n%s' "$referenced_scripts" "$referenced_scripts2" | sort -u | grep . || true)

  missing_scripts=""
  while IFS= read -r ref; do
    [[ -z "$ref" ]] && continue
    if [[ ! -f "${SKILL_DIR}/${ref}" ]]; then
      missing_scripts="${missing_scripts} ${ref}"
    fi
  done <<< "$referenced_scripts"

  if [[ -n "$missing_scripts" ]]; then
    fail "Referenced scripts not found:${missing_scripts}"
  elif [[ -n "$referenced_scripts" ]]; then
    pass "All referenced scripts exist on disk"
  else
    pass "No script references in SKILL.md (scripts may be standalone)"
  fi

  # Check for package installation in scripts (per AGENTS.md rules)
  # Only check non-comment lines to avoid false positives
  install_violations=""
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    [[ -f "$f" ]] || continue
    # Strip comment lines and lines containing grep/regex patterns before checking
    if grep -vP '^\s*(#|//)' "$f" 2>/dev/null | grep -vP '(grep|sed|awk)' | grep -qP '(pip install|npm install|apt-get install|yum install)'; then
      install_violations="${install_violations} $(basename "$f")"
    fi
  done < <(find "${SKILL_DIR}/scripts" -maxdepth 1 -type f 2>/dev/null)

  if [[ -n "$install_violations" ]]; then
    warn "Scripts with package installs (violates AGENTS.md):${install_violations}"
  else
    pass "No package installation commands in scripts"
  fi

  # Check scripts have shebang or recognizable extension
  bad_scripts=""
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    [[ -f "$f" ]] || continue
    fname=$(basename "$f")
    # Check for shebang or recognized extension
    has_shebang=$(head -1 "$f" | grep -c '^#!' || true)
    has_ext=$(echo "$fname" | grep -cP '\.(sh|bash|py|js|ts)$' || true)
    if [[ $has_shebang -eq 0 ]] && [[ $has_ext -eq 0 ]]; then
      bad_scripts="${bad_scripts} ${fname}"
    fi
  done < <(find "${SKILL_DIR}/scripts" -maxdepth 1 -type f 2>/dev/null)

  if [[ -n "$bad_scripts" ]]; then
    warn "Scripts without shebang or recognized extension:${bad_scripts}"
  else
    pass "All scripts have shebang or recognizable extension"
  fi

  echo ""
fi

# ===========================================================================
# Summary
# ===========================================================================
echo "--- Summary ---"
total=$((errors + warnings + passes))
echo "  Checks passed: ${passes}"
echo "  Errors:        ${errors}"
echo "  Warnings:      ${warnings}"
echo "  Total checks:  ${total}"

if [[ $errors -gt 0 ]]; then
  echo ""
  echo "✗ Validation FAILED with ${errors} error(s)"
  exit 1
elif [[ $warnings -gt 0 ]] && [[ $STRICT -eq 1 ]]; then
  echo ""
  echo "✗ Validation FAILED in strict mode with ${warnings} warning(s)"
  exit 1
elif [[ $warnings -gt 0 ]]; then
  echo ""
  echo "⚠ Validation passed with ${warnings} warning(s)"
  exit 0
else
  echo ""
  echo "✓ Validation PASSED"
  exit 0
fi
