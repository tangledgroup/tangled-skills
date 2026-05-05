# Agent Guidelines for Tangled Skills

This document provides guidance for AI agents working with the tangled-skills repository.

## Repository Structure

**Ignore misc directory content**: Ignore content from `misc/` directory.

```
tangled-skills/
├── .agents/skills/
│   ├── <skill-name>/
│   │   ├── SKILL.md                  # Main skill file (required, must include YAML header)
│   │   └── reference/                # Optional reference files (flat structure, numbered)
│   │   │   ├── 01-topic-name.md
│   │   │   └── 02-another-topic.md
│   │   │   ⋮
│   │   │
│   │   ├── scripts/                  # Only if explicitly requested
│   │   │   └── validate.sh           # Validation script
│   │   │   ├── analyze_form.py       # Utility script (executed, not loaded into context)
│   │   │   ├── fill_form.py          # Form filling script
│   │   │   ⋮
│   │   │
│   │   └── assets/                   # Only if explicitly requested
│   │       └── config.yaml
│   │       └── logo.png
│   │       ⋮
│   ⋮
│
├── README.md                         # Skills table and overview (auto-generated)
└── AGENTS.md                         # This file
```

## Package Installation Rules

**Never install packages system-wide.** Always use local or ephemeral environments.
When running scripts that need dependencies, create a temporary virtual environment,
or use `uv run --with <pkg> <script>` for one-off executions.

## Tooling Conventions

- **Python packages**: Prefer `uv` over `pip`/`pip-tools`/`poetry`.
- **Python CLI tools**: Use `uvx <tool>` for one-off runs (ephemeral venv, no persistent install).
- **Node.js CLI tools**: Prefer `npx` over global installs.
- **Scripts in this repo**: Run with `python3` (system Python is sufficient for our simple scripts).
