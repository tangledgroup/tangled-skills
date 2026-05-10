---
name: agent-ralph-loop-claude
description: Implements the Ralph Wiggum technique as a Claude Code plugin for iterative, self-referential AI development loops. Use when building projects that require hands-free AI implementation through continuous bash-style loops inside a single Claude Code session, where the same prompt is repeatedly fed back until completion criteria are met.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - claude-code
  - plugin
  - iterative-development
  - autonomous-agents
  - ralph-wiggum
category: agent-frameworks
external_references:
  - https://claude.com/plugins/ralph-loop
  - https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop
---

# Ralph Loop Claude Plugin v1.0.0

## Overview

Ralph Loop is a Claude Code plugin that implements the **Ralph Wiggum technique** — an iterative development methodology based on continuous AI agent loops. As Geoffrey Huntley describes it: **"Ralph is a Bash loop"** — a `while true` loop that repeatedly feeds an AI agent the same prompt, allowing it to iteratively improve its work until completion.

The plugin works entirely **inside your current Claude Code session** — no external bash loops needed. A Stop hook intercepts Claude's exit attempts and feeds the same prompt back, creating a self-referential feedback loop where Claude sees its own previous work in files and git history on each iteration.

## When to Use

**Good for:**

- Well-defined tasks with clear success criteria
- Tasks requiring iteration and refinement (e.g., getting tests to pass)
- Greenfield projects where you can walk away
- Tasks with automatic verification (tests, linters, build checks)

**Not good for:**

- Tasks requiring human judgment or design decisions
- One-shot operations
- Tasks with unclear success criteria
- Production debugging (use targeted debugging instead)

## Core Concepts

### The Ralph Loop Mechanism

The core loop works like this:

1. You run `/ralph-loop` with a task description once
2. Claude works on the task, modifying files
3. Claude tries to exit the session
4. A Stop hook intercepts the exit attempt
5. The Stop hook feeds the **same prompt** back to Claude
6. Claude sees its previous work in files and git history
7. Claude autonomously improves on its past work
8. Repeat until completion criteria are met

The "self-referential" aspect comes from Claude seeing its own previous work persisted in files — not from feeding output text back as input. Each iteration starts fresh with the same prompt, but the workspace has evolved.

### State Management

Ralph Loop uses a markdown state file at `.claude/ralph-loop.local.md` with YAML frontmatter:

```yaml
---
active: true
iteration: 1
session_id: <session-id>
max_iterations: 20
completion_promise: "DONE"
started_at: "2025-01-15T10:30:00Z"
---

Your task prompt text here...
```

The state file tracks iteration count, session isolation, max iterations, and the completion promise. The Stop hook reads this file to decide whether to block exit and continue the loop.

### Completion Promises

To signal genuine task completion, Claude outputs a `<promise>` tag:

```
<promise>TASK COMPLETE</promise>
```

The Stop hook extracts text from `<promise>` tags and compares it against the `--completion-promise` value. The match must be exact — no partial or fuzzy matching.

### Session Isolation

Each Ralph loop is scoped to a specific Claude Code session via `session_id`. If multiple Claude Code sessions are open in the same project, only the session that started the loop will be affected by its Stop hook.

## Advanced Topics

**Plugin Architecture**: Internal structure — commands, hooks, scripts, and plugin manifest → [Plugin Architecture](reference/01-plugin-architecture.md)

**Stop Hook Deep Dive**: The exit-interception mechanism, transcript parsing, and loop continuation logic → [Stop Hook Deep Dive](reference/02-stop-hook-deep-dive.md)

**Prompt Engineering**: Writing effective Ralph prompts with clear completion criteria and self-correction patterns → [Prompt Engineering](reference/03-prompt-engineering.md)

**Setup Script Reference**: Argument parsing, state file creation, and validation logic → [Setup Script Reference](reference/04-setup-script-reference.md)
