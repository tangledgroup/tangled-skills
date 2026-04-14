---
name: write-skill
description: Generate fine-grained agent skills from minimal prompts, complex requirements, URL documentation crawling, git introspection, and directory analysis. Researches and creates complete, spec-compliant skills using available tools.
version: "0.5.2"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - skill-generation
  - automation
  - meta-skill
  - documentation-crawling
  - content-extraction
  - git-introspection
category: tooling
external_references:
  - url: https://docs.example.com
    description: Official documentation for the target tool or framework
  - url: https://github.com/example/repo
    description: GitHub repository with source code and examples
  - url: https://piechowski.io/post/git-commands-before-reading-code/
    description: Git introspection techniques for understanding codebases before reading files
---

# write-skill

A meta-skill that generates other agent skills by analyzing user requirements, crawling documentation URLs, and examining codebases with git introspection. Uses available tools to research and create complete, spec-compliant skills.

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
| Line count | < 400 lines | > 400 lines |
| Topics | Single focused task | Multiple topics |
| Structure | Single SKILL.md | SKILL.md + references/ |
| Use case | One specific workflow | APIs, frameworks, extensive docs |

See [Skill Templates](references/06-skill-templates.md) for structure details.

### Step 4: Validation

Run validation checklist before finalizing:

- ✅ Frontmatter complete (name, description, version, etc.)
- ✅ Third-person throughout document
- ✅ No XML tags in frontmatter values
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

**Simple skills (< 400 lines):**
```
my-skill/
└── SKILL.md              # All content inline, no references directory
```

**Complex skills (> 400 lines):**
```
my-skill/
├── SKILL.md              # Overview + navigation hub (under 500 lines)
└── references/           # Extracted documentation only
    ├── 01-core-concepts.md
    ├── 02-advanced-workflow.md
    └── 03-api-reference.md
```

## Important Notes

1. **Check tools first** - Test available tools (bash/curl preferred), don't ask user
2. **Prefer bash/curl** - Primary method for web fetching and file operations
3. **Respect rate limits** - Add delays between URL requests, check robots.txt
4. **Validate output** - Run checklist before presenting generated skill
5. **Auto-detect structure** - Use single-file for < 400 lines, multi-file for > 400 lines
6. **User review** - Always present generated skill for approval before writing
7. **Third-person descriptions** - Required throughout (Claude compatibility)
8. **No XML in frontmatter** - Never include XML tags in YAML values
9. **Numbered reference files** - Use 2-digit prefixes (`01-`, `02-`, `03-`) for consistent ordering
10. **Cross-platform compatible** - Generate skills for pi, opencode, claude, and hermes
11. **external_references field** - Include only user-provided starting URLs, not all crawled pages
12. **Directory analysis then git** - Scan directory structure first, then use git introspection to validate and prioritize content

## Cross-Platform Compatibility

Generated skills work across these platforms:

| Platform | Validation | Notes |
|----------|-----------|-------|
| **pi** | Lenient | Warns on violations but loads skill |
| **opencode** | Strict | Missing `description` prevents loading |
| **claude** | Strict | Requires third-person, rejects XML in frontmatter |
| **hermes** | Flexible | Supports platform filtering and env passthrough |

See [Validation Checklist](references/07-validation-checklist.md) for detailed requirements.

## Limitations

- Tool availability depends on agent configuration (bash/curl assumed available)
- URL crawling depth limited by time/bandwidth preferences
- Directory analysis limited to files user allows reading
- Cannot execute discovered scripts, only analyze and reference them
- Generated skills should be tested before production use
- **HTML conversion quality** - Best with pandoc/pandoc-bin; basic extraction used otherwise
- **PDF extraction quality** - Best with poppler-utils (pdftotext -layout); ghostscript provides fallback
- **Git introspection** - Requires git repository; falls back to directory analysis for non-git projects

## Optional Tools for Enhanced Processing

Install these tools for better content processing:

| Tool | Purpose | Install Command |
|------|---------|-----------------|
| **pandoc** or **pandoc-bin** | HTML → Markdown with structure preservation | `apt install pandoc` or `brew install pandoc` |
| **poppler-utils** (pdftotext) | Best quality PDF text extraction with layout | `apt install poppler-utils` or `brew install poppler` |
| **ghostscript** (gs) | Alternative PDF processor | `apt install ghostscript` or `brew install ghostscript` |

Without these tools, the skill uses basic text extraction which may lose formatting but remains functional.

See [Tool Detection](references/01-tool-detection.md) for installation details and benefits.
