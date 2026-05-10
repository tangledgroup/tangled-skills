---
name: ralph-orchestrator-2-9-2
description: Hat-based orchestration framework that keeps AI agents in a loop until the task is done. Supports Claude Code, Kiro, Gemini CLI, Codex, Amp, Copilot CLI, OpenCode, and Pi backends with event-driven hat coordination, backpressure quality gates, persistent memories and tasks, parallel loops via git worktrees, agent waves for intra-loop parallelism, and human-in-the-loop via Telegram. Use when building autonomous AI coding workflows, orchestrating multi-step agent pipelines, or implementing the Ralph Wiggum technique for hands-free task completion.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - ai-orchestration
  - ralph-wiggum
  - autonomous-agents
  - hat-system
  - event-driven
  - multi-backend
category: agent-frameworks
external_references:
  - https://github.com/mikeyobrien/ralph-orchestrator
  - https://mikeyobrien.github.io/ralph-orchestrator/
---

# Ralph Orchestrator 2.9.2

## Overview

Ralph Orchestrator is a Rust-based framework that implements the **Ralph Wiggum technique** — autonomous task completion through continuous iteration. Give Ralph a task, and it keeps an AI agent in a loop until the work is done or limits are reached.

At its core, Ralph is a thin coordination layer, not a platform. It trusts the AI agent to do the actual work and provides structure through hats (specialized personas), events (typed messages), backpressure (quality gates), and persistent state (memories, tasks).

Built as a Cargo workspace with seven crates:

- **ralph-proto** — Protocol types: Event, Hat, Topic
- **ralph-core** — Orchestration engine: EventLoop, Config, Memory/Task stores
- **ralph-adapters** — CLI backend integrations (Claude, Kiro, Gemini, etc.)
- **ralph-tui** — Terminal UI using ratatui
- **ralph-cli** — Binary entry point and commands
- **ralph-e2e** — End-to-end testing framework
- **ralph-bench** — Benchmarking harness

## When to Use

- Running autonomous AI coding loops that iterate until completion
- Orchestrating multi-step workflows with specialized agent personas (hats)
- Enforcing quality gates through backpressure (tests, lint, typecheck)
- Coordinating parallel work via git worktrees or intra-loop waves
- Building human-in-the-loop workflows with Telegram integration
- Migrating from manual AI-assisted coding to hands-free orchestration

## Installation

Ralph is distributed as a Rust binary. Three installation methods:

```bash
# Via npm (recommended)
npm install -g @ralph-orchestrator/ralph-cli

# Via GitHub Releases installer
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/mikeyobrien/ralph-orchestrator/releases/latest/download/ralph-cli-installer.sh | sh

# Via Cargo
cargo install ralph-cli
```

Prerequisites: Rust 1.75+ and at least one AI CLI backend (Claude Code, Kiro, Gemini CLI, Codex, Amp, Copilot CLI, OpenCode, or Pi).

## Quick Start

```bash
# 1. Initialize with your preferred backend
ralph init --backend claude

# 2. Plan your feature (interactive PDD session)
ralph plan "Add user authentication with JWT"

# 3. Implement the feature
ralph run -p "Implement the feature in specs/user-authentication/"

# Or run directly without planning
ralph run -p "Add input validation to the /users endpoint"
```

Ralph iterates until the agent outputs `LOOP_COMPLETE` or hits iteration/runtime limits.

## Core Concepts

### Two Modes of Operation

**Traditional mode** — A simple loop. Ralph feeds the prompt to the backend AI, captures output, checks for `LOOP_COMPLETE`, and repeats. No hats needed.

```yaml
cli:
  backend: "claude"
event_loop:
  completion_promise: "LOOP_COMPLETE"
  max_iterations: 100
```

**Hat-based mode** — Specialized personas coordinate through typed events. Each hat has triggers (events that activate it), publishes (events it can emit), and instructions (prompt injected when active).

```yaml
event_loop:
  starting_event: "task.start"
  completion_promise: "LOOP_COMPLETE"

hats:
  planner:
    triggers: ["task.start"]
    publishes: ["plan.ready"]
    instructions: "Create an implementation plan."

  builder:
    triggers: ["plan.ready"]
    publishes: ["build.done"]
    instructions: "Implement the plan. Evidence required: tests pass."
```

### The Ralph Wiggum Technique

The technique is a Bash loop at heart:

```bash
while :; do cat PROMPT.md | claude ; done
```

Key insight: each iteration starts with **fresh context**. The AI re-reads the prompt and codebase from scratch every cycle. This prevents accumulated confusion and gives each iteration a clean chance to succeed. Files on disk are the only persistent state — the prompt, the codebase, git history, and memory files.

The technique requires faith in eventual consistency: Ralph doesn't guarantee immediate success, but given enough iterations and achievable tasks, it converges.

### Six Tenets

1. **Fresh Context Is Reliability** — Each iteration clears context. Re-read specs, plan, code every cycle.
2. **Backpressure Over Prescription** — Don't prescribe how; create gates that reject bad work.
3. **The Plan Is Disposable** — Regeneration costs one planning loop. Cheap.
4. **Disk Is State, Git Is Memory** — Files are the handoff mechanism.
5. **Steer With Signals, Not Scripts** — The codebase is the instruction manual. Add signs for next time.
6. **Let Ralph Ralph** — Sit *on* the loop, not *in* it. Tune like a guitar, don't conduct like an orchestra.

### Configuration Layers

Ralph composes configuration from up to three layers (deep merge):

1. `~/.ralph/config.yml` — User-level defaults
2. `ralph.yml` in workspace (or `$RALPH_CONFIG` / `-c <file>`) — Project overrides
3. `-c core.field=value` — CLI overrides applied last

## Supported Backends

- **Claude Code** (`claude`) — Recommended, primary support
- **Kiro** (`kiro`) — Amazon/AWS
- **Gemini CLI** (`gemini`) — Google
- **Codex** (`codex`) — OpenAI
- **Amp** (`amp`) — Sourcegraph
- **Copilot CLI** (`copilot`) — GitHub
- **OpenCode** (`opencode`) — Community
- **Pi** (`pi`) — Multi-provider

Ralph auto-detects installed backends. Override with `--backend <name>` or via config.

## Built-in Hat Collections

```bash
ralph init --list-presets
ralph run -c ralph.yml -H builtin:code-assist -p "Add user authentication"
```

Five supported builtins:

- **code-assist** — Default implementation workflow (planner, builder, critic, finalizer)
- **debug** — Root-cause debugging (investigator, tester, fixer, verifier)
- **research** — Read-only analysis (researcher, synthesizer)
- **review** — Adversarial code review (reviewer, analyzer)
- **pdd-to-code-assist** — Full idea-to-code pipeline (advanced, multi-stage)

## Advanced Topics

**The Ralph Wiggum Technique**: How the loop really works — fresh context, eventual consistency, tuning signals → [Ralph Wiggum Loop](reference/01-ralph-wiggum-loop.md)

**Hats and Events**: Specialized personas, event routing with glob patterns, coordination patterns (pipeline, critic-actor, fan-out, cyclic rotation) → [Hats & Events](reference/02-hats-and-events.md)

**Configuration Reference**: Full YAML schema, CLI overrides, environment variables, scratchpad modes, per-hat settings → [Configuration](reference/03-configuration.md)

**Parallelism**: Git worktree loops for inter-loop parallelism, agent waves for intra-loop parallelism, auto-merge with conflict resolution → [Parallel Loops & Waves](reference/04-parallel-loops-waves.md)

**Memories, Tasks & Backpressure**: Persistent learning across sessions, runtime work tracking, quality gates that reject incomplete work → [Memories Tasks & Backpressure](reference/05-memories-tasks-backpressure.md)
