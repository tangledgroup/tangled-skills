# The Ralph Wiggum Loop

## Origin

Created by Geoffrey Huntley and named after Ralph Wiggum from The Simpsons: "Me fail English? That's unpossible!" — just keep trying until you succeed.

At its purest form, Ralph is a Bash loop:

```bash
while :; do cat PROMPT.md | claude ; done
```

This is "deterministically bad in an undeterministic world" — it fails predictably but in ways you can address through tuning.

## How The Loop Really Works

### Iteration Lifecycle

Each iteration follows this cycle:

1. **Fresh context** — Previous conversation is discarded. Only files on disk persist.
2. **Prompt assembly** — Ralph reads `PROMPT.md` (or inline prompt), injects guardrails, memories, scratchpad state, and hat instructions if active.
3. **Backend execution** — The assembled prompt is passed to the AI CLI backend via PTY (pseudo-terminal) for real-time output capture.
4. **Output parsing** — Ralph captures agent output line by line, looking for:
   - `LOOP_COMPLETE` (or configured completion promise) → loop terminates
   - `ralph emit "topic" payload` → event published to the bus
   - Tool calls and their results
5. **Hat routing** (hat-based mode) — If an event was emitted, the EventBus routes it to the matching hat. That hat's instructions become the prompt for the next iteration.
6. **Checkpoint** — Every N iterations (default: 5), Ralph commits a git checkpoint.
7. **Repeat** — Back to step 1 with fresh context.

### The Completion Promise

The loop terminates when the agent outputs the completion promise string. Default is `LOOP_COMPLETE`. Configurable:

```yaml
event_loop:
  completion_promise: "LOOP_COMPLETE"
```

A hat can output this directly in its response, or the loop can detect a specific event that signals completion.

### Loop Termination Conditions

The loop stops when any of these occurs:

- Agent outputs `LOOP_COMPLETE` (success, exit code 0)
- `max_iterations` reached (exit code 2)
- `max_runtime_seconds` exceeded (exit code 2)
- Idle timeout (`idle_timeout_secs`, default 30 minutes)
- User interrupts via TUI (Ctrl-C, exit code 130)
- Loop requests restart (exit code 3)

### Context Window Management

Ralph optimizes for the "smart zone" — 40-60% of the usable context window. The key principle: **allocate as little as possible to the primary context window**.

What goes into context each iteration:

- The prompt/task description
- Guardrails (rules injected into every prompt)
- Hat instructions (if hat-based mode)
- Memories (auto-injected, budget-limited, default 2000 tokens)
- Scratchpad content (per-hat or global)
- Task list (if tasks enabled)

What stays on disk (not in context):

- The codebase itself (agent reads files as needed via tools)
- Memory file (`.ralph/agent/memories.md`)
- Event history (`.ralph/events.jsonl`)
- Git history

### Scratchpad vs. Context

The scratchpad is a file on disk that persists across iterations. It is the agent's working memory within a single loop run. Each iteration, the scratchpad content is read and injected into the prompt.

```yaml
core:
  scratchpad:
    enabled: true
    path: .ralph/agent/scratchpad.md
```

In hat-based mode, each hat can have its own scratchpad:

```yaml
hats:
  planner:
    scratchpad: .ralph/agent/planner.md
  builder:
    scratchpad: .ralph/agent/builder.md
  reviewer:
    scratchpad:
      enabled: false  # No scratchpad needed
```

When memories and tasks are enabled (default), the legacy scratchpad is disabled in favor of those systems.

## Tuning Ralph

Ralph is tuned like a guitar, not conducted like an orchestra. When Ralph fails in a specific way, add a signal for next time:

### Adding Guardrails

Global rules injected into every prompt:

```yaml
core:
  guardrails:
    - "Always run tests before declaring done"
    - "Never modify production database directly"
    - "Follow existing code patterns in the repository"
```

### Adding Backpressure

Define quality gates that reject incomplete work:

```yaml
hats:
  builder:
    instructions: |
      Implement the feature.
      Evidence required: tests: pass, lint: pass, typecheck: pass, audit: pass, coverage: pass
```

### Recording Memories

When Ralph discovers something useful, store it:

```bash
ralph tools memory add "API handlers return Result<Json<T>, AppError>" -t pattern
```

Memories are auto-injected in future iterations, so the agent learns.

### The Tuning Loop

1. Run Ralph and watch the TUI stream
2. Observe where Ralph goes wrong (wrong direction, missing steps, bad output)
3. Add a signal: guardrail, backpressure gate, memory, or scratchpad note
4. Let Ralph iterate again with the new signal
5. Repeat until Ralph produces acceptable results

## Prompt Design

There is no "perfect prompt." Prompts evolve through continual tuning based on observation of LLM behavior. Key principles:

- **One thing per loop** — Ask Ralph to do one focused task. Relax as the project progresses, but narrow back down if things go off the rails.
- **Reference files, don't inline everything** — Use `@fix_plan.md` and `@specs/*` to allocate plans and specs to context every loop.
- **Deterministic stack allocation** — Items you want in context every loop (plans, specs) should be referenced consistently.
- **Trust the agent's prioritization** — LLMs are surprisingly good at reasoning about what is important to implement next.

## Anti-Patterns

- **Building features into the orchestrator that agents can handle** — Agents are smart; let them do the work
- **Complex retry logic** — Fresh context handles recovery naturally
- **Detailed step-by-step instructions** — Use backpressure gates instead
- **Scoping work at task selection time** — Scope at plan creation
- **Assuming functionality is missing without code verification** — Search first

## Real-World Results

- Y Combinator hackathon: team shipped 6 repositories overnight
- One engineer completed a $50,000 contract for $297 in API costs
- Geoffrey Huntley's 3-month loop created CURSED, a complete esoteric programming language
