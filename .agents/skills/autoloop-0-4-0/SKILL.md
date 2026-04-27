---
name: autoloop-0-4-0
description: Simpler, opinionated loop harness for inspectable long-running agent workflows. Spinoff of ralph-orchestrator that emphasizes preset-driven multi-role loops with event-based routing, append-only journaling, metareview hygiene passes, worktree isolation, and structured parallelism. Use when building autonomous coding agents that need iterative plan-build-review cycles, quality gates between roles, persistent memory across runs, git worktree isolation for concurrent modifications, or operator visibility into agent execution through inspectable journals and a local dashboard.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.4.0"
tags:
  - autonomous-agents
  - multi-role-loops
  - event-routing
  - preset-workflows
  - agent-harness
  - loop-engine
category: agent-frameworks
external_references:
  - https://github.com/mikeyobrien/autoloop
  - https://github.com/mikeyobrien/autoloop/tree/main/docs
---

# autoloop 0.4.0

## Overview

autoloop is a Node.js-based loop harness for long-running, multi-role agent workflows. It spins out the core ideas from ralph-orchestrator into something simpler and more opinionated: inspectable runs driven by reusable presets, event-based role routing with soft backpressure, an append-only JSONL journal as the canonical source of truth, and operator surfaces that both humans and agents can use directly.

The central idea is that long-running agent work improves dramatically when every iteration is recorded, workflows are declarative preset directories rather than code changes, and the system is designed for inspection — not just execution.

## When to Use

- Building autonomous coding agents that iterate through plan → build → review → finalize cycles
- Needing quality gates between roles (e.g., critic must pass before completion)
- Running concurrent agent workflows without file conflicts (worktree isolation)
- Requiring persistent memory across loop runs (learnings, preferences, metadata)
- Composing multi-stage pipelines from reusable workflow presets (chains)
- Building operator dashboards or CLI surfaces for monitoring agent execution
- Designing agent systems where inspection matters as much as automation

## Core Concepts

**Presets are the product.** Every workflow is a self-contained directory containing `autoloops.toml` (config), `topology.toml` (role graph), `harness.md` (shared instructions), and `roles/*.md` (per-role prompts). No code changes needed for new workflows.

**Event-driven soft routing.** Roles declare what events they can emit. A handoff map routes events to suggested next roles. The model receives advisory suggestions — it is not locked into a hard state machine. Backpressure at the event-emit boundary prevents protocol violations without forcing rigid transitions.

**Append-only journal as canonical truth.** Every lifecycle event, agent action, and coordination record is appended to `.autoloop/journal.jsonl`. Nothing is mutated or deleted. Higher-level views (scratchpad, metrics, coordination state) are projections derived from the journal.

**Metareview hygiene loop.** A periodic meta-level review pass runs between normal iterations to consolidate stale context, trim noisy working files, and store durable learnings — without directly advancing the task. It can hot-reload configuration mid-run.

**Three orchestration layers.** Topology handles intra-loop role routing. Chains compose inter-loop preset sequences. Dynamic chains allow a meta-orchestrator (an LLM agent) to plan and spawn new chain episodes at runtime with explicit budgets and lineage tracking.

## Installation / Setup

```bash
npm install -g @mobrienv/autoloop
```

Or from source:

```bash
git clone https://github.com/mikeyobrien/autoloop.git && cd autoloop
npm install && npm run build
node bin/autoloop --help
```

Requires Node.js >= 18.

## Usage Examples

Start a coding loop with the bundled `autocode` preset:

```bash
autoloop run autocode "Fix the login bug"
```

Watch it in real time:

```bash
autoloop loops watch <run-id>
```

Inspect what happened after completion:

```bash
autoloop inspect journal <run-id>
autoloop inspect scratchpad --format md
autoloop inspect metrics --format csv
```

Run a multi-stage chain (code then QA):

```bash
autoloop run . --chain autocode,autoqa "Implement the approved change and validate it"
```

Keep implementation isolated in a git worktree with auto-merge:

```bash
autoloop run autocode --worktree --automerge "Implement the approved fix"
```

Open the local dashboard:

```bash
autoloop dashboard
```

## Advanced Topics

**Platform Architecture**: Control plane, presets, journals, and external shells → [Platform Architecture](reference/01-platform-architecture.md)

**Topology and Event Routing**: Role definitions, handoff maps, soft routing with backpressure, design patterns → [Topology and Event Routing](reference/02-topology-and-routing.md)

**Journal System**: Append-only JSONL lifecycle events, agent events, coordination events, scratchpad projections → [Journal System](reference/03-journal-system.md)

**Memory and Tasks**: Two-tier memory (project + run), materialization with tombstones, task completion gates → [Memory and Tasks](reference/04-memory-and-tasks.md)

**Metareview Loop**: Periodic hygiene reviews, hot-reload mid-run, context pressure management → [Metareview Loop](reference/05-metareview-loop.md)

**Configuration Reference**: `autoloops.toml` keys for event loop, backend, review, parallelism, worktree, memory → [Configuration Reference](reference/06-configuration-reference.md)

**Worktree Isolation**: Git-level isolation for concurrent runs, merge strategies, lifecycle management → [Worktree Isolation](reference/07-worktree-isolation.md)

**Chains and Dynamic Chains**: Named chain compositions, runtime chain spawning with budgets and lineage → [Chains and Dynamic Chains](reference/08-chains-and-dynamic-chains.md)

**Creating Custom Presets**: Step-by-step preset authoring — topology, roles, harness, configuration → [Creating Custom Presets](reference/09-creating-presets.md)

**Bundled Preset Family**: The `auto*` workflow taxonomy — autocode, autospec, autofix, autoqa, and more → [Bundled Preset Family](reference/10-bundled-presets.md)

**CLI and Dashboard**: Complete CLI subcommand reference and browser-based operator dashboard → [CLI and Dashboard](reference/11-cli-and-dashboard.md)
