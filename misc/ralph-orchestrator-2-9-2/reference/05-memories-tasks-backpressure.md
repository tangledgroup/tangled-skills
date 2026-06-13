# Memories, Tasks & Backpressure

## Memories

Memories persist learning across sessions. They capture patterns, decisions, fixes, and context that Ralph should remember. Stored in `.ralph/agent/memories.md`.

### Memory Types

- **pattern** — Codebase conventions discovered
- **decision** — Architectural choices and rationale
- **fix** — Solutions to recurring problems
- **context** — Project-specific knowledge

### Creating Memories

```bash
# Pattern: discovered convention
ralph tools memory add "All API handlers return Result<Json<T>, AppError>" \
  -t pattern --tags api,error-handling

# Decision: architectural choice
ralph tools memory add "Chose JSONL over SQLite: simpler, git-friendly" \
  -t decision --tags storage,architecture

# Fix: recurring problem solution
ralph tools memory add "cargo test hangs: kill orphan postgres" \
  -t fix --tags testing,postgres
```

### Searching and Managing

```bash
ralph tools memory search "api"            # Broad search
ralph tools memory search -t fix "error"   # Filter by type
ralph tools memory search --tags api,auth  # Filter by tags
ralph tools memory list                    # List all memories
ralph tools memory show <id>               # Show a specific memory
ralph tools memory delete <id>             # Delete a memory
ralph tools memory prime                   # Prime context memory output
```

### Memory Injection

Memories are automatically injected at the start of each iteration:

```yaml
memories:
  enabled: true
  inject: auto      # auto, manual, or none
  budget: 2000      # Max tokens to inject
  filter:
    types: []       # Filter by type (empty = all)
    tags: []        # Filter by tags (empty = all)
    recent: 0       # Days limit (0 = no limit)
```

Injection modes:
- **auto** — Automatically inject at iteration start
- **manual** — Agent must call `ralph tools memory prime`
- **none** — No injection

### Memory Best Practices

- Be specific: "Uses barrel exports" not "Has good patterns"
- Include why: "Chose X because Y" not just "Uses X"
- One concept per memory: split complex learnings
- Tag consistently: reuse existing tags

## Tasks

Tasks track runtime work items during orchestration. Stored in `.ralph/agent/tasks.jsonl`.

### Creating Tasks

```bash
# Basic task
ralph tools task add "Implement user authentication"

# With priority (1-5, 1 = highest)
ralph tools task add "Fix critical bug" -p 1

# With dependency
ralph tools task add "Deploy to production" --blocked-by setup-infra
```

### Managing Tasks

```bash
ralph tools task list        # List all tasks
ralph tools task ready       # List unblocked tasks only
ralph tools task close <id>  # Mark task complete
ralph tools task fail <id>   # Mark task failed
ralph tools task show <id>   # Show task details
```

### Task Workflow

1. Ralph creates tasks from the prompt/plan
2. Tasks are worked in priority order
3. Dependencies are respected (blocked tasks wait)
4. Completed tasks are closed
5. Loop ends when no open tasks remain + consecutive `LOOP_COMPLETE`

### Task Closure Rules

Tasks must only be closed when:

1. Implementation is actually complete
2. Tests pass
3. Build succeeds (if applicable)
4. Evidence of completion exists

```bash
# Good: Close with evidence
cargo test  # passes
ralph tools task close task-123

# Bad: Close without verification
ralph tools task close task-123  # No tests run!
```

### File Formats

**memories.md:**
```markdown
# Memories

## Patterns

### mem-1737372000-a1b2
> All API handlers return Result<Json<T>, AppError>
<!-- tags: api, error-handling | created: 2024-01-20 -->
```

**tasks.jsonl:**
```json
{"id":"task-001","title":"Implement auth","priority":2,"status":"open","created":"2024-01-20T10:00:00Z"}
{"id":"task-002","title":"Add tests","priority":3,"status":"open","blocked_by":["task-001"],"created":"2024-01-20T10:01:00Z"}
```

## Backpressure

Backpressure is Ralph's mechanism for enforcing quality gates. Instead of prescribing how to do something, you define gates that reject incomplete work.

### The Concept

Traditional approach (prescription):
```
1. First, write the function
2. Then, write the tests
3. Then, run the tests
4. Then, fix any failures
```

Backpressure approach:
```
Implement the feature.
Evidence required: tests: pass, lint: pass, typecheck: pass, audit: pass, coverage: pass
```

The AI figures out the "how" — it's smart enough. Your job is defining what success looks like.

### Implementing Backpressure in Hat Instructions

```yaml
hats:
  builder:
    instructions: |
      Implement the assigned task.

      ## Backpressure Requirements

      Before emitting build.done, you MUST have:
      - tests: pass (run `cargo test`)
      - lint: pass (run `cargo clippy`)
      - typecheck: pass (run `cargo check`)
      - audit: pass (run `cargo audit`)
      - coverage: pass

      Include evidence in your event:
      ralph emit "build.done" "tests: pass, lint: pass, typecheck: pass, audit: pass, coverage: pass"
```

### Types of Backpressure

**Technical gates:**

- **Tests** — `cargo test`, `npm test` — Catches regressions and bugs
- **Lint** — `cargo clippy`, `eslint` — Catches code quality issues
- **Typecheck** — `cargo check`, `tsc` — Catches type errors
- **Audit** — `cargo audit`, `npm audit` — Known vulnerabilities
- **Format** — `cargo fmt --check` — Style violations
- **Build** — `cargo build` — Compilation errors

**Behavioral gates** (LLM-as-judge for subjective criteria):

```yaml
hats:
  quality_judge:
    triggers: ["code.written"]
    instructions: |
      Evaluate the code quality:
      - Is it readable?
      - Are names meaningful?
      - Is complexity justified?
      Pass or fail with explanation.
```

**Documentation gates:**

```yaml
hats:
  doc_reviewer:
    triggers: ["feature.done"]
    instructions: |
      Check documentation:
      - README updated
      - API docs complete
      - Examples work
      Reject if documentation is missing.
```

### Implementing Backpressure in Guardrails

Global rules injected into every prompt:

```yaml
core:
  guardrails:
    - "Tests must pass before declaring done"
    - "Never skip linting"
    - "All public functions need doc comments"
```

### Backpressure Flow

```
Build Complete? → Tests Pass? → No → Fix & Retry
                        ↓ Yes
                  Lint Pass? → No → Fix & Retry
                        ↓ Yes
                  Typecheck Pass? → No → Fix & Retry
                        ↓ Yes
              Emit build.done with evidence
```

### Best Practices

1. **Start with tests** — The most fundamental gate
2. **Add lint for quality** — Catches common issues
3. **Include evidence** — Don't just claim, prove
4. **Verify claims** — Use reviewer hats to re-run checks
5. **Keep it achievable** — Too strict blocks progress

### Anti-Patterns

- **No backpressure** — Instructions with no quality requirements
- **Fake evidence** — Claiming gates passed without actually running them
- **Too many gates** — Overwhelming requirements that block all progress

## Integration with Hats

Hats can use memories and tasks together:

```yaml
hats:
  builder:
    triggers: ["task.start"]
    instructions: |
      1. Check memories for relevant patterns
      2. Pick a task from `ralph tools task ready`
      3. Implement the task
      4. Record learnings as memories
      5. Close the task with `ralph tools task close <id>`
```

## Legacy Scratchpad Mode

To disable memories and tasks (returns to legacy scratchpad):

```yaml
memories:
  enabled: false
tasks:
  enabled: false
```

In this mode, `.ralph/agent/scratchpad.md` is used for all state.
