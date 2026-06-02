---
name: plan
description: Phase/task based workflow system with PLAN.md as single source of truth. Use when tackling projects that require structured iteration through Planning, Analysis, Design, Implementation, Testing, Deployment, Maintenance, etc phases with clear dependency graphs.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.9"
tags:
  - meta
  - meta-skill
  - plan
  - workflow
  - task-management
category: meta
---

# Plan - create, read, execute and update plan(s)

## Overview

Plan/phase/task based planning system with `PLAN.md` as single source of truth.
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

## PLAN.md Header Template

Command `python3 -B scripts/plan.py PLAN.md create ...` creates PLAN.md like:

```markdown
<!-- Plan Title is short but descriptive title of current plan -->
# ☐ Plan: Plan Title

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

### Plan Status Derivation

The plan emoji is **derived from its phases**, not set independently:

- ☑ **Completed** — only when **all** phases have reached ☑
- ⚙️ **Active** — when at least one phase is ⚙️ or has a task that is ⚙️
- ❓ **Needs Clarification** — when no phase is ⚙️/☑ but at least one is ❓
- ❌ **Blocked** — when no phase is ⚙️/☑ but at least one is ❌
- ☐ **Not Started** — all phases are still ☐

When a plan transitions to ☑, it means every single task in every single phase is ☑. The script auto-derives the plan emoji after edits, so this happens automatically when using `plan.py`. Do not mark the plan as completed until this condition is met.

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

## Phase Status Derivation

A phase emoji is **derived from its tasks**, not set independently:

- ☑ **Done** — only when **all** tasks within the phase have reached ☑
- ⚙️ **Active** — when at least one task is ⚙️ (Doing)
- ❓ **Needs Clarification** — when no task is ⚙️ or ☑ but at least one is ❓
- ❌ **Blocked** — when no task is ⚙️ or ☑ but at least one is ❌
- ☐ **To Do** — all tasks are still ☐

The script (`plan.py`) auto-derives phase and plan emojis after every task status change. Phase and plan emojis are always derived — never set manually.

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

Before producing the completion report, run the validator. The plan is only considered complete when the validator reports zero errors and all tasks are ☑.

When all phases and tasks reach ☑ (Done), produce a short completion report summarizing:
- What was accomplished (list of completed phases)
- Any blockers or errors that were resolved
- Any open questions or items left for future work
- Path to the PLAN.md file

## Dependencies

Scripts require: `python3` 3.10+ with only built-in modules (`argparse`, `re`, `sys`, `datetime`, `pathlib`).
No third-party packages needed.

### Usage Examples

Always use scripts to update `PLAN.md`.

```bash
#
# Create a new PLAN.md with header
#
python3 -B scripts/plan.py PLAN.md create "My Project"
python3 -B scripts/plan.py PLAN.md create "Plan ABC" "../other/PLAN.md"
python3 -B scripts/plan.py PLAN.md create "Plan XYZ" "../a/PLAN.md" "../../b/PLAN.md"

#
# Header reads
#
python3 -B scripts/plan.py PLAN.md get-plan-title
python3 -B scripts/plan.py PLAN.md get-plan-depends-on
python3 -B scripts/plan.py PLAN.md get-plan-created
python3 -B scripts/plan.py PLAN.md get-plan-updated
python3 -B scripts/plan.py PLAN.md get-plan-current-phase
python3 -B scripts/plan.py PLAN.md get-plan-current-task

#
# Header writes
#
python3 -B scripts/plan.py PLAN.md set-plan-title "My Project"
python3 -B scripts/plan.py PLAN.md set-plan-depends-on NONE
python3 -B scripts/plan.py PLAN.md set-plan-depends-on "../other/PLAN.md"
python3 -B scripts/plan.py PLAN.md set-plan-depends-on "../a/PLAN.md" "../../b/PLAN.md"
python3 -B scripts/plan.py PLAN.md set-plan-created --now # UTC ISO format "%Y-%m-%dT%H:%M:%SZ"
python3 -B scripts/plan.py PLAN.md set-plan-created $(date -u +"%Y-%m-%dT%H:%M:%SZ")
python3 -B scripts/plan.py PLAN.md set-plan-updated --now # UTC ISO format "%Y-%m-%dT%H:%M:%SZ"
python3 -B scripts/plan.py PLAN.md set-plan-updated $(date -u +"%Y-%m-%dT%H:%M:%SZ")
python3 -B scripts/plan.py PLAN.md set-plan-current-phase "Phase 2" # copies `[emoji-of-phase]` of "Phase 2"
python3 -B scripts/plan.py PLAN.md set-plan-current-task "Task 2.3" # copies `[emoji-of-task]` of "Task 2.3"

#
# Status reads
#
python3 -B scripts/plan.py PLAN.md get-plan-status # returns `[emoji-of-plan]` of plan
python3 -B scripts/plan.py PLAN.md get-phase-status "Phase 2" # returns `[emoji-of-phase]` of "Phase 2"
python3 -B scripts/plan.py PLAN.md get-task-status "Task 2.3" # returns `[emoji-of-task]` of "Task 2.3"

#
# Status writes
#
python3 -B scripts/plan.py PLAN.md set-all-statuses ☐ # set plan, all phases, and all tasks status to be the same - use with caution
python3 -B scripts/plan.py PLAN.md set-plan-status ⚙️ # sets `[emoji-of-plan]` for plan
python3 -B scripts/plan.py PLAN.md set-phase-status "Phase 2" ⚙️ # sets `[emoji-of-phase]` for "Phase 2"
python3 -B scripts/plan.py PLAN.md set-task-status "Task 2.3" ⚙️ # sets `[emoji-of-task]` for "Task 2.3"

# 
# add-phase
# 
python3 -B scripts/plan.py PLAN.md add-phase "Phase 2 - Description of phase..." # sets phase status to ☐

#
# add-task
#
python3 -B scripts/plan.py PLAN.md add-task "Phase 2" "Task 2.4 - Description of task..." # sets task status to ☐, phase status ❓
# or
python3 -B scripts/plan.py PLAN.md add-task "Phase 2 - Description of phase..." "Task 2.4 - Description of task..." # sets task status to ☐, phase status ❓

#
# update-phase
#
python3 -B scripts/plan.py PLAN.md update-phase "Phase 2 - New description of phase..." # sets phase status to ❓

#
# update-task
#
python3 -B scripts/plan.py PLAN.md update-task "Phase 2" "Task 2.4 - New description of task..." # sets status to ❓
# or
python3 -B scripts/plan.py PLAN.md update-task "Phase 2 - New description of phase..." "Task 2.4 - New description of task..." # sets status to ❓

#
# remove-phase
#
python3 -B scripts/plan.py PLAN.md remove-phase "Phase 2" # sets plan status to ❓
# or
python3 -B scripts/plan.py PLAN.md remove-phase "Phase 2 - Description of phase..." # sets plan status to ❓

#
# remove-task
#
python3 -B scripts/plan.py PLAN.md remove-task "Phase 2" "Task 2.4" # sets plan and phase status to ❓
# or
python3 -B scripts/plan.py PLAN.md remove-task "Phase 2" "Task 2.4 - Description of task..." # sets plan and phase status to ❓
# or
python3 -B scripts/plan.py PLAN.md remove-task "Phase 2 - Description of phase..." "Task 2.4 - Description of task..." # sets plan and phase status to ❓
```
