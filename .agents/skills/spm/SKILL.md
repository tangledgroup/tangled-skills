---
name: spm
description: Skill Package Manager, spm, it is meta skill for skill authoring and skill package manager for AI agents.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - meta
  - meta skill
  - skill package manager
  - authoring
category: meta
external_references:
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
  - https://opencode.ai/docs/skills
  - https://pi.dev/docs/latest/skills
---

# spm - Skill Package Manager

## Overview

It is meta skill for skill authoring and skill package manager for AI agents.

## Mandatory Post-Change Step

After **every** skill addition, deletion, rename, or YAML header edit, regenerate
the README.md skills table:

```bash
scripts/gen-skills-table.sh
```

This keeps the public skills index in sync with the actual `.agents/skills/` contents.
