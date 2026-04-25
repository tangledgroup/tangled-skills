---
name: plan
description: |
  Read-only exploration mode for safe code analysis. Restricts tools to read-only operations, extracts numbered steps from Plan: sections, tracks progress with [DONE: n] markers, and persists state across sessions. Use when analyzing unfamiliar codebases before making changes, creating implementation plans, or needing structured task execution with progress tracking.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - planning
  - workflow
  - task-management
  - read-only
category: agents
external_references:
  - https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/examples/extensions/plan-mode
---
## Overview
Plan mode restricts the agent to read-only tools and commands during code exploration. The agent analyzes the project, creates a numbered plan, and executes it step by step with explicit progress tracking. Two modes: **plan** (read-only) and **execution** (full access).

## When to Use
- Analyzing unfamiliar codebases before making changes
- Creating implementation plans for complex tasks
- Structured task execution with progress tracking
- Safe read-only exploration of project structure

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Commands
- `plan` — Toggle plan mode on/off
- `todo` — Show current plan progress

## Usage
1. Enable plan mode with the `plan` command
2. Ask the agent to analyze code and create a plan
3. The agent outputs a numbered plan under a `Plan:` header
4. Choose to execute the plan
5. During execution, the agent marks steps complete with `[DONE: n]` tags

## How It Works
### Plan Mode (Read-Only)

Only read-only tools are available. Bash commands are filtered through an allowlist. The agent explores the codebase and creates a plan without making any changes.

### Execution Mode

Full tool access is restored. The agent executes plan steps in order, marks each with `[DONE: n]` completion markers, and tracks progress.

## Plan Format
Output a numbered plan under a `Plan:` header. This format is machine-parseable — steps are extracted automatically.

```
Plan:
- [ ] 1. First step description
- [ ] 2. Second step description
- [ ] 3. Third step description
```

Rules:

- Header must be `Plan:` (optionally bold: `**Plan:**`)
- Number steps sequentially starting from 1
- Each step on its own line: `- [ ] N. <description>`
- Steps should be concrete and independently verifiable
- After completing each task, change `- [ ] N. <description>` to `- [x] N. <description>`

## Completion Markers
After finishing each numbered plan step, include `[DONE: n]` in the response where `n` is the step number.

Example after completing step 2:

```
Added JWT verification helper. Function validates token signature and extracts claims.

[DONE: 2]
```

Multiple completions in one turn:

```
Implemented the refresh endpoint and wrote its tests.

[DONE: 3]
[DONE: 4]
```

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

- If execution was in progress, re-scan messages for `[DONE: n]` markers to rebuild completion state
- Continue from the first incomplete step
- If all steps were completed in a previous session, the plan is considered done

