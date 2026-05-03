#!/usr/bin/env python3
"""Deterministically regenerate the Skills Table in README.md from YAML headers.

Usage:
    python3 scripts/gen-skills-table.py [--dry-run]

Reads every .agents/skills/<name>/SKILL.md, extracts YAML header fields,
and replaces the ## Skills Table section (through ## Statistics) in README.md.
"""

import re
import sys
import pathlib


def extract_project(name: str) -> str:
    """Derive project name by stripping version suffix from skill name."""
    p = name

    # Date suffix: -YYYY-MM-DD
    p = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', p)

    # Three-part semver with optional pre-release: -MAJOR-MINOR-PATCH[-pre]
    p = re.sub(r'-\d+-\d+-\d+(?:-[a-zA-Z0-9]+(?:-\d+)?)?$', '', p)

    # Two-part version: -MAJOR-MINOR
    p = re.sub(r'-\d+-\d+$', '', p)

    # Single number: -N
    p = re.sub(r'-\d+$', '', p)

    return "-" if p == "" else p


def extract_yaml_fields(skill_md: pathlib.Path):
    """Extract name, version, description, tags from YAML header."""
    content = skill_md.read_text()
    m = re.search(r'^---\s*\n(.*?)\n^---\s*\n', content, re.MULTILINE | re.DOTALL)
    if not m:
        return None

    header = m.group(1)

    name_m = re.search(r'^name:\s*(\S+)', header, re.MULTILINE)
    ver_m = re.search(r'^version:\s*["\']?([^"\'\n]+)', header, re.MULTILINE)

    # Extract description: handle inline, block literal (>, >-), and folded (|)
    desc_line = re.search(r'^description:\s*(.*)$', header, re.MULTILINE)
    if desc_line:
        val = desc_line.group(1).strip()
        if val in ('>', '>-', '|'):
            # Block literal — read indented lines after this one
            header_lines = header.split('\n')
            start_idx = header_lines.index(desc_line.group(0))
            block_lines = []
            for bl in header_lines[start_idx + 1:]:
                if bl and (bl[0] == ' ' or bl[0] == '\t'):
                    block_lines.append(bl)
                else:
                    break
            indent = None
            cleaned = []
            for bl in block_lines:
                stripped = bl.lstrip()
                if not stripped:
                    continue
                if indent is None:
                    indent = len(bl) - len(stripped)
                cleaned.append(bl[indent:])
            desc_text = ' '.join(cleaned).strip()
        else:
            # Inline description
            desc_text = val.strip('"\'')
    else:
        desc_text = ""

    # Extract tags array
    tags = []
    in_tags = False
    for line in header.split('\n'):
        if line.strip().startswith('tags:'):
            in_tags = True
            continue
        if in_tags and re.match(r'\s*-\s+\S', line):
            tags.append(line.strip()[2:].strip())
        elif in_tags and not re.match(r'\s*-', line):
            in_tags = False

    name = name_m.group(1) if name_m else None
    version = ver_m.group(1).strip().strip('"\'') if ver_m else ""

    return {
        'name': name,
        'version': version,
        'description': desc_text,
        'tags': tags,
    }


def escape_md_pipe(text: str) -> str:
    """Escape pipe characters in markdown table cells."""
    return text.replace('|', '\\|')


def truncate_desc(desc: str, max_len: int = 120) -> str:
    """Truncate description, breaking at word boundary."""
    if len(desc) <= max_len:
        return desc
    truncated = desc[:max_len]
    last_space = truncated.rfind(' ')
    if last_space > max_len * 0.5:
        truncated = truncated[:last_space]
    return truncated + "..."


def generate_table(skills_dir: pathlib.Path) -> str:
    """Generate the full Skills Table markdown from skill YAML headers."""
    rows = []

    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir():
            continue
        skill_md = d / "SKILL.md"
        if not skill_md.exists():
            continue

        fields = extract_yaml_fields(skill_md)
        if not fields or not fields['name']:
            continue

        name = fields['name']
        project = extract_project(name)
        version = fields['version']
        tags_str = ", ".join(fields['tags'][:5]) if fields['tags'] else "-"
        desc = truncate_desc(fields['description'])

        # Escape pipes in all text fields
        desc = escape_md_pipe(desc)
        tags_str = escape_md_pipe(tags_str)

        rows.append((name, project, version, tags_str, desc))

    header = "| No | Skill | Project | Version | Technologies | Description |"
    sep = "|----|-------|---------|---------|--------------|-------------|"

    lines = [header, sep]
    for i, (name, project, version, tags_str, desc) in enumerate(rows, 1):
        lines.append(f"| {i} | {name} | {project} | {version} | {tags_str} | {desc} |")

    return "\n".join(lines)


def update_readme(readme_path: pathlib.Path, table: str, total: int) -> None:
    """Replace the Skills Table section in README.md."""
    content = readme_path.read_text()

    stats_line = f"- **Total Skills**: {total}"

    # Replace from "## Skills Table" through the statistics line
    pattern = r'(## Skills Table\n\n).*?(## Statistics\n\n' + r'- \*\*Total Skills\*\*: \d+)'
    replacement = rf'\g<1>{table}\n\n## Statistics\n\n{stats_line}'

    matched = re.search(pattern, content, flags=re.DOTALL)
    if not matched:
        print("ERROR: Could not find Skills Table section to replace", file=sys.stderr)
        sys.exit(1)

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if new_content == content:
        print("README.md is already up to date")
        return

    readme_path.write_text(new_content)


def main():
    dry_run = "--dry-run" in sys.argv

    repo_root = pathlib.Path(__file__).resolve().parent.parent
    skills_dir = repo_root / ".agents" / "skills"
    readme_path = repo_root / "README.md"

    if not skills_dir.exists():
        print(f"ERROR: Skills directory not found: {skills_dir}", file=sys.stderr)
        sys.exit(1)

    table = generate_table(skills_dir)
    # Count data rows (total lines minus header and separator)
    total = len(table.split('\n')) - 2

    if dry_run:
        print(f"[dry-run] Would generate {total} skill entries")
        print(table)
        return

    update_readme(readme_path, table, total)
    print(f"Updated README.md with {total} skills")


if __name__ == "__main__":
    main()
