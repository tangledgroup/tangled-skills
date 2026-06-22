# Phases and Tasks

## Phases

Add phases with `plan.sh add-phase`. Each phase has a unique ID in the format `Phase X` (X = sequential number starting from 1).

Phases are inserted in ascending numeric order — adding Phase 3 after Phase 1 places it correctly. Use `plan.sh sort PLAN.md` to reorder if phases become out of order.

A phase with zero tasks can never reach ✅ (Done) and is likely a mistake — the script will warn.

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

Dependencies are managed with `plan.sh add-task-dependency` and `plan.sh remove-task-dependency`. Dependent tasks must reach ✅ before the current task can proceed.

For **phase-bound** dependencies (same phase), reference by task ID: `Task X.Y`.
For **cross-phase** dependencies, use full form: `Phase X - Task X.Y`.

`plan.sh` enforces dependency satisfaction: it will **reject** transitioning a task to ⚙️ if any dependency is not ✅.

## Argument Convention

Phase and task commands accept ID and title as **separate arguments**, making them easier for smaller models to construct correctly:

- Phase: `add-phase PLAN.md "Phase 2" "Description"` — ID required, title optional
- Task: `add-task PLAN.md "Phase 2" "Task 2.4" "Description"` — task ID optional (auto-numbered if omitted), title required

For `add-phase` and `add-task`: if the ID argument starts with `Phase N` or `Task X.Y`, that number is used; otherwise, the next sequential number is auto-assigned. Omit the ID to auto-number.

Dependencies are always added separately with `add-task-dependency`.

**Title validation:** Titles cannot be empty, must not contain newlines, and are limited to 2048 characters. The script rejects invalid titles with a clear error message.
