# Hats & Events

## Hat System Overview

Hats are specialized Ralph personas that coordinate through typed events. Each hat defines:

- **Triggers** — Event patterns that activate this hat
- **Publishes** — Events this hat is allowed to emit
- **Instructions** — Prompt injected when the hat is active
- **Optional**: `default_publishes`, `max_activations`, `backend` override, per-hat scratchpad

```yaml
hats:
  planner:
    name: "Planner"
    triggers: ["task.start"]
    publishes: ["plan.ready", "plan.blocked"]
    instructions: |
      Create an implementation plan for the task.
      When done, emit plan.ready with a summary.
```

## Event System

Events are typed messages routed through an EventBus:

- **Topic** — What kind of event (e.g., `build.done`)
- **Payload** — Optional string or JSON data
- **Source hat** — Which hat published it
- **Target hat** — Determined by subscription matching

### Publishing Events

Agents publish events using `ralph emit`:

```bash
# Simple payload
ralph emit "build.done" "tests: pass, lint: pass, typecheck: pass"

# JSON payload
ralph emit "review.done" --json '{"status": "approved", "issues": 0}'
```

### Event Routing

Events route to hats via glob-style pattern matching:

- `task.start` — Exact match only
- `build.*` — Matches `build.done`, `build.failed`, etc.
- `*.done` — Matches `build.done`, `review.done`, etc.
- `*` — Global wildcard (Ralph's fallback handler)

Specific patterns take precedence over wildcards. If multiple hats have specific subscriptions to the same event, that is an error (ambiguous routing).

### Starting Event and Completion

```yaml
event_loop:
  starting_event: "task.start"       # First event published on startup
  completion_promise: "LOOP_COMPLETE" # Output that ends the loop
```

When Ralph starts in hat-based mode, it publishes the `starting_event`. The matching hat activates, does its work, and emits an event. That event triggers the next hat. The cycle continues until `LOOP_COMPLETE` is output.

## Hat Configuration Fields

- **name** (required) — Display name for the hat
- **description** — Purpose description
- **triggers** (required) — List of event subscription patterns
- **publishes** (required) — Allowed event types this hat can emit
- **default_publishes** — Default event if agent emits nothing explicit
- **max_activations** — Limit how many times this hat can activate
- **backend** — Override the global backend for this specific hat
- **scratchpad** — Per-hat scratchpad override (string path or object with `enabled`/`path`)
- **instructions** (required) — Hat-specific prompt text
- **concurrency** — Max parallel workers for wave execution (default: 1)
- **aggregate** — Buffer results mode for downstream hats

## Coordination Patterns

### 1. Linear Pipeline

Work flows through a fixed sequence of specialists:

```yaml
hats:
  planner:
    triggers: ["task.start"]
    publishes: ["plan.ready"]

  builder:
    triggers: ["plan.ready"]
    publishes: ["build.done"]

  tester:
    triggers: ["build.done"]
    publishes: ["test.passed", "test.failed"]

  deployer:
    triggers: ["test.passed"]
    publishes: ["LOOP_COMPLETE"]
```

### 2. Critic-Actor Loop

One proposes, another critiques, iterate until approved:

```yaml
hats:
  actor:
    triggers: ["task.start", "critic.rejected"]
    publishes: ["proposal.ready"]

  critic:
    triggers: ["proposal.ready"]
    publishes: ["critic.approved", "critic.rejected"]
```

### 3. Fan-Out / Coordinator-Specialist

A coordinator delegates to specialists based on work type:

```yaml
hats:
  analyzer:
    triggers: ["gap.start", "verify.complete"]
    publishes: ["analyze.spec", "report.request"]

  verifier:
    triggers: ["analyze.spec"]
    publishes: ["verify.complete"]

  reporter:
    triggers: ["report.request"]
    publishes: ["report.complete"]
```

### 4. Cyclic Rotation

Multiple roles take turns, each bringing a different perspective:

```yaml
hats:
  navigator:
    triggers: ["mob.start", "observation.noted"]
    publishes: ["direction.set", "mob.complete"]

  driver:
    triggers: ["direction.set"]
    publishes: ["code.written"]

  observer:
    triggers: ["code.written"]
    publishes: ["observation.noted"]
```

### 5. Adversarial Review

Two roles with opposing objectives ensure robustness:

```yaml
hats:
  builder:
    triggers: ["security.review", "fix.applied"]
    publishes: ["build.ready"]

  red_team:
    triggers: ["build.ready"]
    publishes: ["vulnerability.found", "security.approved"]

  fixer:
    triggers: ["vulnerability.found"]
    publishes: ["fix.applied"]
```

### 6. Hypothesis-Driven Investigation

The scientific method applied to debugging:

```yaml
hats:
  observer:
    triggers: ["science.start", "hypothesis.rejected"]
    publishes: ["observation.made"]

  theorist:
    triggers: ["observation.made"]
    publishes: ["hypothesis.formed"]

  experimenter:
    triggers: ["hypothesis.formed"]
    publishes: ["hypothesis.confirmed", "hypothesis.rejected"]

  fixer:
    triggers: ["hypothesis.confirmed"]
    publishes: ["fix.applied"]
```

## Built-in Hat Collections

Five supported builtins (loaded with `-H builtin:<name>`):

- **code-assist** — `planner`, `builder`, `critic`, `finalizer` — Default implementation workflow
- **debug** — `investigator`, `tester`, `fixer`, `verifier` — Root-cause debugging
- **research** — `researcher`, `synthesizer` — Read-only analysis
- **review** — `reviewer`, `analyzer` — Adversarial code review
- **pdd-to-code-assist** — Multi-stage design + build pipeline (9 hats, advanced)

Additional example presets exist in the `presets/` directory for patterns like spec-driven development, red-team review, mob programming, fresh-eyes loops, gap analysis, PR review, refactoring, and wave-enabled parallel review.

## Best Practices

- **Keep events small** — Events are routing signals, not data transport. Put detailed output in memories.
- **Use clear triggers** — Specific patterns (`plan.ready`) over broad wildcards (`*`).
- **One responsibility per hat** — Each hat should have a single, focused purpose.
- **Include evidence in events** — `ralph emit "build.done" "tests: pass, lint: pass"` not just `"done"`.
- **Verify claims with reviewer hats** — A separate hat re-runs checks before approving.
