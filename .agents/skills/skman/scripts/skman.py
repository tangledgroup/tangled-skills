#!/usr/bin/env python3
"""skman — Skill Package Manager

Single-entry CLI for validating skills, regenerating the README table,
and syncing upstream skills from tangled-skills.

Usage:
    python3 -B skman.py validate [--strict] <SKILL_DIR>
    python3 -B skman.py gen-table [SKILLS_DIR] [README_PATH]
    python3 -B skman.py sync [TARGET_DIR]
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LEN = 64
MAX_DESC_LEN = 1024
SKILL_MAX_LINES = 500
README_TABLE_COL = 120

UPSTREAM_REPO = "https://github.com/tangledgroup/tangled-skills"
UPSTREAM_BRANCH = "main"
UPSTREAM_PATH = ".agents/skills"


# ---------------------------------------------------------------------------
# YAML helpers (no external parser — built-in only)
# ---------------------------------------------------------------------------

def _extract_yaml_field(text: str, field: str) -> str:
    """Extract a single-line or block-scalar YAML field from frontmatter."""
    lines = text.split("\n")
    in_header = False
    in_block = False
    strip_mode = False
    buf = []

    for i, line in enumerate(lines):
        if i == 0 and line.strip() == "---":
            in_header = True
            continue
        if line.strip() == "---" and in_header:
            # End of header
            if in_block:
                val = " ".join(buf)
                return val.strip()
            break
        if not in_header:
            break

        if in_block:
            if line.startswith("  ") or line.strip() == "":
                buf.append(line[2:].strip())
                continue
            else:
                val = " ".join(buf)
                in_block = False
                buf = []
                # Fall through to process this line

        key_match = re.match(rf"^{re.escape(field)}\s*:\s*(.*)", line)
        if key_match:
            val = key_match.group(1).strip()
            if val in (">-", ">"):
                strip_mode = val == ">-"
                in_block = True
                buf = []
                continue
            # Strip quotes
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                val = val[1:-1]
            return val

    return ""


def _count_yaml_fields(text: str) -> list[str]:
    """Return list of top-level field names in the YAML header."""
    fields = []
    lines = text.split("\n")
    in_header = False
    in_block = False

    for i, line in enumerate(lines):
        if i == 0 and line.strip() == "---":
            in_header = True
            continue
        if line.strip() == "---" and in_header:
            break
        if not in_header:
            continue

        if in_block:
            if line.startswith("  ") or line.strip() == "":
                continue
            else:
                in_block = False

        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*)\s*:", line)
        if m:
            fields.append(m.group(1))
            val = line[m.end():].strip()
            if val in (">-", ">"):
                in_block = True

    return fields


# ---------------------------------------------------------------------------
# validate subcommand
# ---------------------------------------------------------------------------

class _Validator:
    """Collect pass/fail/warn results for a skill directory."""

    def __init__(self, strict: bool):
        self.strict = strict
        self.errors = 0
        self.warnings = 0
        self.passes = 0
        self.sections: dict[str, list[tuple[str, str]]] = {}

    # -- output helpers
    def _section(self, name: str):
        self.sections.setdefault(name, [])

    def pass_(self, section: str, msg: str):
        self.passes += 1
        self._section(section)
        self.sections[section].append(("✓", msg))
        print(f"  ✓ {msg}")

    def fail(self, section: str, msg: str):
        self.errors += 1
        self._section(section)
        self.sections[section].append(("✗", msg))
        print(f"  ✗ {msg}")

    def warn(self, section: str, msg: str):
        self.warnings += 1
        self._section(section)
        self.sections[section].append(("⚠", msg))
        print(f"  ⚠ {msg}")

    # -- checks
    def check_yaml_header(self, skill_dir: Path):
        print("--- YAML Header ---")
        sec = "YAML Header"
        skill_file = skill_dir / "SKILL.md"

        text = skill_file.read_text(encoding="utf-8")
        lines = text.split("\n")

        # Starts with ---
        if lines[0].strip() == "---":
            self.pass_(sec, "File starts with --- on line 1")
        else:
            self.fail(sec, f"File does not start with --- on line 1 (got: '{lines[0]}')")

        # Closing ---
        dash_indices = [i for i, l in enumerate(lines) if l.strip() == "---"]
        if len(dash_indices) < 2:
            self.fail(sec, "No closing --- found for YAML header")
        else:
            self.pass_(sec, f"YAML header block properly closed with --- (line {dash_indices[1] + 1})")

        # name field
        yaml_name = _extract_yaml_field(text, "name")
        dir_name = skill_dir.name

        if not yaml_name:
            self.fail(sec, "Missing 'name' field in YAML header")
        elif yaml_name != dir_name:
            self.fail(sec, f"'name' field '{yaml_name}' does not match directory name '{dir_name}'")
        else:
            self.pass_(sec, "'name' field matches directory name")

        if yaml_name and not NAME_RE.match(yaml_name):
            self.fail(sec, f"'name' '{yaml_name}' does not match regex ^[a-z0-9]+(-[a-z0-9]+)*$")
        elif yaml_name:
            self.pass_(sec, "'name' matches required format")

        # description field
        yaml_desc = _extract_yaml_field(text, "description")
        if not yaml_desc:
            self.fail(sec, "Missing 'description' field in YAML header")
        elif len(yaml_desc) > MAX_DESC_LEN:
            self.warn(sec, f"'description' is {len(yaml_desc)} chars (max recommended: {MAX_DESC_LEN})")
        else:
            self.pass_(sec, f"'description' present ({len(yaml_desc)} chars)")

        # Exactly two fields
        fields = _count_yaml_fields(text)
        extra = [f for f in fields if f not in ("name", "description")]
        if extra:
            self.fail(sec, f"Extra fields in YAML header: {', '.join(extra)}. Only name and description allowed.")
        else:
            self.pass_(sec, "YAML header has exactly two fields (name, description)")

        print()

    def check_directory(self, skill_dir: Path):
        print("--- Directory Structure ---")
        sec = "Directory Structure"

        self.pass_(sec, "SKILL.md exists")

        # reference/
        ref_dir = skill_dir / "reference"
        has_reference = ref_dir.is_dir()
        if has_reference:
            self.pass_(sec, "reference/ directory exists")
            nested = [d for d in ref_dir.rglob("*") if d.is_dir() and d != ref_dir]
            if nested:
                self.fail(sec, f"reference/ contains subdirectories (should be flat): {', '.join(str(d) for d in nested)}")
            else:
                self.pass_(sec, "reference/ has flat structure (no subdirectories)")

            ref_files = sorted(ref_dir.glob("*.md"))
            bad_named = [f.name for f in ref_files if not re.match(r"^[0-9][0-9]-.*\.md$", f.name)]
            if bad_named:
                self.fail(sec, f"reference/ files not matching NN-*.md pattern: {', '.join(bad_named)}")
            else:
                self.pass_(sec, f"reference/ files match NN-*.md naming ({len(ref_files)} files)")

            empty = [f.name for f in ref_files if f.stat().st_size == 0]
            if empty:
                self.fail(sec, f"Empty reference files: {', '.join(empty)}")
            else:
                self.pass_(sec, "Reference files are non-empty")
        else:
            self.pass_(sec, "No reference/ directory (simple skill)")

        # scripts/
        has_scripts = (skill_dir / "scripts").is_dir()
        if has_scripts:
            self.pass_(sec, "scripts/ directory exists (opt-in)")
        else:
            self.pass_(sec, "No scripts/ directory")

        # assets/
        if (skill_dir / "assets").is_dir():
            self.pass_(sec, "assets/ directory exists (opt-in)")
        else:
            self.pass_(sec, "No assets/ directory")

        # Unexpected root files
        allowed = {"SKILL.md", "reference", "scripts", "assets"}
        unexpected = [
            e.name for e in skill_dir.iterdir()
            if not e.is_dir() and e.name not in allowed and not e.name.startswith(".")
        ]
        if unexpected:
            self.warn(sec, f"Unexpected files in skill root: {', '.join(unexpected)}")
        else:
            self.pass_(sec, "No unexpected files in skill root")

        # Disallowed dirs/files
        disallowed = []
        for vc in (".git", ".svn", ".hg"):
            if (skill_dir / vc).is_dir():
                disallowed.append(f"{vc}/")
        for env in skill_dir.glob(".env*"):
            if env.exists():
                disallowed.append(env.name)
        if disallowed:
            self.fail(sec, f"Disallowed files/dirs found: {', '.join(disallowed)}")
        else:
            self.pass_(sec, "No disallowed files/directories (.git, .env*, etc.)")

        # Backslashes
        backslash = [str(f) for f in skill_dir.rglob("*\\*") if f != skill_dir]
        if backslash:
            self.fail(sec, "Files with backslashes in names found")
        else:
            self.pass_(sec, "No backslashes in file paths")

        print()
        return has_reference, has_scripts

    def check_content(self, skill_dir: Path, has_reference: bool):
        print("--- Content Sections ---")
        sec = "Content Sections"
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")

        if re.search(r"^## Overview", text, re.MULTILINE):
            self.pass_(sec, "## Overview section present")
        else:
            self.fail(sec, "Missing '## Overview' section")

        if re.search(r"^## When to Use", text, re.MULTILINE):
            self.pass_(sec, "## When to Use section present")
        else:
            self.fail(sec, "Missing '## When to Use' section")

        if has_reference:
            line_count = text.count("\n")
            if line_count > SKILL_MAX_LINES:
                self.warn(sec, f"SKILL.md is {line_count} lines (max recommended: {SKILL_MAX_LINES} when reference/ exists)")
            else:
                self.pass_(sec, f"SKILL.md under {SKILL_MAX_LINES} lines ({line_count} lines)")

            if re.search(r"^## Advanced Topics", text, re.MULTILINE):
                self.pass_(sec, "## Advanced Topics section present")

                # All reference files linked from SKILL.md
                ref_dir = skill_dir / "reference"
                ref_names = [f.name for f in ref_dir.glob("*.md")]
                missing = [r for r in ref_names if f"reference/{r}" not in text]
                if missing:
                    self.warn(sec, f"Reference files not linked from SKILL.md: {', '.join(missing)}")
                else:
                    self.pass_(sec, "All reference files linked from SKILL.md")
            else:
                self.fail(sec, "Missing '## Advanced Topics' section (required when reference/ exists)")

            # Reference files have headings
            no_heading = []
            for f in (skill_dir / "reference").glob("*.md"):
                head = f.read_text(encoding="utf-8", errors="replace").split("\n")[:5]
                if not any(l.startswith("#") for l in head):
                    no_heading.append(f.name)
            if no_heading:
                self.fail(sec, f"Reference files missing headings: {', '.join(no_heading)}")
            else:
                self.pass_(sec, "Reference files have headings")

        print()

    def check_scripts(self, skill_dir: Path):
        sec = "Scripts"
        scripts_dir = skill_dir / "scripts"
        if not scripts_dir.is_dir():
            return

        print(f"--- {sec} ---")
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")

        # Referenced scripts exist on disk
        refs = set(re.findall(r"scripts/[a-zA-Z0-9_.\-]+", text))
        missing = [r for r in refs if not (skill_dir / r).exists()]
        if missing:
            self.fail(sec, f"Referenced scripts not found: {', '.join(missing)}")
        elif refs:
            self.pass_(sec, "All referenced scripts exist on disk")
        else:
            self.pass_(sec, "No script references in SKILL.md (scripts may be standalone)")

        # No package installs in scripts
        install_re = re.compile(r"(pip install|npm install|apt-get install|yum install)")
        skip_tokens = {"grep", "sed", "awk", "re.compile", "re.search", "re.findall",
                       "install_re", "INSTALL"}
        violations = []
        for f in scripts_dir.iterdir():
            if f.is_file():
                content = f.read_text(encoding="utf-8", errors="replace")
                # Skip comment lines and lines that are regex/pattern definitions
                code_lines = [l for l in content.split("\n")
                              if not re.match(r"^\s*(#|//)", l)
                              and not any(t in l for t in skip_tokens)]
                if any(install_re.search(l) for l in code_lines):
                    violations.append(f.name)
        if violations:
            self.warn(sec, f"Scripts with package installs (violates AGENTS.md): {', '.join(violations)}")
        else:
            self.pass_(sec, "No package installation commands in scripts")

        # Shebang or recognized extension
        ext_re = re.compile(r"\.(sh|bash|py|js|ts)$")
        bad = []
        for f in scripts_dir.iterdir():
            if f.is_file():
                first = f.read_text(encoding="utf-8", errors="replace").split("\n")[0]
                if not first.startswith("#!") and not ext_re.search(f.name):
                    bad.append(f.name)
        if bad:
            self.warn(sec, f"Scripts without shebang or recognized extension: {', '.join(bad)}")
        else:
            self.pass_(sec, "All scripts have shebang or recognizable extension")

        print()

    def summary(self):
        total = self.errors + self.warnings + self.passes
        print("--- Summary ---")
        print(f"  Checks passed: {self.passes}")
        print(f"  Errors:        {self.errors}")
        print(f"  Warnings:      {self.warnings}")
        print(f"  Total checks:  {total}")

        if self.errors > 0:
            print(f"\n✗ Validation FAILED with {self.errors} error(s)")
            return 1
        if self.strict and self.warnings > 0:
            print(f"\n✗ Validation FAILED in strict mode with {self.warnings} warning(s)")
            return 1
        if self.warnings > 0:
            print(f"\n⚠ Validation passed with {self.warnings} warning(s)")
            return 0
        print("\n✓ Validation PASSED")
        return 0


def cmd_validate(args):
    """Validate structural integrity of a skill directory."""
    skill_dir = Path(args.skill_dir)
    if not skill_dir.is_dir():
        print(f"Error: Directory not found: {args.skill_dir}", file=sys.stderr)
        sys.exit(1)
    if not (skill_dir / "SKILL.md").is_file():
        print(f"Error: SKILL.md not found in: {skill_dir}", file=sys.stderr)
        sys.exit(1)

    skill_dir = skill_dir.resolve()
    print(f"Validating skill: {skill_dir.name}")
    print(f"Directory: {skill_dir}")
    print()

    v = _Validator(strict=args.strict)
    v.check_yaml_header(skill_dir)
    has_ref, has_scripts = v.check_directory(skill_dir)
    v.check_content(skill_dir, has_ref)
    if has_scripts:
        v.check_scripts(skill_dir)
    code = v.summary()
    sys.exit(code)


# ---------------------------------------------------------------------------
# gen-table subcommand
# ---------------------------------------------------------------------------

def _strip_version_suffix(name: str) -> str:
    """Derive project name from skill directory by stripping version suffix."""
    # Strip trailing pre-release
    name = re.sub(r"-(alpha|beta|rc)-[0-9]+$", "", name)
    # Strip trailing -NUMBER segments
    name = re.sub(r"(-[0-9]+)+$", "", name)
    return name


def _truncate(text: str, max_len: int = README_TABLE_COL) -> str:
    """Truncate text at word boundary, appending '...' if needed."""
    if len(text) <= max_len:
        return text
    cut = max_len - 3
    truncated = text[:cut]
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space]
    return f"{truncated}..."


def cmd_gen_table(args):
    """Regenerate the Skills Table section in README.md."""
    skills_dir = Path(args.skills_dir)
    readme_path = Path(args.readme_path)

    if not skills_dir.is_dir():
        print(f"Error: Skills directory '{skills_dir}' not found.", file=sys.stderr)
        sys.exit(1)
    if not readme_path.is_file():
        print(f"Error: README file '{readme_path}' not found.", file=sys.stderr)
        sys.exit(1)

    rows = []
    count = 0

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            continue

        text = skill_file.read_text(encoding="utf-8")
        name = _extract_yaml_field(text, "name")
        description = _extract_yaml_field(text, "description")
        project = _strip_version_suffix(skill_dir.name)
        desc_trunc = _truncate(description)

        count += 1
        rows.append((skill_dir.name, count, project, desc_trunc))

    # Build replacement table
    header = (
        "\n## Skills Table\n\n"
        "| No | Skill | Project | Version | Technologies | Description |\n"
        "|----|-------|---------|---------|--------------|-------------|\n"
    )
    body_lines = []
    for skill_name, num, project, desc in rows:
        escaped = desc.replace("|", "\\|")
        body_lines.append(f"| {num} | {skill_name} | {project} |  |  | {escaped} |")

    replacement = header + "\n".join(body_lines) + "\n"

    # Replace in README
    readme_text = readme_path.read_text(encoding="utf-8")

    table_match = re.search(r"^## Skills Table$", readme_text, re.MULTILINE)
    stats_match = re.search(r"^## Statistics$", readme_text, re.MULTILINE)
    if not table_match or not stats_match:
        print(f"Error: Could not find '## Skills Table' or '## Statistics' in {readme_path}", file=sys.stderr)
        sys.exit(1)

    # Find last non-blank line before table
    before_end = table_match.start()
    while before_end > 0 and readme_text[before_end - 1] in ("\n", " "):
        before_end -= 1

    # Rebuild: content before table + replacement + blank line + stats section onward
    new_readme = (
        readme_text[:before_end]
        + replacement
        + "\n"
        + readme_text[stats_match.start():]
    )

    # Update statistics count
    new_readme = re.sub(
        r"- \*\*Total Skills\*\*: \d+",
        f"- **Total Skills**: {count}",
        new_readme,
    )

    readme_path.write_text(new_readme, encoding="utf-8")
    print(f"Generated skills table with {count} skills in {readme_path}")


# ---------------------------------------------------------------------------
# sync subcommand
# ---------------------------------------------------------------------------

def cmd_sync(args):
    """Sync local .agents/skills with tangled-skills upstream."""
    target = Path(args.target_dir)
    if not target.is_dir():
        print(f"Error: Target directory '{target}' does not exist.", file=sys.stderr)
        sys.exit(1)

    target = target.resolve()
    skills_dest = target / UPSTREAM_PATH
    skills_dest.mkdir(parents=True, exist_ok=True)

    url = f"{UPSTREAM_REPO}/archive/refs/heads/{UPSTREAM_BRANCH}.tar.gz"
    print(f"Syncing tangled-skills into {skills_dest} ...")

    try:
        # Download tarball to temp file
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
            tmp_path = tmp.name

        subprocess.run(
            ["curl", "-sL", "-o", tmp_path, url],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Extract .agents/skills from archive
        subprocess.run(
            [
                "tar", "-xz",
                f"--strip-components=3",
                f"-C", str(skills_dest),
                f"tangled-skills-{UPSTREAM_BRANCH}/{UPSTREAM_PATH}",
            ],
            check=True,
        )

        os.unlink(tmp_path)

    except FileNotFoundError as e:
        print(f"Error: Required command not found: {e}", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}: {' '.join(e.cmd)}", file=sys.stderr)
        # Clean up temp file if it exists
        if "tmp_path" in dir() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        sys.exit(1)

    print(f"Sync complete. Skills directory: {skills_dest}/")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skman",
        description="Skill Package Manager — validate, generate tables, and sync agent skills.",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # -- validate
    p_validate = sub.add_parser(
        "validate",
        help="Validate structural integrity of a skill directory",
        description=(
            "Checks YAML header fields, directory layout, file naming, "
            "section presence, and script references."
        ),
    )
    p_validate.add_argument(
        "--strict",
        action="store_true",
        help="Promote warnings to errors (exit 1 on warnings)",
    )
    p_validate.add_argument(
        "skill_dir",
        help="Path to the skill directory containing SKILL.md",
    )

    # -- gen-table
    p_table = sub.add_parser(
        "gen-table",
        help="Regenerate the Skills Table section in README.md",
        description="Scans all skills and rebuilds the markdown table in README.md.",
    )
    p_table.add_argument(
        "skills_dir",
        nargs="?",
        default=".agents/skills",
        help="Directory containing skill subdirectories (default: .agents/skills)",
    )
    p_table.add_argument(
        "readme_path",
        nargs="?",
        default="README.md",
        help="Path to README.md to update (default: README.md)",
    )

    # -- sync
    p_sync = sub.add_parser(
        "sync",
        help="Sync local .agents/skills with tangled-skills upstream",
        description=(
            "Fetches the main branch of tangled-skills from GitHub and "
            "extracts .agents/skills into the target directory."
        ),
    )
    p_sync.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="Target directory (default: current directory)",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "validate": cmd_validate,
        "gen-table": cmd_gen_table,
        "sync": cmd_sync,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
