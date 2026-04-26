---
name: agent-ralph-wiggum-fstandhartinger
description: Autonomous AI coding with spec-driven development combining iterative bash loops and SpecKit-style specifications for fully autonomous AI-assisted software development. Use when building projects that require hands-free AI implementation, working from specification files, or running autonomous development loops with completion verification.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.3.0"
tags:
  - autonomous-development
  - spec-driven
  - iterative-loops
  - ai-coding
  - ralph-wiggum
  - specification-based
category: development
external_references:
  - https://ralph-wiggum.ai/
  - https://github.com/fstandhartinger/ralph-wiggum
---

# Ralph Wiggum — Autonomous AI Coding Loop

## Overview

Ralph Wiggum is a bash-loop-driven autonomous coding system that combines Geoffrey Huntley's iterative loop methodology with SpecKit-style specifications. It turns AI agents into reliable builders: each loop iteration picks one task from a spec, implements it completely, verifies acceptance criteria, commits changes, and exits — then restarts with fresh context for the next task.

The project by fstandhartinger provides:
- Shell scripts for Claude Code, OpenAI Codex, Google Gemini, and GitHub Copilot
- Spec-driven development with testable acceptance criteria
- Interactive AI-guided installation with constitution creation
- NR_OF_TRIES tracking for stuck specs
- Optional Telegram notifications and completion logs

## When to Use

- Setting up autonomous AI coding in a project from scratch
- Converting an existing codebase to spec-driven autonomous development
- Running the Ralph loop (build or plan mode) against specs
- Debugging stuck specs or tuning loop behavior
- Creating project constitutions that guide agent behavior
- Installing Ralph Wiggum via agent skill installers or manually

## Core Concepts

**The Ralph Loop**: A bash `while` loop that repeatedly starts a fresh AI agent process. Each iteration reads the constitution and specs from disk, picks one incomplete task, implements it, verifies acceptance criteria, then outputs `<promise>DONE</promise>` only when 100% complete. The loop checks for this magic phrase — if found, moves to next iteration; if not, retries with fresh context.

**Fresh Context Each Loop**: Unlike exit-hook approaches that force the same session to continue indefinitely (causing context overflow and lossy compaction), Ralph terminates and restarts cleanly between tasks. Every iteration gets a clean context window.

**Shared State on Disk**: `IMPLEMENTATION_PLAN.md` (optional) or the `specs/` folder persists between loops. The agent reads it each time to pick tasks.

**Backpressure via Tests**: Tests, lints, and builds reject invalid work. The agent must fix issues before outputting the completion signal. Natural convergence through iteration.

**Completion Signal**: `<promise>DONE</promise>` means all acceptance criteria verified, tests pass, changes committed and pushed. `<promise>ALL_DONE</promise>` means no work remains.

## Installation / Setup

### Agent Skill Installers

```bash
# Vercel add-skill
npx add-skill fstandhartinger/ralph-wiggum

# OpenSkills
openskills install fstandhartinger/ralph-wiggum

# Skillset
skillset add fstandhartinger/ralph-wiggum
```

### AI-Guided Setup (Recommended)

Point your AI agent to the repo:

> "Set up Ralph Wiggum in my project using https://github.com/fstandhartinger/ralph-wiggum"

The agent reads `INSTALLATION.md` and guides through:
1. Creating directory structure (`.specify/memory/`, `specs/`, `scripts/`, `logs/`, etc.)
2. Downloading loop scripts from GitHub
3. Interactive interview about project vision, principles, and tech stack
4. Generating `.specify/memory/constitution.md` — the single source of truth

### Manual Setup

See [Manual Setup](reference/01-manual-setup.md) for step-by-step directory creation, script downloads, and constitution authoring.

## Usage

### Two Modes

- **Build mode** (default) — Pick spec/task, implement, test, commit: `./scripts/ralph-loop.sh`
- **Plan mode** (optional) — Create detailed task breakdown from specs: `./scripts/ralph-loop.sh plan`

### Multiple Agent Backends

| Script | Agent |
|--------|-------|
| `ralph-loop.sh` | Claude Code |
| `ralph-loop-codex.sh` | OpenAI Codex |
| `ralph-loop-gemini.sh` | Google Gemini |
| `ralph-loop-copilot.sh` | GitHub Copilot |

### Limiting Iterations

```bash
./scripts/ralph-loop.sh        # Unlimited iterations
./scripts/ralph-loop.sh 20     # Max 20 iterations
```

### Spec Status Convention

A spec is **COMPLETE** when it contains `Status: COMPLETE` at the start of a line (supports `## Status: COMPLETE`, `**Status**: COMPLETE`, etc.). Any other status or missing status means **INCOMPLETE**.

### NR_OF_TRIES Tracking

Each spec tracks attempt count via `<!-- NR_OF_TRIES: N -->` at the bottom. After 10 attempts without completion, the spec is flagged as stuck and should be split into smaller specs.

```bash
source scripts/lib/nr_of_tries.sh
print_stuck_specs_summary
```

## Advanced Topics

**Manual Setup**: Directory structure, script downloads, constitution authoring → See [Manual Setup](reference/01-manual-setup.md)

**Constitution Reference**: The single source of truth for agent behavior, with template and optional sections → See [Constitution Reference](reference/02-constitution-reference.md)

**Loop Internals**: How ralph-loop.sh works — prompt generation, iteration cycle, completion detection, logging → See [Loop Internals](reference/03-loop-internals.md)

**Optional Features**: Telegram notifications, GitHub Issues integration, completion logs, audio alerts → See [Optional Features](reference/04-optional-features.md)

## Credits

Based on Geoffrey Huntley's original Ralph Wiggum methodology. Combined with SpecKit by GitHub for spec-driven development. Influenced by Matt Pocock's variant. Official Claude Code plugin available from Anthropic.
