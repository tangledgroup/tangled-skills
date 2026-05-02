---
name: write-skill
description: Generate fine-grained agent skills from user requirements, creating complete spec-compliant markdown files that work across pi, opencode, claude, and codex platforms. Use when creating new skills or converting existing documentation into skill format.
version: "0.7.3"
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
- Any task that requires producing spec-compliant `.agents/skills/<name>/SKILL.md` files

## Core Concepts

### Source Types

The user provides at least one source:

- **URLs** — HTTP(S) links to web pages, documentation, or raw files
- **Filesystem paths** — absolute or relative paths to directories or files
- **Mixed** — combination of both

### Output Structure

Generated skills are created in `.agents/skills/<skill-name>/`:

**Simple skill** (SKILL.md < 500 lines):
```
my-skill/
└── SKILL.md              # All content inline
```

**Complex skill** (SKILL.md > 500 lines):
```
my-skill/
├── SKILL.md              # Overview + navigation hub
└── reference/           # Flat structure, numbered files
    ├── 01-core-concepts.md
    └── 02-advanced-topics.md
```

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

### Complexity Decision

While analyzing content, estimate total output lines:
- `< 500` → simple (single SKILL.md)
- `≥ 500` → complex (SKILL.md + reference/)

Split into references when:
- Total expected output exceeds ~500 lines
- Content naturally falls into distinct topics
- Dense reference material benefits from progressive disclosure

**Progressive disclosure patterns:**

- **High-level guide with references**: SKILL.md provides quick-start examples, then links to detailed reference files for advanced features. Agent loads references only when needed.
- **Domain-specific organization**: For skills covering multiple domains, split by domain (e.g., `reference/finance.md`, `reference/sales.md`) so the agent loads only relevant context.
- **Conditional details**: Show basic content in SKILL.md, link to advanced content that the agent reads conditionally based on the task.

**Keep references one level deep from SKILL.md.** All reference files should link directly from SKILL.md. Never chain references (reference → reference → reference) — this causes incomplete information loading.

## Generation Workflow

### Step 1: Validate Input

Check that the skill name matches `^[a-z0-9]+(-[a-z0-9]+)*$` and version is a non-empty string matching the upstream project's versioning scheme (SemVer, date-based, two-part, or pre-release).

### Step 2: Crawl and Collect Content

Follow the crawling strategy below to gather all source material.

### Step 3: Analyze and Determine Structure

Assess collected content to decide simple vs complex output structure.

### Step 4: Generate YAML Header

Create a valid YAML header with validated name, description, version, and metadata fields.

### Step 5: Write Output Files

Write SKILL.md (simple) or SKILL.md + reference/ (complex).

### Step 6: Validate

Run the validation checklist before considering the skill complete.

### Step 7: Report

Report success with file tree and validation results.

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

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | 1-64 chars, regex `^[a-z0-9]+(-[a-z0-9]+)*$`, matches directory name |
| `description` | Yes | 1-1024 chars, third person, includes WHAT and WHEN |
| `license` | No | **Always MIT** — this is the skill file's license, never the upstream project's |
| `author` | No | Format: `Name <email@example.com>` |
| `version` | No | Non-empty string — preserve upstream version as-is (SemVer, date, two-part, pre-release) |
| `tags` | No | Array of string tags |
| `category` | No | Skill category classification |
| `external_references` | No | User-provided starting URLs only |
| `compatibility` | No | Max 500 chars, environment requirements |
| `metadata` | No | String-to-string map |
| `allowed-tools` | No | Pre-approved tools (experimental, pi only) |
| `disable-model-invocation` | No | Hidden from system prompt (pi only) |

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

### Description Best Practices

```yaml
# Good — specific, third person, includes WHAT and WHEN
description: Extracts text and tables from PDF files and merges multiple PDFs. Use when working with PDF documents.

# Poor — too vague
description: Helps with PDFs.
```

## Crawling Strategy

When sources are provided (URLs or filesystem paths), recursively crawl by default unless the user specifies otherwise.

### URL Crawling

Recursively follow all links within the same domain and subdomains:

1. Fetch and parse the initial URL
2. Extract all relative links from the page
3. For each link, check if it resolves to the same domain or subdomain:
   - Same domain (`example.com`) → include
   - Subdomain (`api.example.com`) → include
   - Different domain (`other.com`) → skip, note as external
4. Fetch each included URL using the appropriate tool
5. Repeat for every fetched page (depth-first)
6. Track visited URLs to prevent cycles

**Domain matching:** Base domain strips `www.` prefix. Include subdomains; exclude different domains. Do not follow login pages, auth flows, or authenticated API endpoints.

**Cycle prevention:**
- Maintain a visited URL set
- Skip already-visited URLs
- Maximum depth: 5 levels from initial URL
- Maximum pages: 50 per crawl

### Filesystem Path Crawling

Recursively visit all files and directories:

1. Read the initial path (file or directory)
2. If file → analyze content directly
3. If directory → list entries
4. For each entry:
   - Directory → recurse
   - File → check analyzable extension, then read
5. Repeat for all nested directories

**Analyzable extensions:**

| Category | Extensions | Tool |
|----------|-----------|------|
| Markdown | `.md`, `.markdown`, `.mkd` | Direct read |
| Text/Code | `.txt`, `.rst`, `.adoc` | Direct read |
| HTML | `.html`, `.htm` | `pandoc -f html -t markdown`, fallback raw |
| PDF | `.pdf` | `pdftotext -layout` or `gs` |
| Config | `.yaml`, `.yml`, `.json`, `.toml`, `.ini`, `.cfg` | Direct read |
| Scripts | `.sh`, `.bash`, `.py`, `.c`, `.h`, `.cpp`, `.rs`, `.go`, `.js`, `.ts` | Direct read |
| Man pages | `.1`–`.9` | Direct read |

**Skip rules:**
- Binary files (`.png`, `.jpg`, `.gif`, `.zip`, `.tar`, `.gz`, `.whl`, `.pyc`, `.so`, `.dll`, `.exe`)
- Hidden files/directories (`.` prefix) unless explicitly requested
- Version control dirs (`.git/`, `.svn/`, `.hg/`) always
- **Do not skip by size** — large files may be complex text documents

### Mixed Sources

When both URLs and filesystem paths are provided:
1. Process independently in parallel
2. Merge collected content, deduplicating by URL or path
3. Prefer the most specific/authoritative source on overlap
4. Note external links encountered (skipped per domain rules)

### Custom Instructions Override

Default recursive crawling can be overridden:

```
"Just analyze this one page" → skip recursion
"Only look at src/ and docs/" → apply path filters
"Follow 3 pages max" → override depth/limit
```

Always prioritize user instructions. Document any deviations from default behavior.

## URL Handling Tools

| Type | Tool | Output |
|------|------|--------|
| `.md` (GitHub raw) | `curl -sL` | Parse Markdown |
| Man pages (`.en`) | `curl -sL` | Extract text |
| PDF (`.pdf`) | `pdftotext -layout` or `gs` | Rendered text |
| Static HTML | `pandoc -f html -t markdown` first, fallback raw | Clean Markdown |
| SPA-rendered | Note limitation | Available text only |

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

## Output Constraints

### Default: Markdown-Only

By default, generated skills contain only Markdown files:
- `SKILL.md` (always)
- `reference/*.md` (optional, for complex skills)

Do **not** generate `scripts/` or `assets/` directories on your own initiative.

### Opt-In: Scripts and Assets

Only create `scripts/` or `assets/` when the user explicitly requests them (e.g., "include a validation script", "add example config files"). If you think they would be useful, suggest it to the user first and wait for confirmation — never generate them proactively.

Even when scripts or assets are requested, generated skills must never instruct installing packages (`pip`, `npm`, `cargo`, etc.). Use only tools already available on the system.

**Script invocation in generated skills:**

When a skill includes scripts, the SKILL.md must show how to execute them using bash. Scripts are run from the skill directory, so paths are relative to the skill root:

```
## Utility scripts

**validate.py**: Check configuration for errors

```bash
python scripts/validate.py config.yaml
# Returns: "OK" or lists specific errors with line numbers
```

**analyze.py**: Extract metadata from input files

```bash
python scripts/analyze.py input.pdf > metadata.json
```
```

- Always use forward slashes in paths (`scripts/helper.py`), never backslashes
- State clearly whether the agent should **execute** the script or **read it as reference**
- Show expected output format so the agent knows what to expect
- Scripts must handle errors explicitly — never bare `except:` or unhandled exceptions
- Document all magic numbers/constants with justification comments

### Tool Preference Hierarchy

1. **Bash first** — file manipulation, validation, parsing, YAML checks, directory operations, URL fetching with `curl`, text processing with `sed`/`awk`/`grep`
2. **Python stdlib only** — use when Bash is awkward (JSON parsing, complex string manipulation, version validation). Only standard library modules: `json`, `pathlib`, `urllib`, `re`, `hashlib`, etc.
3. **System tools** — `pandoc` for HTML→Markdown conversion, `pdftotext`/`gs` for PDFs, `jq` for JSON processing

### Inline Bash Examples

Bash scripts are preferred for validation and file operations. Write them inline where the skill needs to perform checks. Scripts execute via bash — they are not loaded into context, only their output consumes tokens.

To validate a YAML header:
```bash
yaml_block=$(sed -n '1,/^---$/p' SKILL.md | sed '1d;$d')

if [ -z "$yaml_block" ]; then
    echo "✗ Invalid (no YAML block)"
else
    echo "✓ Valid"
fi
```

To count lines in a skill:
```bash
wc -l SKILL.md | awk '{print $1}'
```

To execute a skill script (when scripts are requested):
```bash
python scripts/validate.py input.pdf
# Output: "OK" or specific error messages with line numbers
```

**Key principle:** Scripts should solve problems, not punt to the agent. Handle errors explicitly and provide specific, actionable error messages.

### Inline Python Examples

Use Python stdlib only when Bash is impractical:

```python
import json, pathlib

# Read and parse JSON data
with open("data.json") as f:
    data = json.load(f)

# List all .md files in a directory
for p in pathlib.Path(".").rglob("*.md"):
    print(p)
```

## Validation Checklist

### YAML Header
- [ ] File starts with `---` on line 1
- [ ] Valid YAML block between first pair of `---` delimiters
- [ ] `name` present and matches directory name
- [ ] `name` matches regex `^[a-z0-9]+(-[a-z0-9]+)*$`
- [ ] `description` present (1-1024 characters)
- [ ] `license` is "MIT" (always — this is the skill file's license, not the upstream project's)
- [ ] `author` format: `Name <email@example.com>`
- [ ] `version` is non-empty and matches the upstream project's version string
- [ ] Header ends with `---` before main content

### Structure
- [ ] Directory name matches skill name
- [ ] SKILL.md exists
- [ ] If complex: `reference/` with zero-padded two-digit numbered files (`01-`, `02-`, … `10-`, `11-`)
- [ ] No nested `reference/` directories
- [ ] SKILL.md under 500 lines (if references exist)
- [ ] No `scripts/` or `assets/` unless explicitly requested by user
- [ ] All file paths use forward slashes (no backslashes)
- [ ] Reference files are one level deep from SKILL.md (no chained references)

### Content
- [ ] "Overview" section present
- [ ] "When to Use" with specific scenarios
- [ ] At least one code example (if applicable to the skill type)
- [ ] No hallucinated content — all from downloaded sources
- [ ] Content is concise — no over-explaining basics the agent already knows
- [ ] Consistent terminology throughout (one term per concept)
- [ ] No time-sensitive information (or placed in "old patterns" section)
- [ ] Single recommended approach given (not multiple options causing confusion)

### Scripts (if explicitly requested)
- [ ] Script paths use forward slashes
- [ ] Execution intent is clear ("Run" vs "See for reference")
- [ ] Scripts handle errors explicitly (no bare exceptions)
- [ ] All constants documented with justification
- [ ] Expected output format shown in SKILL.md
- [ ] No install instructions in scripts (only system-available tools)

## Behavioral Guidelines

### Think Before Coding
- State assumptions explicitly
- Present multiple interpretations if they exist
- Push back if the request is too vague or conflicts with existing skills

### Simplicity First
- Minimum content that solves the problem
- No abstractions for single-use code
- If a simpler approach exists, use it

### Surgical Changes
- Don't modify unrelated skills when adding/updating one
- Match existing repository style
- Mention dead code in other files — don't delete it

### Goal-Driven Execution
Define success criteria before generating:
```
1. Generate SKILL.md → verify: YAML parses, name matches directory
2. Validate content → verify: all required sections present
3. Check structure → verify: reference/ numbered correctly
```

### No Proactive Asset Generation
- Never generate `scripts/` or `assets/` on your own initiative
- Only create them when the user explicitly requests them (e.g., "include scripts", "add assets")
- If you think they would be useful, suggest it to the user first and wait for confirmation

### No External Dependencies
- Never instruct installing packages (`pip install`, `npm install`, `cargo install`, etc.)
- Use only tools available on the system: `bash`, `python3`, `curl`, `jq`, `pandoc`, `pdftotext`, `gs`, `grep`, `sed`, `awk`
- This applies even when scripts or assets are explicitly requested
- If a required tool is missing, note it rather than generating install instructions

### Prefer Simple References Over Tables
- **Do not use markdown tables unless nothing else fits better.** This is the default, not an exception.
- Reference file links must use simple text references: `[Core Concepts](reference/01-core-concepts.md)`
- Express examples, concepts, and guidance as prose, lists, or code blocks — tables are the last resort
- YAML field rules are acceptable as a table since each row is a key-value pair with no simpler alternative
- Extension mappings are acceptable as a table when listing many file types concisely

### Conciseness and Clarity
- Assume the consuming agent already knows fundamentals (what PDFs are, how libraries work)
- Only add context the agent doesn't already have — challenge each paragraph's token cost
- Use consistent terminology throughout (one term per concept, never mix synonyms)
- Avoid time-sensitive information; use "old patterns" collapsible sections for legacy content
- Provide a single recommended approach with an escape hatch, not a list of alternatives
- All file paths use forward slashes (`scripts/helper.py`), never backslashes
- Keep references one level deep from SKILL.md — no chained references
