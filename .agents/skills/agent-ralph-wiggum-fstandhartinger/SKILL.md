---
name: agent-ralph-wiggum-fstandhartinger
description: Autonomous AI coding with spec-driven development combining iterative bash loops and SpecKit-style specifications for fully autonomous AI-assisted software development. Use when building projects that require hands-free AI implementation, working from specification files, or running autonomous development loops with completion verification.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - autonomous-development
  - spec-driven
  - iterative-loops
  - ai-coding
  - ralph-wiggum
  - specification-based
category: development
external_references:
  - https://ralph-wiggum.ai/
  - https://github.com/fstandhartinger/ralph-wiggum
---
## Overview
Autonomous AI coding with spec-driven development combining iterative bash loops and SpecKit-style specifications for fully autonomous AI-assisted software development. Use when building projects that require hands-free AI implementation, working from specification files, or running autonomous development loops with completion verification.

Autonomous AI coding with spec-driven development. Ralph Wiggum combines Geoffrey Huntley's original iterative bash loop methodology with SpecKit-style specifications for fully autonomous AI-assisted software development.

## When to Use
- Building projects that require hands-free AI implementation
- Working from specification files with clear acceptance criteria
- Running autonomous development loops with completion verification
- Implementing features iteratively with self-correction
- Managing multiple specs in priority order
- Needing fresh context windows for each iteration

## Usage Examples
### Install as Agent Skill

```bash
# Using Vercel's add-skill
npx add-skill agent-ralph-wiggum-fstandhartinger

# Using OpenSkills
openskills install agent-ralph-wiggum-fstandhartinger
```

### Manual Setup

See [Setup and Configuration](reference/01-setup-configuration.md) for detailed installation.

## Core Concepts
Ralph Wiggum operates on a simple but powerful principle: **each iteration picks ONE task, implements it completely, verifies acceptance criteria, and only outputs `<promise>DONE</promise>` when 100% complete**.

### The Ralph Loop

```
┌─────────────────────────────────────────────────────────────┐
│                     RALPH LOOP                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    Orient    │───▶│  Pick Task   │───▶│  Implement   │  │
│  │  Read specs  │    │  from Plan   │    │   & Test     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                   │         │
│         ┌────────────────────────────────────────┘         │
│         ▼                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Verify     │───▶│   Commit     │───▶│  Output DONE │  │
│  │  Criteria    │    │   & Push     │    │  (if passed) │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                   │         │
│         ┌────────────────────────────────────────┘         │
│         ▼                                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Bash loop checks for <promise>DONE</promise>         │  │
│  │ If found: next iteration | If not: retry             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

See [The Ralph Loop Methodology](reference/02-ralph-loop-methodology.md) for detailed workflow explanation.

## Running Ralph
### Build Mode (Default)

```bash
./scripts/ralph-loop.sh           # Unlimited iterations
./scripts/ralph-loop.sh 20        # Max 20 iterations
```

### Planning Mode (Optional)

```bash
./scripts/ralph-loop.sh plan      # Create IMPLEMENTATION_PLAN.md from specs
```

See [Running Ralph Loops](reference/03-running-ralph-loops.md) for all commands and modes.

## Creating Specifications
Specifications define what to build with clear acceptance criteria:

```bash
# Using Cursor command
/speckit.specify Add user authentication with OAuth

# Or describe to your AI agent
"Create a spec for implementing the billing dashboard"
```

See [Creating Specifications](reference/04-creating-specifications.md) for spec structure and templates.

## Advanced Topics
## Advanced Topics

- [Setup Configuration](reference/01-setup-configuration.md)
- [Ralph Loop Methodology](reference/02-ralph-loop-methodology.md)
- [Running Ralph Loops](reference/03-running-ralph-loops.md)
- [Creating Specifications](reference/04-creating-specifications.md)
- [Advanced Features](reference/05-advanced-features.md)
- [Troubleshooting](reference/06-troubleshooting.md)

## Troubleshooting
### Stuck Specs

After 10 attempts without completion, specs are flagged as stuck:

```bash
source scripts/lib/nr_of_tries.sh
print_stuck_specs_summary
```

Consider splitting into smaller specs. See [Troubleshooting](reference/06-troubleshooting.md).

### Circuit Breaker

The circuit breaker halts execution after detecting stagnation:

```bash
# Check status
show_circuit_status

# Reset manually
reset_circuit_breaker "Fixed blocking issue"
```

## Important Notes
1. **Acceptance criteria must be testable** - Not "works correctly" but specific verifiable conditions
2. **Fresh context each loop** - Every iteration starts with clean context window
3. **Shared state on disk** - `IMPLEMENTATION_PLAN.md` persists between loops
4. **Planning is optional** - Most projects work fine directly from specs
5. **YOLO mode recommended** - Enables autonomous command execution without approval prompts
