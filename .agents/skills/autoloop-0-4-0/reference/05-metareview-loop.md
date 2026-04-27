# Metareview Loop

## Purpose

The metareview is a meta-level review pass that runs periodically between normal loop iterations. Its job is to improve loop hygiene — consolidating stale context, trimming noisy working files, and storing durable learnings — without directly advancing the task.

## When It Runs

The review fires **before** an iteration, not after. The scheduling check:

```
iteration > 1 AND (iteration - 1) is divisible by review_every
```

With the default cadence, a review runs before iteration 2, then before iteration 2 + review_every, and so on. The first iteration always runs without review.

### Default Cadence

If `review.every_iterations` is not set (or set to `0`), the harness derives the cadence from the topology:

- **Topology has roles:** `review_every` = number of roles (one full rotation per review)
- **No topology / zero roles:** `review_every` = 1 (review every iteration)

## What the Metareview Can Do

The review receives a system prompt that grants bounded permissions:

- May modify runtime-facing loop files on disk: `autoloops.toml`, `topology.toml`, `harness.md`, `metareview.md`, `roles/*.md`, `.autoloop/context.md`, `.autoloop/plan.md`, `.autoloop/progress.md`, `.autoloop/logs/`, `.autoloop/docs/*.md`
- Must NOT edit app/product source code, tests, package manifests, `.autoloop/` state, or journal history
- Must NOT emit normal loop events during review (allowed-events set is `__metareview_disabled__`)
- Should use `autoloop memory add ...` for short durable lessons

## The Review Prompt

The review prompt includes:

1. A role statement: "You are the metareview meta-reviewer for this loop."
2. Bounded-permissions instructions (what files can/cannot be edited)
3. Constraint that scratchpad is projected from journal and cannot be edited directly
4. Custom review instructions from `metareview.md` (if present)
5. A **Context pressure** block summarizing memory usage vs budget, active entry counts, and number of invalid emits seen so far
6. Latest backpressure note (if the loop recently rejected an invalid event)
7. Current loop memory (subject to `memory.prompt_budget_chars`)
8. Review trigger iteration number and latest routing event
9. Full topology rendering
10. Current scratchpad in compact form
11. Useful `autoloop inspect` commands for the latest iteration
12. Fallback: "If no improvements are needed, store a short learning explaining why and exit cleanly."

## The `metareview.md` File

The default review prompt file is `metareview.md` at the root of the project directory. A typical one:

```markdown
You are the loop's meta agent.

Review the journal, topology, roles, harness instructions, loop memory, and shared working files.

Your job is to improve loop hygiene, not to finish the task directly.
You may modify runtime-facing loop files on disk when that will make the next iterations better.
Prefer bounded hygiene edits to `autoloops.toml`, `topology.toml`, `harness.md`, `metareview.md`, `roles/*.md`.
Do not edit app/product source code, tests, package manifests, `.autoloop/` state, or journal history during review.
```

## Hot-Reload After Review

After the review process finishes, the harness calls `reload_loop` — re-reading runtime config, topology, harness instructions, and review prompt inputs from disk before the next task turn. This means the metareview can modify loop-facing instructions and configuration, and those changes take effect on the very next iteration.

## Runtime Environment

During a review invocation:

- `AUTOLOOP_REVIEW_MODE` is set to `metareview` (signals this is a review pass)
- `AUTOLOOP_ITERATION` is set to the current iteration number
- The Pi adapter routes stream logs to `pi-review.<iteration>.jsonl` instead of the normal `pi-stream.<iteration>.jsonl`

## Configuration

```toml
review.enabled = true              # enable/disable (default: true)
review.every_iterations = 0        # 0 = auto-derive from topology
review.command = "pi"              # fallback to backend.command
review.kind = "pi"                 # fallback to backend.kind
review.timeout_ms = 300000         # 5 minutes (default)
review.prompt = ""                 # inline text (takes priority over prompt_file)
review.prompt_file = "metareview.md"  # path to custom review prompt
```

Set `review.enabled = false` to completely skip the review scheduling check.
