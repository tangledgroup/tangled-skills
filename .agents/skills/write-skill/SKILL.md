---
name: write-skill
description: Generate fine-grained agent skills from user requirements, creating complete spec-compliant markdown files that work across pi, opencode, claude, and codex platforms. Use when creating new skills or converting existing documentation into skill format.
version: "0.8.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - meta
  - meta-skill
  - skill-writing
  - skill-generation
  - automation
category: tooling
---

# write-skill — Generate Agent Skills

## Overview

Generates spec-compliant, cross-platform agent skills from user requirements. Takes project/tool name, version, and documentation sources (URLs or filesystem paths), then produces complete SKILL.md files that work on pi, opencode, Claude Code, and Codex platforms.

Skills are Markdown-only by default — no scripts or assets are generated unless the user explicitly requests them. If OS-level operations are needed, inline bash or Python with built-in modules is used instead.

**Conciseness principle:** Assume the consuming agent already knows basics (what PDFs are, how libraries work). Only add context the agent doesn't already have. Challenge each piece of information: "Does the agent really need this explanation?" The description field is critical for skill selection — it must include both WHAT and WHEN so the agent can pick the right skill from potentially 100+ available skills.

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
│   └── validate.py       # Validation script
└── assets/               # Only if explicitly requested
    └── example-config.yaml
```

**Script invocation:** When scripts exist, the skill must clearly state whether the agent should **execute** the script (preferred — "Run `python scripts/validate.py input.pdf`") or **read it as reference** ("See `scripts/validate.py` for the validation algorithm"). Scripts are executed via bash without loading their full contents into context — only output consumes tokens.

**Script quality rules:**
- Scripts must handle errors explicitly (never punt to the agent with bare exceptions)
- All constants must be documented with justification (no "voodoo numbers")
- Provide clear, specific error messages that help the agent fix issues
- Make execution intent unambiguous in instructions

### Progressive Disclosure Patterns

- **High-level guide with references**: SKILL.md provides quick-start examples, then links to detailed reference files for advanced features. Agent loads references only when needed.
- **Domain-specific organization**: For skills covering multiple domains, split by domain (e.g., `reference/finance.md`, `reference/sales.md`) so the agent loads only relevant context.
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

→ [Crawling Strategy](reference/01-crawling-strategy.md)

### Step 3: Analyze and Determine Structure

Assess collected content to decide simple vs complex output structure. Consider:
- Does the content have 2+ distinct subtopics? → complex
- Would an agent typically need only part of the skill per task? → complex
- Is it a single cohesive topic under 300 lines? → simple

### Step 4: Generate YAML Header

Create a valid YAML header with validated name, description, version, and metadata fields.

### Step 5: Write Output Files

Write SKILL.md (simple) or SKILL.md + reference/ (complex).

### Step 6: Validate

Run the validation checklist before considering the skill complete.

→ [Validation Checklist](reference/03-validation-checklist.md)

### Step 7: Report

Report success with file tree and validation results.

### Step 8: Sync README

After every skill addition, deletion, rename, or YAML header edit, regenerate the README skills table:

```bash
python3 scripts/gen-skills-table.py
```

This keeps the public skills index in sync with `.agents/skills/` contents.

## YAML Header Rules

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

### Field Rules

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

### Name Validation

```
^[a-z0-9]+(-[a-z0-9]+)*$
```

Valid: `pdf-processing`, `data-analysis`, `fastapi-0-115`
Invalid: `PDF-Processing`, `-pdf`, `pdf--processing`, `pdf processing`

### Version Field Rules

The `version` field records the upstream project's version — **preserve it as-is**. Do not force it into a specific format. Acceptable formats:

- **SemVer 2.0.0**: `1.2.3` (strict three-part `MAJOR.MINOR.PATCH`)
- **SemVer pre-release**: `1.0.0-alpha`, `1.0.0-beta.2`, `1.0.0-rc.1`
- **SemVer with build metadata**: `1.0.0+20130313144700` (ignored in precedence)
- **Date-based**: `2025-11-25`, `2026-04-16` (for specs, snapshots, documentation releases)
- **Two-part**: `0.16`, `0.5` (some projects only use `MAJOR.MINOR`)

When constructing the **directory name**, hyphenate version components: `project-1-2-3`, `project-0-16`, `project-2025-11-25`. The `name` field in YAML must match the directory name exactly.

### Description Formula

Construct descriptions using this pattern:

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

## Output File Templates

### SKILL.md Template

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

### Degrees of Freedom

Match the level of instruction specificity to the task's fragility:

- **High freedom** (text-based instructions): Use when multiple approaches are valid and decisions depend on context. Example: "Analyze the code structure and suggest improvements."
- **Medium freedom** (pseudocode or scripts with parameters): Use when a preferred pattern exists but some variation is acceptable. Example: provide a template function with configurable parameters.
- **Low freedom** (specific scripts, few or no parameters): Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed. Example: "Run exactly this command: `python scripts/migrate.py --verify --backup`. Do not modify the command."

### Workflow Patterns

For complex multi-step tasks, provide checklists the agent can copy and track:

```markdown
## Task workflow

Copy this checklist and track your progress:

```
Task Progress:
- [ ] Step 1: Analyze input (run analyze.py)
- [ ] Step 2: Create plan file
- [ ] Step 3: Validate plan (run validate.py)
- [ ] Step 4: Execute changes
- [ ] Step 5: Verify output (run verify.py)
```

**Step 1: Analyze input**

Run: `python scripts/analyze.py input.pdf`

This extracts fields and saves to `fields.json`.
```

For quality-critical tasks, implement feedback loops: run validator → fix errors → repeat. Only proceed when validation passes.

## Advanced Topics

**Crawling Strategy**: URL and filesystem crawling rules, cycle prevention, analyzable extensions → [Crawling Strategy](reference/01-crawling-strategy.md)

**Output Constraints**: Markdown-only default, opt-in scripts/assets, tool preference hierarchy with `uv`/`uvx`, inline examples → [Output Constraints](reference/02-output-constraints.md)

**Validation Checklist**: YAML header checks, structure checks, content checks, script checks → [Validation Checklist](reference/03-validation-checklist.md)

**Behavioral Guidelines**: Think before coding, simplicity first, surgical changes, no external dependencies, conciseness rules → [Behavioral Guidelines](reference/04-behavioral-guidelines.md)
