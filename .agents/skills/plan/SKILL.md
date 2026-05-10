---
name: plan
description: Phase/task based workflow system with PLAN.md as single source of truth. Use when tackling projects that require structured iteration through Planning, Analysis, Design, Implementation, Testing, Deployment, Maintenance, etc phases with clear dependency graphs.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.6"
tags:
  - meta
  - meta-skill
  - workflow
  - task-management
category: meta
---

# Plan - create, read, execute and update plan(s)

## Overview

Phase/task based planning system with `PLAN.md` as single source of truth.
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

1. **PLAN.md doesn't exist?** → Create `PLAN.md` with all phases based on given requirements. There are no predefined phases — determine them from context. Calibrate phase/task granularity to the requirements complexity and detect whether the requester is a beginner, advanced, or expert user. Ask clarifying questions before finalizing the plan. If unable to ask (non-interactive mode), proceed with best-effort assumptions and document them in the plan. After creating, run the validator (see ## Validation).
2. **PLAN.md exists?** → Open it. Examine `**Current Phase:**` and `**Current Task:**` and propose a continuation point (hint: the next pending task could be one of the lowest-numbered but in this order ⚙️ ❓ ❌ ☐). All running tasks have to be re-run with status ⚙️ because they were probably interrupted.

## Status Update Rules (MANDATORY)

**ALL status changes MUST use scripts. NEVER use `edit` or `write` to change
task, phase, plan emojis, or header fields.** The `edit` and `write` tools may only be used for structural changes: adding/removing phases or tasks, changing titles, updating dependencies, adding sub-bullets, or modifying non-status content.

After every PLAN.md edit (structural or status), run the validator (see ## Validation). If errors are reported, fix them before proceeding.

All PLAN.md edits must go through the atomic update pattern (see ## Atomic Updates)
to prevent concurrent processes from overwriting each other.

### After Writing PLAN.md — Validate Every Section

After writing or structurally editing a PLAN.md file, **always run the validator**
which checks all 8 sections:

```bash
bash scripts/validate-plan.sh path/to/PLAN.md
```

The validator reports errors section by section. Fix any errors before proceeding.
If the validator reports derivation mismatches, re-derive:

```bash
bash scripts/update-plan.sh path/to/PLAN.md rederive-all
```

### After Structural Edits — Use Scripts for Status/Header Updates

Once PLAN.md is written, **all subsequent updates to statuses and header fields must go through scripts**. The `edit` and `write` tools may only be used for structural changes (adding/removing phases or tasks). Even after structural edits, run the validator and re-derive emojis.

### Script Operations Reference

| Operation | Command |
|-----------|---------|
| **Status reads (lock-free, deterministic)** | |
| Get task status | `bash scripts/update-plan.sh PLAN.md get-task-status "Task X.Y"` |
| Get phase status | `bash scripts/update-plan.sh PLAN.md get-phase-status "Phase X"` |
| Get plan status | `bash scripts/update-plan.sh PLAN.md get-plan-status` |
| **Header reads (lock-free, deterministic)** | |
| Get current task | `bash scripts/update-plan.sh PLAN.md get-current-task` |
| Get current phase | `bash scripts/update-plan.sh PLAN.md get-current-phase` |
| Get plan title | `bash scripts/update-plan.sh PLAN.md get-plan-title` |
| Get depends-on | `bash scripts/update-plan.sh PLAN.md get-depends-on` |
| Get created timestamp | `bash scripts/update-plan.sh PLAN.md get-created` |
| Get all header fields | `bash scripts/update-plan.sh PLAN.md get-plan-header` |
| **Status writes (atomic, auto-derives emojis)** | |
| Set task status | `bash scripts/update-plan.sh PLAN.md set-task-status "Task X.Y" "⚙️"` |
| Set phase status | `bash scripts/update-plan.sh PLAN.md set-phase-status "Phase X" "⚙️"` |
| **Header writes (atomic, canonical format)** | |
| Set current task | `bash scripts/update-plan.sh PLAN.md set-current-task "⚙️ Task 2.3"` |
| Set current phase | `bash scripts/update-plan.sh PLAN.md set-current-phase "⚙️ Phase 2"` |
| Set plan title | `bash scripts/update-plan.sh PLAN.md set-plan-title "My Project"` |
| Set depends-on | `bash scripts/update-plan.sh PLAN.md set-depends-on "../other/PLAN.md"` |
| Update timestamp | `bash scripts/update-plan.sh PLAN.md update-timestamp` |
| **Re-derivation** | |
| Re-derive all emojis | `bash scripts/update-plan.sh PLAN.md rederive-all` |
| **Full workflow (edit + validate + rollback)** | |
| Any action with validation | `bash scripts/workflow.sh PLAN.md <action> [args...]` |

The scripts auto-derive phase emojis from tasks and plan emojis from phases.
You never set a phase or plan emoji manually — it is always derived.

**Plan emoji preservation on update:** When editing a PLAN.md for any reason
other than completing it (e.g., adding tasks, fixing content, updating
dependencies), only change the plan emoji to ☐ if it was previously ☑.
Otherwise preserve whatever status is present. The only statuses that persist
across non-completion edits are: ❓ ⚙️ ❌.

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

### Plan Status Derivation

The plan emoji is **derived from its phases**, not set independently:

- ☑ **Completed** — only when **all** phases have reached ☑
- ⚙️ **Active** — when at least one phase is ⚙️ or has a task that is ⚙️
- ❓ **Needs Clarification** — when no phase is ⚙️/☑ but at least one is ❓
- ❌ **Blocked** — when no phase is ⚙️/☑ but at least one is ❌
- ☐ **Not Started** — all phases are still ☐

When a plan transitions to ☑, it means every single task in every single phase
is ☑. The scripts auto-derive the plan emoji after edits, so this happens
automatically when using `update-plan.sh` or `workflow.sh`. Do not mark the
plan as completed until this condition is met.

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

The scripts (`update-plan.sh`, `workflow.sh`) auto-derive phase and plan
emojis after every task/phase status change. Phase and plan emojis are
always derived — never set manually.

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

Before producing the completion report, run the validator (see ## Validation).
The plan is only considered complete when the validator reports zero errors and
all tasks are ☑.

When all phases and tasks reach ☑ (Done), produce a short completion report summarizing:
- What was accomplished (list of completed phases)
- Any blockers or errors that were resolved
- Any open questions or items left for future work
- Path to the PLAN.md file

## Dependencies

Scripts require: bash 4+, awk, sed, grep, flock, mktemp, date.
All are available on Linux/macOS. On minimal containers, ensure `util-linux` (flock) is installed.

## Validation

After **every** PLAN.md edit (initial creation or subsequent updates), run the
validator script. This catches structural problems that manual editing can
introduce. Emoji derivation (does phase emoji match its tasks?) is checked
automatically — the validator focuses on things that fail silently.

Scripts live in `scripts/` relative to this SKILL.md. Use paths relative to
the skill directory:

```bash
bash scripts/validate-plan.sh path/to/PLAN.md
```

**What it validates (section by section):**
1. **Plan Header** — title line exists with valid emoji format (`# [emoji] Plan: Title`) and emoji is from allowed set
2. **Header Fields** — all required fields present (`Depends On`, `Created`, `Updated`, `Current Phase`, `Current Task`) with non-empty values
3. **Phases** — at least one phase, sequential numbering from 1, no duplicates, each has a title
4. **Tasks** — at least one task, sequential numbering within each phase, proper phase binding
5. **Emoji Validity** — all phase/task emojis are from the allowed set {☐ ❓ ⚙️ ❌ ☑}
6. **Zero-Task Phases** — flagged as warnings (can never reach ☑)
7. **Phase Emoji Derivation** — each phase emoji matches its derived status from tasks
8. **Plan Emoji Derivation** — plan emoji matches its derived status from phases

**What it does NOT validate (requires LLM judgment):**
- Dependency references point to existing tasks
- `**Current Phase:**` and `**Current Task:**` reference existing entries
- Whether the actual work described by a task was completed
- Whether acceptance criteria were met
- Semantic correctness of the plan content

## Atomic Updates

When multiple processes or agents might edit PLAN.md concurrently, use the
provided scripts for advisory locking and atomic writes. This prevents
overwrites and partial writes.

### Available Scripts

All paths are relative to this skill's directory (where SKILL.md lives).

| Script | Mode | Purpose |
|--------|------|---------|
| [scripts/update-plan.sh](scripts/update-plan.sh) | **Execute** | Lock-and-edit with `flock` + atomic rename. Supports all set/get actions for statuses, header fields, and re-derivation. Auto-derives phase and plan emojis after status changes. Read actions (`get-*`) are lock-free and deterministic. |
| [scripts/derive-phase-emoji.sh](scripts/derive-phase-emoji.sh) | **Execute** | Derive phase emoji from its tasks' emojis using AWK. Priority: ⚙️ > ❓ > ❌ > ☑ > ☐. |
| [scripts/derive-plan-emoji.sh](scripts/derive-plan-emoji.sh) | **Execute** | Derive plan emoji from all phases (re-deriving each phase from its tasks). Priority: ⚙️ > ❓ > ❌ > ☑ > ☐. |
| [scripts/workflow.sh](scripts/workflow.sh) | **Execute** | Full workflow: lock → edit (via update-plan.sh) → re-derive all phases → validate with automatic rollback on validation failure. Same actions as update-plan.sh plus read-through for `get-*`. |
| [scripts/common.sh](scripts/common.sh) | **Source** | Shared helpers: emoji constants, derivation functions, header field access, lock management. Sourced by other scripts — do not run directly. |

### Usage Examples

```bash
# Status reads (deterministic, no lock)
bash scripts/update-plan.sh PLAN.md get-task-status "Task 2.3"
bash scripts/update-plan.sh PLAN.md get-phase-status "Phase 2"
bash scripts/update-plan.sh PLAN.md get-plan-status

# Header reads (deterministic, no lock)
bash scripts/update-plan.sh PLAN.md get-current-task
bash scripts/update-plan.sh PLAN.md get-current-phase
bash scripts/update-plan.sh PLAN.md get-plan-title
bash scripts/update-plan.sh PLAN.md get-depends-on
bash scripts/update-plan.sh PLAN.md get-created
bash scripts/update-plan.sh PLAN.md get-plan-header

# Status writes (atomic, auto-derives phase + plan emojis)
bash scripts/update-plan.sh PLAN.md set-task-status "Task 2.3" "⚙️"
bash scripts/update-plan.sh PLAN.md update-timestamp
bash scripts/update-plan.sh PLAN.md set-current-task "⚙️ Task 2.3"

# Header writes (atomic, canonical format)
bash scripts/update-plan.sh PLAN.md set-plan-title "My Project"
bash scripts/update-plan.sh PLAN.md set-depends-on "../other/PLAN.md"

# Re-derive all emojis (fix stale phase/plan emojis)
bash scripts/update-plan.sh PLAN.md rederive-all

# Full workflow (edit + re-derive all phases + validate + rollback)
bash scripts/workflow.sh PLAN.md set-task-status "Task 2.3" "☑"

# Standalone derivation (read-only, no file changes)
echo "Phase 2 emoji: $(bash scripts/derive-phase-emoji.sh PLAN.md 2)"
echo "Plan emoji: $(bash scripts/derive-plan-emoji.sh PLAN.md)"

# Validation
bash scripts/validate-plan.sh PLAN.md
```

### Properties
- **`flock -w 30`** — blocks other writers, times out after 30s to avoid deadlocks (configurable via `PLAN_LOCK_TIMEOUT`)
- **Stale lock detection** — locks older than timeout with no holding process are automatically removed
- **`mktemp` + `mv -f`** — write to temp then atomic rename, so PLAN.md is never left partial
- **Advisory lock** — readers can still read PLAN.md while locked (they see the old version)
- **Automatic rollback** — `workflow.sh` backs up the file and restores it if validation fails
- **Cleanup on exit** — temp files, backups, and lock files are removed via trap on normal exit, INT, and TERM
- **Lock-free reads** — `get-*` actions skip locking entirely (read-only)
- **Lock file cleanup** — the physical `.lock` file is removed after each operation (flock advisory lock is released when the file descriptor closes; the script also removes the lock file itself via trap)
- **Nested lock safety** — `workflow.sh` sets `PLAN_SKIP_LOCK` when calling `update-plan.sh` to avoid deadlocks
- **Deterministic header access** — all `get-*` and `set-*` for header fields use canonical parsing/writing via `common.sh`, ensuring values are always read and written in a consistent format
