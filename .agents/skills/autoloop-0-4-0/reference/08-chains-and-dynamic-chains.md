# Chains and Dynamic Chains

## Three Orchestration Layers

| Layer | Config | Scope |
|-------|--------|-------|
| **Topology** | `topology.toml` | Intra-loop role routing (planner → builder → critic) |
| **Chains** | `chains.toml` / `--chain` | Inter-loop preset composition (autocode → autoqa) |
| **Dynamic chains** | Runtime chain specs | Meta-level chain planning, selection, and spawning |

## Named Chains

Named chains are defined in `chains.toml`:

```toml
[[chain]]
name = "code-and-qa"
steps = ["autocode", "autoqa"]

[[chain]]
name = "full-pipeline"
steps = ["autospec", "autocode", "autotest", "autoqa"]
```

Each step runs as an isolated loop in `.autoloop/chains/<chain-run-id>/step-<n>/`. Chains advance on bounded-success stops (`completion_event`, `completion_promise`, or `max_iterations`) and stop only on real failures (backend errors, timeouts).

### CLI

```bash
autoloop chain list                          # show defined chains
autoloop chain run code-and-qa "Build feature X"  # run a named chain
```

Or compose ad hoc on the command line:

```bash
autoloop run . --chain autocode,autoqa "Implement and validate"
```

### Chain Events in the Journal

- `chain.start` — chain execution began (fields: `name`, `steps`, `step_count`)
- `chain.step.start` / `chain.step.finish` — individual step boundaries
- `chain.complete` — chain finished (fields: `name`, `steps_completed`, `outcome`)

## Dynamic Chain Generation

Dynamic chain generation allows a meta-level orchestrator (an LLM agent) to create and execute preset chains at runtime. This enables bounded open-ended execution — a long-lived sequence of inspectable, resumable chain episodes with explicit budgets, lineage, and quality gates.

**"Open-ended" means bounded autonomous episodes, not literal unbounded recursion.**

### Budget Model

Every dynamic chain session is constrained by explicit budgets in `chains.toml`:

```toml
[budget]
max_depth = 5                    # max nested chain depth
max_steps = 50                   # max total steps across all chains
max_runtime_ms = 3600000         # wall clock limit (1 hour)
max_children = 10                # max descendant chains
max_consecutive_failures = 3     # stop after N no-op/failed chains
```

### Quality Gates

Before spawning a new chain, the system checks:
1. Budget constraints (depth, steps, children, failures)
2. If the last 2+ chains ended in failure, spawning is blocked until the agent consolidates

This prevents unjustified runaway chain creation.

### Chain Specs

Dynamic chain specs are durable JSON files stored in `.autoloop/chains/specs/`:

```json
{"chain_id": "dyn-1", "parent_id": "chain-2", "steps": "autocode,autoqa", "justification": "Code changes need validation"}
```

Each spec records: `chain_id`, `parent_id` (lineage), `steps` (preset sequence), and `justification` (why created).

### Lineage Tracking

Every dynamic chain records its parent chain ID, creating an inspectable ancestry tree:

```
chain-1 (root)
  └─ dyn-1 (spawned by chain-1)
       └─ dyn-2 (spawned by dyn-1)
```

Lineage is visible in the journal via `chain.spawn` events and in spec files.

### Preset Vocabulary Constraint

Dynamic chains are constrained to known presets. The `validate_preset_vocabulary` function rejects unknown preset names.

### Agent Interaction

Agents can emit `chain.spawn` coordination events to request dynamic chain creation. The harness passes these through without affecting topology routing.

### Design Principles

- Durable data over ephemeral prompts — chain specs persist as files
- Budget-first — every chain episode has hard limits
- Inspectable from disk — journal events, spec files, handoff/result artifacts
- No giant scheduler — the meta-orchestrator is just an LLM with chain tools
- Bounded episodes — resumable autonomous sessions, not infinite loops
