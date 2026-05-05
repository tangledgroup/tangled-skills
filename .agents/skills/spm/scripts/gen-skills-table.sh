#!/usr/bin/env bash
# gen-skills-table.sh — Regenerate the Skills Table section in README.md
#
# Usage:
#   bash gen-skills-table.sh [SKILLS_DIR] [README_PATH]
#
# Arguments:
#   SKILLS_DIR  Directory containing skill subdirectories (default: .agents/skills)
#   README_PATH Path to README.md to update         (default: README.md)
#
# Pure bash — no Python, no external YAML parsers.
# Uses: grep, sed, awk, sort, find (all POSIX).

set -euo pipefail

SKILLS_DIR="${1:-.agents/skills}"
README_PATH="${2:-README.md}"

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "Error: Skills directory '$SKILLS_DIR' not found." >&2
  exit 1
fi

if [[ ! -f "$README_PATH" ]]; then
  echo "Error: README file '$README_PATH' not found." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# extract_yaml_field FILE FIELD
#   Extract a simple single-line YAML field from the header block.
#   For 'description', also handles block-scalar (>) multi-line values
#   by collapsing continuation lines into one line.
# ---------------------------------------------------------------------------
extract_yaml_field() {
  local file="$1"
  local field="$2"
  awk -v field="$field" '
    BEGIN { found=0; in_block=0; buf="" }
    # Only process the YAML header (between first pair of ---)
    NR==1 && /^---$/ { next }
    /^---$/ { if (!header_end) { header_end=1; next }; exit }
    !header_end {
      if (in_block) {
        # Continuation line: must start with spaces
        if ($0 ~ /^  /) {
          line = substr($0, 3)
          gsub(/^ +| +$/, "", line)
          buf = buf " " line
          next
        } else {
          # End of block scalar — print accumulated buffer
          gsub(/^ +| +$/, "", buf)
          print buf
          in_block=0
          buf=""
          found=2
          # Fall through to process this line normally
        }
      }
      if (found == 0 && $0 ~ "^" field ":") {
        val = $0
        sub("^" field ": *", "", val)
        # Check for block scalar (>)
        if (val ~ /^ *> *$/) {
          in_block=1
          buf=""
          next
        }
        # Single-line value
        gsub(/^ +| +$/, "", val)
        print val
        found=2
        next
      }
    }
  ' "$file"
}

# ---------------------------------------------------------------------------
# extract_tags FILE
#   Extract tags array from YAML header, return first 5 joined with ", ".
#   Handles both "  - tag" and "- tag" indentation styles.
# ---------------------------------------------------------------------------
extract_tags() {
  local file="$1"
  awk '
    BEGIN { in_tags=0; count=0 }
    /^tags:/ { in_tags=1; next }
    in_tags && /^[[:space:]]*-/ {
      tag = $0
      sub(/^[[:space:]]*-[[:space:]]*/, "", tag)
      gsub(/^ +| +$/, "", tag)
      count++
      if (count <= 5) {
        if (buf) buf = buf ", " tag
        else buf = tag
      }
      next
    }
    in_tags && !/^[[:space:]]*-/ {
      print buf
      exit
    }
  ' "$file"
}

# ---------------------------------------------------------------------------
# strip_version_suffix DIR_NAME
#   Derive the "project" name from a skill directory name by removing
#   the version suffix. Strips trailing numeric segments and pre-release
#   tags (alpha/beta/rc).
#
#   Examples:
#     a2a-1-0-0                → a2a
#     jsonpath-rfc-9535-1-0-0  → jsonpath-rfc
#     crdt-2026-05-03          → crdt
#     rustfs-1-0-0-alpha-93    → rustfs
#     networkxternal-0-5       → networkxternal
#     git                      → git
# ---------------------------------------------------------------------------
strip_version_suffix() {
  local dir="$1"

  # Strip trailing pre-release: -(alpha|beta|rc)-N
  dir=$(echo "$dir" | sed -E 's/-(alpha|beta|rc)-[0-9]+$//')

  # Strip trailing sequences of -NUMBER (handles multi-segment versions)
  dir=$(echo "$dir" | sed -E 's/(-[0-9]+)+$//')

  echo "$dir"
}

# ---------------------------------------------------------------------------
# truncate_desc TEXT MAX_LEN
#   Truncate text to MAX_LEN characters (including "..."). If already short,
#   return as-is. Cuts at word boundary.
# ---------------------------------------------------------------------------
truncate_desc() {
  local text="$1"
  local max="${2:-120}"

  if [[ ${#text} -le $max ]]; then
    echo "$text"
    return
  fi

  # Cut to (max - 3) chars, then find last space for clean break
  local cut_len=$((max - 3))
  local truncated="${text:0:$cut_len}"

  # Find last space to avoid mid-word cuts
  local last_space
  last_space=$(echo "$truncated" | awk '{
    pos = 0
    for (i=1; i<=length($0); i++) {
      if (substr($0, i, 1) == " ") pos = i
    }
    print pos
  }')

  if [[ $last_space -gt 0 ]]; then
    truncated="${truncated:0:$last_space}"
  fi

  echo "${truncated}..."
}

# ---------------------------------------------------------------------------
# Main: Collect skill data, build table, update README.md
# ---------------------------------------------------------------------------

# Temporary file for sorted rows
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT

count=0

for skill_dir in "$SKILLS_DIR"/*/; do
  # Skip if not a directory
  [[ -d "$skill_dir" ]] || continue

  skill_name=$(basename "$skill_dir")
  skill_file="${skill_dir}SKILL.md"

  # Skip if no SKILL.md
  [[ -f "$skill_file" ]] || continue

  # Extract fields
  version=$(extract_yaml_field "$skill_file" "version" | tr -d '"')
  description=$(extract_yaml_field "$skill_file" "description")
  tags=$(extract_tags "$skill_file")

  # Derive project name from directory
  project=$(strip_version_suffix "$skill_name")

  # Truncate description
  desc_truncated=$(truncate_desc "$description" 120)

  # Escape any pipe characters in fields (safety)
  desc_escaped="${desc_truncated//|/\\|}"

  # Write to temp file for sorting: sort key \t full row
  printf '%s\t%s\n' "$skill_name" "| $((count + 1)) | ${skill_name} | ${project} | ${version} | ${tags} | ${desc_escaped} |" >> "$tmpfile"

  count=$((count + 1))
done

# Sort by skill name (first field), then renumber
sorted=$(sort -t$'\t' -k1,1 "$tmpfile" | cut -f2- | awk '{
  NR_count++
  # Replace the first number field with sequential count
  sub(/\| [0-9]+ \|/, "| " NR_count " |")
  print
}')

# Build the complete table section
table="## Skills Table"
table="${table}"$'\n'
table="${table}"$'\n'"| No | Skill | Project | Version | Technologies | Description |"
table="${table}"$'\n'"|----|-------|---------|---------|--------------|-------------|"
table="${table}"$'\n'"${sorted}"

# Update README.md: replace everything from "## Skills Table" to just before
# "## Statistics". Preserve content before and after.
awk -v table="$table" '
  BEGIN { printed_table=0; in_section=0 }
  /^## Skills Table/ {
    in_section=1
    print ""
    print table
    next
  }
  /^## Statistics/ {
    in_section=0
  }
  !in_section { print }
' "$README_PATH" > "${README_PATH}.tmp"

mv -f "${README_PATH}.tmp" "$README_PATH"

# Update the statistics line
sed -i "s/- \*\*Total Skills\*\*: .*/- **Total Skills**: ${count}/" "$README_PATH"

echo "Generated skills table with ${count} skills in ${README_PATH}"
