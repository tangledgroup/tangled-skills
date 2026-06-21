---
name: plan
description: Phase/task based workflow system with PLAN.md as single source of truth. Use when tackling projects that require structured iteration through Planning, Analysis, Design, Implementation, Testing, Deployment, Maintenance, etc phases with clear dependency graphs.
metadata:
  tags:
    - meta
---

# plan

Phase/task based workflow system with `PLAN.md` as single source of truth.

## Overview

Structured planning system using phases and tasks, tracked in `PLAN.md` files.

### Rules

1. **Always use `plan.sh` — never write or edit PLAN.md directly.** The LLM should not generate PLAN.md content itself. All operations (create, add, update, remove, status changes) go through `plan.sh` commands. Scripts enforce status transitions, auto-derive emojis, detect dependency cycles, and maintain integrity via checksums. Direct edits bypass all safeguards and corrupt the plan.
2. **Smaller models especially must not hallucinate PLAN.md content.** When unsure of a command, read the Usage section or run `plan.sh --help`. Do not guess the file format.
3. **There can be multiple `PLAN.md` files** in different locations, forming a DAG via `Depends On` headers.
4. **Status emojis are derived automatically** by the script after every mutation.** Prefer relying on auto-derivation. `set-plan-status` and `set-phase-status` exist for manual override (e.g., marking a plan as ❓ when scope is unclear), but `check --fix` will re-derive them from actual task states.

### File Format (for understanding only)

The structure below describes what `plan.sh` produces. Do not write it yourself.

- Title: `# [emoji] Plan ➖ Title`
- Header fields: `Depends On`, `Created`, `Updated`, `Current Phase`, `Current Task`
- Phases: `## [emoji] Phase N ➖ Title` with numbered tasks underneath
- Tasks: `- [emoji] Task X.Y ➖ Title ⚓ ...` (dependencies optional)
- Checksum comment at bottom for integrity verification

## When to Use

Use this skill when:
- Starting a project that requires structured phase-by-phase execution
- Tackling complex tasks with multiple dependent steps (implementation, testing, deployment)
- Coordinating work across multiple `PLAN.md` files with inter-plan dependencies
- Resuming interrupted work by tracking current phase and task state
- Validating plan consistency — run `plan.sh check PLAN.md --fix` to detect and repair issues
- Any workflow needing a single source of truth for progress

## PLAN.md Structure

`PLAN.md` files are created and modified exclusively via `plan.sh`. The file structure is an implementation detail of the script — do not write or edit it manually. Use `plan.sh get-plan PLAN.md --tree --json` to inspect a plan's structure.

## Universal emoji-coded statuses

Strictly use only the following emojis for statuses: ☐ ❓ ⚙️ ❌ ☑
⚙️ (Doing) is always required before reaching ☑ (Done).

## Plan Statuses

The plan itself carries a status via `[emoji-of-plan]` in its title:
```
# [emoji-of-plan] Plan ➖ Plan Title
```

Strictly use following emojis for `[emoji-of-plan]` status:

- ☐ **Todo** — plan created but no work has begun on any phase or task
- ❓ **Question** — plan exists but requirements or scope need clarification before work can begin
- ⚙️ **Doing** — at least one phase or task is in progress
- ❌ **Error** — cannot proceed due to dependency cycles, unresolved external blockers, or critical failures across the plan
- ☑ **Done** — all phases and all tasks within them have reached ☑

### Plan Status Transitions

These are valid state transitions for `[emoji-of-plan]`:

- ☐ → ⚙️ — begin work on the plan (start first task)
- ☐ → ❓ — plan created but scope or requirements need clarification before starting
- ⚙️ → ❓ — during work, something unexpected happened, need clarification
- ⚙️ → ❌ — critical error or blocker stops all progress across the plan
- ⚙️ → ☑ — all phases and tasks completed successfully
- ❓ → ⚙️ — question resolved, begin work
- ❓ → ❌ — during clarification, a critical blocker was discovered that makes the plan unactionable (e.g., required infrastructure unavailable, budget cut, technology incompatible). Marking ❌ signals "cannot proceed until this blocker is resolved" without requiring ⚙️ first. Run `check --fix` to restore the derived value from actual task states.
- ❌ → ⚙️ — error resolved, resume work
- ❌ → ❓ — need clarification to proceed

⚙️ (Doing) is always required before reaching ☑ (Done). You cannot skip to Done from Todo or Error states.

These transitions are **enforced by `plan.sh`** — calling `plan.sh set-task-status` with an invalid transition will error. Do not manually set emojis in PLAN.md.

### Plan Status Derivation

The plan emoji is **derived from its phases**, not set independently:

- ☑ **Done** — only when **all** phases have reached ☑
- ⚙️ **Doing** — when at least one phase is ⚙️ or has a task that is ⚙️
- ❓ **Question** — when no phase is ⚙️/☑ but at least one is ❓
- ❌ **Error** — when no phase is ⚙️/☑ but at least one is ❌
- ☐ **Todo** — fallback (all phases are ☐, or mixed with no active status)

When a plan transitions to ☑, it means every single task in every single phase is ☑. The script auto-derives the plan emoji after every edit. Do not mark the plan as completed until this condition is met.

**Manual override:** `set-plan-status` and `set-phase-status` allow temporary manual overrides (e.g. marking a plan as ❓ when scope is unclear). Plan-level overrides additionally allow ❓ → ❌ (blocker discovered during clarification). Run `check --fix` to restore derived values from actual task/phase states.

## Plan Dependencies

Multiple `PLAN.md` files can exist in different locations, forming a directed acyclic graph (DAG) via the `Depends On` header field. Manage dependencies with `plan.sh set-plan-depends-on`.

- Multiple dependencies are comma-separated with spaces: `../a/PLAN.md , ../../b/PLAN.md`
- Default value is `NONE` when the plan has no dependencies
- Cycles are not allowed. The script checks for cycles (including transitive) whenever `Depends On` is modified. If a cycle is detected, report it to the user and stop until resolved
- The dependency graph is resolved transitively by visiting referenced `PLAN.md` headers — not inline-expanded
- When a dependency is incomplete, ask the user what to do before proceeding

## Phases

Add phases with `plan.sh add-phase`. Each phase has a unique ID in the format `Phase X` (X = sequential number starting from 1).

Phases are inserted in ascending numeric order — adding Phase 3 after Phase 1 places it correctly. Use `plan.sh sort PLAN.md` to reorder if phases become out of order.

A phase with zero tasks can never reach ☑ (Done) and is likely a mistake — the script will warn.

## Tasks

Add tasks with `plan.sh add-task`. Each task has a unique ID in the format `Task X.Y` (X = phase number, Y = sequential task number within that phase).

Tasks are inserted in ascending numeric order within their phase. Use `plan.sh sort PLAN.md` to reorder if tasks become out of order.

**Creating a phase inline:** When adding a task to a phase that doesn't exist yet, first create the phase with `add-phase`, then add the task. This avoids ambiguity and is clearer for smaller models.

Sub-bullets under a task are optional — they capture acceptance criteria, implementation notes, or context. They carry no status tracking and do not affect plan status derivation.

### Task Granularity

Each task should be small enough to complete in one focused work session and large enough to produce a verifiable outcome:

- One task = one clear deliverable (a file, a function, a test, a config change)
- If a task requires more than three sub-steps, split it into separate tasks
- Tasks within a phase should be roughly comparable in scope
- Use sub-bullets under the task to record acceptance criteria or key details

### Task Dependencies

Dependencies are managed with `plan.sh add-task-dependency` and `plan.sh remove-task-dependency`. Dependent tasks must reach ☑ before the current task can proceed.

For **phase-bound** dependencies (same phase), reference by task ID: `Task X.Y`.
For **cross-phase** dependencies, use full form: `Phase X - Task X.Y`.

`plan.sh` enforces dependency satisfaction: it will **reject** transitioning a task to ⚙️ if any dependency is not ☑.

## Phase Status Derivation

A phase emoji is **derived from its tasks**, not set independently:

- ☑ **Done** — only when **all** tasks within the phase have reached ☑
- ⚙️ **Doing** — when at least one task is ⚙️ (Doing)
- ❓ **Question** — when no task is ⚙️ or ☑ but at least one is ❓
- ❌ **Error** — when no task is ⚙️ or ☑ but at least one is ❌
- ☐ **Todo** — fallback (all tasks are ☐, or mixed ☑+☐ with no active status)

The script auto-derives phase and plan emojis after every mutation. You can temporarily override with `set-plan-status` or `set-phase-status`, but `check --fix` will restore derived values.

**Error propagation:** When a task reaches ❌ (Error), its phase derives to ❌, and the plan derives to ❌ if no other phase is ⚙️ or ☑. Error cascades up: Task ❌ → Phase ❌ → Plan ❌. This means a single failed task can block the entire plan status from reaching ☑.

## Phase and Task Statuses

Strictly use following emojis for `[emoji-of-phase]` and `[emoji-of-task]` status:

- ☐ **Todo** – backlog / new
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

## Argument Convention

Phase and task commands accept ID and title as **separate arguments**, making them easier for smaller models to construct correctly:

- Phase: `add-phase PLAN.md "Phase 2" "Description"` — ID required, title optional
- Task: `add-task PLAN.md "Phase 2" "Task 2.4" "Description"` — task ID optional (auto-numbered if omitted), title required

For `add-phase` and `add-task`: if the ID argument starts with `Phase N` or `Task X.Y`, that number is used; otherwise, the next sequential number is auto-assigned. Omit the ID to auto-number.

Dependencies are always added separately with `add-task-dependency`.

**Title validation:** Titles cannot be empty, must not contain newlines, and are limited to 2048 characters. The script rejects invalid titles with a clear error message.

## Plan Completion

Run `plan.sh check PLAN.md` before producing the completion report. The plan is complete only when the validator reports zero errors and all tasks are ☑.

When complete, produce a short report summarizing:
- What was accomplished (list of completed phases)
- Any blockers or errors that were resolved
- Any open questions or items left for future work
- Path to the PLAN.md file

## Dependency Management

Manage dependencies incrementally as you identify them using `plan.sh add-task-dependency` and `plan.sh remove-task-dependency`. Don't wait until all tasks are listed.

- **Add dependencies** when a new task depends on an existing one, or cross-phase prerequisites are discovered
- **Remove dependencies** when restructuring makes them invalid, or a task split moves the dependency

There is no bulk command — call `add-task-dependency` for each individual edge.

## Gotchas

- **Never generate PLAN.md content with the LLM** — do not write, edit, or append to PLAN.md using text generation. Always use `plan.sh` commands. The script enforces status transitions, auto-derives emojis, checks dependency cycles, and maintains a SHA-256 checksum. Any direct edit will cause checksum failures and silent corruption.
- **Do not guess PLAN.md format** — if you are unsure of a command, read the Usage section below or run `plan.sh --help`. Smaller models are especially prone to hallucinating file content. Resist this impulse.
- **Never remove-and-re-add phases or tasks** — use update commands (`update-phase`, `update-task`, `set-task-status`, `add-task-dependency`). Removing and re-adding loses numbering continuity, breaks dependencies, and resets statuses. Only remove when the item is genuinely no longer part of the plan.
- **Updating a plan usually means changing statuses** — most "updates" are status transitions (`set-task-status`, `set-phase-status`). Title/description changes via `update-phase` / `update-task` are rare and should only happen when scope changes. Use sub-bullets for added details.
- **Run `plan.sh check PLAN.md --fix` after any plan update** — validates checksum integrity, emoji derivation, numbering gaps, ordering, and dependency references. The `--fix` flag auto-repairs recoverable issues (wrong emojis, numbering gaps, out-of-order items, dangling dependency references). When tasks are renumbered, self-dependencies created by the rename are automatically removed.
- **Titles must be non-empty and single-line** — empty titles, titles with newlines, or titles exceeding 2048 characters are rejected. This prevents file format corruption from multi-line entries.
- **All subcommands output JSON** — parse the `status` field to determine success/error. Use `"success"`, `"warning"`, `"error"`, or `"skipped"` (in batch mode when a previous step failed).
- **Batch mode preserves successful mutations on error** — if any step fails, PLAN.md IS written with all successful changes applied up to that point. If the failed command is `set-task-status`, the task is marked ❌ (Error) so you can see what happened. Remaining steps are marked `"skipped"` and not executed.
- **Error propagates up through the hierarchy** — a single task at ❌ causes its phase to derive as ❌, which can cause the entire plan to derive as ❌. To unblock the plan, resolve the error task (`❌ → ⚙️ → ☑`) or mark it as done if the error was a false alarm.
- **Direct status overrides require valid transitions** — `set-plan-status` and `set-phase-status` follow transition rules. Tasks and phases cannot jump from ☐ to ❌ (must go through ⚙️ first: `☐ → ⚙️ → ❌`). Plan-level transitions additionally allow ❓ → ❌ (discovered a blocker during clarification). Use `check --fix` to restore auto-derived values.

## Dependencies

Scripts require: `python3` 3.10+ with only built-in modules, and no third-party packages needed.

## Usage

Use `plan.sh` for every PLAN.md operation. Never edit PLAN.md directly — not even to fix a typo or add a comment. The script is the only valid way to interact with plan files.

### JSON Output

Every subcommand outputs valid JSON to stdout with these fields:
- **`status`** — one of: `"success"`, `"warning"`, `"error"`, or `"skipped"`
- **`command`** — the subcommand name (e.g., `"add-phase"`)
- **`message`** — human-readable description
- Additional fields vary by command (e.g., `path`, `value`, `data`, `issues`)

On error, exit code is 1. On success or warning, exit code is 0.

### Batch Mode — Preserve Mutations, Mark Errors

In batch mode, if any step returns `"error"`, all remaining steps are marked as `"skipped"` and not executed. Successful mutations are preserved and written to PLAN.md. If the failed step is `set-task-status`, the task is automatically marked ❌ (Error) so the plan reflects what actually happened. This allows mixing mutating and read-only operations in the same batch.

```bash
#
# Create a new PLAN.md with header
#
plan.sh create PLAN.md "My Project"
plan.sh create PLAN.md "Plan ABC" "../other/PLAN.md"
plan.sh create PLAN.md "Plan XYZ" "../a/PLAN.md" "../../b/PLAN.md"

#
# Header reads
#
plan.sh get-plan-title PLAN.md
plan.sh get-plan-depends-on PLAN.md
plan.sh get-plan-created PLAN.md
plan.sh get-plan-updated PLAN.md
plan.sh get-plan-current-phase PLAN.md
plan.sh get-plan-current-task PLAN.md

#
# Header writes
#
plan.sh set-plan-title PLAN.md "My Project"
plan.sh set-plan-depends-on PLAN.md NONE
plan.sh set-plan-depends-on PLAN.md "../other/PLAN.md"
plan.sh set-plan-depends-on PLAN.md "../a/PLAN.md" "../../b/PLAN.md"
plan.sh set-plan-created PLAN.md --now # UTC ISO format "%Y-%m-%dT%H:%M:%SZ"
plan.sh set-plan-created PLAN.md $(date -u +"%Y-%m-%dT%H:%M:%SZ")
plan.sh set-plan-updated PLAN.md --now # UTC ISO format "%Y-%m-%dT%H:%M:%SZ"
plan.sh set-plan-updated PLAN.md $(date -u +"%Y-%m-%dT%H:%M:%SZ")
plan.sh set-plan-current-phase PLAN.md "Phase 2" # copies `[emoji-of-phase]` of "Phase 2"
plan.sh set-plan-current-task PLAN.md "Task 2.3" # copies `[emoji-of-task]` of "Task 2.3"

#
# Status reads
#
plan.sh get-plan-status PLAN.md # returns `[emoji-of-plan]` of plan
plan.sh get-phase-status PLAN.md "Phase 2" # returns `[emoji-of-phase]` of "Phase 2"
plan.sh get-task-status PLAN.md "Task 2.3" # returns `[emoji-of-task]` of "Task 2.3"

#
# Status writes
#
plan.sh set-all-statuses PLAN.md ☐ # set plan, all phases, and all tasks status to be the same - use with caution
plan.sh set-plan-status PLAN.md ⚙️ # manual override — `check --fix` re-derives from phases
plan.sh set-phase-status PLAN.md "Phase 2" ⚙️ # manual override — `check --fix` re-derives from tasks
plan.sh set-task-status PLAN.md "Task 2.3" ⚙️ # sets `[emoji-of-task]` for "Task 2.3"

#
# add-phase — ID and title as separate arguments
#
plan.sh add-phase PLAN.md "Phase 2" "Description of phase..." # explicit phase number + title
plan.sh add-phase PLAN.md "Planning" # auto-numbered (no explicit ID)

#
# add-task — phase ref, task ID, and title as separate arguments
#
plan.sh add-task PLAN.md "Phase 2" "Task 2.4" "Description of task..." # explicit task number + title
plan.sh add-task PLAN.md "Phase 2" "Do thing" # auto-numbered
# to add a task to a new phase, create the phase first:
#   plan.sh add-phase PLAN.md "Phase 2" "New Phase"
#   plan.sh add-task PLAN.md "Phase 2" "Task 2.1" "First task"

#
# update-phase — phase ref and optional new title
#
plan.sh update-phase PLAN.md "Phase 2" "New description of phase..." # change title
plan.sh update-phase PLAN.md "Phase 2" # no-op (title unchanged)

#
# update-task — phase ref, task ref, and optional new title
#
plan.sh update-task PLAN.md "Phase 2" "Task 2.4" "New description of task..." # change title
plan.sh update-task PLAN.md "Phase 2" "Task 2.4" # no-op (title unchanged)

#
# remove-phase
#
plan.sh remove-phase PLAN.md "Phase 2" # re-derives plan status from remaining phases

#
# remove-task
#
plan.sh remove-task PLAN.md "Phase 2" "Task 2.4" # re-derives phase and plan status from remaining tasks

#
# add-task-dependency
# 
plan.sh add-task-dependency PLAN.md "Phase 2" "Task 2.4" "Task 2.1" # re-derives phase and plan status
plan.sh add-task-dependency PLAN.md "Phase 3" "Task 3.5" "Task 3.4" # re-derives phase and plan status

#
# remove-task-dependency
# 
plan.sh remove-task-dependency PLAN.md "Phase 2" "Task 2.4" "Task 2.1" # re-derives phase and plan status
plan.sh remove-task-dependency PLAN.md "Phase 3" "Task 3.5" "Task 3.4" # re-derives phase and plan status

#
# sort — reorder phases and tasks by number
#
plan.sh sort PLAN.md  # sorts phases by number, then tasks within each phase

#
# check — validate PLAN.md consistency (with optional --fix)
#
# Checks: checksum, emoji derivation, numbering gaps/duplicates,
# ordering, dangling deps, empty phases.
plan.sh check PLAN.md              # report issues
plan.sh check PLAN.md --fix        # report + auto-fix recoverable issues

#
# get-plan — structured plan output (read-only, no file lock needed)
#
# View modes: --list (flat) or --tree (nested). Default: --list.
# Output formats: --json or --yaml. Default: --json.
#
plan.sh get-plan PLAN.md                 # default: --list --json
plan.sh get-plan PLAN.md --list --json   # flat list, JSON (same as default)
plan.sh get-plan PLAN.md --list --yaml   # flat list, YAML
plan.sh get-plan PLAN.md --tree --json   # nested tree, JSON
plan.sh get-plan PLAN.md --tree --yaml   # nested tree, YAML

#
# batch — chain multiple operations under a single lock
# Reads commands from stdin or a file (--input FILE). Mode auto-detected from
# file extension: .txt/.md → line mode, .json → JSON mode. Use --json to force.
#
# Line mode (stdin):
#   echo 'create "My Project"
#   add-phase "Phase 1" "Planning"
#   add-task "Phase 1" "Task 1.1" "Define scope"' | plan.sh batch PLAN.md
#
# Line mode (.txt or .md file):
#   plan.sh batch --input commands.txt PLAN.md
#   plan.sh batch --input commands.md PLAN.md
#
# JSON mode (stdin with --json flag):
#   echo '[{"command":"create","args":["My Project"]},'
#   '{"command":"add-phase","args":["Phase 1","Planning"]}]' | plan.sh batch --json PLAN.md
#
# JSON mode (.json file, auto-detected):
#   plan.sh batch --input commands.json PLAN.md
#
# Force JSON mode on non-.json file:
#   plan.sh batch --input commands.txt --json PLAN.md
#
# Both modes produce identical output. All mutating commands are supported.
# Lines starting with # are treated as comments (line mode only).
#
# Output is a JSON object with "status" and "results" array.
# If any step fails ("error"), remaining steps are marked "skipped".
# PLAN.md IS written with all successful mutations applied.
# If the failed step is set-task-status, the task is marked ❌ (Error).
```
