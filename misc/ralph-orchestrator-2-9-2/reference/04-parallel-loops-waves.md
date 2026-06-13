# Parallel Loops & Agent Waves

## Parallel Loops (Inter-Loop Parallelism)

Ralph supports multiple orchestration loops running simultaneously using git worktrees for filesystem isolation.

### How It Works

1. **First loop** acquires `.ralph/loop.lock` and runs in-place (primary loop)
2. **Additional loops** automatically spawn into `.worktrees/<loop-id>/`
3. **Each loop** has isolated events, tasks, and scratchpad
4. **Memories are shared** — symlinked back to the main repo's `.ralph/agent/memories.md`
5. **On completion**, worktree loops queue for merge; primary loop processes the merge queue when it finishes

```
Primary Loop (holds .ralph/loop.lock)
├── Runs in main workspace
├── Processes merge queue on completion
└── Spawns merge-ralph for queued loops

Worktree Loops (.worktrees/<loop-id>/)
├── Isolated filesystem via git worktree
├── Symlinked memories, specs, tasks → main repo
├── Queue for merge on completion
└── Exit cleanly (no spawn)
```

### Usage

```bash
# Terminal 1: Primary loop
ralph run -p "Add authentication"

# Terminal 2: Automatically spawns to worktree
ralph run -p "Add logging"

# Monitor running loops
ralph loops list

# View logs
ralph loops logs <loop-id>
ralph loops logs <loop-id> --follow

# Force sequential execution
ralph run --exclusive -p "Task that needs main workspace"

# Skip auto-merge
ralph run --no-auto-merge -p "Experimental feature"
```

### Loop States

- `running` — Actively executing
- `queued` — Completed, waiting for merge
- `merging` — Merge operation in progress
- `merged` — Successfully merged to main
- `needs-review` — Merge failed, requires manual resolution
- `crashed` — Process died unexpectedly
- `orphan` — Worktree exists but not tracked
- `discarded` — Explicitly abandoned

### Managing Loops

```bash
ralph loops list [--json] [--all]
ralph loops logs <id> [--follow]
ralph loops history <id> [--json]
ralph loops diff <id> [--stat]
ralph loops attach <id>           # Open shell in worktree
ralph loops retry <id>            # Re-run merge for failed loop
ralph loops stop <id> [--force]   # SIGTERM or SIGKILL
ralph loops resume <id>           # Resume suspended loop
ralph loops discard <id> [-y]     # Abandon and cleanup
ralph loops prune                 # Clean up stale/orphaned loops
ralph loops merge <id> [--force]  # Manual merge
ralph loops process               # Process merge queue
```

### Auto-Merge Workflow

When a worktree loop completes, it queues for merge. The primary loop processes the queue when it finishes, spawning a **merge-ralph** with specialized hats:

- `merger` — Performs `git merge`, runs tests
- `resolver` — Resolves merge conflicts by understanding intent
- `tester` — Verifies tests pass after conflict resolution
- `cleaner` — Removes worktree and branch
- `failure_handler` — Marks loop for manual review

Conflict resolution strategy:
1. **No conflicts**: Merge → Run tests → Clean up → Done
2. **With conflicts**: Detect → AI resolves (preserving both intents) → Run tests → Clean up
3. **Unresolvable**: Abort → Mark for review → Keep worktree for manual fix

### Best Practices

Use parallel loops when:
- Independent features with minimal file overlap
- Bug fixes while feature work continues
- Documentation updates parallel to code changes

Use `--exclusive` (sequential) when:
- Large refactoring touching many files
- Database migrations or schema changes
- Tasks that modify shared configuration

## Agent Waves (Intra-Loop Parallelism)

Waves enable a single hat to process multiple work items in parallel within one iteration. Without waves, items are processed sequentially across iterations. Waves collapse that into one parallel burst.

### When to Use Waves

- Running specialized reviewers in parallel (Rust, frontend, docs)
- Researching N questions simultaneously
- Running N independent analyses concurrently

### Wave Lifecycle

1. **Dispatch** — A hat emits N events as a wave using `ralph wave emit`
2. **Execute** — The loop runner spawns parallel backend instances (up to `concurrency` limit)
3. **Aggregate** — Results merge back into the main event stream

```
Coordinator → ralph wave emit → [Worker 0] ──┐
                                              ├──→ Synthesizer
                                            [Worker 1] ──┤
                                                        │
                                            [Worker 2] ──┘
```

### Configuration

Two hat config fields enable wave execution:

**concurrency** — Maximum parallel backend instances for this hat:

```yaml
hats:
  reviewer:
    triggers: ["review.perspective"]
    publishes: ["review.done"]
    concurrency: 3   # Three workers run simultaneously
    instructions: |
      Review code from your assigned specialist perspective.
```

**aggregate** — Downstream hat buffers results until all arrive:

```yaml
hats:
  synthesizer:
    triggers: ["review.done"]
    publishes: ["review.complete"]
    aggregate:
      mode: wait_for_all   # Wait for every worker to finish
      timeout: 300          # Give up after 5 minutes
    instructions: |
      Combine all review findings into a unified report.
```

A hat cannot have both `concurrency > 1` and `aggregate`.

### Wave Dispatch

```bash
ralph wave emit <topic> --payloads "item1" "item2" "item3"
```

Each payload becomes a separate event tagged with a shared `wave_id`. The loop runner detects tagged events and spawns parallel workers.

### Three-Hat Wave Pattern

```yaml
event_loop:
  starting_event: "review.start"
  completion_promise: "LOOP_COMPLETE"

hats:
  coordinator:
    name: "Coordinator"
    triggers: ["review.start"]
    publishes: ["review.perspective"]
    instructions: |
      Dispatch specialized reviewers as a wave:
      ralph wave emit review.perspective --payloads \
        "ROLE: Rust Reviewer. Focus on ownership, error handling." \
        "ROLE: Frontend Reviewer. Focus on React patterns, a11y." \
        "ROLE: Docs Reviewer. Focus on README accuracy, examples."

  reviewer:
    name: "Reviewer"
    triggers: ["review.perspective"]
    publishes: ["review.done"]
    concurrency: 3
    instructions: |
      You are a specialized reviewer. Read your role from
      the event payload and review strictly from that perspective.

  synthesizer:
    name: "Synthesizer"
    triggers: ["review.done"]
    publishes: ["review.complete"]
    aggregate:
      mode: wait_for_all
      timeout: 300
    instructions: |
      Merge all specialist findings into a unified report.
```

### Worker Isolation

Each wave worker runs with:

- `RALPH_WAVE_WORKER=1` — Marks as wave worker
- `RALPH_WAVE_ID` — Shared wave correlation ID
- `RALPH_WAVE_INDEX` — 0-based worker index
- `RALPH_EVENTS_FILE` — Per-worker events file path

Workers publish results via standard `ralph emit`. The loop runner merges all worker outputs into the main events file.

### Nested Wave Prevention

Wave workers cannot dispatch their own waves. Enforced at two levels:
- **Hard guard** — `ralph wave emit` checks `RALPH_WAVE_WORKER` env var and refuses
- **Soft guard** — Worker prompts explicitly prohibit `ralph wave emit`

### Concurrency Control

If a wave has 10 items but `concurrency: 4`, only 4 workers run at a time. A semaphore gates additional workers until slots open.

### Current Limitations

- **One wave per iteration** — If multiple waves detected, only the lexicographically first `wave_id` executes
- **No nested waves** — Workers cannot dispatch sub-waves
- **Global backend fallback** — Workers use global backend when hat has no override
- **No TUI progress** — Wave workers run headless

### Built-in Wave Preset

`wave-review` — Specialized parallel code review with 3 reviewers (Rust, Frontend, Docs) and a synthesizer.

```bash
ralph run -c ralph.yml -H presets/wave-review.yml -p "Review the authentication module"
```
