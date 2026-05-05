#!/usr/bin/env bash
# gen-skill-list.sh — Regenerate the Skills Table in README.md from YAML headers.
#
# Pure bash/awk equivalent of misc/gen-skills-table.py.
# Uses only POSIX tools: bash, awk, sed, grep, sort, mktemp, mv.
#
# Usage:
#   bash scripts/gen-skill-list.sh [--dry-run]
#
# Reads every .agents/skills/<name>/SKILL.md, extracts YAML header fields,
# and replaces the ## Skills Table section (through ## Statistics) in README.md.

set -euo pipefail

# ── Resolve paths relative to repo root ──────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# scripts/ lives at .agents/skills/skill/scripts/ → 4 levels up = repo root
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SKILLS_DIR="$REPO_ROOT/.agents/skills"
README_PATH="$REPO_ROOT/README.md"

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=1
fi

# Pre-declare tmpfile so trap doesn't fail with unbound variable on early exit
TMPFILE=""

# ── Validate prerequisites ───────────────────────────────────────────────────
if [[ ! -d "$SKILLS_DIR" ]]; then
    echo "ERROR: Skills directory not found: $SKILLS_DIR" >&2
    exit 1
fi

if [[ ! -f "$README_PATH" ]]; then
    echo "ERROR: README.md not found: $README_PATH" >&2
    exit 1
fi

# ── Extract YAML fields from a single SKILL.md ──────────────────────────────
# Outputs tab-separated: name\tversion\tdescription\ttags_csv
extract_yaml() {
    local skill_md="$1"

    awk '
    BEGIN { in_header=0; in_tags=0; tag_count=0 }

    # Detect YAML header boundaries
    /^---[[:space:]]*$/ {
        if (!in_header) { in_header = 1; next }
        else { in_header = 0; exit }
    }

    !in_header { next }

    # Extract name
    /^name:[[:space:]]/ {
        sub(/^name:[[:space:]]+/, "")
        gsub(/[[:space:]]*$/, "")
        name = $0
        next
    }

    # Extract version (strip surrounding quotes with sed-like approach)
    /^version:[[:space:]]/ {
        sub(/^version:[[:space:]]+/, "")
        gsub(/[[:space:]]*$/, "")
        # Remove surrounding quotes if present
        if (substr($0,1,1) == "\"" && substr($0,length($0),1) == "\"") {
            version = substr($0, 2, length($0)-2)
        } else if (substr($0,1,1) == "\x27" && substr($0,length($0),1) == "\x27") {
            version = substr($0, 2, length($0)-2)
        } else {
            version = $0
        }
        next
    }

    # Extract description — handle inline and block literal (>, >-, |)
    /^description:[[:space:]]/ {
        sub(/^description:[[:space:]]+/, "")
        val = $0
        gsub(/[[:space:]]*$/, "")
        if (val == ">" || val == ">-" || val == "|") {
            desc_mode = "block"
            indent = -1
            desc_text = ""
            next
        } else {
            # Strip surrounding quotes
            if (substr(val,1,1) == "\"" && substr(val,length(val),1) == "\"") {
                desc_text = substr(val, 2, length(val)-2)
            } else if (substr(val,1,1) == "\x27" && substr(val,length(val),1) == "\x27") {
                desc_text = substr(val, 2, length(val)-2)
            } else {
                desc_text = val
            }
            next
        }
    }

    # Collect block literal description lines
    desc_mode == "block" {
        if ($0 ~ /^[[:space:]]/) {
            stripped = $0
            gsub(/^[[:space:]]+/, "", stripped)
            if (stripped == "") next
            if (indent < 0) {
                indent = length($0) - length(stripped)
            }
            line = substr($0, indent + 1)
            desc_text = (desc_text == "" ? line : desc_text " " line)
        } else {
            desc_mode = ""
        }
        next
    }

    # Collect tags array (limit to first 5, comma-space separated)
    /^tags:[[:space:]]*$/ || /^tags:[[:space:]]*#/ {
        in_tags = 1
        next
    }

    in_tags && /^[[:space:]]*- / {
        if (tag_count < 5) {
            tag = $0
            sub(/^[[:space:]]*- /, "", tag)
            gsub(/[[:space:]]*$/, "", tag)
            tags = (tags == "" ? tag : tags ", " tag)
            tag_count++
        }
        next
    }

    in_tags && !/^[[:space:]]*- / {
        in_tags = 0
    }

    END {
        if (name != "") {
            # Truncate description at ~120 chars, break at word boundary
            desc = desc_text
            if (length(desc) > 120) {
                truncated = substr(desc, 1, 120)
                last_space = 0
                half = int(length(truncated) * 0.5)
                for (i = half; i <= length(truncated); i++) {
                    if (substr(truncated, i, 1) == " ") last_space = i
                }
                if (last_space > half) {
                    truncated = substr(truncated, 1, last_space - 1)
                }
                desc = truncated "..."
            }
            # Escape pipe chars in all fields
            gsub(/\|/, "\\|", desc)
            gsub(/\|/, "\\|", tags)
            if (tags == "") tags = "-"

            printf "%s\t%s\t%s\t%s\n", name, version, desc, tags
        }
    }
    ' "$skill_md"
}

# ── Derive project name by stripping version suffix ──────────────────────────
extract_project() {
    local name="$1"
    echo "$name" | sed -E 's/-[0-9]{4}-[0-9]{2}-[0-9]{2}$//' \
        | sed -E 's/-[0-9]+-[0-9]+-[0-9]+(-[a-zA-Z0-9]+(-[0-9]+)?)?$//' \
        | sed -E 's/-[0-9]+-[0-9]+$//' \
        | sed -E 's/-[0-9]+$//'
}

# ── Generate table rows from all skills ──────────────────────────────────────
generate_table() {
    local header="| No | Skill | Project | Version | Technologies | Description |"
    local sep="|----|-------|---------|---------|--------------|-------------|"

    echo "$header"
    echo "$sep"

    local count=0
    # Use LC_ALL=C sort for byte-level ordering matching Python's sorted()
    local dirs
    dirs="$(ls -1 "$SKILLS_DIR" | LC_ALL=C sort)"
    for dir_name in $dirs; do
        [[ -d "$SKILLS_DIR/$dir_name" ]] || continue
        local skill_md="$SKILLS_DIR/$dir_name/SKILL.md"
        [[ -f "$skill_md" ]] || continue

        local row
        row="$(extract_yaml "$skill_md")"
        [[ -n "$row" ]] || continue

        local name version desc tags
        name="$(echo "$row" | awk -F'\t' '{print $1}')"
        version="$(echo "$row" | awk -F'\t' '{print $2}')"
        desc="$(echo "$row" | awk -F'\t' '{print $3}')"
        tags="$(echo "$row" | awk -F'\t' '{print $4}')"

        local project
        project="$(extract_project "$name")"
        [[ -z "$project" ]] && project="-"

        count=$((count + 1))
        echo "| ${count} | ${name} | ${project} | ${version} | ${tags} | ${desc} |"
    done

    # Return count via stderr (subshell workaround)
    echo "__COUNT__${count}" >&2
}

# ── Main ─────────────────────────────────────────────────────────────────────
main() {
    TMPFILE="$(mktemp)"
    # Set up cleanup using a function to avoid unbound variable issues
    _cleanup() { rm -f "$TMPFILE" "${TMPFILE}.count" "${TMPFILE}.new" 2>/dev/null; }
    trap _cleanup EXIT

    # Generate table to temp file, capture count from stderr
    generate_table >"$TMPFILE" 2>"$TMPFILE.count"
    local total
    total="$(grep '^__COUNT__' "$TMPFILE.count" | sed 's/^__COUNT__//')"

    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "[dry-run] Would generate $total skill entries"
        cat "$TMPFILE"
        return 0
    fi

    # Check that README has the expected sections
    if ! grep -q '^## Skills Table' "$README_PATH"; then
        echo "ERROR: Could not find '## Skills Table' section in README.md" >&2
        exit 1
    fi

    # Build replacement content
    local stats_line="- **Total Skills**: ${total}"

    # Use awk to replace from "## Skills Table\n\n" through the statistics line
    awk -v table_file="$TMPFILE" -v stats="$stats_line" '
    BEGIN { replaced=0 }

    /^## Skills Table$/ {
        replaced = 1
        print $0
        print ""
        next
    }

    replaced && /^## Statistics$/ {
        # Print table, then blank line, then this section header, then blank line
        while ((getline line < table_file) > 0) {
            print line
        }
        close(table_file)
        print ""
        print $0
        print ""
        next
    }

    replaced && /^- \*\*Total Skills\*\*: / {
        print stats
        next
    }

    # Skip all lines between ## Skills Table and ## Statistics
    replaced && !/^## / { next }

    { print }
    ' "$README_PATH" >"$TMPFILE.new"

    mv -f "$TMPFILE.new" "$README_PATH"
    echo "Updated README.md with $total skills"
}

main
