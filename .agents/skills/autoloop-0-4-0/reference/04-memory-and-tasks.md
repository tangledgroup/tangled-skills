# Memory and Tasks

## Two-Tier Memory System

Loop memory is a two-tier, append-only store that carries learnings, preferences, and metadata across iterations. It is split into **project memory** (durable, shared across runs) and **run memory** (ephemeral, per-run).

Memory is **soft-deletable** — entries are never physically removed; instead, a tombstone entry marks the target as inactive.

### Entry Types

Four entry types exist:

**Learning** — a durable lesson discovered during a loop run:
```json
{"id": "mem-1", "type": "learning", "text": "Use vitest for testing", "source": "manual", "created": "2026-03-27T01:00:19Z"}
```

**Preference** — a categorized behavioral preference (always project-scoped):
```json
{"id": "mem-2", "type": "preference", "category": "Workflow", "text": "Always run tests before emitting review.ready", "created": "2026-03-27T02:00:00Z"}
```

**Meta** — arbitrary key-value metadata (always run-scoped):
```json
{"id": "meta-1", "type": "meta", "key": "smoke_iteration", "value": "2", "created": "2026-03-27T03:00:00Z"}
```

**Tombstone** — soft-deletes a previous entry:
```json
{"id": "ts-1", "type": "tombstone", "target_id": "mem-2", "reason": "no longer applicable", "created": "2026-03-27T04:00:00Z"}
```

### Tier Resolution

| Command | Target Tier | Override |
|---------|-------------|----------|
| `memory add learning <text>` | Run | `--project` flag → Project |
| `memory add preference <cat> <text>` | Project | None (always project) |
| `memory add meta <key> <value>` | Run | None (always run) |
| `memory promote <id>` | Run → Project | N/A |

### Materialization

Before memory is rendered into the prompt, it goes through **materialization** — a process that produces a clean, deduplicated view from the raw append-only log:

1. Read all lines from the JSONL file
2. Walk entries from newest to oldest
3. For each tombstone, record its `target_id` as inactive
4. For each non-tombstone entry, skip it if its `id` has been tombstoned or already seen
5. For meta entries, additionally deduplicate by `key` — only the most recent value for each key is kept
6. Collect surviving entries into three buckets: preferences, learnings, meta

### Prompt Injection

Materialized memory is rendered as a text block and injected into the iteration prompt between the objective and the topology section:

```
Loop memory:
Project memory:
Preferences:
- [mem-1] [Workflow] Always run tests before emitting review.ready
Learnings:
- [mem-3] (promoted) Use .tsx for JSX files

Run memory:
Learnings:
- [mem-1] (manual) This task uses vitest for testing
Meta:
- [meta-1] smoke_iteration: 2
```

The rendered text is truncated to `memory.prompt_budget_chars` characters (default: **8000**). Run memory entries are dropped before project entries. Within each tier: meta → learnings → preferences (bottom to top).

### Memory CLI

```bash
autoloop memory list                         # show materialized memory
autoloop memory status                       # rendered size, budget, counts
autoloop memory find "routing lag"           # search active entries
autoloop memory add learning "lesson text"   # add to run memory
autoloop memory add learning --project "..." # add to project memory
autoloop memory add preference Workflow "..."# add preference
autoloop memory add meta key "value"         # add metadata
autoloop memory remove <id> "reason"         # tombstone an entry
autoloop memory promote <id>                # promote run → project
```

## Task System

Tasks are lightweight work items that agents create and track during a loop run. They use the same append-only JSONL with tombstones pattern as memory.

**Open tasks gate loop completion** — a run cannot emit its completion event while tasks remain open.

### Entry Format

```json
{"id": "task-1", "type": "task", "text": "implement retry logic", "status": "open", "source": "manual", "created": "2026-04-07T12:00:00Z"}
```

Fields: `id` (sequential `task-N`), `type` (`"task"`), `text` (description), `status` (`"open"` or `"done"`), `source` (origin), `created` (ISO 8601), `completed` (optional, set when done).

### Lifecycle

```
add (open) → complete (done)
         ↘ update (open, new text)
         ↘ remove (tombstoned)
```

### Completion Gate

When a loop emits its completion event, the harness checks for open tasks. If any remain, the emit is rejected with a `task.gate` journal entry and an error listing the open task IDs. The agent must complete or remove all open tasks before the loop can finish.

### Task CLI

```bash
autoloop task add "description of work item"    # create open task
autoloop task complete task-1                   # mark done
autoloop task update task-1 "new description"   # replace text
autoloop task remove task-1 "no longer needed"  # tombstone
autoloop task list                              # show all tasks grouped by status
```

### Prompt Integration

Tasks are rendered into the iteration prompt under a `Tasks:` header:

```
Tasks:
Open:
- [ ] [task-1] implement retry logic
Done:
- [x] [task-2] set up test fixtures (done)
```

Subject to `tasks.prompt_budget_chars` (default 4000). Tasks also appear in the context pressure summary at the top of each iteration prompt.
