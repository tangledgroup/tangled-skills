# Plan Demos

Valid PLAN.md files demonstrating `plan.sh` subcommand execution patterns and all status combinations. All files pass `plan.sh check`.

## One-by-One Subcommand Execution

| File | Description | Plan Status | Phase Statuses |
|---|---|---|---|
| [demo-mixed-statuses.md](demo-mixed-statuses.md) | Full stack app with mixed statuses, cross-phase deps, current phase/task tracking | ⚙️ Doing | ☑ Done, ⚙️ Doing, ❓ Question, ⚙️ Doing |
| [demo-question-state.md](demo-question-state.md) | Plan blocked by clarification needs in Phase 2 | ❓ Question | ☑ Done, ❓ Question, ☐ Todo |
| [demo-error-cascade.md](demo-error-cascade.md) | Single task error cascades: Task ❌ → Phase ❌ → Plan ❌ | ❌ Error | ☑ Done, ❌ Error, ☐ Todo |

## Batch Subcommand Execution

### Line Mode (stdin / .txt / .md files)

| File | Description | Plan Status | Notes |
|---|---|---|---|
| [demo-batch-line-mode.md](demo-batch-line-mode.md) | Auth service redesign built entirely via batch line mode | ⚙️ Doing | Phases 1-3, statuses set in same batch |

### JSON Mode (.json files / stdin with --json)

| File | Description | Plan Status | Notes |
|---|---|---|---|
| [demo-batch-json-mode.md](demo-batch-json-mode.md) | Database migration built entirely via batch JSON mode | ☑ Done | All tasks completed, demonstrates full completion |

### Batch Error Handling

| File | Description | Plan Status | Notes |
|---|---|---|---|
| [demo-batch-error-handling.md](demo-batch-error-handling.md) | Invalid transition (☐→❌) triggers error; successful mutations preserved, remaining steps skipped | ❌ Error | Demonstrates batch fault tolerance: Task 2.1 auto-marked ❌ on `set-task-status` failure |

## Mixed One-by-One + Batch Execution

| File | Description | Plan Status | Notes |
|---|---|---|---|
| [demo-mixed-execution.md](demo-mixed-execution.md) | Phase 1 created one-by-one; Phases 2-3 + statuses added via batch; dep enforcement tested one-by-one | ⚙️ Doing | Shows seamless interleaving of both modes |

## Cross-Plan Dependencies

| File | Description | Plan Status | Notes |
|---|---|---|---|
| [demo-cross-plan-infra.md](demo-cross-plan-infra.md) | Infrastructure setup (dependency target, ⚙️ Doing) | ⚙️ Doing | `Depends On: NONE` |
| [demo-cross-plan-app.md](demo-cross-plan-app.md) | App deployment depends on infra plan | ☐ Todo | `Depends On: demo6a-infra.md` — blocked until infra completes |

## All Statuses Represented

| File | Description | Plan Status | Phase Statuses |
|---|---|---|---|
| [demo-all-statuses.md](demo-all-statuses.md) | Kitchen sink: every status (☐, ❓, ⚙️, ❌, ☑) appears in a different phase | ⚙️ Doing | ☑ Done, ⚙️ Doing, ❓ Question, ❌ Error, ☐ Todo |

## Original Demos

| File | Description | Plan Status |
|---|---|---|
| [demo-plan-mid-progress.md](demo-plan-mid-progress.md) | API gateway with Phase 1 done, Phase 2-3 todo | ☐ Todo |
| [demo-plan-advanced-progress.md](demo-plan-advanced-progress.md) | Data pipeline with Phases 1-2 done, Phase 3 partial | ☐ Todo |
| [demo-plan-completed.md](demo-plan-completed.md) | Microservice migration fully completed | ☑ Done |

## Execution Patterns Demonstrated

### One-by-One Commands Tested
- `create`, `set-plan-created`, `add-phase`, `add-task`
- `add-task-dependency` (phase-bound and cross-phase)
- `set-task-status` (all valid transitions: ☐→⚙️, ⚙️→☑, ⚙️→❓, ⚙️→❌)
- `set-plan-current-phase`, `set-plan-current-task`
- `set-plan-updated`
- `check --fix`

### Batch Commands Tested
- Line mode via stdin (`echo ... | plan.sh batch`)
- JSON mode via file (`plan.sh batch --input commands.json`)
- Status transitions within batch
- Error handling: invalid transition → `"error"`, remaining steps → `"skipped"`
- Mutation preservation on error (successful changes written to PLAN.md)

### Dependency Enforcement
- Cross-phase deps use `Phase X - Task X.Y` format
- `set-task-status` rejects ⚙️ if dependencies are not ☑
- ❓ transition does not require dependency satisfaction

## Status Derivation Rules

Verified through demos:
- **Task → Phase**: Phase derives from its tasks (e.g., any task ❌ → phase ❌)
- **Phase → Plan**: Plan derives from its phases (priority: ☑ > ⚙️ > ❓ > ❌ > ☐)
- **Error cascade**: Single task ❌ can propagate to entire plan
- **Manual override**: `set-plan-status` / `set-phase-status` allow temporary overrides; `check --fix` restores derived values
