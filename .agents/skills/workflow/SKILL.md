---
name: workflow
description: Phase-based workflow system with PLAN.md as single source of truth, strict task numbering (P X.Y), inline dependency tracking, and emoji-coded status prefixes (📋💬✔️⚠️🛑❌❓). Use when tackling projects that require structured iteration through Planning, Analysis, Design, Implementation, Testing, Deployment, and Maintenance phases with clear dependency graphs.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - meta
  - workflow
  - task-management
category: meta
---

# workflow skill

**Target Level:** Beginner / Intermediate / Advanced / Expert

## Quick Start (first open)

1. **No PLAN.md?** → Create `PLAN.md` from the template at the bottom and start **Phase 1**.
2. **PLAN.md exists?** → Open it. It contains **all numbered tasks + dependencies**.  
   Continue from the highest-numbered unfinished task whose dependencies are all ✔️ Done.
3. Update **Current Phase** here after every transition.

**Status from PLAN.md:** Read PLAN.md and paste 1-line summary here, e.g. "Phase 3 · Tasks 3.1–3.4 Done · Stopped at 3.5 (depends on 3.2, 2.1)"

## Phases (high-level)

```markdown
## P 1 📋 **Planning**
## P 2 📋 **Analysis**
## P 3 📋 **Design**
## P 4 📋 **Implementation**
## P 5 📋 **Testing**
## P 6 📋 **Deployment**
## P 7 📋 **Maintenance**
```

**All task status, numbering and dependencies live in PLAN.md — see below**

## Live Plan & Tasks

**All phases, tasks, additions, changes, removals, transitions and dependencies live ONLY in [PLAN.md](./PLAN.md)**

**Strict numbering & dependency rules:**
- Every task **MUST** have a unique ID in the exact format **`P X.Y`**  
  (X = phase number, Y = sequential task number **within that phase**)
- Dependencies are encoded **inline** at the end of each task line for maximum efficiency and clarity.
- Format: `P X.Y [emoji] Status - Task description (depends on: P [emoji] A.B, P [emoji] C.D)`
- Dependencies are **phase-bound by default** (most will be same-phase).  
  Cross-phase dependencies are explicitly allowed and listed with full `P [emoji] X.Y`.
- When a task has no dependencies → omit the `(depends on: …)` part.
- This creates a clear directed graph that any reader (human or agent) can parse instantly.

**Task status prefixes (use exactly these emojis):**
- 📋 **To Do** – backlog / new
- 💬 **Doing** – in progress / wip
- ✔️ **Done** – completed / done
- ⚠️ **Warning** – warning / attention required
- 🛑 **Blocked** – blocker
- ❌ **Error** – error
- ❓ **Question** – question or clarification

**Phase transition rules:**
1. Mark all tasks in current phase as ✔️ **Done** (or ❌ **Cancelled**).
2. Create next phase section in PLAN.md.
3. Add new tasks starting with the next phase number (e.g. `P [emoji] 4.1`).
4. Update **Current Phase** in SKILL.md.

**PLAN.md = single source of truth**: project with dependency graph.

**PLAN.md Starter Template**: Here is an example of new file named `PLAN.md`:

```markdown
# PLAN.md — workflow

**Current Phase:** P 1 Planning
**Current Task:** P 1.1 📋 To Do - Define skill success criteria (depends on: none)
**Last Updated:** YYYY-MM-DD HH:MM:SS

## Phase P 1 Planning
P 1.1 📋 To Do - Define skill success criteria (depends on: none)
P 1.2 📋 To Do - Identify prerequisites and constraints

## Phase P 2 Analysis
P 2.1 📋 To Do - Break down workflow into core components (depends on: P 📋 1.1, P 📋 1.2)
P 2.2 📋 To Do - Research best practices and common pitfalls

## Phase P 3 Design
P 3.1 📋 To Do - Create learning roadmap and milestones (depends on: P 📋 2.1)
P 3.2 📋 To Do - Define deliberate practice routines

## Phase P 4 Implementation
P 4.1 📋 To Do - Follow roadmap and study fundamentals (depends on: P 📋 3.1, P 📋 3.2)

## Phase P 5 Testing
P 5.1 📋 To Do - Deliberate practice with feedback loops (depends on: P 📋 4.1)

## Phase P 6 Deployment
P 6.1 📋 To Do - Apply workflow in real scenarios (depends on: P 📋 5.1)

## Phase P 7 Maintenance
P 7.1 📋 To Do - Set up regular practice schedule (depends on: P 📋 6.1)
```
