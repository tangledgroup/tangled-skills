#!/usr/bin/env python3
"""Migrate SKILL.md frontmatter: keep only name+description, move rest to assets/MISC.md."""

import os
import re
import sys
import yaml

SKILLS_DIR = os.environ.get("SKILLS_DIR", ".agents/skills")


def parse_frontmatter(skill_md_path):
    """Extract YAML frontmatter and body from SKILL.md."""
    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match YAML block between first pair of --- delimiters
    m = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if not m:
        return None, None, content

    yaml_str = m.group(1)
    body = m.group(2)
    try:
        meta = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        print(f"  YAML parse error: {e}", file=sys.stderr)
        return None, None, content

    if not isinstance(meta, dict):
        return None, None, content

    return meta, body, content


def write_misc(skill_dir, meta):
    """Write assets/MISC.md with all non-required fields."""
    assets_dir = os.path.join(skill_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    misc_path = os.path.join(assets_dir, "MISC.md")

    # Collect all fields except name and description
    misc_fields = {}
    for key in ("license", "author", "version", "tags", "category",
                "external_references", "compatibility", "metadata",
                "allowed-tools", "disable-model-invocation"):
        if key in meta:
            misc_fields[key] = meta[key]

    # Also capture any unexpected keys
    known_keys = {"name", "description"} | misc_fields.keys()
    for key in meta:
        if key not in known_keys:
            misc_fields[key] = meta[key]

    if not misc_fields:
        return False  # Nothing to migrate

    yaml_block = yaml.dump(misc_fields, default_flow_style=False, sort_keys=False, allow_unicode=True)

    content = f"""# Skill Metadata

Moved from SKILL.md frontmatter. Not loaded into agent context.

```yaml
{yaml_block.rstrip()}
```
"""
    with open(misc_path, "w", encoding="utf-8") as f:
        f.write(content)

    return True


def write_skill_md(skill_md_path, meta, body):
    """Rewrite SKILL.md with simplified frontmatter (name + description only)."""
    name = meta.get("name", "")
    desc = meta.get("description", "")

    # Serialize description preserving multi-line if needed
    new_yaml = yaml.dump(
        {"name": name, "description": desc},
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=1000,  # prevent unwanted line wrapping
    )

    content = f"---\n{new_yaml.rstrip()}\n---\n{body}"

    with open(skill_md_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    skills_dir = os.path.abspath(SKILLS_DIR)
    if not os.path.isdir(skills_dir):
        print(f"ERROR: {skills_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    errors = 0
    skipped = 0
    processed = 0
    no_migration = 0

    for entry in sorted(os.listdir(skills_dir)):
        skill_dir = os.path.join(skills_dir, entry)
        if not os.path.isdir(skill_dir):
            continue

        skill_md = os.path.join(skill_dir, "SKILL.md")
        if not os.path.isfile(skill_md):
            print(f"SKIP {entry}: no SKILL.md", file=sys.stderr)
            skipped += 1
            continue

        meta, body, original = parse_frontmatter(skill_md)
        if meta is None:
            print(f"ERROR {entry}: could not parse frontmatter", file=sys.stderr)
            errors += 1
            continue

        # Write simplified SKILL.md
        write_skill_md(skill_md, meta, body)

        # Migrate extra fields to MISC.md
        migrated = write_misc(skill_dir, meta)
        if migrated:
            processed += 1
        else:
            no_migration += 1

    print(f"\nDone. Processed={processed}, NoMigration={no_migration}, Skipped={skipped}, Errors={errors}")


if __name__ == "__main__":
    main()
