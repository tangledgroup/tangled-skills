---
name: spm
description: Skill Package Manager, spm, it is meta skill for skill authoring and skill package manager for AI agents.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - meta
  - meta skill
  - skill package manager
  - authoring
category: meta
external_references:
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
  - https://opencode.ai/docs/skills
  - https://pi.dev/docs/latest/skills
---

# spm - Skill Package Manager

## Overview

It is meta skill for skill authoring and skill package manager for AI agents.

Generates spec-compliant, cross-platform agent skills from user requirements. Takes project/tool name, version, and documentation sources (URLs or filesystem paths), then produces complete SKILL.md files that work on pi, opencode, Claude Code, and Codex platforms.

Skills are Markdown-only by default — no scripts or assets are generated unless the user explicitly requests them. If OS-level operations are needed, inline bash or Python with built-in modules is used instead.

## When to Use

- Creating a new agent skill from scratch for a project, library, or tool
- Converting existing documentation into a skill format
- Generating skills from official documentation URLs or local codebases
- Updating an existing skill for a new upstream version
- Any task that requires producing spec-compliant `.agents/skills/<name>/SKILL.md` files

## Core Concepts

### Source Types

The user provides at least one source:

- **URLs** — HTTP(S) links to web pages, documentation, or raw files
- **Filesystem paths** — absolute or relative paths to directories or files
- **Mixed** — combination of both

### Output Structure

Generated skills are created in `.agents/skills/<skill-name>/`:

**Simple skill** (single SKILL.md):
```
my-skill/
└── SKILL.md              # All content inline
```

Use simple when the topic is conceptual, single-domain, or has no natural subtopic split.

**Complex skill** (SKILL.md + reference/):
```
my-skill/
├── SKILL.md              # Overview + navigation hub
└── reference/           # Flat structure, numbered files
    ├── 01-core-concepts.md
    └── 02-advanced-topics.md
```

Use complex when content has distinct subtopics that benefit from progressive disclosure — an agent would only need 1-2 reference files per task. Line count is secondary; a 200-line skill covering 4 domains should still split.

**Opt-in extras** (only when user explicitly requests scripts or assets):
```
my-skill/
├── SKILL.md
├── reference/
├── scripts/              # Only if explicitly requested
│   ├── analyze_form.py   # Utility script (executed, not loaded into context)
│   ├── fill_form.py      # Form filling script
│   └── validate.sh       # Validation script
└── assets/               # Only if explicitly requested
    └── example-config.yaml
```

**Script quality rules:**
- Scripts must handle errors explicitly (never punt to the agent with bare exceptions)
- All constants must be documented with justification
- Provide clear, specific error messages that help the agent fix issues
- Make execution intent unambiguous in instructions

### Progressive Disclosure Patterns

- **High-level guide with references**: SKILL.md provides quick-start examples, then links to detailed reference files for advanced features. Agent loads references only when needed.
- **Domain-specific organization**: For skills covering multiple domains, split by domain (e.g., `reference/01-finance.md`, `reference/02-sales.md`) so the agent loads only relevant context.
- **Conditional details**: Show basic content in SKILL.md, link to advanced content that the agent reads conditionally based on the task.

**Keep references one level deep from SKILL.md.** All reference files should link directly from SKILL.md. Never chain references (reference → reference → reference) — this causes incomplete information loading.

## Generation Workflow

### Step 0: Detect Mode

Determine whether this is a **new skill** or an **update**:

- **New**: No existing directory matches the name. Proceed with full generation.
- **Update**: Existing skill directory found (e.g., `curl-8-19-0` → `curl-8-20-0`). Read the existing SKILL.md, crawl new sources, diff against old content, preserve structure and working sections, update only changed parts. Create a new versioned directory — never overwrite the old one.

**Conflict detection:** Before creating, check `.agents/skills/` for:
- Exact name match (same version) → warn user, ask if they meant to update
- Name without version that overlaps → suggest versioned naming
- Near-duplicate coverage → note the overlap in description

### Step 1: Validate Input

Check that the skill name matches `^[a-z0-9]+(-[a-z0-9]+)*$` and version is a non-empty string matching the upstream project's versioning scheme (SemVer, date-based, two-part, or pre-release).

### Step 2: Crawl and Collect Content

Follow the crawling strategy to gather all source material.

**URL Crawling:** Recursively follow all links within the same domain and subdomains.

**Filesystem Path Crawling:** Recursively visit all files and directories.

**Analyzable extensions:**

- **Markdown**: `.md`, `.mdx`, `.markdown`, `.mkd` — direct read (`.md` and `.mdx` are treated identically), or `curl -sL` then read
- **RST/Docs**: `.rst`, `.adoc` — direct read. For `.rst` sources (common in Python docs), you may need to read many files to reconstruct the hierarchical document structure before synthesizing skill content
- **Text**: `.txt` — direct read
- **HTML**: `.html`, `.htm` — `pandoc -f html -t markdown`, fallback raw
- **PDF**: `.pdf` — `pdftotext -layout` or `gs`
- **Config**: `.yaml`, `.yml`, `.json`, `.toml`, `.ini`, `.cfg` — direct read
- **Scripts**: `.sh`, `.bash`, `.py`, `.c`, `.h`, `.cpp`, `.rs`, `.go`, `.js`, `.ts` — direct read
- **Man pages**: `.1`–`.9` — direct read

**Skip rules:**
- Binary files (`.png`, `.jpg`, `.gif`, `.zip`, `.tar`, `.gz`, `.whl`, `.pyc`, `.so`, `.dll`, `.exe`)
- Hidden files/directories (`.` prefix) unless explicitly requested
- Environment configuration files (`.env`, `.env*`) unless explicitly requested
- Version control dirs (`.git/`, `.svn/`, `.hg/`) always
- **Do not skip by size** — large files may be complex text documents

### Step 3: Analyze and Determine Structure

Assess collected content to decide simple vs complex output structure. Consider:
- Does the content have 2+ distinct subtopics? → complex
- Would an agent typically need only part of the skill per task? → complex
- Is it a single cohesive topic under 300 lines? → simple

### Step 4: Generate YAML Header

Create a valid YAML header with validated name, description, version, and metadata fields.

YAML Header Rules:

Every generated skill MUST have a valid YAML header. Invalid YAML prevents loading on all platforms.

```yaml
---
name: <skill-name>
description: <1-1024 char description, third person, includes WHAT and WHEN>
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "<upstream-version>"
tags:
  - <tag1>
  - <tag2>
category: <category>
external_references:
  - https://<user-provided-url>
---
```

Field Rules:
- `name` — **Required**. 1-64 chars, regex `^[a-z0-9]+(-[a-z0-9]+)*$`, matches directory name.
- `description` — **Required**. 1-1024 chars, third person, includes WHAT and WHEN.
- `license` — **Always MIT** — this is the skill file's license, never the upstream project's.
- `author` — Format: `Name <email@example.com>`.
- `version` — Non-empty string — preserve upstream version as-is (SemVer, date, two-part, pre-release).
- `tags` — Array of string tags, 3-7 recommended. Mix broad and specific. Include the upstream project name when distinctive.
- `category` — Skill category classification. Common values: `tooling`, `networking`, `database`, `language-runtime`, `ml-ai`, `web-framework`, `cli-tool`, `library`, `protocol`, `devops`.
- `external_references` — User-provided starting URLs only.
- `compatibility` — Max 500 chars, environment requirements.
- `metadata` — String-to-string map.
- `allowed-tools` — Pre-approved tools (experimental, pi only).
- `disable-model-invocation` — Hidden from system prompt (pi only).

Name Validation:

```
^[a-z0-9]+(-[a-z0-9]+)*$
```

Valid: `pdf-processing`, `data-analysis`, `fastapi-0-115`
Invalid: `PDF-Processing`, `-pdf`, `pdf--processing`, `pdf processing`

Version Field Rules:

The `version` field records the upstream project's version — **preserve it as-is**. Do not force it into a specific format. Acceptable formats:

- **SemVer 2.0.0**: `1.2.3` (strict three-part `MAJOR.MINOR.PATCH`)
- **SemVer pre-release**: `1.0.0-alpha`, `1.0.0-beta.2`, `1.0.0-rc.1`
- **SemVer with build metadata**: `1.0.0+20130313144700` (ignored in precedence)
- **Date-based**: `2025-11-25`, `2026-04-16` (for specs, snapshots, documentation releases)
- **Two-part**: `0.16`, `0.5` (some projects only use `MAJOR.MINOR`)

When constructing the **directory name**, hyphenate version components: `project-1-2-3`, `project-0-16`, `project-2025-11-25`. The `name` field in YAML must match the directory name exactly.

Description Formula — Construct descriptions using this pattern:

```
[WHAT it does] + [key capabilities, comma-separated] + Use when [specific scenarios].
```

Aim for **150-400 characters**. Under 100 = too vague, over 600 = token waste.

```yaml
# Good — specific, third person, includes WHAT and WHEN
description: Extracts text and tables from PDF files and merges multiple PDFs. Use when working with PDF documents.

# Poor — too vague
description: Helps with PDFs.
```

Output File Templates — SKILL.md Template:

Every generated skill MUST include the YAML header and these core sections:

```markdown
---
name: <skill-name>
description: <specific description with WHAT and WHEN>
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "<upstream-version>"
tags:
  - <tag1>
  - <tag2>
category: <category>
external_references:
  - https://<user-provided-url>
---

# <Project Name> <Version>

## Overview

Brief description of what the project/tool does and its primary use cases.

## When to Use

Clear guidance on when this skill should be invoked. Include specific scenarios.

## Core Concepts

Key concepts, terminology, and fundamental ideas related to the topic.
```

The following sections are **optional** — include only when applicable:

`## Installation / Setup` — Include when the tool/library requires installation, configuration, or environment setup steps. Skip for conceptual, guideline, or meta-skills that have no install process.

`## Usage Examples` — Include when practical code examples are relevant. Provide copy-pasteable code blocks with language tags. Skip for conceptual, guideline, or meta-skills where code examples don't apply.

`## Advanced Topics` — Include **only** when the skill has companion reference files in `reference/`. Use this section as a navigation hub linking to them:

```markdown
## Advanced Topics

**Core Concepts**: Deep dive into fundamentals → [Core Concepts](reference/01-core-concepts.md)
**Advanced Workflow**: Complex patterns and edge cases → [Advanced Workflow](reference/02-advanced-workflow.md)
**API Reference**: Detailed function/method documentation → [API Reference](reference/03-api-reference.md)
```

### Reference File Template

```markdown
# <Topic Name>

## Contents
- Subsection 1
- Subsection 2
- Subsection 3

## Subsection 1
Content here...

## Subsection 2
Content here...
```

For reference files longer than 100 lines, include a table of contents at the top so the agent can see the full scope of available information even when previewing.

### Step 5: Write Output Files

Write SKILL.md (simple) or SKILL.md + reference/ (complex).

### Step 6: Validate

Run the validation checklist before considering the skill complete.

#### Contents
1. YAML Header Checks
2. Structure Checks
3. Content Checks
4. Script Checks (if applicable)

Run this checklist before considering the skill complete.

#### 1. YAML Header

- File starts with `---` on line 1
- Valid YAML block between first pair of `---` delimiters
- `name` present and matches directory name
- `name` matches regex `^[a-z0-9]+(-[a-z0-9]+)*$`
- `description` present (1-1024 characters)
- `license` is "MIT" (always — this is the skill file's license, not the upstream project's)
- `author` format: `Name <email@example.com>`
- `version` is non-empty and matches the upstream project's version string
- Header ends with `---` before main content

#### 2. Structure

- Directory name matches skill name
- SKILL.md exists
- If complex: `reference/` with zero-padded two-digit numbered files (`01-`, `02-`, … `10-`, `11-`)
- No nested `reference/` directories
- SKILL.md under 500 lines (if references exist)
- No `scripts/` or `assets/` unless explicitly requested by user
- All file paths use forward slashes (no backslashes)
- Reference files are one level deep from SKILL.md (no chained references)

#### 3. Content

- "Overview" section present
- "When to Use" with specific scenarios
- At least one code example (if applicable to the skill type)
- No hallucinated content — all from downloaded sources
- Content is concise — no over-explaining basics the agent already knows
- Consistent terminology throughout (one term per concept)
- No time-sensitive information (or placed in "old patterns" section)
- Single recommended approach given (not multiple options causing confusion)

#### 4. Scripts (if explicitly requested)

- Script paths use forward slashes
- Execution intent is clear ("Run" vs "See for reference")
- Scripts handle errors explicitly (no bare exceptions)
- All constants documented with justification
- Expected output format shown in SKILL.md
- No install instructions in scripts (only system-available tools)

### Step 7: Report

Report success with file tree and validation results.

### Step 8: Sync README

After **every** skill addition, deletion, rename, update, or YAML header edit, regenerate the README.md skills table:

```bash
bash .agents/skills/spm/scripts/gen-skills-table.sh [SKILLS_DIR] [README_PATH]
```

Arguments (both optional):
- `SKILLS_DIR` — path to the skills directory (default: `.agents/skills`)
- `README_PATH` — path to README.md to update (default: `README.md`)

This keeps the public skills index in sync with the actual `.agents/skills/` contents.

The script is a pure bash tool — no Python or external YAML parsers required. It extracts YAML headers from each SKILL.md, derives project names by stripping version suffixes, truncates descriptions to ~120 characters, and rewrites the Skills Table section in README.md.
