# Agent Guidelines for Tangled Skills

This document provides guidance for AI agents working with the tangled-skills repository.

## Repository Structure

```
tangled-skills/
├── .agents/skills/
│   ├── <skill-name>/
│   │   ├── SKILL.md                # Main skill file (required, must include YAML header)
│   │   └── reference/              # Optional reference files (flat structure, numbered)
│   │       ├── 01-topic-name.md
│   │       └── 02-another-topic.md
├── README.md                       # Skills table and overview
├── README.md                       # Skills table and overview (auto-generated)
├── scripts/
│   └── gen-skills-table.py         # Regenerates README.md skills table from YAML headers
└── AGENTS.md                       # This file
```

## Mandatory Post-Change Step

After **every** skill addition, deletion, rename, or YAML header edit, regenerate
the README.md skills table:

```bash
python3 scripts/gen-skills-table.py
```

This keeps the public skills index in sync with the actual `.agents/skills/` contents.
