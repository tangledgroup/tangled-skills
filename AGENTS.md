# Agent Guidelines for Tangled Skills

This document provides guidance for AI agents working with the tangled-skills repository.

## Repository Structure

```
tangled-skills/
├── .agents/skills/
│   ├── <skill-name>/
│   │   ├── SKILL.md          # Main skill file (required, must include YAML header)
│   │   └── references/       # Optional reference files (flat structure, numbered)
│   │       ├── 01-topic-name.md
│   │       └── 02-another-topic.md
├── README.md                 # Skills table and overview
└── AGENTS.md                 # This file
```

## How Skills Are Written

### 1. Skill Name Convention

Skills follow the naming pattern: `<project>-<version>` or `<category>-<identifier>`

Examples:
- `uv-0-11-6` → Project: uv, Version: 0.11.6
- `aiohttp-3-13` → Project: aiohttp, Version: 3.13
- `git` → Standalone project without version
- `write-skill` → Meta-skill for generating other skills

### 2. Main Skill File (SKILL.md)

Each skill has a `SKILL.md` file that **MUST include a YAML header** followed by the main content:

```markdown
---
name: <skill-name>
description: <1-1024 character description, third person, includes WHAT and WHEN>
license: MIT
author: <Your Name> <email@example.com>
version: "<semver version>"
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

Clear guidance on when this skill should be invoked. Include specific scenarios and use cases.

## Core Concepts

Key concepts, terminology, and fundamental ideas related to the topic.

## Installation / Setup

How to install or set up the tool (if applicable).

## Usage Examples

Common patterns and code examples demonstrating typical usage.

## Advanced Topics

Deeper topics that may be in separate reference files.

## References

- Official documentation: <URL>
- GitHub repository: <URL>
- Other relevant resources
```

**YAML Header Requirements (CRITICAL):**
- File must start with `---` on line 1
- `name`: Must match directory name, lowercase alphanumeric with hyphens (`^[a-z0-9]+(-[a-z0-9]+)*$`)
- `description`: 1-1024 characters, specific enough for proper skill matching across platforms
- All fields properly quoted if containing special characters
- Header must end with `---` before main content
- **Invalid YAML will prevent skill from loading on most platforms**

### 3. Reference Files (Optional)

For large topics (> 500 lines in SKILL.md), break content into modular reference files:

**Simple skills** (< 500 lines):
```
<skill-name>/
└── SKILL.md                  # All content inline, no references directory
```

**Complex skills** (> 500 lines):
```
<skill-name>/
├── SKILL.md                  # Overview + navigation hub (under 500 lines)
└── references/               # Flat structure only, numbered with 2-digit prefixes
    ├── 01-core-concepts.md
    ├── 02-advanced-workflow.md
    └── 03-api-reference.md
```

**Important rules:**
- Use `references/` directory (not `refs/`)
- Number files with 2-digit prefixes (`01-`, `02-`, `03-`) for consistent ordering
- Keep SKILL.md under 500 lines; reference files can be longer
- Flat structure only - no nested references directories
- Reference files allow loading specific topics on demand, keeping context usage efficient

### 4. Creating a New Skill

1. **Determine the skill name** following the naming convention (`^[a-z0-9]+(-[a-z0-9]+)*$`)
2. **Create the skill directory**: `.agents/skills/<skill-name>/`
3. **Write SKILL.md** with:
   - Valid YAML header (REQUIRED - see section 2)
   - Overview, when to use, core concepts, examples, and references
4. **Determine structure** based on content size:
   - < 500 lines: Keep everything in SKILL.md (no references/)
   - > 500 lines: Move detailed topics to `references/` with numbered files
5. **Validate YAML header** using Python yaml.safe_load before finalizing
6. **Update README.md** by adding a new row to the skills table

### 5. YAML Header Field Requirements

**Required fields (all platforms):**
- `name`: 1-64 chars, matches directory name, regex: `^[a-z0-9]+(-[a-z0-9]+)*$`
- `description`: 1-1024 characters, specific enough for proper skill matching

**Optional fields (union across platforms):**
- `license` (pi, opencode)
- `compatibility` (pi, opencode)
- `metadata` - string-to-string map (pi, opencode)
- `allowed-tools` (pi - experimental)
- `disable-model-invocation` (pi)
- `agents/openai.yaml` for codex UI metadata and policy

**Validation:**
```bash
python3 -c "import yaml; data=yaml.safe_load(open('SKILL.md').read().split('---',2)[1].split('---')[0]); print('✓ Valid' if 'name' in data and 'description' in data else '✗ Invalid')"
```

### 6. Skill Content Guidelines

- **Be specific**: Clearly state when to use the skill
- **Include examples**: Provide practical, copy-pasteable code
- **Link references**: Always include official documentation URLs
- **Stay concise**: Aim for completeness within ~10K tokens per skill
- **Use Markdown**: All content must be plain Markdown

## Important: Updating README.md

**Every time a new skill is added, the table in `README.md` MUST be updated.**

Add a new row to the skills table with:
| Skill | Project | Version | Technologies |
|-------|---------|---------|--------------|
| `<skill-name>` | `<project-name>` | `<version>` | `<tech1>, <tech2>, ...` |

Example update:
```markdown
| uv-0-11-6 | uv | 0.11.6 | Python, package manager |
```

## Using the write-skill Skill

The `write-skill` skill can generate new skills automatically. To use it:

1. Provide the target project/tool name and version
2. Include official documentation URLs
3. Specify key topics to cover
4. The skill will generate SKILL.md and any needed reference files

Example prompt for write-skill:
```
Create a skill for "fastapi-0-115" using:
- Official docs: https://fastapi.tiangolo.com/
- GitHub: https://github.com/tiangolo/fastapi
- Focus on: routing, dependencies, Pydantic models, async support
```

## Example Skill Structure

Here's a minimal example of a complete skill:

### Directory: `.agents/skills/hello-world-1-0/`

#### SKILL.md
```markdown
---
name: hello-world-1-0
description: A simple greeting library for demonstration purposes. Use when generating greetings or demonstrating basic skill structure.
license: MIT
author: Example Author <example@example.com>
version: "1.0.0"
tags:
  - greeting
  - example
category: utilities
external_references:
  - https://example.com/hello-world
---

# Hello World 1.0

## Overview

A simple greeting library for demonstration purposes.

## When to Use

Use this skill when you need to generate greetings or demonstrate basic skill structure.

## Core Concepts

- Greeting messages
- Localization support

## Installation

```bash
pip install hello-world
```

## Usage Examples

```python
from hello_world import greet

message = greet("Alice")
print(message)  # Hello, Alice!
```

## References

- Documentation: https://example.com/hello-world
- GitHub: https://github.com/example/hello-world
```

## Important Notes

1. **YAML header is REQUIRED** - Every skill must have valid YAML starting on line 1
2. **Validate before finalizing** - Use yaml.safe_load to verify YAML syntax
3. **Name validation** - Must match regex `^[a-z0-9]+(-[a-z0-9]+)*$`
4. **Description length** - Must be 1-1024 characters, third person, includes WHAT and WHEN
5. **Reference directory name** - Use `references/` not `refs/`
6. **Numbered reference files** - Use 2-digit prefixes (`01-`, `02-`, `03-`)
7. **Flat structure** - No nested references directories
8. **Simple vs Complex** - < 500 lines = single file, > 500 lines = add references/
9. **Cross-platform compatible** - Skills work on pi, opencode, claude, codex, hermes
10. **external_references field** - Include only user-provided starting URLs, not all crawled pages

## Best Practices

1. **Research first**: Read official documentation before writing a skill
2. **Test examples**: Ensure code examples are accurate and functional
3. **Keep it focused**: One skill per tool/library version
4. **Update regularly**: Refresh skills when tools have major updates
5. **Link everything**: Always provide URLs to official resources

## Skill Categories

Skills in this repository cover:

- **AI/LLM Tools**: pi-ai, openai, spec-kit
- **Python Libraries**: aiohttp, sqlalchemy, redis-py
- **JavaScript/TypeScript**: solidjs, nextjs, axios
- **Development Tools**: uv, ruff, ty, esbuild
- **Containers**: podman, crun
- **Databases**: sqlite, rqlite, redis
- **Web Frameworks**: tailwindcss, daisyui, htmx
- **Agents**: Various coding agent implementations
