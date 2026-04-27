# Platform Architecture

## The Control Plane Model

autoloop is the execution engine and state model for long-horizon autonomous work. External interfaces — CLI, chat, cron, future API/UI — are thin shells that launch, observe, and report on runs. They do not orchestrate.

The architectural split:

- **Control plane (autoloop)** — Runs multi-role event-driven loops, manages iteration limits, event routing, memory, completion detection, owns the append-only journal as the canonical source of truth, enforces topology constraints and quality gates
- **Presets (product surface)** — Self-contained workflow definitions: topology, roles, harness instructions, config. Each preset answers "what does this loop do?" Enumerable, validatable, composable via chains
- **Journals and artifacts (state model)** — Append-only JSONL journal records every event. Launch metadata in `loop.start` provides identity, lineage, and trigger context. Artifacts are projections derived from the journal — never a competing source of truth
- **External shells (intake and observation)** — CLI launches runs and inspects artifacts, chat accepts objectives and dispatches, cron schedules launches. Shells should get thinner over time

## When to Use autoloop

Use it when the task is:

- **Iterative** — multiple passes with feedback between roles
- **Quality-sensitive** — requires review gates, verification, or structured critique
- **Longer than one-shot** — benefits from journaling, memory, and resumability
- **Worth inspecting** — operators need to answer "what happened and why?"

Do not use it for:

- Trivial deterministic tasks (run a formatter, deploy a known-good artifact)
- One-shot queries needing no iteration, state, or review
- Tasks where loop overhead exceeds the value of structured execution

## Run Identity and Metadata

Every run carries structured launch metadata in its `loop.start` journal event:

- `run_id` — unique identifier (default format: human-readable `<word>-<word>`)
- `preset` — name of the preset driving this run
- `objective` — the task objective (prompt)
- `project_dir` — preset/project directory
- `work_dir` — working directory for state and artifacts
- `created_at` — ISO 8601 timestamp
- `backend` — backend command used
- `trigger` — how the run was launched: `cli`, `chain`, `branch`
- `parent_run_id` — parent run ID for chain steps (empty for top-level runs)

## Design Principles

1. **Journal is canonical.** Registry, analytics, dashboards are derived views. If they drift, rebuild from the journal.
2. **Presets are the product.** New workflows are preset directories, not code changes.
3. **Shells are thin.** CLI, chat, cron dispatch to autoloop — they do not contain loop logic.
4. **Metadata travels with the run.** Every run is self-describing through its launch event.
5. **Fail closed.** Verifier and critic roles prefer explicit evidence over quiet approval.

## Anti-Goals

- autoloop should not become a kitchen sink for every automated task
- Do not build a second orchestrator in chat code, cron code, or external tooling
- Do not replace the journal with a competing state store
- Do not introduce recursive loop-on-loop orchestration without bounded lineage and policy
