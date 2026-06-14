#!/usr/bin/env bash
# mermaid.sh — Mermaid diagram validation tool
#
# Wraps @zabaca/mermaid-validate@1.0.1 with subcommand dispatch,
# runner detection (bun x > npx -y), and directory expansion
# to work around the upstream tool's broken directory mode.
#
# Usage:
#   mermaid.sh validate [OPTIONS] <file|directory|->
#   mermaid.sh --help

set -euo pipefail

readonly PACKAGE="@zabaca/mermaid-validate@1.0.1"

# --- Top-level help ---
usage() {
    cat <<'EOF'
Usage: mermaid.sh <subcommand> [OPTIONS]

Mermaid diagram validation tool.

Subcommands:
  validate   Validate Mermaid diagram syntax in files, directories, or stdin

Global options:
  -h, --help   Show this help message
EOF
}

# --- validate subcommand help ---
validate_usage() {
    cat <<'EOF'
Usage: mermaid.sh validate [OPTIONS] <file|directory|->

Validate Mermaid diagram syntax in files, directories, or stdin.

Options:
  -q, --quiet   Only output errors (suppress valid file markers)
  --json        Output results as JSON
  -h, --help    Show this help message

Arguments:
  <file>       Single .md, .mmd, .markdown, .mdx, or .mermaid file
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
    find "$dir" -type f -regex '.*\.\(md\|mmd\|markdown\|mdx\|mermaid\)$' 2>/dev/null | sort
}

# --- Run the upstream validator with given runner and args ---
run_validator() {
    local runner="$1"
    shift
    # $@ are the remaining args
    if [[ "$runner" == "bun" ]]; then
        bun x "$PACKAGE" "$@"
    else
        npx -y "$PACKAGE" "$@"
    fi
}

# --- validate subcommand ---
cmd_validate() {
    local runner extra_args input

    runner="$(resolve_runner)"
    extra_args=()
    input=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                validate_usage
                exit 0
                ;;
            -q|--quiet)
                extra_args+=("$1")
                shift
                ;;
            --json)
                extra_args+=("$1")
                shift
                ;;
            -)
                if [[ -n "$input" ]]; then
                    echo "ERROR: Multiple inputs specified: $input and -" >&2
                    exit 2
                fi
                input="-"
                shift
                ;;
            -*)
                echo "ERROR: Unknown option: $1" >&2
                validate_usage >&2
                exit 2
                ;;
            *)
                if [[ -n "$input" ]]; then
                    echo "ERROR: Multiple inputs specified: $input and $1" >&2
                    exit 2
                fi
                input="$1"
                shift
                ;;
        esac
    done

    # --- Validate input ---
    if [[ -z "$input" ]]; then
        echo "ERROR: No input specified. Provide a file, directory, or '-' for stdin." >&2
        validate_usage >&2
        exit 2
    fi

    if [[ "$input" != "-" ]] && [[ ! -e "$input" ]]; then
        echo "ERROR: Path does not exist: $input" >&2
        exit 2
    fi

    # --- Execute validation ---
    if [[ "$input" == "-" ]]; then
        # stdin mode
        run_validator "$runner" "${extra_args[@]}" -

    elif [[ -d "$input" ]]; then
        # directory mode — upstream tool has broken dir support, expand manually
        local files=()
        while IFS= read -r f; do
            [[ -n "$f" ]] && files+=("$f")
        done < <(expand_directory "$input")

        if [[ ${#files[@]} -eq 0 ]]; then
            if [[ "${extra_args[*]:-}" == *"--json"* ]]; then
                echo '{"totalValid":0,"totalInvalid":0,"results":[]}'
            else
                echo "No markdown files found"
            fi
            exit 0
        fi

        # Run validator on each file, collecting exit status
        local has_errors=false
        for f in "${files[@]}"; do
            if ! run_validator "$runner" "${extra_args[@]}" "$f" 2>&1; then
                has_errors=true
            fi
        done

        if $has_errors; then
            exit 1
        fi
        exit 0

    else
        # single file mode
        run_validator "$runner" "${extra_args[@]}" "$input"
    fi
}

# --- Main dispatch ---
if [[ $# -eq 0 ]]; then
    usage
    exit 2
fi

case "$1" in
    validate)
        shift
        cmd_validate "$@"
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    *)
        echo "ERROR: Unknown subcommand: $1" >&2
        usage >&2
        exit 2
        ;;
esac
