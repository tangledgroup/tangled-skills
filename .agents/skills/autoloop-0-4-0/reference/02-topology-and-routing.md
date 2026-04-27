# Topology and Event Routing

## The Role Graph

Topology is declared in `topology.toml` at the root of a preset directory. It defines which roles exist, what events they can emit, and how events route to the next role.

Topology is **advisory** — it is not a hard workflow engine. The model receives routing suggestions and allowed events as context, and backpressure enforces the protocol at the event-emit boundary.

### File Format

```toml
name = "autocode"
completion = "task.complete"

[[role]]
id = "planner"
emits = ["tasks.ready", "task.complete"]
prompt_file = "roles/planner.md"

[[role]]
id = "builder"
emits = ["review.ready", "build.blocked"]
prompt_file = "roles/build.md"

[[role]]
id = "critic"
emits = ["review.passed", "review.rejected"]
prompt_file = "roles/critic.md"

[handoff]
"loop.start" = ["planner"]
"tasks.ready" = ["builder"]
"review.ready" = ["critic"]
"review.rejected" = ["builder"]
"review.passed" = ["finalizer"]
```

### Role Definitions

Each `[[role]]` table defines one role:

- `id` — unique identifier, used in handoff maps and prompt rendering
- `emits` — events this role is allowed to emit (determines the allowed-event set for backpressure)
- `prompt` — inline prompt text (optional)
- `prompt_file` — path to a markdown file containing the role's prompt, relative to the project directory

If both `prompt` and `prompt_file` are set, `prompt` takes precedence.

### Handoff Map

The `[handoff]` section maps events to suggested next roles. Each key is an event name, each value is an array of role IDs.

When an event is emitted, the handoff map determines which roles should run next. If the event is not in the handoff map, **all roles** are suggested — the model picks from the full deck.

The special event `"loop.start"` is the initial routing event at the beginning of the loop.

## How Routing Works (Three Layers)

The routing model has three layers:

1. **Suggested roles** — looked up from the handoff map using the most recent event. If the event has no entry, all roles are suggested.
2. **Allowed events** — the union of `emits` arrays from all suggested roles. This is what the model may emit next.
3. **Backpressure** — if the model emits an event not in the allowed set, `autoloop emit` fails immediately and the event is logged as `event.invalid` in the journal. The model is re-prompted with routing context.

This is **soft routing**: the model sees suggestions and constraints but is not forced into a fixed state machine. The backpressure layer prevents protocol violations without requiring hard-coded transitions.

## Prompt Injection

Each iteration, the topology is rendered into the prompt as advisory context:

```
Topology (advisory):
Recent routing event: tasks.ready
Suggested next roles: builder
Allowed next events: review.ready, build.blocked

Role deck:
- role `planner`
  emits: tasks.ready, task.complete
  prompt: You are the planner.
- role `builder`
  emits: review.ready, build.blocked
  prompt: You are the builder.
```

The prompt summary for each role shows the first non-empty line of its prompt text.

## Completion Resolution

The loop completes when the completion event is emitted. The completion event is resolved in this order:

1. `completion` field in `topology.toml`
2. `event_loop.completion_event` in `autoloops.toml`
3. The `completion_promise` text fallback (a string the model can output directly)

Additionally, `autoloops.toml` can declare `event_loop.required_events` — events that must appear in the journal before the completion event is accepted.

## Design Patterns

### Linear Pipeline

Roles hand off in sequence. Each role emits one "success" event that routes to the next role.

```
planner → builder → critic → finalizer
```

### Rejection Loops

A reviewing role can reject and route back to the producing role, creating iterative refinement cycles:

```toml
"review.rejected" = ["builder"]   # builder tries again
"fix.failed" = ["fixer"]          # fixer tries again
```

### Fan-Back to Start

After a cycle completes a unit of work, route back to the first role to pick up the next unit:

```toml
"queue.advance" = ["planner"]     # planner picks next task
```

### Blocked Escalation

A role that cannot proceed emits a `.blocked` event, routing to a role that can re-plan or provide context:

```toml
"build.blocked" = ["planner"]
"fix.blocked" = ["diagnoser"]
```

## Structured Parallel Routing

When `parallel.enabled = true`, the harness recognizes two bounded fan-out forms:

- `explore.parallel` — globally available exploratory fan-out
- `<allowed-event>.parallel` — dispatch fan-out for a normal event already in the current allowed set

Joined events are harness-owned (the model must not emit `*.parallel.joined`). Only one active wave may exist at a time. Branch state is isolated under `.autoloop/waves/<wave-id>/...`.
