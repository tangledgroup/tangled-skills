#!/usr/bin/env python3
"""skman — Skill Manager: scaffold, validate, and inspect agent skills.

Usage:
    skman.sh --help
    skman.sh create --help
    skman.sh validate --help
    skman.sh info --help
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

## Usage

[How to use this skill. Include examples.]

""")

# Matches trailing version suffix: -<digit>[-<digit>]* at end of dir name
# e.g. "uv-0-11-19" -> "0-11-19", "git-8-20-0" -> "8-20-0"
VERSION_SUFFIX_RE = re.compile(r'-(\d+(?:-\d+)+)$')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_frontmatter(text):
    """Return (frontmatter_dict, body_text) or (None, text) if no frontmatter.

    Handles single-line values, quoted multi-line values, block scalars (|, >),
    and indented continuation lines.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    body = text[m.end():]
    fm = {}
    lines = m.group('content').splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        # Skip blank lines and comments
        if not stripped or stripped.startswith('#'):
            i += 1
            continue
        lm = YAML_LINE_RE.match(stripped)
        if not lm:
            i += 1
            continue
        key = lm.group('key')
        value = lm.group('value').strip()
        # Handle block scalars (| or >)
        if value in ('|', '>'):
            i += 1
            block_lines = []
            while i < len(lines):
                bline = lines[i]
                if bline and (bline[0] == ' ' or bline[0] == '\t'):
                    block_lines.append(bline.strip())
                    i += 1
                else:
                    break
            fm[key] = '\n'.join(block_lines)
            continue
        # Handle quoted multi-line values
        if value.startswith('"') and not value.endswith('"'):
            i += 1
            parts = [value[1:]]
            while i < len(lines):
                cline = lines[i].strip()
                if cline.endswith('"'):
                    parts.append(cline[:-1])
                    break
                parts.append(cline)
                i += 1
            fm[key] = '\n'.join(parts)
            continue
        if value.startswith("'") and not value.endswith("'"):
            i += 1
            parts = [value[1:]]
            while i < len(lines):
                cline = lines[i].strip()
                if cline.endswith("'"):
                    parts.append(cline[:-1])
                    break
                parts.append(cline)
                i += 1
            fm[key] = '\n'.join(parts)
            continue
        # Handle indented continuation lines (next line is indented more)
        i += 1
        while i < len(lines):
            next_line = lines[i]
            if not next_line or next_line[0] in (' ', '\t'):
                cont = next_line.strip()
                if cont:
                    value += ' ' + cont
                i += 1
            else:
                break
        fm[key] = value
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
    if re.search(r'<[a-zA-Z/][^>]*>', desc):
        errors.append("description must not contain XML/HTML tags")
    return errors


def _validate_frontmatter(fm):
    """Return list of error strings for the full frontmatter."""
    errors = []
    name = fm.get('name', '') if fm else ''
    errors.extend(_validate_name(name))
    desc = fm.get('description', None) if fm else None
    errors.extend(_validate_description(desc))
    return errors


REQUIRED_SECTIONS = {'#'}  # body must start with a level-1 heading
OPTIONAL_SECTIONS = {'## Overview', '## Usage', '## Gotchas', '## References'}


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


def _check_sections(body):
    """Check for required and optional sections in the body.

    Returns (errors, warnings) lists.
    """
    errors = []
    warnings = []

    # Collect headings, skipping fenced code blocks
    in_fence = False
    found_headings = set()
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith('```'):
            in_fence = not in_fence
            continue
        if not in_fence and stripped.startswith('#'):
            found_headings.add(stripped)

    # Check optional sections — warn if missing
    missing_optional = OPTIONAL_SECTIONS - found_headings
    if missing_optional:
        warnings.append(
            f"missing optional section(s): {', '.join(sorted(missing_optional))}"
        )

    return errors, warnings


def _check_script_permissions(skill_dir, fm_name):
    """Check that scripts/<name>.sh is executable if it exists.

    Returns (errors, warnings) lists.
    """
    errors = []
    warnings = []

    if not fm_name:
        return errors, warnings

    sh_path = os.path.join(skill_dir, 'scripts', f'{fm_name}.sh')
    if os.path.isfile(sh_path):
        if not os.access(sh_path, os.X_OK):
            warnings.append(
                f"scripts/{fm_name}.sh is not executable (run chmod +x)"
            )

    return errors, warnings


def _strip_version_suffix(dir_basename):
    """Strip trailing -<version> suffix from directory basename.

    Returns (name, version_with_hyphens_or_None).
    e.g. 'uv-0-11-19' -> ('uv', '0-11-19')
         'skman'       -> ('skman', None)
    """
    m = VERSION_SUFFIX_RE.search(dir_basename)
    if m:
        name = dir_basename[:m.start()]
        return name, m.group(1)
    return dir_basename, None


def _dir_version_to_dots(version_with_hyphens):
    """Convert hyphen-separated version to dot-separated.

    e.g. '0-11-19' -> '0.11.19'
    """
    return version_with_hyphens.replace('-', '.')


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_create(args):
    """Scaffold a new skill directory."""
    name = args.name.strip()
    description = args.description.strip()
    output_dir = args.output_dir
    version = getattr(args, 'version', None)
    if version:
        version = version.strip()

    # Validate before creating anything
    errors = []
    errors.extend(_validate_name(name))
    errors.extend(_validate_description(description))

    if errors:
        print("create: validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    # Build directory name and H1 title
    if version:
        # Normalize: dots in H1, hyphens in dir name
        version_dots = version.replace('-', '.')
        version_hyphen = version.replace('.', '-')
        dir_name = f"{name}-{version_hyphen}"
        h1_title = f"{name} {version_dots}"
    else:
        dir_name = name
        h1_title = name

    # Create directory structure
    skill_dir = os.path.join(output_dir, dir_name)
    os.makedirs(skill_dir, exist_ok=True)

    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md_path):
        print(f"create: {skill_md_path} already exists — skipping", file=sys.stderr)
        sys.exit(1)

    content = DEFAULT_SKILL_MD.format(name=dir_name, description=description, title=h1_title)
    with open(skill_md_path, 'w') as f:
        f.write(content)

    # Optionally create scripts directory
    if args.with_scripts:
        scripts_dir = os.path.join(skill_dir, 'scripts')
        os.makedirs(scripts_dir, exist_ok=True)

        # Bash wrapper (entry point)
        sh_path = os.path.join(scripts_dir, f'{name}.sh')
        with open(sh_path, 'w') as f:
            f.write(f'#!/usr/bin/env bash\n')
            f.write(f'# {name} — {description}\n')
            f.write(f'set -euo pipefail\n')
            f.write(f'\n')
            f.write(f'SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"\n')
            f.write(f'exec python3 -B "$SCRIPT_DIR/_{name}.py" "$@"\n')
        os.chmod(sh_path, 0o755)

        # Python implementation (underscore prefix)
        py_path = os.path.join(scripts_dir, f'_{name}.py')
        with open(py_path, 'w') as f:
            f.write(f'#!/usr/bin/env python3\n')
            f.write(f'"""{name} — {description}\n')
            f.write(f'\n')
            f.write(f'Usage:\n')
            f.write(f'    {name}.sh --help\n')
            f.write(f'"""\n')
            f.write(f'\n')
            f.write(f'import argparse\n')
            f.write(f'import sys\n')
            f.write(f'\n')
            f.write(f'\ndef main():\n')
            f.write(f'    parser = argparse.ArgumentParser(prog="{name}")\n')
            f.write(f'    parser.parse_args()\n')
            f.write(f'    print("TODO: implement {name}")\n')
            f.write(f'\n')
            f.write(f'\nif __name__ == "__main__":\n')
            f.write(f'    main()\n')

        print(f"create: created bash wrapper at {sh_path}")
        print(f"create: created python impl  at {py_path}")

    # Optionally create references directory
    if args.with_references:
        ref_dir = os.path.join(skill_dir, 'references')
        os.makedirs(ref_dir, exist_ok=True)
        placeholder = os.path.join(ref_dir, '01-reference.md')
        with open(placeholder, 'w') as f:
            f.write(f"# {title} Reference\n\n[Detailed reference content.]\n")
        print(f"create: created references placeholder at {placeholder}")

    print(f"create: scaffolded skill '{dir_name}' at {skill_md_path}")


def cmd_validate(args):
    """Validate a SKILL.md file against spec rules.

    Every check is reported as PASS / WARN / ERROR in a single enumerated list:
      1.  [PASS] …
      2.  [PASS] …
      3.  [WARN] …
      4.  [ERROR] …
    """
    target = args.path
    skill_md = _find_skill_md(target)

    if skill_md is None:
        print(f"validate: no SKILL.md found at '{target}'", file=sys.stderr)
        sys.exit(1)

    with open(skill_md, 'r') as f:
        content = f.read()

    fm, body = _parse_frontmatter(content)

    results = []  # list of (label, message) where label in {"PASS", "WARN", "ERROR"}

    # --- Frontmatter presence ---
    if fm is None:
        results.append(("ERROR", "no YAML frontmatter found (must start with ---)"))
    else:
        results.append(("PASS", "frontmatter present"))

        # Name
        name_errors = _validate_name(fm.get('name', ''))
        if name_errors:
            for e in name_errors:
                results.append(("ERROR", f"name: {e}"))
        else:
            results.append(("PASS", f"name '{fm.get('name', '')}' is valid"))

        # Description
        desc_errors = _validate_description(fm.get('description', None))
        if desc_errors:
            for e in desc_errors:
                results.append(("ERROR", f"description: {e}"))
        else:
            results.append(("PASS", "description is valid"))

        # Unknown fields
        known_fields = {'name', 'description'}
        unknown = set(fm.keys()) - known_fields
        if unknown:
            results.append(("WARN", f"unknown frontmatter fields: {', '.join(sorted(unknown))}"))
        else:
            results.append(("PASS", "no unknown frontmatter fields"))

        # Name vs directory basename consistency
        skill_dir = os.path.dirname(skill_md)
        dir_basename = os.path.basename(skill_dir)
        dir_name, dir_version = _strip_version_suffix(dir_basename)
        fm_name = fm.get('name', '')
        # Accept frontmatter name as either base name ('uv') or full name ('uv-0-11-19')
        name_matches = (fm_name == dir_basename)
        if fm_name and not name_matches:
            results.append(
                ("WARN",
                 f"directory name '{dir_basename}' does not match "
                 f"frontmatter name '{fm_name}' (expected '{dir_basename}')")
            )
        else:
            results.append(("PASS", f"directory name matches frontmatter name '{fm_name}'"))

        # Script permission checks
        perm_errors, perm_warnings = _check_script_permissions(skill_dir, fm_name)
        for e in perm_errors:
            results.append(("ERROR", e))
        for w in perm_warnings:
            results.append(("WARN", w))
        if not perm_errors and not perm_warnings:
            sh_path = os.path.join(skill_dir, 'scripts', f'{fm_name}.sh')
            if os.path.isfile(sh_path):
                results.append(("PASS", f"scripts/{fm_name}.sh is executable"))

    # --- Body checks ---
    body_lines = body.splitlines()
    body_line_count = len(body_lines)

    # Level-1 heading
    first_content_line = None
    for line in body_lines:
        stripped = line.strip()
        if stripped:
            first_content_line = stripped
            break
    if first_content_line is None:
        results.append(("PASS", "body is empty (no content lines)"))
    elif not first_content_line.startswith('# '):
        results.append(
            ("ERROR",
             f"body must start with a level-1 heading (found: '{first_content_line[:60]}...')")
        )
    else:
        # Validate H1 heading format: must be '# <name>' or '# <name> <version>'
        # Derive expected heading from directory structure, not frontmatter name
        h1_text = first_content_line[2:]  # strip '# '
        expected_h1 = dir_name
        if dir_version:
            expected_h1 = f"{dir_name} {_dir_version_to_dots(dir_version)}"
        if h1_text == expected_h1:
            results.append(("PASS", f"H1 heading '{first_content_line}' matches expected format"))
        else:
            results.append(
                ("ERROR",
                 f"H1 heading '{first_content_line}' does not match expected "
                 f"'#{expected_h1}' (must be '# <name>' or '# <name> <version>')")
            )

    # Line count
    if body_line_count > 500:
        results.append(
            ("WARN", f"body has {body_line_count} lines (recommended: under 500)")
        )
    else:
        results.append(("PASS", f"body has {body_line_count} lines (under 500)"))

    # Section checks
    sec_errors, sec_warnings = _check_sections(body)
    for e in sec_errors:
        results.append(("ERROR", e))
    for w in sec_warnings:
        results.append(("WARN", w))
    if not sec_errors and not sec_warnings:
        results.append(("PASS", "all optional sections present"))

    # --- Report ---
    error_count = sum(1 for label, _ in results if label == "ERROR")
    warn_count = sum(1 for label, _ in results if label == "WARN")

    passed = error_count == 0
    if args.strict and warn_count > 0:
        passed = False

    # Print header
    if error_count:
        print("validate: FAILED")
    elif warn_count:
        print("validate: OK (with warnings)")
    else:
        print("validate: OK")

    # Print all checks enumerated: PASSes first, then WARNs, then ERRORs
    passes = [(i, msg) for i, (label, msg) in enumerate(results, 1) if label == "PASS"]
    warns = [(i, msg) for i, (label, msg) in enumerate(results, 1) if label == "WARN"]
    errors_list = [(i, msg) for i, (label, msg) in enumerate(results, 1) if label == "ERROR"]

    counter = 0
    for _, msg in passes:
        counter += 1
        print(f"  {counter}. [PASS] {msg}")
    for _, msg in warns:
        counter += 1
        print(f"  {counter}. [WARN] {msg}")
    for _, msg in errors_list:
        counter += 1
        print(f"  {counter}. [ERROR] {msg}")

    sys.exit(0 if passed else 1)


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
    headings = []
    in_fence = False
    for line in body_lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_fence = not in_fence
            continue
        if not in_fence and stripped.startswith('#'):
            headings.append(stripped)
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
            Scaffold a new skill directory with SKILL.md and optional scripts/references.

            Examples:
              skman.sh create my-skill "Does X and Y"
              skman.sh create my-skill "Desc" --with-scripts --with-references
              skman.sh create my-skill "Desc" -o ./custom-skills
              skman.sh create uv "Package manager" --version 0.11.19
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_create.add_argument('name', help='Skill name (lowercase, hyphens, numbers)')
    p_create.add_argument('description', help='Skill description (max 1024 chars)')
    p_create.add_argument(
        '--version', '-V',
        default=None,
        help='Optional version (e.g. 0.11.19). Dir becomes <name>-<version>, H1 is "# <name> <version>"',
    )
    p_create.add_argument(
        '--output-dir', '-o',
        default='.agents/skills',
        help='Parent directory for the skill (default: .agents/skills)',
    )
    p_create.add_argument(
        '--with-scripts',
        action='store_true',
        help='Also create scripts/ directory with bash wrapper + python stub',
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
              skman.sh validate ./my-skill
              skman.sh validate ./my-skill/SKILL.md
              skman.sh validate --strict ./my-skill
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
              skman.sh info ./my-skill
              skman.sh info ./my-skill/SKILL.md
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
              skman.sh generate
              skman.sh generate --skills-dir ./custom-skills
              skman.sh generate --readme ./docs/README.md
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
