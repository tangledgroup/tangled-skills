# Loop Internals

## How ralph-loop.sh Works

The main loop script (`scripts/ralph-loop.sh`) is a bash script that orchestrates the Ralph Wiggum cycle. Here is the flow:

### Initialization

1. Parse arguments (mode, max iterations)
2. Set up log directory and session log file
3. Check constitution for YOLO setting
4. Generate minimal PROMPT files (`PROMPT_build.md`, `PROMPT_plan.md`)
5. Detect work sources (`IMPLEMENTATION_PLAN.md`, `specs/` folder)
6. Verify agent CLI is available

### Prompt Generation

The scripts generate minimal prompt files at runtime — the constitution contains the full workflow:

**PROMPT_build.md**:
```
# Ralph Loop — Build Mode

You are running inside a Ralph Wiggum autonomous loop (Context A).

Read `.specify/memory/constitution.md` — it contains all project principles, workflow
instructions, work sources, and completion signal requirements.

Find the highest-priority incomplete work item, implement it completely, verify all
acceptance criteria, commit and push, then output `<promise>DONE</promise>`.
```

**PROMPT_plan.md**:
```
# Ralph Loop — Planning Mode

You are running inside a Ralph Wiggum autonomous loop in planning mode.

Read `.specify/memory/constitution.md` for project principles.

Study `specs/` and compare against the current codebase (gap analysis).
Create or update `IMPLEMENTATION_PLAN.md` with a prioritized task breakdown.
Do NOT implement anything.

When the plan is complete, output `<promise>DONE</promise>`.
```

### Iteration Cycle

```
while true; do
    1. Increment iteration counter
    2. Create per-iteration log file
    3. Feed PROMPT_FILE to agent CLI via stdin
    4. Capture all output to log
    5. Check for <promise>DONE</promise> or <promise>ALL_DONE</promise> in output
    6. If found → success, reset failure counter, continue loop
    7. If not found → increment consecutive failures, retry
    8. Push any uncommitted changes to remote
    9. Brief pause (2s) before next iteration
done
```

### Completion Detection

The loop uses `grep -qE "<promise>(ALL_)?DONE</promise>"` to detect the magic phrase. Both `<promise>DONE</promise>` and `<promise>ALL_DONE</promise>` are recognized.

- `DONE` — One spec/task completed successfully
- `ALL_DONE` — No work remains, loop exits

### Consecutive Failure Tracking

After 3 consecutive iterations without completion signal, the loop warns that the agent may be stuck and suggests checking logs or simplifying the current spec. The counter resets after each successful completion.

## Spec Queue Library

`scripts/lib/spec_queue.sh` provides helpers for managing specs:

- `get_root_specs DIR` — List all `.md` files in directory, sorted
- `is_root_spec_complete FILE` — Check if spec has `Status: COMPLETE`
- `get_incomplete_root_specs DIR` — List incomplete specs
- `count_root_specs DIR` — Count total specs
- `count_incomplete_root_specs DIR` — Count incomplete specs
- `get_first_incomplete_root_spec DIR` — Get highest priority incomplete spec

### Spec Status Detection

The library recognizes these patterns as COMPLETE:
- `Status: COMPLETE`
- `**Status**: COMPLETE`
- `## Status: COMPLETE`

Any other status (Draft, TODO, In Progress) or missing status means INCOMPLETE.

## NR_OF_TRIES Library

`scripts/lib/nr_of_tries.sh` tracks attempt counts per spec:

- `get_nr_of_tries FILE` — Read current count from `<!-- NR_OF_TRIES: N -->`
- `increment_nr_of_tries FILE` — Increment counter (adds comment if missing)
- `reset_nr_of_tries FILE` — Reset to 0
- `is_spec_stuck FILE` — Returns true if attempts >= MAX_NR_OF_TRIES (default: 10)
- `get_stuck_specs DIR` — List all stuck specs
- `print_stuck_specs_summary DIR` — Print human-readable stuck specs report

## Logging

All output is captured to log files in `logs/`:

- **Session log**: `logs/ralph_<mode>_session_YYYYMMDD_HHMMSS.log` — Entire run including CLI output
- **Iteration logs**: `logs/ralph_<mode>_iter_N_YYYYMMDD_HHMMSS.log` — Per-iteration output
- **Codex last message**: `logs/ralph_codex_output_iter_N_*.txt`

The session log uses `tee` to capture everything while still displaying to terminal. A rolling output watcher shows the latest lines during long-running iterations.

## Configuration Variables

Environment variables and script-level settings:

- `CLAUDE_CMD` — Override agent command (default: `claude`)
- `MAX_NR_OF_TRIES` — Max attempts before spec is stuck (default: 10)
- `TAIL_LINES` — Lines shown after failed iteration (default: 5)
- `ROLLING_OUTPUT_INTERVAL` — Seconds between rolling output updates (default: 10)
- `ROLLING_OUTPUT_LINES` — Lines shown in rolling output (default: 5)

## Work Source Priority

The loop checks work sources in this order:

1. `IMPLEMENTATION_PLAN.md` — If exists, pick highest priority task from plan
2. `specs/` folder — Pick highest priority incomplete spec (lower number = higher priority)

Planning mode is optional. Most projects work fine directly from specs. Delete `IMPLEMENTATION_PLAN.md` to return to working directly from specs.
