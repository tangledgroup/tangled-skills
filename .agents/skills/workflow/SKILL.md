---
name: workflow
description: Phase/task based workflow system with PLAN.md as single source of truth. Use when tackling projects that require structured iteration through Planning, Analysis, Design, Implementation, Testing, Deployment, Maintenance, etc phases with clear dependency graphs.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.1"
tags:
  - meta
  - meta-skill
  - workflow
  - task-management
category: meta
---

# Workflow - create, read, execute and update plan(s)

## Overview

Phase/task based workflow system with `PLAN.md` as single source of truth.
There can be many `PLAN.md` files in different locations.
Plan files create a dependency graph via `**Depends On:** ...`.
Strict phase numbering (`[emoji-of-phase] Phase X Phase Title`), inline phase dependency tracking, and emoji-coded statuses within current plan.
Strict task numbering (`[emoji-of-task] Task X.Y Task Title`), inline phase/task dependency tracking, and emoji-coded statuses within current plan.

## When to Use

- Starting a new project that requires structured phase-by-phase execution
- Tackling complex tasks with multiple dependent steps (implementation, testing, deployment)
- Coordinating work across multiple PLAN.md files with inter-plan dependencies
- Resuming interrupted work by tracking current phase and task state
- Any workflow where having a single source of truth for progress is valuable

## Initial Setup

When this skill is invoked, follow these steps:

1. **PLAN.md doesn't exist?** → Create `PLAN.md` with all phases based on given requirements. There are no predefined phases — determine them from context. Calibrate phase/task granularity to the requirements complexity and detect whether the requester is a beginner, advanced, or expert user. Ask clarifying questions before finalizing the plan. If unable to ask (non-interactive mode), proceed with best-effort assumptions and document them in the plan.
2. **PLAN.md exists?** → Open it. Examine `**Current Phase:**` and `**Current Task:**` and propose a continuation point (hint: the next pending task could be one of the lowest-numbered but in this order ⚙️ ❓ ❌ ☐). All running tasks have to be re-run with status ⚙️ because they were probably interrupted.

## Plan updates

Update the current `PLAN.md` file after every change:
- Emoji status transitions on any phase or task
- Adding, modifying, or removing phases or tasks
- User-requested plan alterations

Two rules govern `**Current Phase:**` and `**Current Task:**`:

1. **During work** — point to whichever phase/task is currently being worked on (not necessarily the last in list order).
2. **On completion** — when a task transitions to ☑ (Done), auto-advance both `**Current Phase:**` and `**Current Task:**` to the next pending task (lowest-numbered but in this order ❓❌☐ within the same phase, or the next phase if no pending tasks remain in the current phase). If the completed task was the last one overall, keep both fields pointing to it.

## PLAN.md template

```markdown
<!-- Plan Title is short but descriptive title of current plan -->
# [emoji-of-plan] Plan: Plan Title

<!-- default NONE if doesn't have dependencies, or relative paths to other PLAN.md files -->
**Depends On:** ...
<!-- ISO 8601 / UTC (YYYY-MM-DDTHH:MM:SSZ) -->
**Created:** ...
<!-- ISO 8601 / UTC (YYYY-MM-DDTHH:MM:SSZ) -->
**Updated:** ...
<!-- [emoji-of-phase] Phase X Phase Title -->
**Current Phase:** ...
<!-- [emoji-of-phase] Phase X - [emoji-of-task] Task X.Y -->
**Current Task:** ...

<!-- required: PHASES with TASKS start here -->
...
```

## Universal emoji-coded statuses

Strictly use only the following emojis for statuses: ☐ ❓ ⚙️ ❌ ☑
⚙️ (Doing) is always required before reaching ☑ (Done).

## Plan Statuses

The plan itself carries a status via `[emoji-of-plan]` in its title:
```
# [emoji-of-plan] Plan: Plan Title
```

Strictly use following emojis for `[emoji-of-plan]` status:

- ☐ **Not Started** — plan created but no work has begun on any phase or task
- ❓ **Needs Clarification** — plan exists but requirements or scope need clarification before work can begin
- ⚙️ **Active** — at least one phase or task is in progress or pending
- ❌ **Blocked** — cannot proceed due to dependency cycles, unresolved external blockers, or critical failures across the plan
- ☑ **Completed** — all phases and all tasks within them have reached (Done)

### Plan Status Transitions

These are valid state transitions for `[emoji-of-plan]`:

- ☐ → ⚙️ — begin work on the plan (start first task)
- ☐ → ❓ — plan created but scope or requirements need clarification before starting
- ⚙️ → ❓ — during work, something unexpected happened, need clarification
- ⚙️ → ❌ — critical blocker stops all progress across the plan
- ⚙️ → ☑ — all phases and tasks completed successfully
- ❓ → ⚙️ — clarifications resolved, begin work
- ❌ → ⚙️ — blocker resolved, resume work
- ❌ → ❓ — need clarification on how to resolve the blocker

⚙️ (Active) is always required before reaching ☑ (Completed). You cannot skip to Completed from Not Started or Blocked states.

## Plan

**PLAN.md = single source of truth**: project with dependency graph.
Multiple `PLAN.md` files can exist in different locations.
They form a directed acyclic graph (DAG) via the required `**Depends On:**` header field:
- Multiple dependencies are comma-separated with spaces: `../a/PLAN.md , ../../b/PLAN.md`
- Default value is `NONE` when the plan has no dependencies
- Cycles are not allowed. Check for cycles whenever any plan is created or when `**Depends On:**` is modified. If a cycle is detected (including transitive cycles), report it to the user and stop until resolved
- The dependency graph is resolved transitively by visiting referenced `PLAN.md` headers — not inline-expanded
- When a dependency is incomplete, ask what to do before proceeding

## Phases

Phase is strictly formatted as `## [emoji-of-phase] Phase X Phase Title`, where X is unique ID (X = phase number, starting from 1).
Every Phase **MUST** have a unique ID in the exact format `## [emoji-of-phase] Phase X` (X = phase number, starting from 1).
All phases, tasks and their additions, changes, removals, transitions and dependencies live ONLY in `PLAN.md` file.

If a phase has zero tasks, emit a warning — it can never reach ☑ (Done) and is likely a mistake.

## Tasks

Tasks are markdown list items. Each task is strictly formatted as:

```
- [emoji-of-task] Task X.Y Task Title (depends on: ...)
  - optional sub-bullet: acceptance criteria, notes, or implementation details
  - optional sub-bullet: additional context
```

Every task **MUST** have a unique ID in the exact format `- [emoji-of-task] Task X.Y` (X = phase number, Y = sequential task number **within that phase**).

Sub-bullets under a task are optional and carry no status tracking — they exist only to capture acceptance criteria, implementation notes, or context. They do not affect plan status derivation.

### Task Granularity

Each task should be small enough to complete in one focused work session and large enough to produce a verifiable outcome:

- One task = one clear deliverable (a file, a function, a test, a config change)
- If a task requires more than three sub-steps, split it into separate tasks
- Tasks within a phase should be roughly comparable in scope
- Use sub-bullets under the task to record acceptance criteria or key details

### Task Dependencies

Task dependencies are **phase-bound by default** (most will be same-phase).

When a task has dependencies, append to the task title the suffix `(depends on: A , B , ...)`. If a task has no dependencies, don't append `(depends on: ...)` to it.

For phase-bound dependencies, `A`, `B`, etc. are of the form `Task X.Y` where `X` is the current phase.

For cross-phase dependencies, use the full `Phase X - Task X.Y` form where `X` is the other phase's ID and `Y` is the task ID within that phase.

This creates a clear directed graph that any reader (human or agent) can parse instantly.

## Phase and Task Statuses

Strictly use following emojis for `[emoji-of-phase]` and `[emoji-of-task]` status:

- ☐ **To Do** – backlog / new
- ❓ **Question** – question or clarification
- ⚙️ **Doing** – in progress / wip
- ❌ **Error** – error / failure
- ☑ **Done** – completed / done

## Phase and Task Status Transitions

These are valid state transitions:
- ☐ → ⚙️ — new item, everything seems clear, start working
- ☐ → ❓ — new item, something is unclear, ask for clarification
- ⚙️ → ❓ — during work, something unexpected happened, need clarification
- ⚙️ → ❌ — during work, critical error or blocker stopped progress
- ⚙️ → ☑ — during work, successfully completed
- ❓ → ⚙️ — question resolved, resume working
- ❌ → ⚙️ — error state, decide to retry based on experience
- ❌ → ❓ — error state, need clarification to proceed

## Plan Completion

When all phases and tasks reach ☑ (Done), produce a short completion report summarizing:
- What was accomplished (list of completed phases)
- Any blockers or errors that were resolved
- Any open questions or items left for future work
- Path to the PLAN.md file
