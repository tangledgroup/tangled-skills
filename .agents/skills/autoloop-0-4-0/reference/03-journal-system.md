# Journal System

## Append-Only Source of Truth

The journal is the canonical runtime source of truth for an autoloop loop. Every significant event — system lifecycle, agent actions, coordination, review, and chain execution — is appended as a single JSON line to `.autoloop/journal.jsonl`. Nothing is mutated or deleted; the file is append-only.

Higher-level views (scratchpad, coordination state, chain progress) are **projections** — derived by reading the journal and filtering/aggregating events.

## Record Shapes

Two record shapes exist: **system events** (emitted by the harness at lifecycle boundaries) and **agent events** (emitted by the model via `autoloop emit`).

### System Events

```json
{"run": "swift-agent", "iteration": "3", "topic": "iteration.start", "fields": {"recent_event": "tasks.ready", "suggested_roles": "builder", "allowed_events": "review.ready,build.blocked"}}
```

Fields: `run` (run ID), `iteration` (iteration number, empty for `loop.start`), `topic` (event type), `fields` (topic-specific payload).

### Agent Events

```json
{"run": "swift-agent", "iteration": "3", "topic": "review.ready", "payload": "initial implementation complete", "source": "agent"}
```

Fields: same as system events plus `payload` (free-text summary from the agent) and `source` (always `"agent"`).

### Coordination Events

Coordination events use the agent event shape but encode structured data inside the payload using `key=value;` pairs. They bypass backpressure validation — always accepted regardless of the allowed-events set. Examples:

- `issue.discovered` — `id=issue-1; summary=fix login bug; disposition=open; owner=builder;`
- `issue.resolved` — `id=issue-1; resolution=merged fix;`
- `slice.started` — `id=slice-1; description=implement retry logic;`
- `slice.verified` — `id=slice-1;`
- `slice.committed` — `id=slice-1; commit_hash=abc123;`
- `context.archived` — stale context archived from working file to docs
- `chain.spawn` — dynamic sub-chain spawned from within a running loop

## Event Lifecycle

A loop run produces events in this order:

```
loop.start
  iteration.start          ─┐
  backend.start             │  repeated per iteration
  [agent events]            │
  backend.finish            │
  iteration.finish         ─┘
  [review.start]           ─┐  optional, periodic
  [review.finish]          ─┘
  [wave.* events]              optional, during parallel fan-out/join
  [event.invalid]              optional, on bad emit
loop.complete   or   loop.stop
```

### Lifecycle Topics

- `loop.start` — once at the beginning. Fields: `max_iterations`, `completion_promise`, `completion_event`, `review_every`, `objective`
- `iteration.start` — start of each iteration. Fields: `recent_event`, `suggested_roles`, `allowed_events`, `backpressure`, `prompt`
- `backend.start` — before invoking the backend. Fields: `backend_kind`, `command`, `prompt_mode`, `timeout_ms`
- `backend.finish` — after backend returns. Fields: `exit_code`, `timed_out`, `output`
- `iteration.finish` — end of each iteration. Fields: `exit_code`, `timed_out`, `elapsed_s`, `output`
- `review.start` / `review.finish` — metareview review pass boundaries
- `loop.complete` — successful finish. Reason: `"completion_event"` or `"completion_promise"`
- `loop.stop` — halted without completion. Reason: `"max_iterations"`, `"backend_failed"`, or `"backend_timeout"`

### Wave Lifecycle Events (Structured Parallelism)

When `parallel.enabled = true`:

- `wave.start` — parallel wave opened from parent routing context
- `wave.branch.start` / `wave.branch.finish` — individual branch child runs
- `wave.join.start` / `wave.join.finish` — join barrier and resume context preparation
- `wave.timeout` / `wave.failed` / `wave.invalid` — error conditions

### Chain Events

- `chain.start` / `chain.complete` — chain execution boundaries
- `chain.step.start` / `chain.step.finish` — individual chain step loops
- `chain.spawn` — dynamic sub-chain spawned (also a coordination event)

## Backpressure and Event Validation

The model receives advisory routing suggestions but is not locked into a state machine. However, the event-emit boundary enforces constraints:

1. The topology's handoff map determines **suggested roles** from the most recent routing event
2. The **allowed events** are the union of all `emits` arrays from the suggested roles
3. When the agent emits an event, it is checked against the allowed set
4. Coordination events bypass validation — always accepted
5. If the allowed-events list is empty (no topology or unmapped event), all events are accepted

When an invalid event is emitted, an `event.invalid` record is appended to the journal and the emit command fails with a diagnostic. The harness re-prompts the agent with backpressure context on the next iteration.

## Completion Detection

After each valid iteration, in order:

1. **Completion event** — if the completion event appears in the run's journal topics AND all `required_events` have been seen, the loop completes
2. **Completion promise** — if the backend output contains the `completion_promise` string literally, the loop completes
3. Otherwise, the next iteration begins

Required events are cumulative across the entire run, not per-iteration.

## Scratchpad Projection

The scratchpad is a markdown view projected from `iteration.finish` events. It provides a running summary of what happened each iteration:

```markdown
## Iteration 1
exit_code=0
<iteration output>

## Iteration 2
exit_code=0
<iteration output>
```

Two render targets exist: compact view for iteration/review prompts (keeps recent iterations detailed, collapses older ones), and rich view for `autoloop inspect scratchpad --format md`.

## Run Scoping

All journal operations filter to the current run ID. Multiple runs can coexist in the same journal file — each run's events are isolated by their `run` field. The latest run is found by scanning backward for the most recent `loop.start` entry.

## Inspecting the Journal

```bash
autoloop inspect journal --format json       # raw JSONL
autoloop inspect scratchpad --format md       # iteration summaries
autoloop inspect coordination --format md     # issues, slices, commits
autoloop inspect metrics --format csv         # per-iteration metrics
autoloop inspect prompt 3 --format md         # iteration 3 prompt
autoloop inspect output 3 --format text       # iteration 3 output
autoloop inspect chain --format md            # chain execution state
```
