---
name: agent-wiggum-cli-federiconeri
description: Wiggum CLI is an open-source autonomous coding agent that plugs into any codebase — scans your tech stack, generates feature specs through AI-powered interviews, and runs autonomous Ralph loops via Claude Code, Codex CLI, or any CLI-based coding agent. Agent mode reads your GitHub backlog, generates specs, runs loops, reviews diffs, and auto-merges PRs with zero intervention. Use when automating feature development end-to-end, running autonomous coding loops against specs, managing GitHub backlogs with AI, or implementing the Ralph loop methodology in production projects.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.18.3"
tags:
  - autonomous-coding
  - ralph-loop
  - spec-driven-development
  - ai-agent
  - claude-code
  - codex-cli
  - github-integration
  - backlog-automation
category: development
external_references:
  - https://github.com/federiconeri/wiggum-cli
  - https://wiggum.app/
---

# Wiggum CLI v0.18.3

## Overview

Wiggum is an AI agent CLI by Federico Neri that plugs into any codebase and ships features autonomously. It works in two phases. First, **Wiggum itself is the agent**: it scans your project, detects your stack (80+ technologies), and runs an AI-guided interview to produce detailed specs, prompts, and scripts tailored to your codebase. Then it delegates coding loops to Claude Code or Codex CLI, running **implement → test → fix** cycles until completion.

Built on the [Ralph loop technique](https://ghuntley.com/ralph/) pioneered by Geoffrey Huntley, Wiggum provides structured phase isolation (plan, implement, test, verify, PR) rather than undifferentiated retry loops. Specs are agent-agnostic markdown — they work with any CLI-based coding agent.

```
         Wiggum (agent)                    Coding Agent
  ┌────────────────────────────┐    ┌────────────────────┐
  │                            │    │                    │
  │  Scan ──▶ Interview ──▶ Spec ──▶  Run loops           │
  │  detect      AI-guided   .ralph/   implement         │
  │  80+ tech    questions   specs     test + fix        │
  │  plug&play   prompts     guides    until done        │
  │                            │    │                    │
  └────────────────────────────┘    └────────────────────┘
       runs in your terminal          Claude Code / Codex CLI
```

## When to Use

- Automating feature development from spec to merged PR without manual coding
- Running autonomous coding loops against existing codebases (any language, any framework)
- Generating implementation-ready specs through AI-guided interviews grounded in codebase context
- Processing GitHub backlogs autonomously with `wiggum agent` (priority scheduling, dependency ordering, auto-merge)
- Implementing the Ralph loop methodology with phase-level checkpoints instead of bash-script retry loops
- Setting up CI pipelines for autonomous feature delivery with headless mode

## Core Workflow: Three Commands

```bash
npm install -g wiggum-cli      # install (or use npx wiggum-cli)

wiggum init                    # Phase 1: scan codebase, detect stack, generate context
wiggum new user-auth           # Phase 2: AI interview → detailed feature spec
wiggum run user-auth           # Phase 3: autonomous Ralph loop execution
```

### Interactive Mode (TUI)

Running `wiggum` with no arguments opens the terminal UI — the recommended way to use Wiggum:

- `/init` or `/i` — Scan project, configure AI provider
- `/new <feature>` or `/n` — AI interview → feature spec
- `/run <feature>` or `/r` — Run autonomous coding loop
- `/monitor <feature>` or `/m` — Monitor a running feature in real-time
- `/issue [query]` — Browse GitHub issues and start a spec from issue context
- `/agent [flags]` or `/a` — Run autonomous backlog executor
- `/sync` or `/s` — Re-scan project, update context
- `/config [...]` or `/cfg` — Manage API keys and loop settings

### Headless Mode

For CI pipelines, cron jobs, or integration with other agents:

```bash
wiggum new --auto --goals "add rate limiting to API" --issue #42
wiggum sync
wiggum agent --stream --max-items 5
```

## Generated Files

After `wiggum init`, a `.ralph/` directory is created:

```
.ralph/
├── ralph.config.cjs          # Stack detection results + loop config
├── prompts/
│   ├── PROMPT.md             # Implementation prompt
│   ├── PROMPT_feature.md     # Feature planning
│   ├── PROMPT_e2e.md         # E2E testing
│   ├── PROMPT_verify.md      # Verification
│   ├── PROMPT_review_manual.md  # PR review (stop at PR)
│   ├── PROMPT_review_auto.md    # PR review (review, no merge)
│   └── PROMPT_review_merge.md   # PR review (review + auto-merge)
├── guides/
│   ├── AGENTS.md             # Agent instructions
│   ├── FRONTEND.md           # Frontend patterns
│   ├── SECURITY.md           # Security guidelines
│   └── PERFORMANCE.md        # Performance patterns
├── scripts/
│   └── feature-loop.sh       # Main loop script
├── specs/
│   └── _example.md           # Example spec template
└── LEARNINGS.md              # Accumulated project learnings
```

## Requirements

- **Node.js** >= 18.0.0
- **Git** (for worktree features)
- **GitHub CLI (`gh`)** for `/issue` browsing and backlog agent operations
- An AI provider API key (Anthropic, OpenAI, or OpenRouter)
- A supported coding CLI: [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and/or [Codex CLI](https://github.com/openai/codex)

## AI Providers

| Provider | Environment Variable |
|----------|---------------------|
| Anthropic | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |

Optional services:

- `TAVILY_API_KEY` — Web search for current best practices
- `CONTEXT7_API_KEY` — Up-to-date documentation lookup

Keys are stored in `.ralph/.env.local` and never leave your machine.

## Advanced Topics

**The Ralph Loop Methodology**: How the loop really works — phase isolation, checkpoints, error recovery → [Ralph Loop Deep Dive](reference/01-ralph-loop-methodology.md)

**CLI Command Reference**: Full coverage of all commands with flags and options → [CLI Reference](reference/02-cli-reference.md)

**Agent Mode & Backlog Automation**: Autonomous GitHub backlog processing with dependency scheduling → [Agent Mode](reference/03-agent-mode.md)

**Configuration & Loop Tuning**: Model selection, review modes, worktree isolation, prompt templates → [Configuration](reference/04-configuration.md)
