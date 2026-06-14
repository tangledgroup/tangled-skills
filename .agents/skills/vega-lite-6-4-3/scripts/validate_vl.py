#!/usr/bin/env python3
"""Validate Vega-Lite spec(s) against the v6.4.3 JSON schema.

Usage:
    validate_vl.py <spec.json> [<spec2.json> ...]   Validate file(s)
    validate_vl.py --stdin                          Read spec from stdin
    validate_vl.py --dir <directory>                 Validate all .vl.json in directory
    validate_vl.py --extract <markdown.md>           Extract and validate JSON blocks from markdown

Exit codes: 0 = all valid, 1 = validation error(s), 2 = usage/file error
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Schema path: resolve relative to the cloned vega-lite repo
# Skill is at tangled-skills/.agents/skills/vega-lite-6-4-3/
# Repo is at tangled-skills/../vega-lite-6.4.3  (sibling of tangled-skills)
_SCRIPT_DIR = Path(__file__).resolve().parent       # scripts/
_SKILL_DIR = _SCRIPT_DIR.parent                     # vega-lite-6-4-3/
_PARENTS_UP = _SKILL_DIR.parent.parent.parent       # tangled-skills/ (go up: skills → .agents → tangled-skills)
_REPO_DIR = _PARENTS_UP.parent / "vega-lite-6.4.3"  # projects-t/vega-lite-6.4.3
SCHEMA_PATH = _REPO_DIR / "build" / "vega-lite-schema.json"


def load_schema():
    """Load the Vega-Lite JSON schema."""
    if not SCHEMA_PATH.exists():
        print(f"ERROR: Schema not found at {SCHEMA_PATH}", file=sys.stderr)
        sys.exit(2)
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def validate_spec(spec, schema, label="<stdin>"):
    """Validate a single Vega-Lite spec against the schema.

    Returns (is_valid, list_of_error_strings).
    """
    try:
        from jsonschema import validate, ValidationError, Draft7Validator
    except ImportError:
        print("ERROR: jsonschema not available. Install with: pip install jsonschema", file=sys.stderr)
        sys.exit(2)

    errors = []

    # Check $schema field
    schema_url = spec.get("$schema", "")
    if schema_url and "vega-lite" not in schema_url:
        errors.append(f"$schema should reference vega-lite, got: {schema_url}")

    # Note: layered specs (layer: [...]), repeat/concat specs, and specs with
    # params/transform can have data nested inside layers rather than at root.
    # The JSON schema itself handles these cases, so we skip custom top-level checks.

    # Full JSON Schema validation
    validator = Draft7Validator(schema)
    for error in sorted(validator.iter_errors(spec), key=lambda e: list(e.path)):
        path = " -> ".join(str(p) for p in error.path) if error.path else "(root)"
        errors.append(f"{path}: {error.message}")

    is_valid = len(errors) == 0
    status = "VALID" if is_valid else "INVALID"
    print(f"[{status}] {label}")
    if not is_valid:
        for err in errors:
            print(f"         {err}")

    return is_valid, errors


def validate_file(filepath, schema):
    """Validate a single .vl.json file."""
    try:
        with open(filepath) as f:
            spec = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[ERROR]  {filepath}: {e}")
        return False

    is_valid, _ = validate_spec(spec, schema, str(filepath))
    return is_valid


def extract_json_blocks(text):
    """Extract JSON objects from markdown code blocks (```json ... ```)."""
    # Match ```json ... ``` and ``` ... ``` blocks
    blocks = re.findall(r'```(?:json|JSON|vega-lite|VEGA-LITE)\s*\n(.*?)\n```', text, re.DOTALL)
    specs = []
    for block in blocks:
        block = block.strip()
        # Skip if it looks like it's not JSON (e.g., contains markdown headings)
        if block.startswith("#") or not block.startswith("{"):
            continue
        try:
            spec = json.loads(block)
            specs.append(spec)
        except json.JSONDecodeError:
            # Try to find a JSON object within the block
            match = re.search(r'\{.*\}', block, re.DOTALL)
            if match:
                try:
                    spec = json.loads(match.group())
                    specs.append(spec)
                except json.JSONDecodeError:
                    pass
    return specs


def validate_markdown(filepath, schema):
    """Extract and validate all JSON specs from a markdown file."""
    with open(filepath) as f:
        text = f.read()

    specs = extract_json_blocks(text)
    if not specs:
        print(f"[SKIP]   {filepath}: No JSON blocks found")
        return True

    all_valid = True
    for i, spec in enumerate(specs):
        label = f"{filepath} (spec #{i + 1})"
        is_valid, _ = validate_spec(spec, schema, label)
        if not is_valid:
            all_valid = False

    return all_valid


def main():
    parser = argparse.ArgumentParser(description="Validate Vega-Lite specs against v6.4.3 schema")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("files", nargs="*", help="Vega-Lite spec files to validate")
    group.add_argument("--stdin", action="store_true", help="Read spec from stdin")
    group.add_argument("--dir", metavar="DIR", help="Validate all .vl.json in directory")
    group.add_argument("--extract", metavar="MD", help="Extract and validate JSON from markdown file(s)")
    parser.add_argument("--schema", help="Path to schema (default: use bundled v6.4.3 schema)")
    args = parser.parse_args()

    schema = load_schema()
    if args.schema:
        with open(args.schema) as f:
            schema = json.load(f)

    all_valid = True

    if args.stdin:
        spec = json.load(sys.stdin)
        if not validate_spec(spec, schema, "<stdin>"):
            all_valid = False

    elif args.dir:
        dir_path = Path(args.dir)
        if not dir_path.is_dir():
            print(f"ERROR: {dir_path} is not a directory", file=sys.stderr)
            sys.exit(2)
        for filepath in sorted(dir_path.glob("*.vl.json")):
            if not validate_file(filepath, schema):
                all_valid = False

    elif args.extract:
        for md_file in args.extract.split(","):
            md_file = md_file.strip()
            if not validate_markdown(md_file, schema):
                all_valid = False

    elif args.files:
        for filepath in args.files:
            path = Path(filepath)
            if path.suffix == ".md" or path.suffix == ".markdown":
                if not validate_markdown(path, schema):
                    all_valid = False
            else:
                if not validate_file(path, schema):
                    all_valid = False
    else:
        parser.print_help()
        sys.exit(2)

    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
