#!/usr/bin/env bash
# vega-lite-validate.sh — Validate a Vega-Lite spec against the official JSON Schema.
#
# Usage:
#   vega-lite-validate.sh <instance.json>
#
# Arguments:
#   instance.json  Path to a Vega-Lite specification file to validate.
#
# Schema:
#   Uses scripts/vega-lite-schema.json (shipped with this skill) as the schema.
#   The schema path is resolved relative to this script's location, so the
#   script works from any working directory.
#
# Exit Codes:
#   0  — Instance is valid under the Vega-Lite schema.
#   1  — Validation failed (schema errors found).
#   2  — Usage error (missing argument, missing files, etc.).
#
# Output:
#   On success:    "ok -- validation done"
#   On failure:    Detailed per-path error list from check-jsonschema.
#
# Dependencies:
#   uvx or pipx (provides check-jsonschema), bash 4+

set -euo pipefail

# Resolve script directory so schema path is always correct regardless of cwd.
# Schema lives in the sibling assets/ directory.
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCHEMA_FILE="${SKILL_DIR}/assets/vega-lite-schema.json"

# --- Argument validation -------------------------------------------------------

if [[ $# -lt 1 ]]; then
    echo "Error: Missing instance file argument." >&2
    echo "Usage: vega-lite-validate.sh <instance.json>" >&2
    exit 2
fi

INSTANCE_FILE="$1"

# --- File existence checks -----------------------------------------------------

if [[ ! -f "$SCHEMA_FILE" ]]; then
    echo "Error: Schema file not found at ${SCHEMA_FILE}" >&2
    echo "Ensure scripts/vega-lite-schema.json exists (downloaded with this skill)." >&2
    exit 2
fi

if [[ ! -f "$INSTANCE_FILE" ]]; then
    echo "Error: Instance file not found at ${INSTANCE_FILE}" >&2
    exit 2
fi

# --- Runtime selection --------------------------------------------------------
# Prefer uvx (faster, ephemeral venv), fall back to pipx if unavailable.
if command -v uvx &>/dev/null; then
    RUNNER="uvx"
elif command -v pipx &>/dev/null; then
    RUNNER="pipx run"
else
    echo "Error: Neither uvx nor pipx found." >&2
    echo "Install one of them to provide check-jsonschema:" >&2
    echo "  uvx:   https://docs.astral.sh/uv/" >&2
    echo "  pipx:  https://pipx.pypa.io/" >&2
    exit 2
fi

# --- Validation ----------------------------------------------------------------

$RUNNER check-jsonschema --schemafile "$SCHEMA_FILE" "$INSTANCE_FILE"
