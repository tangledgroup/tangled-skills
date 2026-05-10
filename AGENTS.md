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
or use `uvx <tool>` for one-off executions.

## Tooling Conventions

1. Use `uvx <tool>` for Python CLI tools (ephemeral venv, no persistent install).
2. Use `npx <tool>` for Node.js CLI tools (no global installs).
3. Write inline bash scripts for simple shell tasks.
4. Run inline `python3` scripts when system Python suffices.
