# Manual Setup

## Directory Structure

Create these directories at the project root:

```bash
mkdir -p .specify/memory specs scripts logs history completion_log .cursor/commands .claude/commands
```

### Directory Purposes

- `.specify/memory/` — Stores the constitution (single source of truth for agent behavior)
- `specs/` — Feature specifications with acceptance criteria
- `scripts/` — Ralph loop shell scripts
- `logs/` — Session and iteration logs
- `history/` — Per-spec completion history
- `completion_log/` — Visual mermaid diagrams of completed specs
- `.cursor/commands/` — Cursor-specific commands
- `.claude/commands/` — Claude Code-specific commands

## Download Scripts

Fetch loop scripts from the GitHub repository:

```bash
# Claude Code
curl -o scripts/ralph-loop.sh \
  https://raw.githubusercontent.com/fstandhartinger/ralph-wiggum/main/scripts/ralph-loop.sh

# OpenAI Codex
curl -o scripts/ralph-loop-codex.sh \
  https://raw.githubusercontent.com/fstandhartinger/ralph-wiggum/main/scripts/ralph-loop-codex.sh

# Google Gemini
curl -o scripts/ralph-loop-gemini.sh \
  https://raw.githubusercontent.com/fstandhartinger/ralph-wiggum/main/scripts/ralph-loop-gemini.sh

# GitHub Copilot
curl -o scripts/ralph-loop-copilot.sh \
  https://raw.githubusercontent.com/fstandhartinger/ralph-wiggum/main/scripts/ralph-loop-copilot.sh

chmod +x scripts/ralph-loop*.sh
```

## Create Constitution

Write `.specify/memory/constitution.md` with your project's guiding principles, tech stack, and autonomy settings. This is the file the agent reads every iteration. See [Constitution Reference](reference/02-constitution-reference.md) for the full template.

Minimum viable constitution:

```markdown
# My Project Constitution

> Brief description of what the project does.

## Context Detection

**Ralph Loop Mode** (started by ralph-loop*.sh):
- Pick highest priority incomplete spec from `specs/`
- Implement, test, commit, push
- Output `<promise>DONE</promise>` only when 100% complete
- Output `<promise>ALL_DONE</promise>` when no work remains

**Interactive Mode** (normal conversation):
- Be helpful, guide decisions, create specs

## Core Principles

- Principle 1
- Principle 2
- Principle 3

## Autonomy

YOLO Mode: ENABLED
Git Autonomy: ENABLED

## Specs

Specs live in `specs/` as markdown files. Pick the highest priority incomplete spec (lower number = higher priority). A spec is incomplete if it lacks `## Status: COMPLETE`.

## Completion Signal

All acceptance criteria verified, tests pass, changes committed and pushed → output `<promise>DONE</promise>`. Never output this until truly complete.
```

## Create Agent Entry Files

### AGENTS.md (project root)

```markdown
# Agent Instructions

**Read:** `.specify/memory/constitution.md`

That file is your source of truth for this project.
```

### CLAUDE.md (project root)

Same content as AGENTS.md.

## Verify Setup

```bash
# Check directory structure exists
ls -la .specify/memory/constitution.md
ls scripts/ralph-loop.sh

# Check Claude CLI is available (for ralph-loop.sh)
claude --version

# Or check other agent CLIs for alternative scripts
```

## Create Your First Spec

Write `specs/001-feature-name.md` with:

- Feature requirements
- Clear, testable acceptance criteria (specific and measurable)
- Completion signal section

Good acceptance criteria example: "User can log in with Google and session persists across page reloads."

Bad acceptance criteria example: "Works correctly."

## Start the Loop

```bash
./scripts/ralph-loop.sh
```
