---
name: skman
description: Meta skill for authoring and managing agent skills. Generates spec-compliant, cross-platform SKILL.md files from documentation sources (URLs or filesystem paths). Works on pi, opencode, Claude Code, and Codex. Use when creating new skills, converting documentation, updating existing skills, or producing .agents/skills/<name>/SKILL.md files.
---

# skman — Skill Package Manager

## Overview

Generates spec-compliant, cross-platform agent skills from user requirements. Takes a project/tool name, version, and documentation sources (URLs or filesystem paths), then produces complete SKILL.md files that work on pi, opencode, Claude Code, and Codex.

Skills are Markdown-only by default — no scripts or assets unless the user explicitly requests them.

- **Scripts** — Bash or Python for deterministic tasks (validation, analysis, etc.). Executed by the agent, not loaded into context. Only output consumes tokens.
- **Assets** — Supporting files (docs, schemas, diagrams). Not executed; supplementary material the agent reads when needed.

## When to Use

- Creating a new agent skill for a project, library, or tool
- Converting existing documentation into skill format
- Generating skills from URLs or local codebases
- Updating an existing skill for a new upstream version
- Any task producing `.agents/skills/<name>/SKILL.md` files

## Generation Workflow

Follow these steps in order. All paths relative to the skill directory (where SKILL.md lives).

### Step 1: Detect Mode and Validate Input

**New vs update:**
- **New** — No existing directory matches the name. Proceed with full generation.
- **Update** — Existing skill found (e.g., `curl-8-19-0` → `curl-8-20-0`). Read existing SKILL.md, crawl new sources, diff against old content, preserve working sections, update only changed parts. Create a new versioned directory — never overwrite the old one.

**Conflict detection** — Before creating, check `.agents/skills/` for:
- Exact name match → warn user, ask if they meant to update
- Overlapping name without version → suggest versioned naming
- Near-duplicate coverage → note overlap in description

**Name validation** — Must match `^[a-z0-9]+(-[a-z0-9]+)*$`. Include upstream version hyphenated (e.g., `curl-8-20-0`, `fastapi-0-115`). If no version, use just the name (e.g., `git`).

Valid: `pdf-processing`, `data-analysis` &nbsp;|&nbsp; Invalid: `PDF-Processing`, `-pdf`, `pdf--processing`

### Step 2: Crawl and Collect Content

Gather all source material from the provided URLs and filesystem paths.

**URL crawling** — Recursively follow links within the same domain and subdomains.

**Filesystem crawling** — Recursively visit files and directories.

**Readable extensions:**

| Type | Extensions | Method |
|------|-----------|--------|
| Markdown | `.md`, `.mdx`, `.markdown`, `.mkd` | Direct read |
| RST/Docs | `.rst`, `.adoc` | Direct read (`.rst` may need reconstructing hierarchy from many files) |
| Text | `.txt` | Direct read |
| HTML | `.html`, `.htm` | `pandoc -f html -t markdown`, fallback raw |
| PDF | `.pdf` | `pdftotext -layout` or `gs` |
| Config | `.yaml`, `.yml`, `.json`, `.toml`, `.ini`, `.cfg` | Direct read |
| Code | `.sh`, `.py`, `.c`, `.h`, `.cpp`, `.rs`, `.go`, `.js`, `.ts` | Direct read |
| Man pages | `.1`–`.9` | Direct read |

**Skip:**
- Binary files (`.png`, `.jpg`, `.zip`, `.tar`, `.gz`, `.whl`, `.pyc`, `.so`, `.dll`, `.exe`)
- Hidden files/directories (`.` prefix) unless explicitly requested
- Environment files (`.env`, `.env*`) unless explicitly requested
- Version control (`.git/`, `.svn/`, `.hg/`) always
- **Do not skip by size** — large files may be complex text documents

### Step 3: Determine Structure and Write Output

**Choose structure:**

```
If content has 2+ distinct subtopics AND agent only needs 1-2 per task → complex (SKILL.md + reference/)
If single cohesive topic OR under 300 lines                                    → simple (SKILL.md only)
```

- **Simple**: All content in a single SKILL.md.
- **Complex**: SKILL.md as overview + navigation hub, `reference/` with flat numbered files (`01-*.md`, `02-*.md`).
- **Scripts/assets**: Only if explicitly requested by the user.

**Write YAML header** (exactly two fields — all other metadata goes to `assets/MISC.md`):

```yaml
---
name: <skill-name>
description: <1-1024 chars, third person, includes WHAT and WHEN>
---
```

- `name` — Max 64 chars. Must match directory name. Regex `^[a-z0-9]+(-[a-z0-9]+)*$`.
- `description` — Formula: `[WHAT it does] + [key capabilities] + Use when [specific scenarios].` Aim for 150–400 characters. Third person only. Never "I can help" or "you can use".

**Write SKILL.md body** — Required sections: `## Overview`, `## When to Use`, `## Core Concepts`. Optional sections (include only when applicable): `## Installation / Setup`, `## Usage Examples`, `## Advanced Topics` (only if reference/ exists). See [Templates](reference/03-templates.md) for full templates.

**Write reference files** (if complex) — Flat `reference/` directory, `NN-*.md` naming. Each file: heading, table of contents (if over 100 lines), content. Keep individual reference files under 200 lines — split if longer. All reference files must be linked from SKILL.md. Never chain references (reference → reference).

**Write scripts** (if requested) — See Script Rules below.

### Step 4: Validate

**Run structural validator:**
```bash
bash scripts/validate-skill.sh [--strict] <SKILL_DIR>
```
Checks YAML header, directory layout, file naming, section presence, and script references. Use `--strict` to promote warnings to errors.

**LLM judgment checks** (the script cannot verify these):
- Content accuracy — no hallucinated content, all from crawled sources
- Conciseness — no over-explaining basics the target agent already knows
- Single recommended approach — not multiple options confusing the agent
- Consistent terminology — one term per concept throughout
- Code example quality — correct, copy-pasteable, relevant
- Script clarity — execution intent explicit ("Run" vs "See for reference"), errors handled

### Step 5: Report and Update Index

Report success with file tree and validation results.

**Regenerate the skills table** (after every skill addition, deletion, rename, update, or YAML header edit):
```bash
bash scripts/gen-skills-table.sh [SKILLS_DIR] [README_PATH]
```
Both arguments optional. Defaults: `.agents/skills` and `README.md`.

## Rules

Apply these throughout the workflow.

### YAML Header

- File starts with `---` on line 1, ends header with second `---`.
- Exactly two fields: `name` and `description`.
- All other metadata (`license`, `author`, `version`, `tags`, `category`, etc.) goes in `assets/MISC.md` — not loaded into agent context.
- `name`: max 64 chars, regex `^[a-z0-9]+(-[a-z0-9]+)*$`.
- `description`: 1–1024 chars, third person.

### Description Formula

```
[WHAT it does] + [key capabilities, comma-separated] + Use when [specific scenarios].
```

- **WHAT**: Action verb + domain
- **WHEN**: Specific trigger scenarios for skill selection
- **Key terms**: Include distinctive keywords from the project/tool name and primary use cases
- Target 150–400 characters. Under 100 = too vague, over 600 = token waste.

### Directory and Version

- Directory: `<skill-name>` or `<skill-name>-<version>` (e.g., `curl-8-20-0`, `project-2025-11-25`).
- Skill file version (SemVer) tracked in `assets/MISC.md`, not YAML header. Start at `0.1.0`.
  - Patch (`0.1.0` → `0.1.1`): typos, minor corrections
  - Minor (`0.1.0` → `0.2.0`): new content, substantive improvements
  - Major (`0.2.0` → `1.0.0`): structural rewrites, breaking instruction changes

### Script Quality

- Handle errors explicitly — never punt to the agent with bare exceptions.
- Document all constants with justification.
- Clear, specific error messages that help the agent fix issues.
- **Execution intent explicit**: "Run `script.py`" (preferred) vs "See `script.py` for reference".
- Prefer execution over reading — deterministic scripts are more reliable than agent-generated equivalents.
- **Python**: `python3 -B script.py`, built-in modules only unless user requests otherwise. For third-party: `uv run python -B script.py`.
- **Naming**: Default script shares skill base name (e.g., `curl` for `curl-8-20-0`). Additional scripts use descriptive names.
- **Help system**: Every script supports `--help`. Subcommands support independent `--help` (e.g., `script subcmd --help`).

### Anti-Patterns to Avoid

- **Backslash paths** — Always forward slashes (`reference/guide.md`, not `reference\guide.md`).
- **Too many options** — Single recommended approach in SKILL.md. Alternatives go in reference files.
- **Time-sensitive info** — Don't write "latest version is 3.2". Use labeled "old patterns" section for legacy.
- **Over-explaining basics** — Target agent knows what HTTP, databases, etc. are. Challenge each paragraph: "Does this justify its token cost?"
- **Inconsistent terminology** — One term per concept throughout (always "API endpoint", not sometimes "URL" or "route").

### Cross-Model Compatibility

Generated skills must work on both small and large LLMs:

- **SKILL.md should be scannable in 30 seconds** — every paragraph contains at least one actionable instruction or concrete example.
- **Reference files under 200 lines each** — split if longer.
- **One level of references only** — all link directly from SKILL.md, never reference → reference.
- **Progressive disclosure** — SKILL.md gives quick-start + links to details. Agent loads references only when needed.
- **No chained navigation** — an agent reading SKILL.md should find everything it needs or clear paths to exactly 1–2 reference files.

## Commands

### sync — Sync local .agents/skills with tangled-skills

```bash
bash scripts/sync.sh [TARGET_DIR]
```

Fetches the `main` branch of tangled-skills from GitHub, extracts `.agents/skills/` into `TARGET_DIR/.agents/skills/`, overwriting existing skills with upstream versions. Default target: current directory.

**Dependencies:** bash, curl, tar

## Advanced Topics

**Evaluation-Driven Development**: Build evaluations before writing skill content, iterate based on real agent behavior → [Evaluation-Driven Development](reference/01-evaluation-driven-development.md)

**Degrees of Freedom**: Match instruction specificity to task fragility — high, medium, or low freedom → [Degrees of Freedom](reference/02-degrees-of-freedom.md)

**Templates**: Full copy-paste templates for SKILL.md, reference files, and MISC.md → [Templates](reference/03-templates.md)
