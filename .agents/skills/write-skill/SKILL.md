---
name: write-skill
description: Generate fine-grained agent skills from user requirements, creating complete spec-compliant markdown files that work across pi, opencode, claude, and codex platforms. Use when creating new skills or converting existing documentation into skill format.
version: "0.6.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - skill-generation
  - automation
  - meta-skill
category: tooling
external_references:
  - url: https://opencode.ai/docs/skills
    description: OpenCode skills documentation and specification
  - url: https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/skills.md
    description: pi-mono agent skills implementation and format details
  - url: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
    description: Claude agent skills best practices and guidelines
  - url: https://developers.openai.com/codex/skills
    description: OpenAI Codex skills documentation
---

# write-skill

A meta-skill that generates other agent skills by analyzing user requirements and creating complete, spec-compliant markdown files. Skills use standard agent tools (read, write, edit, bash) to perform their tasks.

## When to Use

Load this skill when:
- User asks to "create a skill" or "generate a skill" for a specific task/domain
- User provides URLs to documentation that should be analyzed
- User wants to extract workflows from existing codebases/projects
- User describes complex requirements that should become a reusable skill
- Quick skill bootstrapping from minimal descriptions is needed

## Quick Start

### From Minimal Prompt

```
User: "Create a skill for managing Docker containers"

Workflow:
1. Check available tools (bash/curl preferred)
2. Fetch documentation via curl
3. Extract commands and patterns
4. Generate validated skill
5. Present for review
```

See [Interaction Examples](references/08-interaction-examples.md) for detailed walkthroughs.

### From Documentation URLs

```
User: "Create a skill for GitHub Actions. Check https://docs.github.com/en/actions"

Workflow:
1. Extract base domain (docs.github.com)
2. Run BFS crawl to discover all related pages
3. Deep dive with DFS on key sections
4. Convert HTML to Markdown
5. Generate comprehensive skill with references/
```

See [URL Crawling Strategies](references/02-url-crawling.md) for crawling scripts.

### From Directory Analysis

```
User: "Create a skill for the deployment workflow. Analyze ./infra"

Workflow:
1. Scan directory structure with find/grep
2. Discover configs, scripts, env vars
3. Extract patterns and workflows
4. Generate skill with discovered requirements
5. Run git introspection (if repository exists)
6. Identify most important files from git history
7. Refine skill based on file importance
```

See [Directory Analysis](references/05-directory-analysis.md) for scanning patterns.
See [Git Introspection](references/04-git-introspection.md) for post-analysis enhancement.

## Core Workflow

### Step 1: Tool Detection

Check for available tools before processing:

```bash
# Primary method (preferred)
curl --version

# Optional enhancement tools
command -v pandoc        # HTML → Markdown conversion
command -v pdftotext     # PDF text extraction (best quality)
command -v gs            # PDF fallback
```

**Fallback hierarchy:**
1. bash/curl for web fetching and file operations
2. web_search/web_fetch tools if available
3. read tool for local files
4. write tool for creating skill files

See [Tool Detection](references/01-tool-detection.md) for complete detection logic.

### Step 2: Content Research

**For URLs:** Use hybrid BFS+DFS crawling to discover documentation comprehensively.

**For PDFs:** Extract text with layout preservation using best available method.

**For Directories:** 
1. **Directory scanning first** - Discover configs, scripts, env vars, and dependencies
2. **Extract patterns** - Identify workflows and requirements from content
3. **Git introspection** (if repository exists) - Enhance understanding with file importance
4. **Read priority files** - Focus on most modified/recently changed files

See [Directory Analysis](references/05-directory-analysis.md) for scanning patterns.
See [Git Introspection](references/04-git-introspection.md) for post-analysis enhancement.
See [Content Extraction](references/03-content-extraction.md) for processing workflows.

### Step 3: Skill Structure Selection

Auto-detect whether to create **simple** or **complex** skill:

| Criteria | Simple Skill | Complex Skill |
|----------|--------------|---------------|
| Line count | < 500 lines in SKILL.md | > 500 lines in SKILL.md |
| Topics | Single focused task | Multiple topics (3+) |
| Structure | Single SKILL.md | SKILL.md + references/ |
| Use case | One specific workflow | APIs, frameworks, extensive docs |

**When to use reference files:**
- SKILL.md approaches 500 lines
- User explicitly requests reference files
- User indicates the skill is complex with many topics

See [Skill Templates](references/06-skill-templates.md) for structure details.

### Step 4: Validation

Run validation checklist before finalizing:

- ✅ `name` passes regex: `^[a-z0-9]+(-[a-z0-9]+)*$`
- ✅ `description` is 1-1024 characters
- ✅ Structure matches type (simple vs complex)
- ✅ Relative links resolve correctly
- ✅ Code snippets complete and valid

See [Validation Checklist](references/07-validation-checklist.md) for complete requirements.

## Reference Files

### Core Workflows

- [`references/01-tool-detection.md`](references/01-tool-detection.md) - Tool detection, negotiation, and fallback strategies
- [`references/02-url-crawling.md`](references/02-url-crawling.md) - BFS, DFS, and hybrid crawling scripts for documentation discovery
- [`references/03-content-extraction.md`](references/03-content-extraction.md) - PDF processing, HTML conversion, content extraction patterns
- [`references/04-git-introspection.md`](references/04-git-introspection.md) - Git-based codebase analysis before reading files
- [`references/05-directory-analysis.md`](references/05-directory-analysis.md) - Directory scanning, pattern detection, auto-detection heuristics

### Templates and Validation

- [`references/06-skill-templates.md`](references/06-skill-templates.md) - Simple and complex skill templates, frontmatter requirements
- [`references/07-validation-checklist.md`](references/07-validation-checklist.md) - Complete validation requirements and cross-platform notes
- [`references/08-interaction-examples.md`](references/08-interaction-examples.md) - Detailed examples with expected outputs

## Output Structure

Generated skills are created in `.agents/skills/<skill-name>/`:

**Simple skills (SKILL.md < 500 lines):**
```
my-skill/
└── SKILL.md              # All content inline, no references directory
```

**Complex skills (SKILL.md > 500 lines):**
```
my-skill/
├── SKILL.md              # Overview + navigation hub (under 500 lines)
└── references/           # Flat structure only, no nested references
    ├── 01-core-concepts.md
    ├── 02-advanced-workflow.md
    └── 03-api-reference.md
```

**Note:** Reference files can exceed 500 lines if needed. Only SKILL.md should stay under 500 lines.

## Important Notes

1. **Check tools first** - Test available tools (bash/curl preferred), don't ask user
2. **Prefer bash/curl** - Primary method for web fetching and file operations
3. **Respect rate limits** - Add delays between URL requests, check robots.txt
4. **Validate output** - Run checklist before presenting generated skill
5. **Auto-detect structure** - Use single-file for < 500 lines, multi-file for > 500 lines
6. **User review** - Always present generated skill for approval before writing
7. **Flat reference structure** - No nested references (all refs one level deep from SKILL.md)
8. **Numbered reference files** - Use 2-digit prefixes (`01-`, `02-`, `03-`) for consistent ordering
9. **Cross-platform compatible** - Generate skills for pi, opencode, claude, and codex
10. **external_references field** - Include only user-provided starting URLs, not all crawled pages
11. **Markdown-only skills** - Skills use agent tools (read, write, edit, bash), no bundled scripts/assets required
12. **Clear descriptions** - Write specific descriptions for proper skill matching across platforms

## Cross-Platform Compatibility

Generated skills work across these platforms:

| Platform | Validation | Notes |
|----------|-----------|-------|
| **pi** | Lenient | Warns on violations but loads skill |
| **opencode** | Strict | Missing `description` prevents loading |
| **claude** | Strict | Rejects invalid frontmatter |
| **codex** | Strict | Requires valid name and description |
| **hermes** | Flexible | Supports platform filtering and env passthrough |

### Required Fields (All Platforms)

- `name`: 1-64 chars, lowercase alphanumeric with hyphens (`^[a-z0-9]+(-[a-z0-9]+)*$`)
- `description`: 1-1024 characters, specific enough for proper skill matching

### Optional Fields (Union Across Platforms)

- `license` (pi, opencode)
- `compatibility` (pi, opencode)
- `metadata` - string-to-string map (pi, opencode)
- `allowed-tools` (pi - experimental)
- `disable-model-invocation` (pi)
- `agents/openai.yaml` for codex UI metadata and policy

See [Validation Checklist](references/07-validation-checklist.md) for detailed requirements.

## Limitations

- Tool availability depends on agent configuration (bash/curl assumed available)
- Generated skills should be tested before production use
- Skills are markdown-only by default (use agent tools for execution)
- **Name validation** - Must match regex `^[a-z0-9]+(-[a-z0-9]+)*$`
- **Description length** - Must be 1-1024 characters

## Optional Tools for Enhanced Processing

Install these tools for better content processing:

| Tool | Purpose | Install Commands |
|------|---------|------------------|
| **pandoc** or **pandoc-bin** | HTML → Markdown with structure preservation | Debian/Ubuntu: `apt install pandoc`<br>Arch: `pacman -S pandoc`<br>macOS: `brew install pandoc`<br>Nix: `nix-shell -p pandoc`<br>Docker: `docker run pandoc/core`<br>Podman: `podman run docker.io/pandoc/core` |
| **poppler-utils** (pdftotext) | Best quality PDF text extraction with layout | Debian/Ubuntu: `apt install poppler-utils`<br>Arch: `pacman -S poppler`<br>macOS: `brew install poppler`<br>Nix: `nix-shell -p poppler`<br>Docker: `docker run minidocks/poppler`<br>Podman: `podman run docker.io/minidocks/poppler` |
| **ghostscript** (gs) | Alternative PDF processor | Debian/Ubuntu: `apt install ghostscript`<br>Arch: `pacman -S ghostscript`<br>macOS: `brew install ghostscript`<br>Nix: `nix-shell -p ghostscript`<br>Docker: `docker run minidocks/ghostscript`<br>Podman: `podman run docker.io/minidocks/ghostscript` |

**NixOS users:** Add to `/etc/nixos/configuration.nix`:
```nix
environment.systemPackages = with pkgs; [ pandoc poppler ghostscript ];
```

Without these tools, the skill uses basic text extraction which may lose formatting but remains functional.

See [Tool Detection](references/01-tool-detection.md) for installation details and benefits.


