---
name: rtk-0-42-0
description: CLI proxy that filters and compresses command outputs before they reach LLM context, reducing token consumption by 60-90%. Supports 100+ commands across git, cargo, JavaScript, Python, Go, Docker, Kubernetes, AWS, and more. Use when working with AI coding assistants (Claude Code, Cursor, Copilot, Gemini, Codex, etc.) to reduce LLM token usage during development workflows.
---

# RTK 0.42.0 — Rust Token Killer

## Overview

RTK is a high-performance CLI proxy written in Rust that sits between AI coding assistants and development tools. It intercepts shell commands, filters and compresses their output, and returns only what matters to the LLM — eliminating boilerplate, progress bars, passing test output, and noise.

**Result:** 60–90% fewer tokens consumed per command, with ~5–15ms overhead. Single binary, zero dependencies.

RTK uses four filtering strategies: **smart filtering** (removes noise), **grouping** (aggregates similar items), **truncation** (keeps relevant context, cuts redundancy), and **deduplication** (collapses repeated lines with counts).

## When to Use

- Setting up or configuring RTK for an AI coding assistant
- Diagnosing why certain commands aren't being filtered
- Looking up the correct `rtk` command syntax for a specific tool (git, cargo, docker, AWS, etc.)
- Querying token savings analytics (`rtk gain`, `rtk discover`)
- Configuring per-project or global RTK behavior via `config.toml`
- Integrating RTK with non-hook agents (Cline, Windsurf, Codex, Kilo Code, Antigravity)

## Core Concepts

### Architecture

```
Agent runs: git status
    ↓
Hook intercepts (PreToolUse / plugin event)
    ↓
rtk rewrite "git status"  →  "rtk git status"
    ↓
Agent executes: rtk git status
    ↓
RTK runs git status, captures output, filters it
    ↓
LLM sees compact output (~200 tokens vs ~2,000)
```

### Integration Tiers

| Tier | Mechanism | Examples |
|------|-----------|----------|
| **Shell hook** | Intercept via agent API, transparent rewrite | Claude Code, Cursor, Gemini CLI, Copilot |
| **Plugin** | TypeScript/Python plugin, in-place mutation | OpenCode, Pi, Hermes, OpenClaw |
| **Rules file** | Prompt-level instructions (model must comply) | Cline, Windsurf, Codex, Kilo Code, Antigravity |

Shell hooks guarantee rewriting. Rules files rely on the model following instructions.

### Command Categories & Typical Savings

- **Git:** 75–93% — `rtk git status`, `rtk git log`, `rtk git diff`
- **Test runners:** ~90% — `rtk cargo test`, `rtk pytest`, `rtk go test`, `rtk jest`
- **Build/lint:** 80–90% — `rtk cargo build`, `rtk tsc`, `rtk ruff check`
- **Docker/K8s:** 80% — `rtk docker ps`, `rtk kubectl pods`
- **AWS CLI:** variable — `rtk aws ec2 describe-instances`, `rtk aws lambda list-functions`
- **Files/search:** 70–80% — `rtk ls`, `rtk read`, `rtk grep`, `rtk find`

### Configuration

Global config: `~/.config/rtk/config.toml` (Linux) or `~/Library/Application Support/rtk/config.toml` (macOS).

Key sections:
- `[hooks] exclude_commands` — commands to never auto-rewrite
- `[tee]` — save raw output on command failure for LLM inspection
- `[filters] ignore_dirs / ignore_files` — paths excluded from output
- `[telemetry] enabled` — anonymous daily usage pings (disabled by default)

Environment variable overrides:
- `RTK_DISABLED=1` — disable RTK for a single command
- `RTK_TELEMETRY_DISABLED=1` — block telemetry regardless of consent
- `RTK_TEE_DIR` — override tee directory
- `RTK_HOOK_AUDIT=1` — enable hook audit logging

### Token Savings Example (30-min Claude Code session)

| Operation | Standard | RTK | Savings |
|-----------|----------|-----|---------|
| `ls` / `tree` (10×) | 2,000 | 400 | -80% |
| `cat` / `read` (20×) | 40,000 | 12,000 | -70% |
| `cargo test` (5×) | 25,000 | 2,500 | -90% |
| `git status` (10×) | 3,000 | 600 | -80% |
| `pytest` (4×) | 8,000 | 800 | -90% |
| **Total** | ~118,000 | ~23,900 | **-80%** |

## Installation

See [Installation & Setup](reference/01-installation-setup.md) for all install methods (Homebrew, quick install, cargo, pre-built binaries) and per-agent initialization commands.

## Supported Agents

RTK supports 14+ AI coding tools. See [Supported Agents](reference/02-supported-agents.md) for full setup commands, integration tier details, and per-agent quirks.

## Command Reference

See [Command Categories](reference/03-command-categories.md) for the complete list of 100+ supported commands organized by ecosystem (git, cargo, JS/TS, Python, Go, Ruby, Docker/K8s, AWS, files/search, cloud/data).

## Advanced Topics

**Installation & Setup**: Homebrew, cargo, pre-built binaries, per-agent init → [Installation & Setup](reference/01-installation-setup.md)
**Supported Agents**: 14+ AI tools across 3 integration tiers → [Supported Agents](reference/02-supported-agents.md)
**Command Reference**: 100+ commands by ecosystem with savings data → [Command Categories](reference/03-command-categories.md)
**Analytics & Telemetry**: Token savings, discover missed savings, data collection → [Analytics & Telemetry](reference/04-analytics-telemetry.md)

## Analytics & Telemetry

See [Analytics & Telemetry](reference/04-analytics-telemetry.md) for `rtk gain`, `rtk discover`, `rtk session` usage and telemetry data collection details.

## Usage Examples

### Quick Start (Claude Code)

```bash
# Install hook globally — rewrites commands transparently
rtk init --global

# Restart Claude Code, then use tools normally
git status        # → auto-rewritten to rtk git status
cargo test        # → auto-rewritten to rtk cargo test

# Check savings
rtk gain          # shows token savings dashboard
```

### Per-Category Commands

```bash
# Git — compact status, one-line log, condensed diff
rtk git status
rtk git log -n 10
rtk git diff

# Test runners — failures only
rtk cargo test
rtk pytest
rtk go test
rtk jest

# Build & lint — grouped by file/rule
rtk cargo build
rtk tsc
rtk ruff check

# Docker/Kubernetes — compact listings
rtk docker ps
rtk kubectl pods

# AWS — stripped secrets, one-line output
rtk aws sts get-caller-identity
rtk aws ec2 describe-instances

# Files & search — structured output
rtk ls .
rtk read file.rs -l aggressive   # signatures only
rtk grep "pattern" .
```

### Analytics

```bash
# Token savings dashboard
rtk gain
rtk gain --daily
rtk gain --weekly
rtk gain --all --format json    # export for dashboards

# Find missed savings (commands that ran without RTK)
rtk discover
rtk discover --all --since 7

# Session adoption rate
rtk session
```

### Configuration & Overrides

```bash
# Show current config
rtk config
rtk config --create             # create with defaults

# Disable RTK for one command
RTK_DISABLED=1 git status

# Dry-run init (preview without writing)
rtk init --global --dry-run -v

# Telemetry management
rtk telemetry status
rtk telemetry disable
rtk telemetry forget            # delete all data
```
