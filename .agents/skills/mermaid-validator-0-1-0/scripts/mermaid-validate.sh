#!/usr/bin/env bash
# mermaid-validate.sh — Wrapper for @zabaca/mermaid-validate@1.0.1
#
# Validates Mermaid diagram syntax in files, directories, or stdin.
# Tries `bun x` first, falls back to `npx -y` if bun is unavailable.
# Handles the upstream tool's broken directory mode by expanding directories
# into individual file paths before passing them through.
#
# Usage:
#   bash mermaid-validate.sh [OPTIONS] <file|directory|->
#
# Options:
#   -q, --quiet   Only output errors (suppress valid file markers)
#   --json        Output results as JSON
#   -h, --help    Show this help message
#
# Exit codes:
#   0 — All diagrams valid (or no mermaid blocks found)
#   1 — One or more diagrams have syntax errors
#   2 — Usage error (no input, missing file, etc.)

set -euo pipefail

readonly PACKAGE="@zabaca/mermaid-validate@1.0.1"

usage() {
    cat <<'EOF'
Usage: mermaid-validate.sh [OPTIONS] <file|directory|->

Validate Mermaid diagram syntax in files, directories, or stdin.

Options:
  -q, --quiet   Only output errors (suppress valid file markers)
  --json        Output results as JSON
  -h, --help    Show this help message

Arguments:
  <file>       Single .md, .mmd, .markdown, or .mdx file
  <directory>  Recursively validate all matching files
  -            Read diagram code from stdin

Exit codes:
  0  All diagrams valid (or no mermaid blocks found)
  1  One or more diagrams have syntax errors
  2  Usage error
EOF
}

# --- Resolve runner: prefer bun x, fall back to npx -y ---
resolve_runner() {
    if command -v bun &>/dev/null; then
        echo "bun"
    elif command -v npx &>/dev/null; then
        echo "npx"
    else
        echo "ERROR: Neither bun nor npx found. Install one of them." >&2
        exit 2
    fi
}

# --- Expand a directory into a list of matching files ---
expand_directory() {
    local dir="$1"
    # Use -regex to avoid shell glob expansion issues with -name "*.ext"
    # Regex matches files ending in .md, .mmd, .markdown, .mdx, or .mermaid
    find "$dir" -type f -regex '.*\.\(md\|mmd\|markdown\|mdx\|mermaid\)$' 2>/dev/null | sort
}

# --- Parse arguments ---
RUNNER="$(resolve_runner)"
EXTRA_ARGS=()
INPUT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        -q|--quiet)
            EXTRA_ARGS+=("$1")
            shift
            ;;
        --json)
            EXTRA_ARGS+=("$1")
            shift
            ;;
        -)
            # Stdin marker — must match before -* wildcard
            if [[ -n "$INPUT" ]]; then
                echo "ERROR: Multiple inputs specified: $INPUT and -" >&2
                exit 2
            fi
            INPUT="-"
            shift
            ;;
        -*)
            echo "ERROR: Unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
        *)
            if [[ -n "$INPUT" ]]; then
                echo "ERROR: Multiple inputs specified: $INPUT and $1" >&2
                exit 2
            fi
            INPUT="$1"
            shift
            ;;
    esac
done

# --- Validate input ---
if [[ -z "$INPUT" ]]; then
    echo "ERROR: No input specified. Provide a file, directory, or '-' for stdin." >&2
    usage >&2
    exit 2
fi

if [[ "$INPUT" != "-" ]] && [[ ! -e "$INPUT" ]]; then
    echo "ERROR: Path does not exist: $INPUT" >&2
    exit 2
fi

# --- Execute validation ---
if [[ "$INPUT" == "-" ]]; then
    # stdin mode
    if [[ "$RUNNER" == "bun" ]]; then
        exec bun x "$PACKAGE" "${EXTRA_ARGS[@]}" -
    else
        exec npx -y "$PACKAGE" "${EXTRA_ARGS[@]}" -
    fi

elif [[ -d "$INPUT" ]]; then
    # directory mode — upstream tool has broken dir support, expand manually
    FILES=()
    while IFS= read -r f; do
        [[ -n "$f" ]] && FILES+=("$f")
    done < <(expand_directory "$INPUT")

    if [[ ${#FILES[@]} -eq 0 ]]; then
        if [[ "${EXTRA_ARGS[*]:-}" == *"--json"* ]]; then
            echo '{"totalValid":0,"totalInvalid":0,"results":[]}'
        else
            echo "No markdown files found"
        fi
        exit 0
    fi

    # Run validator on each file, collecting exit status
    HAS_ERRORS=false
    for f in "${FILES[@]}"; do
        if [[ "$RUNNER" == "bun" ]]; then
            if ! bun x "$PACKAGE" "${EXTRA_ARGS[@]}" "$f" 2>&1; then
                HAS_ERRORS=true
            fi
        else
            if ! npx -y "$PACKAGE" "${EXTRA_ARGS[@]}" "$f" 2>&1; then
                HAS_ERRORS=true
            fi
        fi
    done

    if $HAS_ERRORS; then
        exit 1
    fi
    exit 0

else
    # single file mode
    if [[ "$RUNNER" == "bun" ]]; then
        exec bun x "$PACKAGE" "${EXTRA_ARGS[@]}" "$INPUT"
    else
        exec npx -y "$PACKAGE" "${EXTRA_ARGS[@]}" "$INPUT"
    fi
fi
