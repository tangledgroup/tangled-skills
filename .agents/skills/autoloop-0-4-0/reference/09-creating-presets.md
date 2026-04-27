# Creating Custom Presets

## Directory Structure

A preset is a self-contained loop definition in a single directory. All shipped presets follow the same structure — nothing special about the built-in `auto*` family that a custom preset cannot do.

```
my-preset/
├── autoloops.toml    # Loop configuration (required)
├── topology.toml     # Role deck and handoff graph (required for multi-role loops)
├── harness.md        # Shared instructions loaded every iteration (required)
├── README.md         # Human-facing description (optional)
└── roles/            # Role prompt files referenced by topology.toml
    ├── first-role.md
    ├── second-role.md
    └── ...
```

## Step 1: Define the Topology

`topology.toml` declares roles, their allowed events, and how events route between roles.

```toml
name = "my-preset"
completion = "task.complete"

[[role]]
id = "analyst"
emits = ["analysis.done", "task.complete"]
prompt_file = "roles/analyst.md"

[[role]]
id = "implementer"
emits = ["impl.ready", "impl.blocked"]
prompt_file = "roles/implementer.md"

[[role]]
id = "verifier"
emits = ["verified", "rejected"]
prompt_file = "roles/verifier.md"

[handoff]
"loop.start" = ["analyst"]
"analysis.done" = ["implementer"]
"impl.ready" = ["verifier"]
"impl.blocked" = ["analyst"]
"verified" = ["analyst"]
"rejected" = ["implementer"]
```

Key rules:

- Every role needs an `id`, an `emits` list, and either `prompt_file` or `prompt`
- `prompt_file` paths are relative to the preset directory
- The `[handoff]` section maps events to roles that should handle them
- `"loop.start"` is the synthetic event emitted at iteration 1 — use it to define which role kicks off the loop
- Events not listed in the handoff map cause all roles to be suggested (no routing preference)

## Step 2: Write Role Prompts

Each role gets a markdown file in `roles/`. A role prompt should:

1. **Open with identity** — "You are the analyst." This anchors the model.
2. **State what the role does NOT do** — "Do not implement. Do not verify." Boundary-setting prevents role drift.
3. **Define the job** — Numbered steps for what the role does on every activation.
4. **Specify when to emit each event** — Be explicit about the conditions for each event in the role's `emits` list.
5. **List rules** — Constraints, defaults, and fail-closed behaviors.

Example (`roles/analyst.md`):

```markdown
You are the analyst.

Do not implement. Do not verify.

Your job:
1. Read the objective and current state.
2. Break the problem into a prioritized list of tasks.
3. Hand the next task to the implementer.

Emit:
- `analysis.done` with the next task description.
- `task.complete` only when all tasks are done and verified.

Rules:
- One active task at a time.
- Be specific enough that the implementer can act without guessing.
```

## Step 3: Write the Harness Instructions

`harness.md` contains shared rules injected into every iteration regardless of which role is active:

```markdown
This is a custom analysis-and-implementation loop.

Global rules:
- Shared working files are the source of truth: `{{STATE_DIR}}/tasks.md`, `{{STATE_DIR}}/progress.md`.
- One task at a time. Do not start the next task before the current one is verified.
- Use the event tool instead of prose-only handoffs.
- Fresh context every iteration: re-read shared working files before acting.
- Use `{{TOOL_PATH}} memory add learning ...` for durable learnings.
- Do not invent extra phases. Stay inside analyst → implementer → verifier.

State files:
- `{{STATE_DIR}}/tasks.md` — task list with priorities and status.
- `{{STATE_DIR}}/progress.md` — current task, verification results.
```

### Template Placeholders

Use `{{STATE_DIR}}` and `{{TOOL_PATH}}` instead of hardcoding `.autoloop/` paths. The harness expands these at load time:

- `{{STATE_DIR}}` — the loop's state directory (e.g., `.autoloop`)
- `{{TOOL_PATH}}` — the full event tool path (e.g., `./.autoloop/autoloops`)

Raw `.autoloop/` paths in prompt text are not supported and will cause a load error.

## Step 4: Configure the Loop

`autoloops.toml` sets iteration limits, backend, completion conditions, and memory/review settings:

```toml
event_loop.max_iterations = 100
event_loop.completion_event = "task.complete"
event_loop.completion_promise = "LOOP_COMPLETE"
event_loop.required_events = ["verified"]

backend.kind = "pi"
backend.command = "pi"
backend.timeout_ms = 300000

review.enabled = true
review.timeout_ms = 300000

memory.prompt_budget_chars = 8000
harness.instructions_file = "harness.md"

core.state_dir = ".autoloop"
core.journal_file = ".autoloop/journal.jsonl"
core.memory_file = ".autoloop/memory.jsonl"
```

## Step 5: Run the Preset

```bash
# From a custom directory
autoloop run path/to/my-preset "Your objective here"

# Built-in presets by name
autoloop run autocode "Your objective here"

# Override backend
autoloop run -b claude --preset autocode "Your objective here"
```

## Design Patterns

**Linear pipeline:** analyst → implementer → verifier → analyst (cycle) or task.complete

**Rejection loop:** verifier rejects back to implementer, creating tighten-until-correct cycles

**Blocked escalation:** `.blocked` event routes to a role that can replan

**Fan-back:** multiple events route to the same convergence-point role

## Checklist

Before running a new preset:

- [ ] Every event in every role's `emits` list appears in the `[handoff]` map
- [ ] `"loop.start"` is mapped to the kick-off role
- [ ] `event_loop.completion_event` matches a completion event in at least one role's `emits`
- [ ] Required events are reachable in the handoff graph
- [ ] Role prompt files exist at declared paths
- [ ] `harness.md` exists and uses `{{STATE_DIR}}` / `{{TOOL_PATH}}` placeholders
