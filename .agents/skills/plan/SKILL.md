---
name: plan
description: |
  Plan skill is a structured workflow system that enables agents to explore codebases safely and execute complex tasks in a controlled, trackable manner through three distinct modes: plan (read-only exploration), exec (write-enabled execution), and status (progress reporting).
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.3.0"
tags:
  - planning
  - workflow
  - task-management
category: agents
external_references:
  - https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/examples/extensions/plan-mode
---

# Plan Mode

## Overview

Plan skill provides three distinct modes for structured code exploration and task execution: **plan** (read-only exploration), **exec** (write access to execute plan steps), and **status** (progress reporting). The agent analyzes the project, creates a numbered plan. On request, agent executes plan step by step with explicit progress tracking through status states.

## When to Use

- Analyzing unfamiliar codebases or documents before making changes
- Creating implementation plans for complex tasks
- Structured task execution with progress tracking
- Safe read-only exploration of project structure

## Commands

- `plan` — Enter plan mode (read-only), create or display the plan
- `exec` — Enter exec mode (full access), execute plan steps
- `status` — Report current plan progress without changing mode

## Usage

1. Enter plan mode with `plan`
2. Analyze codebase and create a numbered plan
3. Switch to exec mode with `exec` to begin execution
4. Agent works through steps, emitting `Executing:` + `⏳ WIP` for each step
5. Use `status` anytime to check progress without changing mode
6. If blockers arise (`❌`, `❓`), resolve them then continue exec from the reset step

## How It Works

### Plan Mode (Read-Only)

Only read-only tools are available. Bash commands are filtered through an allowlist. The agent explores the codebase and creates a plan without making any changes. Output is prefixed with `Plan:` header.

### Exec Mode (Write)

Full tool access is restored. The agent executes plan steps in order, transitioning each through status states. Before starting each step, the agent emits `Executing:` followed by `⏳ WIP`. The agent must reach a terminal state (`✔️`, `⚠️`, `❌`, `❓`) before advancing to the next step. Execution pauses on blockers until they are resolved and reset to `📜 PENDING`.

### Status Mode (Report)

Read-only query that scans conversation history for all status markers and outputs a grouped summary under `Status:` header. Does not modify plan state. Groups steps into: **In Progress** (`⏳`), **Completed** (`✔️`, `⚠️`), **Needs Attention** (`❌`, `❓`), and **Pending** (`📜`).

## Output Headers

Each mode emits a distinct header so the active mode is identifiable at a glance. These headers are machine-parseable.

### `Plan:`

Appears when creating, updating, or displaying the full plan list.

```markdown
Plan:
- 📜 1. PENDING: Set up project structure
- 📜 2. PENDING: Implement user model
- 📜 3. PENDING: Create database schema
```

### `Executing:`

Appears before the agent starts work on a step, paired with `⏳ WIP`.

```markdown
Executing:
⏳ 2. WIP: Implement user model
```

### `Status:`

Appears when reporting progress via `status` or on session resume.

```markdown
Status:
- ✔️ 1. DONE: Implemented profile related API routes
- ⏳ 2. WIP: Implement user model
- 📜 3. PENDING: Create database schema
- ❌ 4. ERROR: Database migration failed
- 📜 5. PENDING: Write integration tests
- ❓ 6. QUESTION: Which cloud provider?
- ❓ 7. QUESTION: Which auth provider?
```

## Plan Format

Output a numbered plan under a `Plan:` header. This format is machine-parseable — steps are extracted automatically.

```markdown
Plan:
- 📜 1. PENDING: Set up project structure
- 📜 2. PENDING: Implement user model
- 📜 3. PENDING: Create database schema
```

### Rules

- Header must be `Plan:` (optionally bold: `**Plan:**`)
- Number steps sequentially starting from 1
- Each step on its own line: `- 📜 n. PENDING: <description>`
- Steps should be concrete and independently verifiable
- All steps start as `📜 PENDING`

## Status Markers

Each step carries a status marker that reflects its current state. Six statuses are available:

| Marker | State | Meaning |
|--------|-------|---------|
| `📜 n. PENDING` | Pending | Step has not been started, or reset after resolution |
| `⏳ n. WIP` | Work In Progress | Agent is actively working on this step |
| `✔️ n. DONE` | Done | Step completed successfully |
| `⚠️ n. WARNING` | Warning | Step completed but with concerns (deprecation, workaround, partial result) |
| `❌ n. ERROR` | Error | Step failed and cannot proceed |
| `❓ n. QUESTION` | Question | Step blocked — needs human input or clarification |

All statuses except bare `📜 PENDING` (initial listing) must include a description after the marker:

```
⏳ 3. WIP: Refactor auth middleware to use async/await
❌ 4. ERROR: Database migration failed — schema conflict with legacy table
⚠️ 2. WARNING: API works but uses deprecated endpoint, migrate before v2
❓ 7. QUESTION: Which auth provider should we use? OAuth or API key?
✔️ 1. DONE: Implemented profile related API routes
```

## Status Transitions

Steps move through states one transition at a time. Only the following transitions are valid:

```
📜 PENDING → ⏳ WIP
⏳ WIP → ✔️ DONE
⏳ WIP → ⚠️ WARNING
⏳ WIP → ❌ ERROR
⏳ WIP → ❓ QUESTION
⚠️ WARNING → 📜 PENDING
❓ QUESTION → 📜 PENDING
❌ ERROR → 📜 PENDING
```

### Transition Rules

- Only `📜 PENDING` can transition to `⏳ WIP` — no skipping ahead
- Only `⏳ WIP` can reach end states (`✔️`, `⚠️`, `❌`, `❓`)
- **Terminal states** (`✔️`, `⚠️`, `❌`, `❓`) end the WIP phase — the agent cannot advance from them directly
- From terminal states, the user or agent can manually reset to `📜 PENDING` to restart the cycle:
  - `⚠️ WARNING → 📜 PENDING` — rework concerns then retry
  - `❓ QUESTION → 📜 PENDING` — clarification received, ready to retry
  - `❌ ERROR → 📜 PENDING` — blocker resolved, ready to retry
- `✔️ DONE` is permanent unless the user explicitly resets it
- Only one step should be `⏳ WIP` at a time — the agent must finish or block the current step before starting another

## Blocker Handling

When a step reaches `❌ ERROR` or `❓ QUESTION`:

- Note which downstream steps depend on it
- Do not advance past the blocker until it resets to `📜 PENDING` and retries
- Explain dependencies explicitly:

```
❌ 4. ERROR: Cannot connect to database — connection string missing
⚠️ Steps 5, 6, and 8 depend on step 4 and are blocked.
```

### Retry Escalation

Track retry cycles per step (`📜 → ⏳ → ❌/❓ → 📜`). After 3+ retries, the agent should recommend pausing and reassessing the plan itself rather than blindly retrying.

## Command Allowlist

### Safe Commands (Allowed in Plan Mode)

- **File inspection:** `cat`, `head`, `tail`, `less`, `more`
- **Search:** `grep`, `find`, `rg`, `fd`
- **Directory:** `ls`, `pwd`, `tree`
- **Git read:** `git status`, `git log`, `git diff`, `git branch`
- **Package info:** `npm list`, `npm outdated`, `yarn info`
- **System info:** `uname`, `whoami`, `date`, `uptime`

### Blocked Commands

- **File modification:** `rm`, `mv`, `cp`, `mkdir`, `touch`
- **Git write:** `git add`, `git commit`, `git push`
- **Package install:** `npm install`, `yarn add`, `pip install`
- **System:** `sudo`, `kill`, `reboot`
- **Editors:** `vim`, `nano`, `code`

## Session Persistence

Plan state (mode, todos, execution progress) survives session resume. On resume:

- Scan for all status markers (`⏳`, `✔️`, `⚠️`, `❌`, `❓`) to rebuild full state
- If a step is `⏳ WIP`, resume in exec mode from that step
- Highlight any `❌ ERROR` or `❓ QUESTION` steps as needing attention
- Summarize completed `✔️ DONE` and `⚠️ WARNING` counts
- If all steps are terminal (`✔️` or `⚠️`), the plan is considered done
- If no execution has started, offer to switch from `plan` to `exec`
