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

# Workflow - create, read, execute and update plan(s)

Phase/task based workflow system with `PLAN.md` as single source of truth.
There can be many `PLAN.md` files in different locations.
Plan files create a dependency graph via `**Depends on Plans:** ...`.
Strict phase numbering (`[emoji-of-phase] Phase X Phase Title`), inline phase dependency tracking, and emoji-coded statuses within current plan.
Strict task numbering (`[emoji-of-phase] Phase X - [emoji-of-task] Task X.Y Task Title`), inline phase/task dependency tracking, and emoji-coded statuses within current plan.

## First open

1. **PLAN.md doesn't exist?** → Create `PLAN.md` with all phases based on given requirements. There are no predefined phases — determine them from context. Calibrate phase/task granularity to the requirements complexity and detect whether the requester is a beginner, advanced, or expert user. Ask clarifying questions before finalizing the plan. If unable to ask (non-interactive mode), proceed with best-effort assumptions and document them in the plan.
2. **PLAN.md exists?** → Open it. Examine `**Current Phase:**` and `**Current Task:**` and propose a continuation point (hint: the next pending task could be one of the lowest-numbered but in this order ⚙️❓❌☐).

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
<!-- required: Plan Title is short but descriptive title of current plan -->
# [emoji-of-plan] Plan: Plan Title

<!-- required: default NONE if doesn't have dependencies, or relative paths to other PLAN.md files -->
**Depends on Plans:** ...
<!-- required: [emoji-of-phase] Phase X Phase Title -->
**Current Phase:** ...
<!-- required: [emoji-of-phase] Phase X - [emoji-of-task] Task X.Y -->
**Current Task:** ...
<!-- required: ISO 8601 / UTC (YYYY-MM-DDTHH:MM:SSZ) -->
**Created:** ...
<!-- required: ISO 8601 / UTC (YYYY-MM-DDTHH:MM:SSZ) -->
**Updated:** ...

<!-- required: PHASES with TASKS start here -->
...
```

## Emoji-coded statuses

Strictly use only the following emojis for statuses: ☐❓⚙️❌☑

Strictly use following emojis for `[emoji-of-phase]` and `[emoji-of-task]` status:

- ☐ **To Do** – backlog / new
- ❓ **Question** – question or clarification
- ⚙️ **Doing** – in progress / wip
- ❌ **Error** – error / failure
- ☑ **Done** – completed / done

These are valid state transitions:
- ☐ → ⚙️ — new item, everything seems clear, start working
- ☐ → ❓ — new item, something is unclear, ask for clarification
- ⚙️ → ❓ — during work, something unexpected happened, need clarification
- ⚙️ → ❌ — during work, critical error or blocker stopped progress
- ⚙️ → ☑ — during work, successfully completed
- ❓ → ⚙️ — question resolved, resume working
- ❌ → ⚙️ — error state, decide to retry based on experience
- ❌ → ❓ — error state, need clarification to proceed

⚙️ (Doing) is always required before reaching ☑ (Done). You cannot skip to Done from Question or Error states.

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
- ⚙️ → ❓ — during work, scope or requirements need re-evaluation
- ⚙️ → ❌ — critical blocker stops all progress across the plan
- ⚙️ → ☑ — all phases and tasks completed successfully
- ❓ → ⚙️ — clarifications resolved, begin work
- ❌ → ⚙️ — blocker resolved, resume work
- ❌ → ❓ — need clarification on how to resolve the blocker

⚙️ (Active) is always required before reaching ☑ (Completed). You cannot skip to Completed from Not Started or Blocked states.

### Automatic Plan Status Derivation

When updating `**Current Phase:**` or `**Current Task:**`, derive `[emoji-of-plan]` from the aggregate state of all phases and tasks:

1. If **all** phases are ☑ → set plan to ☑ (Completed)
2. If **any** phase or task is ❌ and no task is ⚙️ → set plan to ❌ (Blocked)
3. If **any** task is ❓ and no task is ⚙️ → set plan to ❓ (Needs Clarification)
4. If **any** task is ⚙️ → set plan to ⚙️ (Active)
5. If all phases/tasks are ☐ and none have started → set plan to ☐ (Not Started)

Update `[emoji-of-plan]` in the plan title whenever any phase or task status changes.

## Plan

**PLAN.md = single source of truth**: project with dependency graph.
Multiple `PLAN.md` files can exist in different locations.
They form a directed acyclic graph (DAG) via the required `**Depends on Plans:**` header field:
- Multiple dependencies are comma-separated with spaces: `../a/PLAN.md , ../../b/PLAN.md`
- Default value is `NONE` when the plan has no dependencies
- Cycles are not allowed. Check for cycles whenever any plan is created or when `**Depends on Plans:**` is modified. If a cycle is detected (including transitive cycles), report it to the user and stop until resolved
- The dependency graph is resolved transitively by visiting referenced `PLAN.md` headers — not inline-expanded
- When a dependency is incomplete, ask what to do before proceeding

## Phases

Phase is strictly formatted as `[emoji-of-phase] Phase X Phase Title`, where X is unique ID (X = phase number, starting from 1).
Every Phase **MUST** have a unique ID in the exact format `[emoji-of-phase] Phase X` (X = phase number, starting from 1).
All phases, tasks and their additions, changes, removals, transitions and dependencies live ONLY in `PLAN.md` file.

If a phase has zero tasks, emit a warning — it can never reach ☑ (Done) and is likely a mistake.

## Tasks

Task is strictly formatted as `[emoji-of-phase] Phase X - [emoji-of-task] Task X.Y Task Title` (X = phase number, Y = sequential task number **within that phase**).
Every task **MUST** have a unique ID in the exact format `[emoji-of-phase] Phase X - [emoji-of-task] Task X.Y` (X = phase number, Y = sequential task number **within that phase**).

Task dependencies are **phase-bound by default** (most will be same-phase).

When a task has dependencies, append to the task title the suffix `(depends on: A , B , ...)`. If a task has no dependencies, don't append `(depends on: ...)` to it.

For task that is phase-bound dependencies, `A`, `B`, etc, are dependencies of form `Task X.Y` where `X` is current phase.

For cross-phase task dependencies, `A`, `B`, etc, are explicitly allowed and listed with full `Phase X - Task X.Y` where `X` can be phase ID from that other phase and `Y` matches task ID from its own phase.

This creates a clear directed graph that any reader (human or agent) can parse instantly.

## Plan Completion

When all phases and tasks reach ☑ (Done), produce a short completion report summarizing:
- What was accomplished (list of completed phases)
- Any blockers or errors that were resolved
- Any open questions or items left for future work
- Path to the PLAN.md file
