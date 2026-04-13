# Setup and Configuration

Complete installation guide for Ralph Wiggum, including directory structure, scripts, and configuration.

## Installation Methods

### Method 1: AI-Guided Setup (Recommended)

Point your AI agent to the Ralph Wiggum repository:

```
"Set up Ralph Wiggum in my project using https://github.com/fstandhartinger/ralph-wiggum"
```

The agent will read `INSTALLATION.md` and guide you through an interactive setup with a pleasant interview focused on your project vision.

### Method 2: Manual Installation

Follow these steps for manual setup.

## Directory Structure

Create the required directories:

```bash
mkdir -p .specify/memory
mkdir -p specs
mkdir -p scripts/lib
mkdir -p logs
mkdir -p history
mkdir -p completion_log
mkdir -p .cursor/commands
mkdir -p .claude/commands
```

### Directory Purposes

| Directory | Purpose |
|-----------|---------|
| `.specify/memory/` | Constitution and project context |
| `specs/` | Specification files (NNN-feature-name/spec.md) |
| `scripts/` | Ralph loop scripts and libraries |
| `scripts/lib/` | Helper libraries (circuit_breaker.sh, nr_of_tries.sh, etc.) |
| `logs/` | Session and iteration logs |
| `history/` | Project history documents |
| `completion_log/` | Completed spec summaries with diagrams |
| `.cursor/commands/` | Cursor IDE slash commands |
| `.claude/commands/` | Claude Code commands |

## Downloading Scripts

### Main Loop Scripts

```bash
# Claude Code (main script)
curl -o scripts/ralph-loop.sh \
  https://raw.githubusercontent.com/fstandhartinger/ralph-wiggum/main/scripts/ralph-loop.sh

# OpenAI Codex CLI
curl -o scripts/ralph-loop-codex.sh \
  https://raw.githubusercontent.com/fstandhartinger/ralph-wiggum/main/scripts/ralph-loop-codex.sh

# Google Gemini
curl -o scripts/ralph-loop-gemini.sh \
  https://raw.githubusercontent.com/fstandhartinger/ralph-wiggum/main/scripts/ralph-loop-gemini.sh

# GitHub Copilot
curl -o scripts/ralph-loop-copilot.sh \
  https://raw.githubusercontent.com/fstandhartinger/ralph-wiggum/main/scripts/ralph-loop-copilot.sh

# Make executable
chmod +x scripts/ralph-loop*.sh
```

### Library Scripts

```bash
# Spec queue helpers
curl -o scripts/lib/spec_queue.sh \
  https://raw.githubusercontent.com/fstandhartinger/ralph-wiggum/main/scripts/lib/spec_queue.sh

# NR_OF_TRIES tracking
curl -o scripts/lib/nr_of_tries.sh \
  https://raw.githubusercontent.com/fstandhartinger/ralph-wiggum/main/scripts/lib/nr_of_tries.sh

# Circuit breaker
curl -o scripts/lib/circuit_breaker.sh \
  https://raw.githubusercontent.com/fstandhartinger/ralph-wiggum/main/scripts/lib/circuit_breaker.sh

# Date utilities
curl -o scripts/lib/date_utils.sh \
  https://raw.githubusercontent.com/fstandhartinger/ralph-wiggum/main/scripts/lib/date_utils.sh

# Notifications (Telegram)
curl -o scripts/lib/notifications.sh \
  https://raw.githubusercontent.com/fstandhartinger/ralph-wiggum/main/scripts/lib/notifications.sh

# Response analyzer
curl -o scripts/lib/response_analyzer.sh \
  https://raw.githubusercontent.com/fstandhartinger/ralph-wiggum/main/scripts/lib/response_analyzer.sh

# Make executable
chmod +x scripts/lib/*.sh
```

## Creating the Constitution

The constitution is Ralph's source of truth. Create `.specify/memory/constitution.md`:

```markdown
# [Project Name] Constitution

> [Brief project vision - what it is, what problem it solves, who it's for]

---

## Context Detection

**Ralph Loop Mode** (started by ralph-loop*.sh):
- Pick highest priority incomplete spec from `specs/`
- Implement, test, commit, push
- Output `<promise>DONE</promise>` only when 100% complete
- Output `<promise>ALL_DONE</promise>` when no work remains

**Interactive Mode** (normal conversation):
- Be helpful, guide decisions, create specs

---

## Core Principles

[Principle 1 - e.g., "User experience first"]
[Principle 2 - e.g., "Keep it simple"]
[Principle 3 - e.g., "Security above all"]

---

## Technical Stack

[List your stack or "Detected from codebase"]

---

## Autonomy

YOLO Mode: ENABLED
Git Autonomy: ENABLED

---

## Specs

Specs live in `specs/` as markdown files. Pick the highest priority incomplete spec (lower number = higher priority). A spec is incomplete if it lacks `## Status: COMPLETE`.

When all specs are complete, re-verify a random one before signaling done.

---

## NR_OF_TRIES

Track attempts per spec via `<!-- NR_OF_TRIES: N -->` at the bottom of the spec file. Increment each attempt. At 10+, the spec is too hard — split it into smaller specs.

---

## History

Append a 1-line summary to `history.md` after each spec completion. For details, create `history/YYYY-MM-DD--spec-name.md` with lessons learned, decisions made, and issues encountered. Check history before starting work on any spec.

---

## Completion Signal

All acceptance criteria verified, tests pass, changes committed and pushed → output `<promise>DONE</promise>`. Never output this until truly complete.
```

### Optional: Telegram Notifications Section

Add to constitution if using Telegram:

```markdown
---

## Telegram Notifications

Send progress via Telegram using env vars `TG_BOT_TOKEN` and `TG_CHAT_ID`.

After completing a spec:
  curl -s -X POST "https://api.telegram.org/bot$TG_BOT_TOKEN/sendMessage" \
    -d chat_id="$TG_CHAT_ID" -d parse_mode=Markdown \
    -d text="✅ *Completed:* {spec name}%0A{one-line summary}"

Also notify on: 3+ consecutive failures, stuck specs (NR_OF_TRIES >= 10).
```

### Optional: GitHub Issues Section

Add to constitution if working on GitHub issues:

```markdown
---

## GitHub Issues

Work on issues from `{OWNER/REPO}` in addition to specs. Use `gh` CLI:
  gh issue list --repo {OWNER/REPO} --state open
  gh issue close <number> --repo {OWNER/REPO}
```

### Optional: Completion Logs Section

Add to constitution if tracking completions:

```markdown
---

## Completion Logs

After each spec, create `completion_log/YYYY-MM-DD--HH-MM-SS--spec-name.md` with a brief summary.
```

## Agent Entry Files

### AGENTS.md (project root)

```markdown
# Agent Instructions

**Read:** `.specify/memory/constitution.md`

That file is your source of truth for this project.
```

### CLAUDE.md (project root)

Same content as AGENTS.md.

## Cursor Commands (Optional)

### /speckit.specify Command

Create `.cursor/commands/speckit.specify.md`:

```markdown
---
description: Create or update a feature specification from a natural language description.
---

## User Input

```text
$ARGUMENTS
```

Given that description:

1. **Generate a concise short name** (2-4 words) for the spec folder
2. **Determine the next spec number** (find highest N, use N+1, zero-padded to 3 digits)
3. Create the spec directory structure:
   ```bash
   mkdir -p specs/NNN-short-name/checklists
   ```
4. Write the spec using the template structure
5. **Completion Signal**: Ensure `## Completion Signal` section with checklist and testing requirements
6. Create a quality checklist at `specs/NNN-short-name/checklists/requirements.md`

Return: SUCCESS (spec ready for implementation via Ralph Wiggum)
```

## Environment Variables

### Required for Full Functionality

| Variable | Purpose | How to Get |
|----------|---------|------------|
| `TG_BOT_TOKEN` | Telegram bot authentication | Create bot via @BotFather on Telegram |
| `TG_CHAT_ID` | Telegram chat/channel ID | Get from `/getUpdates` API after messaging bot |
| `CHUTES_API_KEY` | Audio TTS for voice notifications | Sign up at https://chutes.ai |

### Setting Environment Variables

**Shell profile (~/.bashrc, ~/.zshrc):**
```bash
export TG_BOT_TOKEN="your-bot-token-here"
export TG_CHAT_ID="your-chat-id-here"
export CHUTES_API_KEY="cpk_your-key-here"
```

**Project .env file:**
```bash
# Project root .env
TG_BOT_TOKEN=your-bot-token-here
TG_CHAT_ID=your-chat-id-here
CHUTES_API_KEY=cpk_your-key-here
```

Then source before running:
```bash
source .env
./scripts/ralph-loop.sh
```

## Version Tracking

Get the current Ralph Wiggum commit hash for your constitution:

```bash
git ls-remote https://github.com/fstandhartinger/ralph-wiggum.git HEAD | cut -f1
```

Store this in your constitution to track which version you're using.

## Verification

After setup, verify everything works:

```bash
# Check scripts are executable
ls -la scripts/ralph-loop.sh

# Verify directory structure
ls -la .specify/memory/ specs/ logs/

# Test constitution exists
cat .specify/memory/constitution.md

# Run with help
./scripts/ralph-loop.sh --help
```

## Next Steps

1. Create your first specification: `/speckit.specify [feature description]`
2. Start the loop: `./scripts/ralph-loop.sh`
3. Monitor progress in `logs/` directory

See [Running Ralph Loops](03-running-ralph-loops.md) for execution details.
