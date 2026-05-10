---
name: agent-ralph-wiggum-snarktank
description: Autonomous AI coding loop that runs AI coding tools (Amp or Claude Code) repeatedly until all PRD items are complete. Each iteration is a fresh instance with clean context. Memory persists via git history, progress.txt, and prd.json. Use when building features hands-free through iterative AI loops, shipping code while away, or implementing spec-driven development with the Ralph Wiggum technique derived from Geoffrey Huntley's original pattern.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - ralph-wiggum
  - autonomous-agent
  - coding-loop
  - prd-driven
  - claude-code
  - amp
  - hands-free-development
category: agent-techniques
external_references:
  - https://github.com/snarktank/ralph
  - https://snarktank.github.io/ralph/
  - https://ghuntley.com/ralph/
---

# agent-ralph-wiggum-snarktank v0.1.0

## Overview

Ralph is an autonomous AI agent loop created by snarktank, based on Geoffrey Huntley's Ralph Wiggum technique. It runs AI coding tools ([Amp](https://ampcode.com) or [Claude Code](https://docs.anthropic.com/en/docs/claude-code)) repeatedly until all product requirements document (PRD) items are complete. Each iteration spawns a fresh AI instance with clean context — memory persists only through git history, `progress.txt`, and `prd.json`.

The core insight is simple: a Bash loop that pipes a prompt into an AI coding agent, lets the agent implement one user story, then repeats until all stories pass. The technique is "deterministically bad in an undeterministic world" — it embraces eventual consistency rather than demanding perfection in any single iteration.

Ralph can replace the majority of outsourcing at most companies for greenfield projects. It works best for bootstrapping new projects where you expect to reach 90% completion autonomously, then finish the remaining 10% manually.

## When to Use

- Shipping features hands-free (run Ralph while sleeping)
- Implementing spec-driven development with iterative AI loops
- Greenfield projects where you want AI to do the bulk of implementation
- Converting PRDs into working code through autonomous execution
- Projects that benefit from small, incremental commits with fast feedback loops

Do not use Ralph for:
- Exploratory work without clear acceptance criteria
- Major refactors without explicit success conditions
- Security-critical code requiring human review
- Anything needing immediate human judgment

## Core Concepts

### The Ralph Wiggum Technique

Named after the Simpsons character, the technique is fundamentally a Bash loop:

```bash
while :; do cat PROMPT.md | claude-code; done
```

Each loop iteration is a **fresh context window** — the AI has no memory of previous iterations. This is intentional. It keeps each session focused and prevents context bloat. The only state that carries forward is external: git commits, text files, and file system changes.

### One Thing Per Loop

The single most important rule: ask Ralph to do **one thing per loop**. Only one user story, one focused change. As Geoffrey Huntley puts it: "LLMs are surprisingly good at reasoning about what is important to implement and what the next steps are." Trust Ralph to choose the most important unfinished item.

### Deterministic Stack Allocation

Every loop iteration receives the same allocated context: the prompt template, the PRD (task list), and progress logs. This deterministic allocation is crucial — it ensures Ralph always knows what to do, even though each iteration starts with a blank internal state.

### Eventual Consistency

Ralph requires faith in eventual consistency. Individual iterations may make mistakes, but over many iterations, the system converges toward correctness. When Ralph goes wrong, you don't blame the tool — you tune the prompt (add "signs" for Ralph to read). Like tuning a guitar.

### Monolithic, Not Multi-Agent

While the community pursues multi-agent architectures, Ralph is deliberately monolithic. A single process operating in a single repository, performing one task per loop. Consider what microservices would look like if each service were non-deterministic — a "red hot mess." Ralph avoids this by keeping everything in one loop.

## Installation / Setup

### Prerequisites

- One of the following AI coding tools installed and authenticated:
  - [Amp CLI](https://ampcode.com) (default)
  - [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- `jq` installed for JSON processing
- A git repository for your project

### Installation

Copy the Ralph files into your project:

```bash
# From your project root
mkdir -p scripts/ralph
cp /path/to/ralph/ralph.sh scripts/ralph/

# Copy the prompt template for your AI tool of choice:
cp /path/to/ralph/prompt.md scripts/ralph/prompt.md    # For Amp
# OR
cp /path/to/ralph/CLAUDE.md scripts/ralph/CLAUDE.md    # For Claude Code

chmod +x scripts/ralph/ralph.sh
```

**Alternative installation methods:**

- **Global skills (Amp)**: `cp -r skills/prd ~/.config/amp/skills/ && cp -r skills/ralph ~/.config/amp/skills/`
- **Global skills (Claude Code)**: `cp -r skills/prd ~/.claude/skills/ && cp -r skills/ralph ~/.claude/skills/`
- **Claude Code Marketplace**: `/plugin marketplace add snarktank/ralph` then `/plugin install ralph-skills@ralph-marketplace` (installs `/prd` and `/ralph` skills with automatic invocation)

### Configure Amp Auto-Handoff (Recommended)

Add to `~/.config/amp/settings.json`:

```json
{
  "amp.experimental.autoHandoff": { "context": 90 }
}
```

This enables automatic handoff when context fills up, allowing Ralph to handle large stories that exceed a single context window.

## Usage Examples

### Basic Workflow

```bash
# Step 1: Create a PRD using the PRD skill
# (Interactively with Amp or Claude Code)
"Load the prd skill and create a PRD for [your feature description]"

# Step 2: Convert PRD to Ralph format
"Load the ralph skill and convert tasks/prd-[feature-name].md to prd.json"

# Step 3: Run Ralph
./scripts/ralph/ralph.sh [max_iterations]          # Using Amp (default)
./scripts/ralph/ralph.sh --tool claude [max_iterations]  # Using Claude Code
```

### Running Ralph

```bash
# Default: 10 iterations with Amp
./scripts/ralph/ralph.sh

# Custom iteration count
./scripts/ralph/ralph.sh 25

# Using Claude Code
./scripts/ralph/ralph.sh --tool claude 25

# Both flags work
./scripts/ralph/ralph.sh --tool=claude 25
```

### Checking Progress

```bash
# See which stories are done
cat scripts/ralph/prd.json | jq '.userStories[] | {id, title, passes}'

# See learnings from previous iterations
cat scripts/ralph/progress.txt

# Check git history
git log --oneline -10
```

## Advanced Topics

**Theory and Fundamentals**: The Ralph Wiggum technique — monolithic loops, one thing per loop, eventual consistency, and why this works → [Theory and Fundamentals](reference/01-theory-and-fundamentals.md)

**Loop Mechanics**: How ralph.sh works internally — argument parsing, iteration lifecycle, archiving, tool selection → [Loop Mechanics](reference/02-loop-mechanics.md)

**PRD and Task Structure**: Creating PRDs, prd.json format, story sizing rules, acceptance criteria, dependency ordering → [PRD and Task Structure](reference/03-prd-and-task-structure.md)

**Prompt Engineering**: prompt.md and CLAUDE.md templates, signposting, tuning Ralph through observation, preventing placeholder implementations → [Prompt Engineering](reference/04-prompt-engineering.md)

**Memory Systems**: Git history as memory, progress.txt append-only logs, AGENTS.md updates, pattern consolidation → [Memory Systems](reference/05-memory-systems.md)

**Feedback and Backpressure**: Quality gates, testing strategies, browser verification, preventing code degradation across iterations → [Feedback and Backpressure](reference/06-feedback-and-backpressure.md)

**Advanced Patterns**: Subagent delegation, context window management, parallelism control, planning mode, self-improving loops → [Advanced Patterns](reference/07-advanced-patterns.md)
