# Plan Structure

## PLAN.md Structure

`PLAN.md` files are created and modified exclusively via `plan.sh`. The file structure is an implementation detail of the script — do not write or edit it manually. Use `plan.sh get-plan PLAN.md --tree --json` to inspect a plan's structure.

## Universal Emoji-Coded Statuses

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

## Plan Status Derivation

The plan emoji is **derived from its phases**, not set independently:

- ☑ **Done** — only when **all** phases have reached ☑
- ⚙️ **Doing** — when at least one phase is ⚙️ or has a task that is ⚙️
- ❓ **Question** — when no phase is ⚙️/☑ but at least one is ❓
- ❌ **Error** — when no phase is ⚙️/☑ but at least one is ❌
- ☐ **Todo** — fallback (all phases are ☐, or mixed with no active status)

When a plan transitions to ☑, it means every single task in every single phase is ☑. The script auto-derives the plan emoji after every edit. Do not mark the plan as completed until this condition is met.

**Manual override:** `set-plan-status` and `set-phase-status` allow temporary manual overrides (e.g. marking a plan as ❓ when scope is unclear). Plan-level overrides additionally allow ❓ → ❌ (blocker discovered during clarification). Run `check --fix` to restore derived values from actual task/phase states.

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
