---
name: workflow
description: Phase/task based workflow system with PLAN.md as single source of truth. Use when tackling projects that require structured iteration through Planning, Analysis, Design, Implementation, Testing, Deployment, Maintenance, etc phases with clear dependency graphs.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - meta
  - workflow
  - task-management
category: meta
---

# Workflow - create, read, execute and update plan

Phase/task based workflow system with `PLAN.md` as single source of truth, strict phase numbering (`[emoji-of-phase] Phase X **NAME_OF_PHASE**`), strict task numbering (`[emoji-of-phase] Phase X - [emoji-of-task] Task X.Y`), inline dependency tracking, and emoji-coded statuses.

There can be many `PLAN.md` files in different locations. Plan files can create dependency graph via `**Depends on Plan:** ...`.

## First open

1. **No PLAN.md?** → Create `PLAN.md` with all phases based on given requirements. Determine phases and tasks. Ask questions how to build plan.
2. **PLAN.md exists?** → Open it. Show and ask from where to continue.

## Plan updates

Update current `PLAN.md` file after every transition.

## PLAN.md template

```markdown
# PLAN.md — workflow

<!-- optional: relative path to other PLAN.md -->
**Depends on Plan:** ...
<!-- required: [emoji-of-phase] Phase X **NAME_OF_PHASE** -->
**Current Phase:** ...
<!-- required: [emoji-of-phase] Phase X - [emoji-of-task] Task X.Y -->
**Current Task:** ...
<!-- required: YYYY-MM-DD HH:MM:SS -->
**Created:** ...
<!-- required: YYYY-MM-DD HH:MM:SS -->
**Updated:** ...

<!-- required: PHASES with TASKS start here -->
```

## Emoji-coded statuses

Strictly use following emojis for `[emoji-of-phase]` and `[emoji-of-task]`:

- ☐ **To Do** – backlog / new
- ❓ **Question** – question or clarification
- ⚙️ **Doing** – in progress / wip
- ❌ **Error** – error / failure
- ☑ **Done** – completed / done

These are state transitions:
- ☐ → ⚙️ means: transition from new, everything seams clear, to lets start doing/working
- ☐ → ❓ means: transition from new, something is unclear, to ask question/clarification
- ⚙️ → ❓ means: during doing/working state, something unexpected happened, so I need clarification
- ⚙️ → ❌ means: during doing/working state, critical error/failure happened or blocker that stopped pipeline, transition to error state 
- ⚙️ → ☑ means: during doing/working state, successfully solved, so transition to done 
- ❓ → ⚙️ means: I have question, I got answer or was able to figure out what could be solutions, so transition to doing/working
- ❌ → ⚙️ means: in error state, but based on my previous experience, I will decide to try one more time to work
- ❌ → ❓ means: in error state, but I have questions which might for which I might get hit or answer how to solve

After transition is made from ☐ state, next state will be intelligently determined based on past experience and guidance.

## Phases

Phase is strictly formatted as `[emoji-of-phase] Phase X`.

Every Phase **MUST** have a unique ID in the exact format `[emoji-of-phase] Phase X` (X = phase number).

All phases, tasks and their additions, changes, removals, transitions and dependencies live ONLY in `PLAN.md` file.

**PLAN.md = single source of truth**: project with dependency graph.

## Tasks

Task is strictly formatted as `[emoji-of-phase] Phase X - [emoji-of-task] Task X.Y`.

Every task **MUST** have a unique ID in the exact format `[emoji-of-phase] Phase X - [emoji-of-task] Task X.Y` (X = phase number, Y = sequential task number **within that phase**).

Task dependencies are **phase-bound by default** (most will be same-phase).

When a task has dependencies, append to task name the suffix `(depends on: A, B, ...)` part. If current task don't have any dependencies, don't prepend `(depends on: ...)` for that task.

For phase-bound dependencies, `A`, `B`, etc, are dependencies of form `Task X.Y` where `X` is current phase.

For cross-phase task dependencies, `A`, `B`, etc, are explicitly allowed and listed with full `Phase X - Task X.Y` where `X` can be phase ID from other phase and `Y` matches task ID from that other phase.

This creates a clear directed graph that any reader (human or agent) can parse instantly.
