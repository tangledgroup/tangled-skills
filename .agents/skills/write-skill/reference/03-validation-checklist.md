# Validation Checklist

## Contents
- YAML Header Checks
- Structure Checks
- Content Checks
- Script Checks (if applicable)

Run this checklist before considering the skill complete.

## YAML Header

- [ ] File starts with `---` on line 1
- [ ] Valid YAML block between first pair of `---` delimiters
- [ ] `name` present and matches directory name
- [ ] `name` matches regex `^[a-z0-9]+(-[a-z0-9]+)*$`
- [ ] `description` present (1-1024 characters)
- [ ] `license` is "MIT" (always — this is the skill file's license, not the upstream project's)
- [ ] `author` format: `Name <email@example.com>`
- [ ] `version` is non-empty and matches the upstream project's version string
- [ ] Header ends with `---` before main content

## Structure

- [ ] Directory name matches skill name
- [ ] SKILL.md exists
- [ ] If complex: `reference/` with zero-padded two-digit numbered files (`01-`, `02-`, … `10-`, `11-`)
- [ ] No nested `reference/` directories
- [ ] SKILL.md under 500 lines (if references exist)
- [ ] No `scripts/` or `assets/` unless explicitly requested by user
- [ ] All file paths use forward slashes (no backslashes)
- [ ] Reference files are one level deep from SKILL.md (no chained references)

## Content

- [ ] "Overview" section present
- [ ] "When to Use" with specific scenarios
- [ ] At least one code example (if applicable to the skill type)
- [ ] No hallucinated content — all from downloaded sources
- [ ] Content is concise — no over-explaining basics the agent already knows
- [ ] Consistent terminology throughout (one term per concept)
- [ ] No time-sensitive information (or placed in "old patterns" section)
- [ ] Single recommended approach given (not multiple options causing confusion)

## Scripts (if explicitly requested)

- [ ] Script paths use forward slashes
- [ ] Execution intent is clear ("Run" vs "See for reference")
- [ ] Scripts handle errors explicitly (no bare exceptions)
- [ ] All constants documented with justification
- [ ] Expected output format shown in SKILL.md
- [ ] No install instructions in scripts (only system-available tools)
