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
│   └── validate.sh
└── assets/               # Only if explicitly requested
    └── example-config.yaml
```

### Complexity Decision

While analyzing content, estimate total output lines:
- `< 500` → simple (single SKILL.md)
- `≥ 500` → complex (SKILL.md + reference/)

Split into references when:
- Total expected output exceeds ~500 lines
- Content naturally falls into distinct topics
- Dense reference material benefits from progressive disclosure

## Generation Workflow

### Step 1: Validate Input

Check that the skill name matches `^[a-z0-9]+(-[a-z0-9]+)*$` and version follows SemVer 2.0.0 format (`MAJOR.MINOR.PATCH`).

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
version: "<semver>"
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
| `license` | No | License name (default: MIT) |
| `author` | No | Format: `Name <email@example.com>` |
| `version` | No | SemVer 2.0.0 format |
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

### SemVer 2.0.0 Rules

- Format: `MAJOR.MINOR.PATCH` (e.g., `1.0.0`)
- Pre-release: `1.0.0-alpha`, `1.0.0-beta.2`, `1.0.0-rc.1`
- Build metadata: `1.0.0+20130313144700` (ignored in precedence)
- MAJOR: backward incompatible changes
- MINOR: backward compatible additions
- PATCH: backward compatible fixes
- No leading zeros in numeric identifiers

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
version: "<semver>"
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

## <Subsection>
Content here...

## <Subsection>
Content here...
```

## Output Constraints

### Default: Markdown-Only

By default, generated skills contain only Markdown files:
- `SKILL.md` (always)
- `reference/*.md` (optional, for complex skills)

Do **not** generate `scripts/` or `assets/` directories on your own initiative.

### Opt-In: Scripts and Assets

Only create `scripts/` or `assets/` when the user explicitly requests them (e.g., "include a validation script", "add example config files"). If you think they would be useful, suggest it to the user first and wait for confirmation — never generate them proactively.

Even when scripts or assets are requested, generated skills must never instruct installing packages (`pip`, `npm`, `cargo`, etc.). Use only tools already available on the system.

### Tool Preference Hierarchy

1. **Bash first** — file manipulation, validation, parsing, YAML checks, directory operations, URL fetching with `curl`, text processing with `sed`/`awk`/`grep`
2. **Python stdlib only** — use when Bash is awkward (JSON parsing, complex string manipulation, SemVer validation). Only standard library modules: `json`, `pathlib`, `urllib`, `re`, `hashlib`, etc.
3. **System tools** — `pandoc` for HTML→Markdown conversion, `pdftotext`/`gs` for PDFs, `jq` for JSON processing

### Inline Bash Examples

Bash scripts are preferred for validation and file operations. Write them inline where the skill needs to perform checks.

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
- [ ] `license` is "MIT"
- [ ] `author` format: `Name <email@example.com>`
- [ ] `version` follows SemVer 2.0.0
- [ ] Header ends with `---` before main content

### Structure
- [ ] Directory name matches skill name
- [ ] SKILL.md exists
- [ ] If complex: `reference/` with numbered files (`01-`, `02-`, etc.)
- [ ] No nested `reference/` directories
- [ ] SKILL.md under 500 lines (if references exist)
- [ ] No `scripts/` or `assets/` unless explicitly requested by user

### Content
- [ ] "Overview" section present
- [ ] "When to Use" with specific scenarios
- [ ] At least one code example (if applicable to the skill type)
- [ ] No hallucinated content — all from downloaded sources

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
