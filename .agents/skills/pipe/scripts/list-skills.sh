#!/usr/bin/env bash
# list-skills.sh — Enumerate available agent skills with metadata.
#
# Pure inventory: lists skills, does NOT match stages to skills.
# The LLM agent uses this output to decide which skill to invoke.
#
# Usage:
#   list-skills.sh [OPTIONS] [SKILLS_DIR]
#
# Arguments:
#   SKILLS_DIR    Path to .agents/skills directory (default: nearest .agents/skills
#                 found by walking up from CWD, or $SKILLS_DIR env var)
#
# Options:
#   --filter WORD  Only show skills whose name, description, or tags contain WORD
#                  (case-insensitive). Can be repeated.
#   --help         Show this help message
#
# Output format (one block per skill):
#   === Skill: <name> ===
#   description: <text>
#   tags: tag1, tag2, ...
#   ---
#
# Exit codes:
#   0  Success (even if no skills found — prints a message)
#   1  Error (missing directory, permission denied)

set -euo pipefail

# ── Parse arguments ───────────────────────────────────────────────────

FILTERS=()
SKILLS_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            sed -n '2,17p' "$0" | grep '^#' | sed 's/^# \?//'
            exit 0
            ;;
        --filter)
            if [[ -z "${2:-}" ]]; then
                echo "Error: --filter requires a non-empty argument" >&2
                exit 1
            fi
            FILTERS+=("$2")
            shift 2
            ;;
        --*)
            echo "Error: unknown option '$1'" >&2
            echo "Use --help for usage" >&2
            exit 1
            ;;
        *)
            SKILLS_DIR="$1"
            shift
            ;;
    esac
done

# ── Resolve skills directory ──────────────────────────────────────────

if [[ -z "$SKILLS_DIR" ]]; then
    SKILLS_DIR="${SKILLS_DIR:-}"
fi

if [[ -z "$SKILLS_DIR" ]]; then
    # Walk up from CWD looking for .agents/skills
    dir="$(pwd)"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.agents/skills" ]]; then
            SKILLS_DIR="$dir/.agents/skills"
            break
        fi
        dir="$(dirname "$dir")"
    done
fi

if [[ -z "$SKILLS_DIR" ]]; then
    echo "Error: no .agents/skills directory found. Provide a path or set SKILLS_DIR." >&2
    exit 1
fi

if [[ ! -d "$SKILLS_DIR" ]]; then
    echo "Error: directory not found: $SKILLS_DIR" >&2
    exit 1
fi

# ── Enumerate skills ──────────────────────────────────────────────────

FOUND=0
MATCHED=0

for skill_dir in "$SKILLS_DIR"/*/; do
    # Skip if glob didn't match (no subdirectories)
    [[ -d "$skill_dir" ]] || continue

    skill_md="${skill_dir}SKILL.md"
    [[ -f "$skill_md" ]] || continue

    # Extract YAML header fields using awk between first --- pair
    name=""
    description=""
    tags=()
    in_header=0
    in_tags=0
    in_desc_fold=0   # 1 if description uses >- or |- (folded/literal block)

    while IFS= read -r line; do
        # First --- opens header
        if [[ $in_header -eq 0 && "$line" == "---" ]]; then
            in_header=1
            continue
        fi
        # Second --- closes header
        if [[ $in_header -eq 1 && "$line" == "---" ]]; then
            break
        fi

        if [[ $in_header -eq 1 ]]; then
            # Handle folded/literal block scalar continuation for description
            if [[ $in_desc_fold -eq 1 ]]; then
                # Indented line → append to description
                if [[ "$line" =~ ^[[:space:]] ]]; then
                    stripped="${line#"${line%%[![:space:]]*}"}"
                    if [[ -n "$description" ]]; then
                        description="$description $stripped"
                    else
                        description="$stripped"
                    fi
                    continue
                else
                    # Non-indented line ends the block
                    in_desc_fold=0
                fi
            fi

            # Check for tag list items
            if [[ "$line" =~ ^[[:space:]]*-[[:space:]]+(.*) ]]; then
                if [[ $in_tags -eq 1 ]]; then
                    tags+=("${BASH_REMATCH[1]}")
                fi
                continue
            fi

            # Key: value pairs
            if [[ "$line" =~ ^name:[[:space:]]*(.*) ]]; then
                name="${BASH_REMATCH[1]}"
                in_tags=0
            elif [[ "$line" =~ ^description:[[:space:]]*([|>][-]?)(.*) ]]; then
                # Detect folded (>-) or literal (|-) block scalar
                if [[ -n "${BASH_REMATCH[1]}" ]]; then
                    in_desc_fold=1
                    description="${BASH_REMATCH[2]}"
                    # Remove leading/trailing whitespace from inline part
                    description="${description#"${description%%[![:space:]]*}"}"
                else
                    description="${BASH_REMATCH[1]}"
                fi
                in_tags=0
            elif [[ "$line" =~ ^description:[[:space:]]*(.*) ]]; then
                description="${BASH_REMATCH[1]}"
                in_tags=0
            elif [[ "$line" == "tags:" ]]; then
                in_tags=1
            else
                # Non-tag line ends the tags block
                if [[ $in_tags -eq 1 && ! "$line" =~ ^[[:space:]] ]]; then
                    in_tags=0
                fi
            fi
        fi
    done < "$skill_md"

    # Skip skills without a name (malformed)
    [[ -n "$name" ]] || continue

    FOUND=$((FOUND + 1))

    # ── Apply filters (AND logic: all filters must match) ───────────
    if [[ ${#FILTERS[@]} -gt 0 ]]; then
        search_text="${name} ${description}"
        for tag in "${tags[@]}"; do
            search_text="$search_text $tag"
        done
        search_lower="$(echo "$search_text" | tr '[:upper:]' '[:lower:]')"

        all_matched=1
        for filter in "${FILTERS[@]}"; do
            filter_lower="$(echo "$filter" | tr '[:upper:]' '[:lower:]')"
            if [[ "$search_lower" != *"$filter_lower"* ]]; then
                all_matched=0
                break
            fi
        done

        [[ $all_matched -eq 1 ]] || continue
    fi

    MATCHED=$((MATCHED + 1))

    # ── Output skill block ──────────────────────────────────────────
    echo "=== Skill: ${name} ==="
    echo "description: ${description}"

    if [[ ${#tags[@]} -gt 0 ]]; then
        tags_str=""
        for tag in "${tags[@]}"; do
            if [[ -n "$tags_str" ]]; then
                tags_str="$tags_str, $tag"
            else
                tags_str="$tag"
            fi
        done
        echo "tags: $tags_str"
    else
        echo "tags: (none)"
    fi
    echo "---"
done

# ── Summary ───────────────────────────────────────────────────────────

if [[ $FOUND -eq 0 ]]; then
    echo "No skills found in: $SKILLS_DIR"
elif [[ ${#FILTERS[@]} -gt 0 && $MATCHED -eq 0 ]]; then
    filter_str=""
    for f in "${FILTERS[@]}"; do
        [[ -n "$filter_str" ]] && filter_str="$filter_str + "
        filter_str="${filter_str}\"$f\""
    done
    echo "No skills matching ${filter_str} (searched $FOUND skills)."
elif [[ ${#FILTERS[@]} -gt 0 ]]; then
    echo ""
    echo "Found $MATCHED of $FOUND skills matching filter(s)."
fi
