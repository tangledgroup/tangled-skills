---
name: write-skill
description: Generate fine-grained agent skills from user requirements, creating complete spec-compliant markdown files that work across pi, opencode, claude, and codex platforms. Use when creating new skills or converting existing documentation into skill format.
version: "0.7.1"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - skill-writing
  - skill-generation
  - meta-skill
  - automation
category: tooling
---

# write-skill — Generate Agent Skills

## Overview

Generates spec-compliant, cross-platform agent skills from user requirements. Takes project/tool name, version, and documentation sources (URLs or filesystem paths), then produces complete SKILL.md files that work on pi, opencode, Claude Code, and Codex platforms.

Skills are Markdown-only — no scripts or assets. If OS-level operations are needed, inline bash or Python with built-in modules is used instead.

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
└── references/           # Flat structure, numbered files
    ├── 01-core-concepts.md
    └── 02-advanced-topics.md
```

### Complexity Decision

While analyzing content, estimate total output lines:
- `< 500` → simple (single SKILL.md)
- `≥ 500` → complex (SKILL.md + references/)

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

Write SKILL.md (simple) or SKILL.md + references/ (complex).

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

## Installation / Setup

How to install or set up the tool (if applicable).

## Usage Examples

Common patterns and code examples. Include copy-pasteable code blocks with language tags.

## Advanced Topics

Deeper topics. For complex skills, link to reference files:
- [Reference: Core Concepts](references/01-core-concepts.md)

## References

- Official documentation: <URL>
- GitHub repository: <URL>
```

### Reference File Template

```markdown
# <Topic Name>

> **Source:** <original URL or document name>
> **Loaded from:** SKILL.md (via progressive disclosure)

## <Subsection>
Content here...
```

## Skills Are Markdown-Only

No `scripts/` or `assets/` directories. If a skill needs to perform operations:

- **Bash** for OS-level commands (file manipulation, package installation)
- **Python with built-in modules** for other scripting (no external packages)

Example inline guidance:

```markdown
To install dependencies:
```bash
pip install requests
```

To process a file:
```python
import json
with open("data.json") as f:
    data = json.load(f)
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
- [ ] If complex: `references/` with numbered files (`01-`, `02-`, etc.)
- [ ] No nested `references/` directories
- [ ] SKILL.md under 500 lines (if references exist)

### Content
- [ ] "Overview" section present
- [ ] "When to Use" with specific scenarios
- [ ] At least one code example
- [ ] "References" with official documentation URLs
- [ ] No hallucinated content — all from downloaded sources

## Behavioral Guidelines (Karpathy)

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
3. Check structure → verify: references/ numbered correctly
```

## References

- SemVer 2.0.0: https://semver.org
- Agent Skills Standard: https://agentskills.io/specification
- pi-mono skills spec: https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/skills.md
- OpenCode skills: https://opencode.ai/docs/skills
- Pandoc manual: https://man.archlinux.org/man/pandoc.1
- pdftotext manual: https://man.archlinux.org/man/pdftotext.1.en
- Ghostscript manual: https://man.archlinux.org/man/gs.1.en
