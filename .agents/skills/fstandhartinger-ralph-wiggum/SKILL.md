---
name: fstandhartinger-ralph-wiggum
description: Autonomous AI coding with spec-driven development combining iterative bash loops and SpecKit-style specifications for fully autonomous AI-assisted software development. Use when building projects that require hands-free AI implementation, working from specification files, or running autonomous development loops with completion verification.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - autonomous-development
  - spec-driven
  - iterative-loops
  - ai-coding
  - ralph-wiggum
  - specification-based
category: development
required_environment_variables:
  - name: TG_BOT_TOKEN
    prompt: "Enter your Telegram bot token for progress notifications (optional)"
    help: "Create a bot via @BotFather on Telegram"
    required_for: "Telegram notifications"
  - name: TG_CHAT_ID
    prompt: "Enter your Telegram chat ID for notifications (optional)"
    help: "Get from https://api.telegram.org/bot<TOKEN>/getUpdates after messaging your bot"
    required_for: "Telegram notifications"
  - name: CHUTES_API_KEY
    prompt: "Enter your Chutes API key for audio TTS notifications (optional)"
    help: "Get from https://chutes.ai for voice message support"
    required_for: "Audio Telegram notifications"
---

# fstandhartinger-ralph-wiggum

Autonomous AI coding with spec-driven development. Ralph Wiggum combines Geoffrey Huntley's original iterative bash loop methodology with SpecKit-style specifications for fully autonomous AI-assisted software development.

## When to Use

- Building projects that require hands-free AI implementation
- Working from specification files with clear acceptance criteria
- Running autonomous development loops with completion verification
- Implementing features iteratively with self-correction
- Managing multiple specs in priority order
- Needing fresh context windows for each iteration

## Quick Start

### Install as Agent Skill

```bash
# Using Vercel's add-skill
npx add-skill fstandhartinger/ralph-wiggum

# Using OpenSkills
openskills install fstandhartinger/ralph-wiggum
```

### Manual Setup

See [Setup and Configuration](references/01-setup-configuration.md) for detailed installation.

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

See [The Ralph Loop Methodology](references/02-ralph-loop-methodology.md) for detailed workflow explanation.

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

See [Running Ralph Loops](references/03-running-ralph-loops.md) for all commands and modes.

## Creating Specifications

Specifications define what to build with clear acceptance criteria:

```bash
# Using Cursor command
/speckit.specify Add user authentication with OAuth

# Or describe to your AI agent
"Create a spec for implementing the billing dashboard"
```

See [Creating Specifications](references/04-creating-specifications.md) for spec structure and templates.

## Reference Files

- [`references/01-setup-configuration.md`](references/01-setup-configuration.md) - Installation, directory structure, and configuration
- [`references/02-ralph-loop-methodology.md`](references/02-ralph-loop-methodology.md) - Core concepts, workflow, and completion signals
- [`references/03-running-ralph-loops.md`](references/03-running-ralph-loops.md) - Commands, modes, logging, and monitoring
- [`references/04-creating-specifications.md`](references/04-creating-specifications.md) - Spec templates, acceptance criteria, and examples
- [`references/05-advanced-features.md`](references/05-advanced-features.md) - Telegram notifications, GitHub issues, circuit breakers
- [`references/06-troubleshooting.md`](references/06-troubleshooting.md) - Common issues, stuck specs, and debugging

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/fstandhartinger-ralph-wiggum/`). All paths are relative to this directory.

## Troubleshooting

### Stuck Specs

After 10 attempts without completion, specs are flagged as stuck:

```bash
source scripts/lib/nr_of_tries.sh
print_stuck_specs_summary
```

Consider splitting into smaller specs. See [Troubleshooting](references/06-troubleshooting.md).

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
