# Agent Guidelines for Tangled Skills

This document provides guidance for AI agents working with the tangled-skills repository.

## Repository Structure

**Ignore misc directory content**: Ignore content from `misc/` directory.

```
tangled-skills/
├── .agents/skills/
│   ├── <skill-name>/
│   │   ├── SKILL.md                # Main skill file (required, must include YAML header)
│   │   └── reference/              # Optional reference files (flat structure, numbered)
│   │       ├── 01-topic-name.md
│   │       └── 02-another-topic.md
├── README.md                       # Skills table and overview (auto-generated)
└── AGENTS.md                       # This file
```

## Mandatory Post-Change Step

After **every** skill addition, deletion, rename, or YAML header edit, regenerate
the README.md skills table:

```bash
python3 misc/gen-skills-table.py
```

This keeps the public skills index in sync with the actual `.agents/skills/` contents.

## Package Installation Rules

**Never install packages system-wide.** Always use local or ephemeral environments:

| Ecosystem  | Do                                      | Don't                       |
|------------|-----------------------------------------|-----------------------------|
| Python     | `uv venv && uv pip install <pkg>`       | `pip install <pkg>`         |
| Python CLI | `uvx <tool>`                            | `pipx install`, bare `pip`  |
| Node.js    | `npx <pkg>` or project-local `npm i`    | `npm install -g <pkg>`      |
| System     | Use what's already installed            | `apt install`, `brew install`, `apk add`, `pacman -S` |

When running scripts that need dependencies, create a temporary virtual environment
or use `uv run --with <pkg> <script>` for one-off executions.

## Tooling Conventions

- **Python packages**: Prefer `uv` over `pip`/`pip-tools`/`poetry`.
- **Python CLI tools**: Use `uvx <tool>` for one-off runs (ephemeral venv, no persistent install).
- **Node.js CLI tools**: Prefer `npx` over global installs.
- **Scripts in this repo**: Run with `python3` (system Python is sufficient for our simple scripts).
