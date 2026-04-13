# Agent Guidelines for Tangled Skills

This document provides guidance for AI agents working with the tangled-skills repository.

## Repository Structure

```
tangled-skills/
├── .agents/skills/
│   ├── <skill-name>/
│   │   ├── SKILL.md          # Main skill file (required)
│   │   └── refs/             # Optional reference files
│   │       ├── topic1.md
│   │       └── topic2.md
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

Each skill has a `SKILL.md` file that follows this structure:

```markdown
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

### 3. Reference Files (Optional)

For large topics, break content into modular reference files:

```
<skill-name>/
├── SKILL.md
└── refs/
    ├── architecture.md
    ├── api-reference.md
    └── examples.md
```

Reference files allow loading specific topics on demand, keeping context usage efficient.

### 4. Creating a New Skill

1. **Determine the skill name** following the naming convention
2. **Create the skill directory**: `.agents/skills/<skill-name>/`
3. **Write SKILL.md** with overview, when to use, core concepts, examples, and references
4. **Add reference files** if the topic is large (optional)
5. **Update README.md** by adding a new row to the skills table

### 5. Skill Content Guidelines

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
