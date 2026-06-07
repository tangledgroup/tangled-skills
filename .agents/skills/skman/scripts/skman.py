#!/usr/bin/env python3
"""skman — Skill Manager: scaffold, validate, and inspect agent skills.

Usage:
    python3 -B scripts/skman.py --help
    python3 -B scripts/skman.py create --help
    python3 -B scripts/skman.py validate --help
    python3 -B scripts/skman.py info --help
"""

import argparse
import os
import re
import sys
import textwrap


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NAME_RE = re.compile(r'^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$')
MAX_NAME_LEN = 64
MAX_DESC_LEN = 1024

FRONTMATTER_RE = re.compile(
    r'^---\s*\n(?P<content>.*?)^---\s*\n', re.MULTILINE | re.DOTALL
)
YAML_LINE_RE = re.compile(r'^(?P<key>[a-z][a-z0-9_-]*)\s*:\s*(?P<value>.*)$')

DEFAULT_SKILL_MD = textwrap.dedent("""\
---
name: {name}
description: {description}
---

# {title}

## Overview

[Describe what this skill does and when to use it.]

## Setup

[One-time setup steps, if any. Omit section if none needed.]

## Usage

[How to use this skill. Include examples.]

""")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_frontmatter(text):
    """Return (frontmatter_dict, body_text) or (None, text) if no frontmatter."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    fm = {}
    for line in m.group('content').splitlines():
        lm = YAML_LINE_RE.match(line.strip())
        if lm:
            fm[lm.group('key')] = lm.group('value').strip()
    body = text[m.end():]
    return fm, body


def _validate_name(name):
    """Return list of error strings (empty = valid)."""
    errors = []
    if not name:
        errors.append("name is missing")
        return errors
    if len(name) > MAX_NAME_LEN:
        errors.append(f"name exceeds {MAX_NAME_LEN} characters ({len(name)})")
    if not NAME_RE.match(name):
        errors.append(
            "name must be lowercase letters, numbers, and hyphens only; "
            "no leading/trailing/consecutive hyphens"
        )
    return errors


def _validate_description(desc):
    """Return list of error strings (empty = valid)."""
    errors = []
    if desc is None:
        errors.append("description is missing (required)")
        return errors
    if not desc.strip():
        errors.append("description is empty (required)")
        return errors
    if len(desc) > MAX_DESC_LEN:
        errors.append(
            f"description exceeds {MAX_DESC_LEN} characters ({len(desc)})"
        )
    if '<' in desc and '>' in desc:
        errors.append("description must not contain XML tags")
    return errors


def _validate_frontmatter(fm):
    """Return list of error strings for the full frontmatter."""
    errors = []
    name = fm.get('name', '') if fm else ''
    errors.extend(_validate_name(name))
    desc = fm.get('description', None) if fm else None
    errors.extend(_validate_description(desc))
    return errors


def _find_skill_md(path):
    """Given a path (file or dir), return the absolute path to SKILL.md."""
    abs_path = os.path.abspath(path)
    if os.path.isfile(abs_path):
        return abs_path
    if os.path.isdir(abs_path):
        candidate = os.path.join(abs_path, 'SKILL.md')
        if os.path.isfile(candidate):
            return candidate
    return None


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_create(args):
    """Scaffold a new skill directory."""
    name = args.name.strip()
    description = args.description.strip()
    output_dir = args.output_dir or name

    # Validate before creating anything
    errors = []
    errors.extend(_validate_name(name))
    errors.extend(_validate_description(description))

    if errors:
        print("create: validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    # Create directory structure
    skill_dir = os.path.join(output_dir, name) if output_dir != name else output_dir
    os.makedirs(skill_dir, exist_ok=True)

    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md_path):
        print(f"create: {skill_md_path} already exists — skipping", file=sys.stderr)
        sys.exit(1)

    title = name.replace('-', ' ').title()
    content = DEFAULT_SKILL_MD.format(name=name, description=description, title=title)
    with open(skill_md_path, 'w') as f:
        f.write(content)

    # Optionally create references directory
    if args.with_references:
        ref_dir = os.path.join(skill_dir, 'references')
        os.makedirs(ref_dir, exist_ok=True)
        placeholder = os.path.join(ref_dir, '01-reference.md')
        with open(placeholder, 'w') as f:
            f.write(f"# {title} Reference\n\n[Detailed reference content.]\n")

    print(f"create: scaffolded skill '{name}' at {skill_md_path}")
    if args.with_references:
        print(f"create: created references placeholder at {placeholder}")


def cmd_validate(args):
    """Validate a SKILL.md file against spec rules."""
    target = args.path
    skill_md = _find_skill_md(target)

    if skill_md is None:
        print(f"validate: no SKILL.md found at '{target}'", file=sys.stderr)
        sys.exit(1)

    with open(skill_md, 'r') as f:
        content = f.read()

    fm, body = _parse_frontmatter(content)

    errors = []
    warnings = []

    # Frontmatter presence
    if fm is None:
        errors.append("no YAML frontmatter found (must start with ---)")
    else:
        errors.extend(_validate_frontmatter(fm))

        # Check for unknown fields (informational warning)
        known_fields = {'name', 'description'}
        unknown = set(fm.keys()) - known_fields
        if unknown:
            warnings.append(f"unknown frontmatter fields: {', '.join(sorted(unknown))}")

    # Body checks
    body_lines = body.splitlines()
    body_line_count = len(body_lines)
    if body_line_count > 500:
        warnings.append(
            f"body has {body_line_count} lines (recommended: under 500)"
        )

    # Check for heading
    has_heading = any(line.startswith('#') for line in body_lines)
    if not has_heading and fm is not None:
        warnings.append("body has no markdown headings")

    # Report
    ok = True
    if errors:
        ok = False
        print("validate: FAILED")
        for e in errors:
            print(f"  ERROR: {e}")
    elif warnings and not args.strict:
        print("validate: OK (with warnings)")
    else:
        print("validate: OK")

    if warnings:
        for w in warnings:
            print(f"  WARN:  {w}")

    if args.strict and warnings:
        ok = False

    sys.exit(0 if ok else 1)


def cmd_info(args):
    """Print parsed frontmatter and structural summary of a skill."""
    target = args.path
    skill_md = _find_skill_md(target)

    if skill_md is None:
        print(f"info: no SKILL.md found at '{target}'", file=sys.stderr)
        sys.exit(1)

    with open(skill_md, 'r') as f:
        content = f.read()

    fm, body = _parse_frontmatter(content)

    # Print frontmatter
    print("info: SKILL.md analysis")
    print("-" * 40)
    if fm:
        for key in ('name', 'description'):
            val = fm.get(key)
            if val is not None:
                print(f"  {key}: {val}")
        # Show any extra fields
        known_fields = {'name', 'description'}
        extra = set(fm.keys()) - known_fields
        for key in sorted(extra):
            print(f"  {key}: {fm[key]}")
    else:
        print("  (no frontmatter)")

    # Structural summary
    body_lines = body.splitlines()
    headings = [line.strip() for line in body_lines if line.startswith('#')]
    line_count = len(body_lines)
    word_count = len(body.split())

    print(f"  body lines: {line_count}")
    print(f"  body words: {word_count}")
    if headings:
        print("  headings:")
        for h in headings:
            depth = len(h) - len(h.lstrip('#'))
            text = h.lstrip('#').strip()
            indent = "    " * (depth - 1)
            print(f"  {indent}- {text}")

    # Directory listing
    skill_dir = os.path.dirname(skill_md)
    entries = sorted(os.listdir(skill_dir))
    if entries:
        print("  files:")
        for entry in entries:
            full = os.path.join(skill_dir, entry)
            if os.path.isdir(full):
                print(f"    {entry}/")
            else:
                size = os.path.getsize(full)
                print(f"    {entry} ({size} bytes)")


# ---------------------------------------------------------------------------
# generate subcommand
# ---------------------------------------------------------------------------

AUTOGEN_MARKER = "<!-- IMPORTANT: never change after this point because it is automatically generated -->"


def _discover_skills(skills_dir):
    """Scan skills_dir for directories containing SKILL.md.

    Returns a sorted list of (name, description) tuples.
    name = directory basename, description = frontmatter 'description' field.
    """
    skills = []
    if not os.path.isdir(skills_dir):
        return skills

    for entry in sorted(os.listdir(skills_dir)):
        skill_md = os.path.join(skills_dir, entry, 'SKILL.md')
        if not os.path.isfile(skill_md):
            continue
        with open(skill_md, 'r') as f:
            content = f.read()
        fm, _ = _parse_frontmatter(content)
        name = entry
        desc = ''
        if fm:
            name = fm.get('name', entry)
            desc = fm.get('description', '') or ''
        skills.append((name, desc))

    return skills


def _build_table(skills):
    """Build the Skills Table markdown from a list of (name, description)."""
    lines = []
    lines.append("## Skills Table")
    lines.append("")
    lines.append("| No | Skill | Description |")
    lines.append("|----|-------|-------------|")
    for i, (name, desc) in enumerate(skills, 1):
        lines.append(f"| {i} | {name} | {desc} |")
    return "\n".join(lines)


def _build_statistics(total):
    """Build the Statistics section markdown."""
    lines = []
    lines.append("")
    lines.append("## Statistics")
    lines.append("")
    lines.append(f"- **Total Skills**: {total}")
    return "\n".join(lines)


def cmd_generate(args):
    """Generate the Skills Table and Statistics in README.md."""
    skills_dir = args.skills_dir
    readme_path = args.readme

    # Discover all skills
    skills = _discover_skills(skills_dir)
    total = len(skills)

    if total == 0:
        print(f"generate: no skills found in '{skills_dir}'", file=sys.stderr)
        sys.exit(1)

    # Build replacement section
    table = _build_table(skills)
    stats = _build_statistics(total)
    new_section = f"{AUTOGEN_MARKER}\n{table}\n{stats}\n"

    # Read README
    if not os.path.isfile(readme_path):
        print(f"generate: README not found at '{readme_path}'", file=sys.stderr)
        sys.exit(1)

    with open(readme_path, 'r') as f:
        readme = f.read()

    # Replace everything from marker to end of file
    idx = readme.find(AUTOGEN_MARKER)
    if idx == -1:
        print(f"generate: auto-generated marker not found in '{readme_path}'", file=sys.stderr)
        sys.exit(1)

    new_readme = readme[:idx] + new_section

    with open(readme_path, 'w') as f:
        f.write(new_readme)

    print(f"generate: updated {readme_path} with {total} skills")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog='skman',
        description=textwrap.dedent("""\
            Skill Manager — scaffold, validate, and inspect agent skills.

            Subcommands:
              create      Scaffold a new skill directory with SKILL.md
              validate    Check SKILL.md against spec rules
              info        Print frontmatter and structural summary
              generate    Generate Skills Table and Statistics in README.md

            Use '<subcommand> --help' for details on each subcommand.
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest='subcommand')

    # --- create ---
    p_create = sub.add_parser(
        'create',
        description=textwrap.dedent("""\
            Scaffold a new skill directory with SKILL.md and optional references.

            Examples:
              python3 -B scripts/skman.py create my-skill "Does X and Y"
              python3 -B scripts/skman.py create my-skill "Desc" --with-references
              python3 -B scripts/skman.py create my-skill "Desc" --output-dir ./skills
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_create.add_argument('name', help='Skill name (lowercase, hyphens, numbers)')
    p_create.add_argument('description', help='Skill description (max 1024 chars)')
    p_create.add_argument(
        '--output-dir', '-o',
        default=None,
        help='Parent directory for the skill (default: same as name)',
    )
    p_create.add_argument(
        '--with-references',
        action='store_true',
        help='Also create a references/ directory with placeholder',
    )

    # --- validate ---
    p_validate = sub.add_parser(
        'validate',
        description=textwrap.dedent("""\
            Validate a SKILL.md file against the agent skills spec.

            Checks:
              - Frontmatter presence and required fields
              - Name format (lowercase, hyphens, length)
              - Description presence and length
              - Body line count (warning if over 500)

            Examples:
              python3 -B scripts/skman.py validate ./my-skill
              python3 -B scripts/skman.py validate ./my-skill/SKILL.md
              python3 -B scripts/skman.py validate --strict ./my-skill
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_validate.add_argument('path', help='Path to skill directory or SKILL.md file')
    p_validate.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors (non-zero exit on any warning)',
    )

    # --- info ---
    p_info = sub.add_parser(
        'info',
        description=textwrap.dedent("""\
            Print frontmatter and structural summary of a skill.

            Shows:
              - Parsed frontmatter fields
              - Body line/word count
              - Heading outline
              - Directory listing with file sizes

            Examples:
              python3 -B scripts/skman.py info ./my-skill
              python3 -B scripts/skman.py info ./my-skill/SKILL.md
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_info.add_argument('path', help='Path to skill directory or SKILL.md file')

    # --- generate ---
    p_generate = sub.add_parser(
        'generate',
        description=textwrap.dedent("""\
            Generate the Skills Table and Statistics section in README.md.

            Scans all skill directories for SKILL.md files, parses frontmatter,
            and replaces everything from the auto-generated marker to end of file.

            Examples:
              python3 -B scripts/skman.py generate
              python3 -B scripts/skman.py generate --skills-dir ./custom-skills
              python3 -B scripts/skman.py generate --readme ./docs/README.md
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_generate.add_argument(
        '--skills-dir',
        default='.agents/skills',
        help='Directory containing skill subdirectories (default: .agents/skills)',
    )
    p_generate.add_argument(
        '--readme',
        default='README.md',
        help='Path to README.md to update (default: README.md)',
    )

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.subcommand is None:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        'create': cmd_create,
        'validate': cmd_validate,
        'info': cmd_info,
        'generate': cmd_generate,
    }
    dispatch[args.subcommand](args)


if __name__ == '__main__':
    main()
